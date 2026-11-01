# SEQUENCE-001: Desain Sequence Diagram PMB dan Validasi KRS

* **Status:** Disetujui (*Approved*)
* **Tanggal:** 2026-11-01
* **Penyusun:** Arsitek Sistem (*System Architect*)
* **Konteks Sistem:** Platform Akademik Kampus (*Academic Information System / SIAKAD Mini*)

---

## 1. Pendahuluan

Dokumen ini memodelkan interaksi dinamis berurutan waktu (*time-ordered interactions*) antar-objek dan komponen sistem pada dua proses bisnis terpenting dalam platform SIAKAD Mini:
1. **Proses Pendaftaran Mahasiswa Baru (PMB):** Siklus hidup dari pendaftaran awal oleh calon mahasiswa hingga pembentukan akun resmi mahasiswa ber-NIM via `UserFactory`.
2. **Proses Pengisian dan Validasi KRS:** Validasi bertingkat mencakup prasyarat finansial (pelunasan tagihan `Payment`), prasyarat akademik kurikulum (`Course.validasiPrasyarat`), dan persetujuan oleh Dosen Wali dengan pembaruan status reaktif via `IEnrollmentObserver`.

---

## 2. Alur 1: Proses Pendaftaran Mahasiswa Baru (PMB)

### 2.1 Deskripsi Proses
Alur pendaftaran mahasiswa baru menjembatani masa transisi entitas `CalonMahasiswa` menjadi `Mahasiswa`. Proses ini mengintegrasikan portal admisi, penyimpanan berkas legalitas, verifikasi admisi oleh Admin, serta instansiasi polimorfik akun via `UserFactory`.

### 2.2 Partisipan & Peran
* **`👤 Calon Mahasiswa`**: Pengguna yang mengisi formulir pendaftaran dan mengunggah dokumen legalitas.
* **`🌐 Portal PMB`**: Antarmuka web registrasi admisi.
* **`⚙️ PMB Controller`**: Pengontrol logika bisnis pendaftaran dan sinkronisasi.
* **`📁 Document Storage`**: Layanan penyimpanan dokumen digital (Ijazah, SKL, KTP).
* **`👨‍💼 Admin Admisi`**: Staf yang memverifikasi keabsahan dokumen dan mengesahkan status kelulusan seleksi.
* **`🏭 UserFactory`**: Pabrik objek polimorfik yang mengenkapsulasi pembuatan objek `Mahasiswa` dan pembentukan NIM.
* **`🗄️ Database SIAKAD`**: Basis data relasional penyimpanan entitas pengguna dan akademik.

### 2.3 Rincian Tahapan Alur PMB
1. **Tahap Registrasi & Berkas:** Calon mahasiswa mengisi formulir program studi dan jalur masuk, memperoleh nomor pendaftaran unik, lalu mengunggah berkas persyaratan.
2. **Tahap Verifikasi & Seleksi:** Admin mengakses antrean berkas berstatus `PENDING_SELEKSI`, memvalidasi dokumen, dan menginput hasil keputusan kelulusan (`LULUS`).
3. **Tahap Sinkronisasi & Akun:** Sistem memanggil `UserFactory.createUser(role="Mahasiswa", data)` untuk men-generate NIM resmi berdasarkan kode prodi dan tahun akademik, menginstansiasi objek `Mahasiswa`, menyimpannya ke basis data, dan menerbitkan kredensial login SIAKAD kepada mahasiswa baru.

---

## 3. Alur 2: Validasi KRS dengan Pengecekan Prasyarat

### 3.1 Deskripsi Proses
Pengisian Kartu Rencana Studi (KRS) merupakan proses transaksi akademik yang krusial. Sistem menerapkan **dua lapis validasi prasyarat (two-tier prerequisite validation)** sebelum rencana studi disahkan:
1. **Prasyarat Finansial (Financial Prerequisite):** Mahasiswa wajib melunasi kewajiban biaya kuliah (SPP/UKT) semester berjalan (`Payment.isLunas() == true`).
2. **Prasyarat Akademik (Academic Prerequisite):** Setiap mata kuliah lanjutan wajib diverifikasi apakah mahasiswa telah lulus mata kuliah prasyaratnya (`Course.validasiPrasyarat(Mahasiswa) == true`).

### 3.2 Partisipan & Peran
* **`👤 Mahasiswa`**: Aktor civitas yang mengajukan rencana studi.
* **`🌐 Portal SIAKAD (KRS)`**: Antarmuka formulir rencana studi mahasiswa.
* **`⚙️ Enrollment Service`**: Komponen orkestrasi bisnis transaksi perkuliahan.
* **`💳 Payment Entity`**: Entitas tagihan finansial semester berjalan.
* **`📚 Course Entity`**: Entitas kurikulum yang memvalidasi riwayat prasyarat.
* **`📝 Enrollment Entity`**: Entitas asosiasi perkuliahan yang memegang status registrasi (`PENDING_APPROVAL`, `APPROVED`, `REJECTED`).
* **`👨‍🏫 Dosen Wali (DPA)`**: Pembimbing akademik yang meninjau dan mengesahkan pengajuan KRS.
* **`🔔 IEnrollmentObserver`**: Antarmuka observer pada `Mahasiswa` untuk menerima notifikasi otomatis atas perubahan status KRS.

### 3.3 Rincian Tahapan Alur KRS
1. **Validasi Finansial:**
   * Saat mahasiswa membuka menu KRS, sistem memanggil `Payment.isLunas()` untuk semester terkait.
   * **Kasus Pembayaran Belum Lunas:** Akses pengisian KRS dikunci, sistem menampilkan notifikasi tagihan SPP belum diselesaikan.
   * **Kasus Pembayaran Lunas:** Akses dibuka, sistem memuat katalog mata kuliah yang ditawarkan pada semester berjalan.
2. **Validasi Prasyarat Akademik & Pembentukan Draft:**
   * Mahasiswa memilih paket mata kuliah dan men-submit formulir.
   * Sistem melakukan perulangan (*loop*) terhadap setiap mata kuliah yang dipilih dengan mengeksekusi `Course.validasiPrasyarat(Mahasiswa)`.
   * Jika prasyarat belum dipenuhi (misal: belum lulus *Algoritma Pemrograman* untuk mengambil *Struktur Data*), mata kuliah ditolak dan diberi pesan peringatan.
   * Jika prasyarat terpenuhi, record `Enrollment` dibuat berstatus `PENDING_APPROVAL` dan mendaftarkan observer mahasiswa.
3. **Validasi & Persetujuan Dosen Wali:**
   * Dosen Wali menerima notifikasi pengajuan dan memeriksa komposisi mata kuliah.
   * **Jika Disetujui:** Dosen mengonfirmasi `approveKRS()`, status `Enrollment` diperbarui menjadi `APPROVED`, dan event observer memicu notifikasi real-time ke akun mahasiswa.
   * **Jika Ditolak/Perlu Revisi:** Dosen menginput catatan perbaikan, status `Enrollment` disetel ke `REJECTED`, dan mahasiswa diinstruksikan melakukan revisi KRS.

---

## 4. Referensi Diagram & Berkas Terkait
* Source Diagram PMB: [`academic_pmb_sequence_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_pmb_sequence_diagram.mmd)
* Source Diagram KRS: [`academic_krs_sequence_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_krs_sequence_diagram.mmd)
* Vektor Diagram PMB: [`pmb_sequence_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/sequence/pmb_sequence_diagram.svg)
* Vektor Diagram KRS: [`krs_sequence_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/sequence/krs_sequence_diagram.svg)
* Class Diagram: [`academic_class_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_class_diagram.mmd)
* Use Case Diagram: [`academic_usecase_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_usecase_diagram.mmd)
