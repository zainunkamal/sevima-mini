# Dokumentasi Implementasi Minggu 3: Modul PMB (SQLAlchemy 2.0, Alembic, & FastAPI)

Dokumen ini mencatat keputusan teknis, arsitektur skema basis data, dan implementasi endpoint API modul PMB (*Penerimaan Mahasiswa Baru*) pada sistem informasi akademik **SEVIMA Mini** untuk iterasi **Minggu 3**.

---

## 📌 Bagian 1: Skema Basis Data & Migrasi Terkelola

Pada iterasi awal Minggu 3, dilakukan penerjemahan desain struktural PMB ke dalam skema basis data fisik menggunakan **SQLAlchemy 2.0** (`Mapped` dan `mapped_column`) serta migrasi terkelola dengan **Alembic** pada basis data **SQLite**.

### 1. Entitas & Relasi
1. **`program_studi`**:
   - `id`: Primary Key (Integer, autoincrement).
   - `kode`: String(3), UNIQUE, Index, NOT NULL.
   - `nama`: String(100), NOT NULL.
   - `fakultas`: String(100), NOT NULL.
2. **`jalur_masuk`**:
   - `id`: Primary Key (Integer, autoincrement).
   - `nama`: String(50), UNIQUE, Index, NOT NULL (contoh: SNBP, SNBT, Mandiri).
3. **`calon_mahasiswa`**:
   - `id`: Primary Key (Integer, autoincrement).
   - `nama_lengkap`: String(150), NOT NULL.
   - `email`: String(255), UNIQUE, Index, NOT NULL.
   - `phone`: String(20), NOT NULL (disimpan sebagai String, bukan integer, untuk menjaga leading zero dan kode negara).
   - `tanggal_lahir`: Date, nullable.
   - `alamat`: Text, nullable.
   - `program_studi_id`: Foreign Key ke `program_studi.id`, NOT NULL (ondelete: RESTRICT).
   - `jalur_masuk_id`: Foreign Key ke `jalur_masuk.id`, nullable (ondelete: SET NULL).
   - `status`: ENUM (`pending`, `approved`, `rejected`), default `pending`, dengan CHECK constraint aktif di database.
   - `nim`: String(20), UNIQUE, nullable (hanya diterbitkan saat berstatus `approved`).
   - `created_at`: DateTime(timezone=True), server_default NOW.
   - `approved_at`: DateTime(timezone=True), nullable.

### 2. Keputusan Arsitektural Basis Data
1. **Penegakan `PRAGMA foreign_keys = ON;` pada SQLite:**
   - Secara default SQLite menonaktifkan integritas foreign key per koneksi.
   - Diaktifkan secara persisten melalui SQLAlchemy event listener `@event.listens_for(Engine, "connect")` pada `app/database.py` dan pada konfigurasi migrasi `app/alembic/env.py`.
2. **Urutan Eksekusi Migrasi (`upgrade` & `downgrade`):**
   - Pada `upgrade()`: Tabel parent (`program_studi`, `jalur_masuk`) dibuat terlebih dahulu sebelum tabel child (`calon_mahasiswa`).
   - Pada `downgrade()`: Tabel child (`calon_mahasiswa`) **wajib dihapus terlebih dahulu** sebelum tabel parent (`jalur_masuk`, `program_studi`) untuk mematuhi integritas referensial dan mencegah kegagalan foreign key constraint.
3. **Pemisahan Tanggung Jawab Constraint (Database vs Aplikasi):**
   - **Database:** Menjamin batas memori/panjang karakter (`VARCHAR(20)`), integritas referensial FK, keunikan (*Unique Index*), serta konsistensi state dasar via `CHECK (status IN ('pending', 'approved', 'rejected'))`.
   - **Aplikasi:** Melakukan validasi format regex nomor telepon (misal: format internasional/E.164), sanitasi email, dan orkestrasi transisi state approval (penerbitan NIM dan pengisian `approved_at`).

---

## 📌 Bagian 2: Implementasi Endpoint Pendaftaran PMB (`POST /api/pmb/register`)

Endpoint pendaftaran calon mahasiswa baru dibangun menggunakan **FastAPI** dengan mematuhi prinsip *Layered Architecture* (Clean Architecture):

### 1. Skema DTO & Perlindungan Privasi (`app/schemas/pmb.py`)
- **`RegisterRequest`**:
  - `nama_lengkap`: Minimal 3 karakter (`min_length=3`).
  - `email`: Format email valid menggunakan `EmailStr`.
  - `phone`: Regex nomor HP Indonesia (`^(\+62|62|08)[0-9]{7,13}$`).
  - `tanggal_lahir`: Opsional (`date`).
  - `alamat`: Opsional (`str`).
  - `program_studi_id` & `jalur_masuk_id`: Wajib lebih besar dari 0 (`gt=0`).
- **`PendaftarOut`**:
  - Menyajikan data status pendaftaran: `id`, `nama_lengkap`, `email`, `phone`, `program_studi_id`, `jalur_masuk_id`, `status`, `nim`, `created_at`, `approved_at`.
  - **Prinsip Keamanan Privasi Data:** Atribut sensitif seperti `alamat` dan `tanggal_lahir` secara sengaja **tidak disertakan** pada skema respons publik.

### 2. Lapisan Layanan & Anti Race-Condition (`app/services/pmb.py`)
- Melakukan verifikasi eksistensi ganda:
  1. *Pre-check query* untuk memastikan email belum terdaftar (respons instan HTTP 409).
  2. Verifikasi eksistensi `program_studi` dan `jalur_masuk` di database (respons HTTP 400 jika tidak ditemukan).
- Menangani *race condition*:
  - Saat dua permintaan pendaftaran konkuren dengan email identik lolos *pre-check* pada milidetik yang sama, transaksi dicegat oleh *Unique Index* basis data.
  - Blok `try ... except IntegrityError` menangkap *exception* basis data, melakukan `db.rollback()`, dan mengembalikan HTTP 409 yang ramah pengguna tanpa membocorkan pesan mentah SQL.

### 3. Router Tipis & Dependency Injection (`app/routers/pmb.py`)
- Router bertindak sebagai *thin controller* murni yang hanya mendeklarasikan rute, status kode sukses HTTP 201, skema respons, dan menginjeksi sesi database menggunakan `get_db` generator (`yield` + `finally: db.close()`).

### 4. Transformasi Error Validasi Terpusat (`app/main.py`)
- Secara *default*, FastAPI merespons `RequestValidationError` dengan kode HTTP 422 Unprocessable Entity dan struktur error mentah Pydantic.
- Dibuat handler khusus `@app.exception_handler(RequestValidationError)` untuk:
  - Mengubah kode status menjadi **HTTP 400 Bad Request**.
  - Mengonversi pesan teknis menjadi pesan humanis bahasa Indonesia yang terstruktur tanpa memunculkan *stack trace*.

---

## 📊 Matriks Kode Status HTTP Endpoint `/api/pmb/register`

| Kasus Uji | Kode Status HTTP | Keterangan Respon |
| :--- | :--- | :--- |
| **Pendaftaran Sukses** | `201 Created` | Data pendaftar berhasil dibuat berstatus `pending`, menyembunyikan alamat & tanggal lahir. |
| **Email Ganda (Pre-check & Race Condition)** | `409 Conflict` | `"Email sudah terdaftar. Silakan gunakan alamat email lain."` |
| **Program Studi Tidak Ada** | `400 Bad Request` | `"Program studi dengan ID <id> tidak ditemukan."` |
| **Jalur Masuk Tidak Ada** | `400 Bad Request` | `"Jalur masuk dengan ID <id> tidak ditemukan."` |
| **Nama < 3 Karakter** | `400 Bad Request` | `"nama_lengkap: Panjang minimal adalah 3 karakter"` |
| **Format Email Tidak Valid** | `400 Bad Request` | `"email: Format alamat email tidak valid"` |
| **Format No. HP Ilegal (misal: 0809, 021)** | `400 Bad Request` | `"phone: Format nomor HP tidak valid (harus nomor Indonesia dengan awalan 08, 62, atau +62)"` |
| **ID Prodi / Jalur <= 0** | `400 Bad Request` | `"program_studi_id: Nilai harus lebih besar dari 0"` |
| **Tanggal Lahir Masa Depan / Usia < 14 thn** | `400 Bad Request` | `"tanggal_lahir: Tanggal lahir tidak boleh di masa depan"` / `"Usia calon mahasiswa minimal 14 tahun"` |

---

## 📌 Bagian 3: Refactoring Keamanan & Peningkatan Arsitektur

Berdasarkan audit teknis backend dan penelusuran kasus tepi regex, dilakukan penyempurnaan menyeluruh:
1. **Penanganan Spesifik `IntegrityError`:** Mengeliminasi *blind exception handling* dengan memeriksa pesan error asli (`exc.orig`). Hanya kegagalan `UNIQUE constraint ... email` yang mengembalikan HTTP 409, sedangkan pelanggaran constraint lain dikembalikan sebagai HTTP 400 tanpa disamarkan.
2. **Adopsi Penuh SQLAlchemy 2.0:** Memperbarui pemanggilan query pada lapisan service dari `db.query().filter().first()` (gaya 1.x) menjadi `db.scalar(select(...).where(...))` (murni 2.0).
3. **Penyempurnaan Regex & Sanitasi Nomor HP:**
   - Pola regex disesuaikan menjadi `^(\+62|62|0)8[1-9][0-9]{5,10}$` guna mengakomodasi nomor pascabayar lawas 9 digit (misal: kartu Halo era 90-an `081112345`) hingga nomor seluler 13–14 digit.
   - Penambahan pre-validator `@field_validator("phone", mode="before")` untuk membuang spasi, tanda hubung (`-`), titik (`.`), dan tanda kurung `()` sebelum dicek regex, sehingga penulisan humanis seperti `0812-3456-7890` tetap diterima.
4. **Validasi Batas Usia Bisnis pada Tanggal Lahir:** Menambahkan `@field_validator("tanggal_lahir")` pada Pydantic untuk menolak tanggal lahir di masa depan serta membatasi usia wajar calon mahasiswa (14 hingga 80 tahun).
5. **Ketatnya Tipe State Respons:** Mengikat atribut `status` pada `PendaftarOut` langsung ke tipe domain `StatusPMB` Enum.
6. **Keputusan Arsitektur Adopsi Opsi A (RequestValidationError -> 400 & Sinkronisasi Swagger):**
   - Menyelaraskan seluruh kegagalan validasi format klien ke kode status standar `HTTP 400 Bad Request` sesuai kontrak dokumen tugas.
   - Melakukan kustomisasi generator OpenAPI (`app.openapi`) untuk menghapus respons bawaan status `422` dari skema OpenAPI, sehingga dokumentasi Swagger UI secara presisi dan konsisten hanya menampilkan status `201 Created`, `400 Bad Request`, dan `409 Conflict`.

---

## 🧪 Bukti Pengujian Otomatis

Seluruh fungsionalitas telah divalidasi melalui 2 berkas pengujian otomatis (total 17 unit test lolos 100%):
1. [test_pmb.py](file:///home/zainun/git/istn/sevima-mini/tests/test_pmb.py): Menguji 7 skenario integritas skema basis data SQLite dan constraint.
2. [test_api_pmb.py](file:///home/zainun/git/istn/sevima-mini/tests/test_api_pmb.py): Menguji 10 skenario endpoint FastAPI menggunakan `TestClient` (HTTP 201, 409, 400 referensi, 400 format validasi, 400 tanggal lahir masa depan, 400 regex HP non-seluler, 201 nomor humanis dengan spasi/strip, 201 nomor 9 digit lawas, dan 400 nomor premium 0809).

---

## 📜 Architectural Decision Record (ADR) Minggu 3

Keputusan teknis dan arsitektural di atas telah dibukukan secara formal dalam dokumen resmi:
- **[ADR-003: Standardisasi Penanganan Validasi Klien (HTTP 400 vs 422) dan Integritas Relasional Modul PMB](file:///home/zainun/git/istn/sevima-mini/documents/ADR-003.pdf)**: Dokumen keputusan arsitektur resmi dalam format PDF yang mendokumentasikan analisis perbandingan Opsi A vs Opsi B, strategi validasi pertahanan berlapis (*Defense-in-Depth*), penegakan kunci asing SQLite, urutan aman rollback Alembic, dan prinsip perlindungan privasi calon mahasiswa (*Privacy by Design*).
