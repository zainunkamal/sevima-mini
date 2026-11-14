# Dokumentasi Implementasi Minggu 4: Generator NIM Multi-Worker, Model `NimCounter`, & Penanganan Konkurensi Database

Dokumen ini mencatat keputusan teknis, arsitektur skema basis data, dan implementasi sistem penerbitan Nomor Induk Mahasiswa (NIM) untuk modul PMB (*Penerimaan Mahasiswa Baru*) pada sistem informasi akademik **SEVIMA Mini** untuk iterasi **Minggu 4**.

---

## 📌 Bagian 1: Desain & Spesifikasi Sistem Penomoran NIM

### 1. Format & Spesifikasi NIM
- **Format:** 4 digit tahun + 3 digit kode prodi + 4 digit nomor urut (zero padding, tanpa tanda hubung).
  $$\text{NIM} = \underbrace{\text{YYYY}}_{\text{4 digit tahun}} + \underbrace{\text{PPP}}_{\text{3 digit prodi}} + \underbrace{\text{NNNN}}_{\text{4 digit nomor urut}}$$
  - Contoh: Tahun `2026`, Kode Prodi `001`, Nomor Urut `1` $\rightarrow$ `20260010001` (11 digit presisi).
- **Independensi Counter:** Nomor urut dihitung ulang mulai dari 1 untuk setiap kombinasi unik `(tahun, kode_prodi)`. Prodi yang berbeda atau tahun akademik yang berbeda memiliki siklus urutan mandiri.
- **Batas Kuota:** Batas maksimum nomor urut adalah **9999**. Jika terlampaui, sistem melempar `NimLimitExceededError` (HTTP 400 Bad Request).
- **Kepatuhan Multi-Worker (Process Isolation):**
  - Aplikasi berjalan dengan banyak worker proses (Uvicorn / Gunicorn workers).
  - **Larangan `threading.Lock`:** Lock berbasis memori di Python hanya bekerja di dalam satu proses (single OS process). Pada lingkungan multi-worker, setiap worker memiliki memori independen (*isolated memory space*). `threading.Lock` tidak mampu mencegah *race condition* antar-worker.
  - **Solusi:** Serialisasi dan isolasi penomoran didelegasikan langsung ke mesin basis data menggunakan **Exclusive Row Lock (`SELECT ... FOR UPDATE`)**.

---

## 📌 Bagian 2: Skema Basis Data & Migrasi Alembic (`nim_counter`)

### 1. Model SQLAlchemy 2.0 (`NimCounter`)
Model didefinisikan pada [app/models/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/models/pmb.py) menggunakan sintaks deklaratif modern SQLAlchemy 2.0:

```python
class NimCounter(Base):
    __tablename__ = "nim_counter"

    # Composite Primary Key: kombinasi unik per tahun & kode prodi
    tahun: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode_prodi: Mapped[str] = mapped_column(String(3), primary_key=True)
    last_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    def __repr__(self) -> str:
        return f"<NimCounter(tahun={self.tahun}, kode_prodi='{self.kode_prodi}', last_number={self.last_number})>"
```

### 2. Skrip Migrasi Alembic
Skrip migrasi terkelola dibuat pada [app/alembic/versions/20261114_0002_create_nim_counter.py](file:///home/zainun/git/istn/sevima-mini/app/alembic/versions/20261114_0002_create_nim_counter.py):
- **`upgrade()`**: Membangun tabel `nim_counter` dengan composite primary key `(tahun, kode_prodi)`.
- **`downgrade()`**: Menghapus tabel `nim_counter` secara bersih.

### 3. Penegakan Unique Constraint pada Kolom `nim`
Pada tabel `calon_mahasiswa`, kolom `nim` dijamin unik di level basis data melalui `unique=True` dan constraint eksplisit `UniqueConstraint('nim', name='uq_calon_mahasiswa_nim')`. Hal ini menjamin bahwa meskipun terjadi kesalahan manusia (input SQL manual langsung ke DB), duplikasi NIM mustahil tersimpan.

---

## 📌 Bagian 3: Implementasi Fungsi `generate_nim` & Transaksi Bersih

Fungsi diimplementasikan pada [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py):

```python
def generate_nim(db: Session, tahun: int, kode_prodi: str) -> str:
    prodi_str = str(kode_prodi).strip().zfill(3)

    # 1. Kueri counter dengan exclusive row lock (FOR UPDATE)
    stmt = (
        select(NimCounter)
        .where(
            NimCounter.tahun == tahun,
            NimCounter.kode_prodi == prodi_str,
        )
        .with_for_update()
    )
    counter = db.scalar(stmt)

    # 2. Inisialisasi awal aman untuk konkurensi via SAVEPOINT (nested transaction)
    if counter is None:
        try:
            with db.begin_nested():
                counter = NimCounter(tahun=tahun, kode_prodi=prodi_str, last_number=0)
                db.add(counter)
                db.flush()
        except IntegrityError:
            pass  # Worker lain sudah melakukan insert di milidetik yang sama

        counter = db.scalar(stmt)

    # 3. Validasi batas kuota 4 digit
    if counter.last_number >= 9999:
        raise NimLimitExceededError(
            f"Batas nomor urut NIM untuk tahun {tahun} prodi {prodi_str} telah melampaui batas maksimum (9999)."
        )

    # 4. Increment counter
    counter.last_number += 1

    # 5. Flush saja (TIDAK commit di sini!)
    db.flush()

    # 6. Format 11 digit zero-padded
    return f"{tahun:04d}{prodi_str}{counter.last_number:04d}"
```

### Prinsip Transaksi:
1. **Tidak Ada Commit Internal:** `generate_nim` hanya memanggil `db.flush()`. Perubahan nomor urut dikirim ke *engine buffer* transaksi aktif tanpa mengakhiri siklus transaksi.
2. **Kepemilikan Transaksi Ada di Endpoint:** Transaksi basis data sepenuhnya menjadi hak endpoint/service layer. Jika operasi berikutnya (misal approval calon mahasiswa) gagal, endpoint dapat melakukan `db.rollback()`, dan kenaikan nomor urut dibatalkan secara bersih tanpa meninggalkan celah nomor urut loncat (*gap*).
3. **Pencegahan Deadlock Inisialisasi Awal:** Penggunaan `with db.begin_nested()` (SAVEPOINT) mencegah benturan *gap-lock* saat baris counter pertama kali dibuat secara bersamaan oleh dua worker.

---

## 📌 Bagian 4: Pola Penanganan `IntegrityError` dengan Rollback & Retry (Maksimal 3 Kali)

Jika terjadi anomali tak terduga (seperti benturan konkurensi unik atau deadlock di InnoDB), alur approval menerapkan pola *retry* dengan *exponential backoff / jitter*:

```python
def approve_calon_mahasiswa(db: Session, calon_id: int, tahun: Optional[int] = None, max_retries: int = 3) -> CalonMahasiswa:
    for attempt in range(1, max_retries + 1):
        try:
            calon = db.scalar(select(CalonMahasiswa).where(CalonMahasiswa.id == calon_id))
            ...
            calon.nim = generate_nim(db, tahun=tahun, kode_prodi=prodi.kode)
            calon.status = StatusPMB.APPROVED
            calon.approved_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(calon)
            return calon

        except (IntegrityError, OperationalError):
            db.rollback()  # Segera lepas kunci dan bersihkan state sesi
            if attempt == max_retries:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Gagal menerbitkan NIM setelah 3 kali percobaan karena konflik konkurensi integritas data.",
                )
            time.sleep(0.05 * attempt)
```

Endpoint FastAPI diekspos melalui rute `POST /api/pmb/calon-mahasiswa/{calon_id}/approve` pada [app/routers/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/routers/pmb.py).

---

## 📌 Bagian 5: Analisis Konkurensi & Siklus Kunci Database

### 1. Apa yang terjadi jika dua request datang bersamaan?
Misalkan **Request A (Worker 1)** dan **Request B (Worker 2)** sama-sama ingin menyetujui calon mahasiswa pada Program Studi `001` untuk Tahun `2026`:
1. **Request A** tiba di database lebih dulu, mengeksekusi `SELECT ... FOR UPDATE`.
2. Engine InnoDB MySQL menempatkan **Exclusive Row Lock (X-Lock / Record Lock)** pada baris `(tahun=2026, kode_prodi='001')`.
3. **Request B** tiba beberapa mikrodetik kemudian dan mengeksekusi `SELECT ... FOR UPDATE` untuk baris yang sama.
4. Karena baris tersebut sedang dikunci X-Lock oleh Transaksi A, **Request B otomatis masuk ke status BLOCKED (menunggu)** di antrean lock InnoDB.
5. Request A membaca `last_number` (misal 5), menaikkannya menjadi 6, mengaitkannya ke calon mahasiswa, dan memanggil `db.commit()`.
6. Begitu Request A selesai commit, InnoDB secara atomik **melepaskan X-Lock**.
7. Request B seketika **terbuka (*unblocked*)**, membaca data ter-commit terbaru (`last_number = 6`), menaikkannya menjadi 7, dan memproses transaksinya sendiri.
8. **Hasil:** Kedua request mendapatkan nomor urut berurutan tanpa duplikasi (`...0006` dan `...0007`) tanpa terjadi *race condition*.
9. **Paralelisme Antar-Prodi:** Jika datang Request C untuk prodi lain (misal `002`), InnoDB hanya mengunci baris `002`. Request C berjalan secara paralel tanpa terhalang oleh Request A maupun B.

### 2. Kapan kunci dilepas?
- Kunci baris database **TIDAK PERNAH dilepas** saat fungsi `generate_nim` selesai dieksekusi atau saat `db.flush()` dipanggil.
- Kunci ditahan sepanjang masa aktif transaksi dan **BARU DILEPAS** ketika salah satu kondisi berikut tercapai:
  1. `db.commit()`: Transaksi berhasil disimpan permanen.
  2. `db.rollback()`: Transaksi dibatalkan/error.
  3. *Connection Drop / Timeout*: Melebihi `innodb_lock_wait_timeout`.
- **Rekomendasi Arsitektur:** Jaga durasi transaksi sependek mungkin. Hindari operasi lambat (seperti memanggil external payment gateway atau pengiriman email) di dalam blok transaksi aktif pemegang kunci.

### 3. Kompatibilitas MySQL InnoDB (Produksi) vs SQLite (Pengujian)
- Pada MySQL InnoDB di produksi: `with_for_update()` diterjemahkan menjadi kueri SQL murni `SELECT ... FOR UPDATE` dengan *Record Locking*.
- Pada SQLite di lingkungan pengujian: Dialek SQLite SQLAlchemy secara otomatis dan aman mengabaikan klausul `FOR UPDATE` (tanpa memunculkan sintaks error), sementara pengujian integritas transaksi tetap berjalan mulus.

---

## 🧪 Bukti Pengujian Otomatis

Implementasi telah diuji secara menyeluruh melalui berkas [tests/test_nim_counter.py](file:///home/zainun/git/istn/sevima-mini/tests/test_nim_counter.py) dengan 9 skenario pengujian spesifik:
1. `test_01_generate_nim_format_and_sequence`: Format 11 digit zero-padded dan kenaikan sekuensial.
2. `test_02_independent_counter_per_combination`: Penghitungan ulang mulai dari 1 per kombinasi `(tahun, kode_prodi)`.
3. `test_03_numeric_prodi_zfill`: Penambahan leading zero otomatis pada kode prodi numerik (misal `"5"` menjadi `"005"`).
4. `test_04_limit_9999_exceeded_raises_error`: Penolakan dan pelemparan `NimLimitExceededError` saat counter mencapai 9999.
5. `test_05_function_does_not_commit_directly`: Bukti bahwa `generate_nim` tidak commit (rollback sesi membatalkan kenaikan counter).
6. `test_06_approve_calon_mahasiswa_success`: Alur lengkap persetujuan pendaftar PMB menghasilkan status `approved` dan NIM terbit.
7. `test_07_approve_idempotent`: Idempotensi persetujuan ganda.
8. `test_08_approve_retry_on_integrity_error`: Simulasi benturan `IntegrityError` memicu mekanisme rollback dan retry hingga 3 kali.
9. `test_09_api_endpoint_approve_success`: Pengujian rute HTTP `POST /api/pmb/calon-mahasiswa/{id}/approve` via `TestClient`.

Seluruh suite pengujian proyek (total 26 pengujian pada `test_api_pmb.py` dan `test_nim_counter.py`, ditambah 7 pengujian pada `test_pmb.py`) **lolos 100% tanpa error**.
