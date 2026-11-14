# Dokumentasi Implementasi Minggu 3: Modul PMB (SQLAlchemy 2.0 & Alembic)

Dokumen ini mencatat keputusan teknis, arsitektur skema basis data, dan implementasi modul PMB (*Penerimaan Mahasiswa Baru*) pada sistem informasi akademik **SEVIMA Mini** untuk iterasi **Minggu 3**.

---

## 📌 Ringkasan Implementasi

Pada Minggu 3, dilakukan penerjemahan desain struktural PMB ke dalam skema basis data fisik menggunakan **SQLAlchemy 2.0** (`Mapped` dan `mapped_column`) serta migrasi terkelola dengan **Alembic** pada basis data **SQLite**.

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

---

## 🏛️ Keputusan Arsitektural & Integritas Basis Data

1. **Penegakan `PRAGMA foreign_keys = ON;` pada SQLite:**
   - Secara default SQLite menonaktifkan integritas foreign key per koneksi.
   - Diaktifkan secara persisten melalui SQLAlchemy event listener `@event.listens_for(Engine, "connect")` pada `app/database.py` dan pada konfigurasi migrasi `alembic/env.py`.
2. **Urutan Eksekusi Migrasi (`upgrade` & `downgrade`):**
   - Pada `upgrade()`: Tabel parent (`program_studi`, `jalur_masuk`) dibuat terlebih dahulu sebelum tabel child (`calon_mahasiswa`).
   - Pada `downgrade()`: Tabel child (`calon_mahasiswa`) **wajib dihapus terlebih dahulu** sebelum tabel parent (`jalur_masuk`, `program_studi`) untuk mematuhi integritas referensial dan mencegah kegagalan foreign key constraint.
3. **Pemisahan Tanggung Jawab Constraint (Database vs Aplikasi):**
   - **Database:** Menjamin batas memori/panjang karakter (`VARCHAR(20)`), integritas referensial FK, keunikan (*Unique Index*), serta konsistensi state dasar via `CHECK (status IN ('pending', 'approved', 'rejected'))`.
   - **Aplikasi:** Melakukan validasi format regex nomor telepon (misal: format internasional/E.164), sanitasi email, dan orkestrasi transisi state approval (penerbitan NIM dan pengisian `approved_at`).
