# ADR-003: Desain Sequence Diagram Pendaftaran Mahasiswa Baru (PMB) dan Validasi KRS Bertingkat

* **Status:** Diterima (*Accepted*)
* **Tanggal:** 2026-11-01
* **Penyusun:** Arsitek Sistem (*System Architect*)
* **Konteks Sistem:** Platform Akademik Kampus (*Academic Information System / SIAKAD Mini*)

---

## 1. Konteks & Latar Belakang (Context)

Dalam Sistem Informasi Akademik, dua proses transaksi data memiliki risiko integritas tertinggi:
1. **Transisi Status Pengguna Baru (PMB):** Proses migrasi dari calon pendaftar (`CalonMahasiswa`) menjadi civitas resmi (`Mahasiswa`) dengan penomoran induk mahasiswa (NIM) yang unik, terikat prodi dan tahun akademik.
2. **Validasi Pengisian Rencana Studi (KRS):** Registrasi perkuliahan mahasiswa yang melibatkan multi-prasyarat, verifikasi kapasitas kelas, dan persetujuan dosen wali (*academic advisor*).

Tantangan perancangan interaksi dinamis:
* Memastikan *lifecycle* pembuatan akun mahasiswa baru terisolasi melalui pola perancangan *Factory Pattern* (`UserFactory`).
* Mencegah *race condition* atau bypass aturan akademik saat pengisian KRS dengan menerapkan **Validasi Bertingkat (Two-Tier Prerequisite Validation)**: lapis finansial terlebih dahulu, disusul lapis kurikulum akademik.
* Menyediakan notifikasi status kelulusan KRS secara *decoupled* menggunakan pola *Observer Pattern* (`IEnrollmentObserver`).

---

## 2. Keputusan Arsitektur & Interaksi Objek (Architectural Decision)

### 2.1 Alur 1: Pendaftaran Mahasiswa Baru (PMB)

Alur sekuensial dibagi ke dalam tiga tahap utama:
1. **Tahap Registrasi & Unggah Berkas:**
   * Calon mahasiswa mengisi formulir pendaftaran melalui portal PMB.
   * Dokumen legalitas (Ijazah, KTP, SKL) diunggah dan disimpan ke *Document Storage*, menghasilkan `berkasPath`.
   * Record pendaftaran tersimpan di basis data dengan status `PENDING_SELEKSI`.
2. **Tahap Verifikasi & Keputusan Seleksi:**
   * Admin Admisi mengakses daftar pendaftar berstatus `PENDING_SELEKSI`.
   * Admin melakukan verifikasi dokumen dan mencatat hasil seleksi (`LULUS`).
3. **Tahap Enkapsulasi Instansiasi via `UserFactory`:**
   * Sistem memicu `UserFactory.createUser("Mahasiswa", dataCalon)`.
   * `UserFactory` men-generate NIM unik dengan format standar: `[KodeProdi][TahunMasuk][NomorUrut]`.
   * Entitas polimorfik `Mahasiswa` dibuat lengkap dengan atribut akademik awal (IPK=0.0, semester=1, status="AKTIF").
   * Kredensial login dikirimkan ke calon mahasiswa melalui kanal notifikasi resmi.

---

### 2.2 Alur 2: Validasi KRS dengan Pengecekan Prasyarat Bertingkat

Sistem menerapkan validasi dua lapis (*two-tier prerequisite check*) sebelum rencana studi dapat diajukan:

```
[Mulai Pengisian KRS]
         │
         ▼
[Lapis 1: Validasi Finansial]
Payment.isLunas() ────(False)───► [KRS Terkunci: Wajib Pelunasan SPP]
         │ (True)
         ▼
[Katalog Penawaran Matakuliah Dibuka]
         │
         ▼
[Lapis 2: Validasi Prasyarat Akademik] (Per Matakuliah)
Course.validasiPrasyarat(Mahasiswa) ──(False)──► [Matakuliah Ditolak / Warning]
         │ (True)
         ▼
[Draft Enrollment Dibuat: PENDING_APPROVAL]
         │
         ▼
[Persetujuan Dosen Wali (DPA)]
         │
         ├──(Setuju)──► Enrollment.status = "APPROVED" ──► Observer Trigger (Notifikasi Mahasiswa)
         └──(Tolak)───► Enrollment.status = "REJECTED" ──► Mahasiswa Revisi KRS
```

#### Rincian Mekanisme Sekuensial KRS:
1. **Lapis 1: Prasyarat Finansial (`Payment.isLunas()`):**
   * Service memeriksa entitas `Payment` mahasiswa pada semester berjalan.
   * Jika status belum lunas, alur dihentikan seketika dan portal menampilkan instruksi pembayaran SPP.
   * Jika lunas, katalog penawaran kelas dibuka.
2. **Lapis 2: Prasyarat Akademik (`Course.validasiPrasyarat()`):**
   * Mahasiswa memilih daftar mata kuliah (`List<Course>`) dan mengajukan KRS.
   * Dalam perulangan (*loop*), sistem memvalidasi kelulusan mata kuliah prasyarat pada riwayat KHS mahasiswa.
   * Jika lolos, dibuat objek `Enrollment` dengan status `PENDING_APPROVAL`, dan observer mahasiswa didaftarkan (`attachObserver(mahasiswa)`).
3. **Lapis 3: Persetujuan Dosen Wali & Notifikasi Reaktif:**
   * Dosen Wali meninjau rencana studi mahasiswa bimbingan.
   * Jika disetujui, method `approveKRS()` memperbarui status menjadi `APPROVED` dan memicu `IEnrollmentObserver.onEnrollmentStatusChanged()` untuk memberitahu mahasiswa secara *real-time*.
   * Jika ditolak, status disetel ke `REJECTED` beserta catatan perbaikan untuk diproses kembali oleh mahasiswa.

---

## 3. Pertimbangan Desain & Pola Arsitektur (Patterns & Trade-offs)

### 3.1 Factory Pattern pada PMB
* **Kelebihan:** Memisahkan logika pembuatan identitas dan perhitungan format NIM dari controller admisi. Menjamin kepatuhan prinsip *Single Responsibility* (SRP).
* **Trade-off:** Menambah abstraksi kelas; dimitigasi dengan keseragaman instansiasi seluruh tipe user di sistem (`Mahasiswa`, `Dosen`, `Admin`).

### 3.2 Two-Tier Validation (Fail-Fast Approach)
* **Kelebihan:** Validasi finansial dievaluasi paling awal (*Fail-Fast*) sebelum komputasi pengecekan prasyarat kurikulum dan alokasi kursi kelas dilakukan. Hal ini menghemat *resource query* basis data saat jutaan mahasiswa mengakses KRS serentak.
* **Trade-off:** Mahasiswa dengan kendala dispensasi pembayaran memerlukan jalur khusus (*extend use case: ajukan dispensasi*) agar bendera status pembayaran dapat disetujui sementara.

### 3.3 Observer Pattern pada Status Enrollment
* **Kelebihan:** Memisahkan modul persetujuan KRS oleh dosen wali dari modul penyedia notifikasi (Email, Push Notification, Dashboard UI).
* **Trade-off:** Memerlukan pengelolaan *lifecycle* observer dalam memori atau *event bus* saat transaksi skala besar.

---

## 4. Referensi Berkas Terkait
* Diagram Sequence PMB Mermaid: [`academic_pmb_sequence_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_pmb_sequence_diagram.mmd)
* Diagram Sequence KRS Mermaid: [`academic_krs_sequence_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_krs_sequence_diagram.mmd)
* Vektor Diagram PMB SVG: [`pmb_sequence_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/sequence/pmb_sequence_diagram.svg)
* Vektor Diagram KRS SVG: [`krs_sequence_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/sequence/krs_sequence_diagram.svg)
* Class Diagram: [`academic_class_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_class_diagram.mmd)
