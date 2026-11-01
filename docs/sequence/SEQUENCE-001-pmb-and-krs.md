# SEQUENCE-001: Desain Sequence Diagram PMB dan Validasi KRS

* **Status:** Disetujui (*Approved*)
* **Tanggal:** 2026-11-01
* **Penyusun:** Arsitek Sistem (*System Architect*)
* **Konteks Sistem:** Platform Akademik Kampus (*Academic Information System / SEVIMA-Mini*)

---

## 1. Pendahuluan

Dokumen ini memodelkan interaksi dinamis berurutan waktu (*time-ordered interactions*) antar-objek dan komponen sistem pada dua proses bisnis terpenting dalam platform SEVIMA-Mini:
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
* **`🗄️ Database SEVIMA-Mini`**: Basis data relasional penyimpanan entitas pengguna dan akademik.

### 2.3 Rincian Tahapan Alur PMB
1. **Tahap Registrasi & Berkas:** Calon mahasiswa mengisi formulir program studi dan jalur masuk, memperoleh nomor pendaftaran unik, lalu mengunggah berkas persyaratan.
2. **Tahap Verifikasi & Seleksi:** Admin mengakses antrean berkas berstatus `PENDING_SELEKSI`, memvalidasi dokumen, dan menginput hasil keputusan kelulusan (`LULUS`).
3. **Tahap Sinkronisasi & Akun:** Sistem memanggil `UserFactory.createUser(role="Mahasiswa", data)` untuk men-generate NIM resmi berdasarkan kode prodi dan tahun akademik, menginstansiasi objek `Mahasiswa`, menyimpannya ke basis data, dan menerbitkan kredensial login SEVIMA-Mini kepada mahasiswa baru.

---

## 3. Alur 2: Validasi KRS dengan Pengecekan Prasyarat

### 3.1 Deskripsi Proses
Pengisian Kartu Rencana Studi (KRS) merupakan proses transaksi akademik yang krusial. Sistem menerapkan **dua lapis validasi prasyarat (two-tier prerequisite validation)** sebelum rencana studi disahkan:
1. **Prasyarat Finansial (Financial Prerequisite):** Mahasiswa wajib melunasi kewajiban biaya kuliah (SPP/UKT) semester berjalan (`Payment.isLunas() == true`).
2. **Prasyarat Akademik (Academic Prerequisite):** Setiap mata kuliah lanjutan wajib diverifikasi apakah mahasiswa telah lulus mata kuliah prasyaratnya (`Course.validasiPrasyarat(Mahasiswa) == true`).

### 3.2 Partisipan & Peran
* **`👤 Mahasiswa`**: Aktor civitas yang mengajukan rencana studi (`isiKRS`).
* **`🌐 Portal SEVIMA-Mini (KRS)`**: Antarmuka formulir pengajuan rencana studi mahasiswa.
* **`⚙️ Layanan KRS (KRSService)`**: Komponen orkestrasi bisnis transaksi dan validasi rencana studi.
* **`⚖️ ValidationRule (Strategy Pattern)`**: Aturan validasi polimorfik: `PaymentValidationRule`, `PrerequisiteRule`, `SksLimitRule` (max 24), `ScheduleConflictRule`, dan `DoubleEnrollmentRule`.
* **`📚 Entitas Mata Kuliah (Course)`**: Entitas kurikulum yang memvalidasi prasyarat matakuliah.
* **`📅 Entitas Jadwal (Schedule)`**: Entitas jadwal kuliah yang menyediakan kuota kapasitas dan deteksi bentrok hari/jam perkuliahan.
* **`📋 Entitas Rencana Studi (KRS)`**: Agregat dokumen rencana studi mahasiswa per semester berjalan.
* **`📝 Entitas Pendaftaran (Enrollment)`**: Entitas asosiasi perkuliahan yang memegang status registrasi (`PENDING_APPROVAL`, `APPROVED`, `REVISED / REJECTED`).
* **`🗄️ Database SEVIMA-Mini`**: Basis data relasional penyimpanan entitas KRS dan Enrollment.
* **`🔔 Layanan Notifikasi (NotificationService)`**: Layanan pengiriman notifikasi instan ke pengguna dan broadcast event pembaruan status KRS.
* **`👨‍🏫 Dosen PA (Pembimbing Akademik)`**: Pembimbing akademik yang meninjau dan mengesahkan/menolak pengajuan KRS mahasiswa bimbingan.

### 3.3 Rincian Tahapan Alur KRS & Alternate Flows
1. **Tahap 1: Pengajuan KRS & Validasi Jadwal Periode (Masa KRS):**
   * Mahasiswa membuka formulir dan men-submit draft KRS.
   * `KRSService` memeriksa jadwal periode aktif (`cekKelayakanPengisianKRS`).
   * **Alt Flow 1 (Masa KRS Ditutup):** Sistem menolak pengajuan dan menampilkan pesan bahwa masa pengisian KRS telah berakhir.
2. **Tahap 2: Pengecekan Syarat Finansial (Pembayaran SPP):**
   * Sistem mengevaluasi `PaymentValidationRule.validate(krs, mahasiswa)`.
   * **Alt Flow 2 (Tagihan SPP Belum Lunas):** Pengajuan KRS terkunci, sistem menampilkan instruksi pelunasan kewajiban SPP.
3. **Tahap 3: Pengecekan Kuota Kapasitas Kelas:**
   * Sistem memverifikasi kuota via `Schedule.getKapasitas()`.
   * **Alt Flow 3 (Kapasitas Penuh):** Jika sisa kuota = 0, sistem menolak matakuliah tersebut dan meminta mahasiswa memilih kelas lain.
4. **Tahap 4: Eksekusi Multi-Rule Validasi KRS (Strategy Pattern):**
   * `KRSService` mengeksekusi loop daftar `ValidationRule`:
     * **PrerequisiteRule:** Evaluasi kelulusan prasyarat via `Course.validasiPrasyarat(mahasiswa)`. (**Alt Flow 4a:** Ditolak jika prasyarat belum lulus).
     * **SksLimitRule:** Evaluasi batas kuota maksimal &le; 24 SKS. (**Alt Flow 4b:** Ditolak jika total beban SKS > 24).
     * **ScheduleConflictRule:** Deteksi bentrok hari/jam via `Schedule.cekBentrok(other)`. (**Alt Flow 4c:** Ditolak jika jadwal bertabrakan).
     * **DoubleEnrollmentRule:** Pencegahan pendaftaran matakuliah duplikat. (**Alt Flow 4d:** Ditolak jika matakuliah ganda terdeteksi).
5. **Tahap 5: Pembentukan Rencana Studi & Penetapan Status:**
   * Entitas `Enrollment` dibentuk dan diset ke status `"PENDING_APPROVAL"`.
   * Total SKS dihitung dan status `KRS` disetel ke `"PENDING_APPROVAL"`.
6. **Tahap 6: Persistensi Data ke Basis Data:**
   * Sistem melakukan commit transaksi data ke database via `DB.simpanKRS(krs)`.
   * **Alt Flow 5 (Error Database):** Jika terjadi `DatabaseException` / connection timeout, sistem menampilkan notifikasi galat transaksi server dan meminta mahasiswa melakukan submit ulang.
7. **Tahap 7: Notifikasi Pengajuan KRS ke Dosen PA:**
   * Sistem mengambil Dosen PA via `Mahasiswa.getDosenPA()`.
   * `NotificationService` mengirimkan notifikasi ke Dosen PA dan mem-broadcast pembaruan status ke observer (`onEnrollmentStatusChanged`).
8. **Tahap 8: Evaluasi & Persetujuan Dosen PA:**
   * Dosen PA membuka portal validasi dan meninjau detail KRS (`KRSService.getDetailKRS`).
   * **Persetujuan (Approve):** Dosen memanggil `approveKRS()`, status diubah menjadi `"APPROVED"`, notifikasi terkirim ke mahasiswa.
   * **Penolakan / Revisi (Reject):** Dosen menginput catatan perbaikan via `rejectKRS()`, status diubah menjadi `"REVISED / REJECTED"`, notifikasi revisi terkirim ke mahasiswa.

---

## 4. Referensi Diagram & Berkas Terkait
* Source Diagram PMB: [`diagrams/sequence-pmb.mmd`](file:///home/zainun/Git/istn/sevima-mini/diagrams/sequence-pmb.mmd)
* Source Diagram KRS: [`diagrams/sequence-krs.mmd`](file:///home/zainun/Git/istn/sevima-mini/diagrams/sequence-krs.mmd)
* Vektor Diagram PMB: [`docs/sequence/pmb_sequence_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/sequence/pmb_sequence_diagram.svg)
* Vektor Diagram KRS: [`docs/sequence/krs_sequence_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/sequence/krs_sequence_diagram.svg)
* Class Diagram: [`diagrams/class-diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/diagrams/class-diagram.mmd)
* Use Case Diagram: [`diagrams/usecase-diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/diagrams/usecase-diagram.mmd)
