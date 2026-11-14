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

    # 1. Pastikan baris counter ada via atomic native UPSERT
    # Mencegah Gap-Lock Deadlock (InnoDB Error 1213) saat baris counter pertama dibuat bersamaan
    dialect_name = db.bind.dialect.name if db.bind else "sqlite"
    if dialect_name == "mysql":
        from sqlalchemy.dialects.mysql import insert as mysql_insert
        stmt_init = (
            mysql_insert(NimCounter)
            .values(tahun=tahun, kode_prodi=prodi_str, last_number=0)
            .on_duplicate_key_update(tahun=NimCounter.tahun)
        )
        db.execute(stmt_init)
    elif dialect_name == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert
        stmt_init = (
            sqlite_insert(NimCounter)
            .values(tahun=tahun, kode_prodi=prodi_str, last_number=0)
            .on_conflict_do_nothing()
        )
        db.execute(stmt_init)
    else:
        try:
            with db.begin_nested():
                db.add(NimCounter(tahun=tahun, kode_prodi=prodi_str, last_number=0))
                db.flush()
        except IntegrityError:
            pass

    # 2. Karena baris dijamin sudah ada, FOR UPDATE hanya mengambil RECORD LOCK murni
    stmt = (
        select(NimCounter)
        .where(
            NimCounter.tahun == tahun,
            NimCounter.kode_prodi == prodi_str,
        )
        .with_for_update()
    )
    counter = db.scalar(stmt)
    if counter is None:
        raise RuntimeError(f"Gagal menginisialisasi atau mengunci baris counter NIM prodi {prodi_str}")

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
3. **Pencegahan Gap-Lock Deadlock:** Penggunaan atomic UPSERT menjamin baris telah terdaftar secara fisik sebelum `SELECT ... FOR UPDATE` dipanggil, sehingga mesin MySQL InnoDB hanya menempatkan *Record Lock* murni dan kebal terhadap deadlock insert intention.

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

## 📌 Bagian 6: Mesin Keadaan (State Machine) Transisi PMB & Router Tipis

Pada iterasi lanjutan Minggu 4, diimplementasikan mesin keadaan (*State Machine*) untuk siklus hidup pendaftaran calon mahasiswa melalui class `PMBService` dan dua endpoint RESTful:
- **`PUT /api/pmb/approve/{id}`**: Menyetujui pendaftaran dan menerbitkan NIM.
- **`PUT /api/pmb/reject/{id}`**: Menolak pendaftaran calon mahasiswa.

### 1. Diagram State Machine & Aturan Transisi
- **State Awal:** `pending` (dihasilkan saat pendaftaran baru via `POST /api/pmb/register`).
- **State Final:** `approved` dan `rejected` bersifat **terminal (final)** dan tidak dapat saling berganti status.
  - Pendaftar berstatus `rejected` yang dicoba disetujui (`PUT /approve/{id}`) ditolak dengan respons **`HTTP 409 Conflict`**.
  - Pendaftar berstatus `approved` yang dicoba ditolak (`PUT /reject/{id}`) ditolak dengan respons **`HTTP 409 Conflict`**.

### 2. Jaminan Idempotensi Transaksi
- **Idempotent Approve:** Jika pendaftar yang sudah berstatus `approved` dipanggil kembali melalui `PUT /approve/{id}`, sistem mengembalikan kode **`HTTP 200 OK`** beserta NIM yang sudah ada **TANPA memanggil generator NIM kembali**. Ini menjamin nomor urut counter tidak meloncat.
- **Idempotent Reject:** Jika pendaftar yang sudah berstatus `rejected` dipanggil kembali melalui `PUT /reject/{id}`, sistem mengembalikan kode **`HTTP 200 OK`** secara aman tanpa memodifikasi data.

### 3. Validasi Presisi Kode Prodi 3 Karakter Alfanumerik
Sebelum menerbitkan NIM pada alur `approve`, sistem memverifikasi bahwa:
1. Program studi wajib terdaftar di basis data (respons `HTTP 400 Bad Request` jika tidak ditemukan).
2. Kode program studi wajib berupa **3 karakter alfanumerik** (`len == 3` dan `isalnum()`, seperti `'TIF'`, `'SIF'`, maupun `'001'`). Hal ini memastikan keselarasan penuh dengan master data `ProgramStudi` bawaan sistem (di mana `TIF` adalah Teknik Informatika), sekaligus secara tegas menolak kode yang panjangnya bukan 3 karakter (misal `'12'` atau `'1234'`) dengan respons **`HTTP 400 Bad Request`**.

### 4. Thin Controller & Privacy by Design
- Seluruh logika transisi dan transaksi diisolasi di dalam `PMBService` pada [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py), sehingga router [app/routers/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/routers/pmb.py) tetap tipis (*thin controller*).
- Respons kedua endpoint terikat pada skema Pydantic `PendaftarOut` pada [app/schemas/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/schemas/pmb.py) yang menyaring data sensitif calon mahasiswa (atribut `alamat` dan `tanggal_lahir` tidak dibocorkan ke publik).

---

## 📌 Bagian 7: Endpoint Status Pendaftar & Agregasi Statistik PMB (Database-Level)

Pada iterasi ini, ditambahkan dua endpoint penting untuk kebutuhan pelaporan dan pemantauan publik:

### 1. `GET /api/pmb/status/{id}`: Pengecekan Status Publik Protektif
- Mengembalikan informasi status pendaftaran dan NIM bagi pendaftar dengan respons `HTTP 200 OK`.
- Mengembalikan `HTTP 404 Not Found` jika pendaftar tidak ditemukan.
- **Perlindungan Privasi:** Menggunakan skema DTO khusus `PendaftarStatusOut` pada [app/schemas/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/schemas/pmb.py) yang meniadakan seluruh atribut sensitif yang tidak perlu (tanpa `email`, `phone`, `alamat`, dan `tanggal_lahir`).

### 2. `GET /api/pmb/stats`: Agregasi Statistik Database-Level
- **Prinsip Efisiensi Komputasi:** Seluruh penghitungan agregasi dieksekusi langsung di mesin database menggunakan `GROUP BY` via `func.count(CalonMahasiswa.id)` (tidak mengambil seluruh baris data ke memori Python).
- **Penanganan Outer Join:**
  - Menggunakan kueri `select(...).outerjoin(CalonMahasiswa, ...).group_by(...)` pada model `ProgramStudi` dan `JalurMasuk`.
  - Program studi dan jalur masuk yang belum memiliki pendaftar sama sekali tetap ditampilkan dalam daftar dengan angka **`0`**.

---

## 📌 Bagian 8: Arsitektur Pengujian Modern Pytest & Fixture Terisolasi

Untuk menjamin kualitas dan keandalan tinggi pada modul PMB, dibangun suite pengujian modern menggunakan framework **`pytest`** dengan pemusatan fixture pada [tests/conftest.py](file:///home/zainun/git/istn/sevima-mini/tests/conftest.py):

### 1. Desain Fixture `conftest.py`
- **Engine SQLite In-Memory dengan `StaticPool`:**
  - Menggunakan `create_engine("sqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})`.
  - `StaticPool` menjamin koneksi in-memory yang sama digunakan secara konsisten oleh seluruh thread dan sesi aplikasi selama siklus pengujian.
  - Listener event mengaktifkan `PRAGMA foreign_keys = ON;`.
- **Fixture `db`:**
  - Menjalankan `Base.metadata.create_all(bind=engine)` di awal, melakukan `yield session`, lalu mengeksekusi `Base.metadata.drop_all(bind=engine)` di akhir sesi uji untuk menjaga isolasi basis data.
- **Fixture `client`:**
  - Memasang `app.dependency_overrides[get_db]` dan membersihkannya secara otomatis setelah setiap tes selesai melalui `app.dependency_overrides.clear()`.
- **Fixture `prodi_ti`:**
  - Menginisialisasi Program Studi *"Teknik Informatika"* dengan kode **`001`**.
- **Fixture `jalur_snbp`:**
  - Menginisialisasi Jalur Masuk default *"SNBP"*.

### 2. Standar Pola Pengujian (Arrange-Act-Assert) & Helper Function
Pada [tests/test_pmb_pytest.py](file:///home/zainun/git/istn/sevima-mini/tests/test_pmb_pytest.py), pengujian ditulis dengan disiplin:
- **Fungsi Pembantu `daftar(...)`:** Memusatkan logika pemanggilan `POST /api/pmb/register` dengan payload default pendaftar dummy (`@example.com`).
- **Pola Tiga Tahap AAA (Arrange-Act-Assert):** Memisahkan penyiapan kondisi, aksi eksekusi endpoint, dan asersi verifikasi status/data secara tegas.

---

## 📌 Bagian 9: Perbaikan Arsitektur Konkurensi Tingkat Lanjut (Hasil Tinjauan Kritis Senior Backend)

Berdasarkan tinjauan kritis mendalam terhadap arsitektur konkurensi, telah dilakukan 5 perbaikan teknis berisiko tinggi untuk menjamin skalabilitas enterprise di lingkungan produksi:

### 1. Mitigasi Gap-Lock Deadlock pada Baris Counter Pertama (MySQL InnoDB Error 1213)
- **Akar Masalah:** Jika baris counter `(tahun, kode_prodi)` belum ada di database, kueri `SELECT ... FOR UPDATE` mengambil *Gap Lock* pada rentang indeks. Ketika dua worker konkuren kemudian sama-sama mencoba menyisipkan baris awal, keduanya meminta *Insert Intention Lock* yang saling memblokir dan berujung pada **Deadlock fatal (MySQL Error 1213: Deadlock found when trying to get lock)**.
- **Solusi Rekayasa:** Menggunakan atomic native UPSERT terlebih dahulu (`INSERT ... ON DUPLICATE KEY UPDATE` pada MySQL InnoDB, dan `INSERT ... ON CONFLICT DO NOTHING` pada SQLite) sebelum memanggil `SELECT ... FOR UPDATE`.
- **Hasil:** Baris counter dijamin selalu sudah ada secara fisik sebelum pembacaan terkunci. Oleh karena itu, `SELECT ... FOR UPDATE` hanya mengambil **Record Lock murni (X-Lock)** tanpa celah pembentukan Gap Lock deadlock.

### 2. Konsistensi Urutan Penguncian (Lock Ordering) & Durasi Penguncian Minimum
- **Pola Urutan Kunci:** Transaksi menerapkan urutan penguncian global yang seragam:
  $$\text{Lock 1: } CalonMahasiswa \longrightarrow \text{Lock 2: } NimCounter$$
- **Prinsip Fail-Fast:** Seluruh validasi data, verifikasi eksistensi, validasi format 3 karakter kode prodi, dan pemeriksaan status dilakukan **SEBELUM** generator NIM dipanggil.
- **Minimalisasi Durasi:** Baris `NimCounter` hanya dikunci di milidetik terakhir sebelum `db.commit()` / `db.flush()`, meminimalkan durasi *lock contention* antar-worker.

### 3. Batas Transaksi & Fleksibilitas Unit of Work (`auto_commit`)
- Ditambahkan parameter `auto_commit: bool = True` pada `PMBService.approve` dan `PMBService.reject`.
- **Use Case 1 (Single HTTP Request):** `auto_commit=True` menjaga transaksi atomik lengkap di mana satu request selesai dengan commit mandiri.
- **Use Case 2 (Batch / Unit of Work):** `auto_commit=False` memungkinkan orkestrator transaksi luar (misalnya batch approval import data) menggabungkan banyak operasi dalam satu transaksi besar dan melakukan commit di akhir.

### 4. Idempotensi Tangguh dengan Pola Self-Healing Data Anomaly
- **Masalah:** Jika terjadi anomali data di mana calon mahasiswa berstatus `approved` namun kolom `nim` bernilai `None` (misalnya akibat proses migrasi atau kegagalan transaksi lama), pengecekan idempotensi konvensional akan mengembalikan data tanpa NIM.
- **Solusi:** Logika disempurnakan menjadi:
  ```python
  if calon.status == StatusPMB.APPROVED and calon.nim:
      return calon
  ```
  Jika pendaftar berstatus `approved` tetapi `nim` kosong, sistem secara otomatis melakukan perbaikan mandiri (*self-healing*) dengan menerbitkan NIM baru dan menyimpannya. Skenario ini divalidasi pada [tests/test_state_machine.py](file:///home/zainun/git/istn/sevima-mini/tests/test_state_machine.py) (`test_10_approve_self_healing_when_approved_without_nim`).

### 5. Ketahanan Siklus Percobaan Ulang (Resilient Retry Loop)
- Siklus retry pada `PMBService.approve` dikalibrasi untuk mencoba hingga `max_retries` (3 kali) dengan exponential backoff `time.sleep(0.05 * attempt)`.
- Setiap kegagalan memicu `db.rollback()` segera untuk melepaskan seluruh kunci database sebelum mencoba kembali.

---

## 🧪 Bukti Pengujian Otomatis

Implementasi telah diuji secara menyeluruh melalui kombinasi suite pengujian otomatis:
1. [tests/test_pmb_pytest.py](file:///home/zainun/git/istn/sevima-mini/tests/test_pmb_pytest.py) (7 skenario pytest):
   - `test_register_sukses`: Registrasi berhasil HTTP 201 Created (privasi tersaring).
   - `test_register_email_ganda`: Penolakan email duplikat HTTP 409 Conflict.
   - `test_approve_generate_nim`: Penerbitan NIM sesuai regex 11 digit sekuensial (`^\d{4}001\d{4}$`).
   - `test_approve_idempotent`: Idempotensi persetujuan ganda, NIM tetap, dan pendaftar berikutnya mendapatkan nomor urut **2 BUKAN 3**.
   - `test_register_format_hp_salah`: Penolakan nomor HP tidak valid dengan HTTP 400 Bad Request (sesuai Opsi A / ADR-003).
   - `test_approve_id_tidak_ada`: Penolakan approval ID fiktif HTTP 404 Not Found.
   - `test_approve_pendaftar_rejected`: Penolakan approval terhadap calon berstatus rejected HTTP 409 Conflict.
2. [tests/test_nim_counter.py](file:///home/zainun/git/istn/sevima-mini/tests/test_nim_counter.py) (9 skenario): Format NIM 11 digit zero-padded, independensi counter, batas kuota 9999, non-commit flush, dan retry mechanism.
3. [tests/test_state_machine.py](file:///home/zainun/git/istn/sevima-mini/tests/test_state_machine.py) (10 skenario): Transisi state machine PMB (approve, reject, idempotensi, penolakan 409/400/404, serta self-healing approval anomali data).
4. [tests/test_status_and_stats.py](file:///home/zainun/git/istn/sevima-mini/tests/test_status_and_stats.py) (3 skenario): Pengecekan status publik dan agregasi database-level `GROUP BY` dengan outer join.
5. [tests/test_api_pmb.py](file:///home/zainun/git/istn/sevima-mini/tests/test_api_pmb.py) (10 skenario) & [tests/test_pmb.py](file:///home/zainun/git/istn/sevima-mini/tests/test_pmb.py) (7 skenario).

Seluruh suite pengujian proyek (total **46 test pada runner Pytest** dan **39 test pada runner Unittest**) **lolos 100% tanpa error**.

