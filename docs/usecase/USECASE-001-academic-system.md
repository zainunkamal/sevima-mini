# USECASE-001: Spesifikasi & Diagram Use Case Sistem Informasi Akademik (SIAKAD Mini)

* **Status:** Disetujui (*Approved*)
* **Tanggal:** 2026-11-01
* **Penyusun:** Arsitek Sistem (*System Architect*)
* **Konteks Sistem:** Platform Akademik Kampus (*Academic Information System / SIAKAD Mini*)

---

## 1. Pendahuluan & Batasan Sistem (*System Boundary*)

Diagram Use Case ini memodelkan fungsionalitas inti dan interaksi aktor di dalam batasan sistem **Sistem Informasi Akademik (SIAKAD Mini)**. Sistem ini melayani pengelolaan siklus hidup perkuliahan mahasiswa mulai dari admisi (pendaftaran), pembayaran kewajiban perkuliahan, registrasi rencana studi (KRS), penilaian akademik, hingga pencetakan transkrip dan kartu hasil studi.

---

## 2. Identifikasi Aktor (*Actor Profiles*)

| Aktor | Tipe | Peran & Tanggung Jawab Utama |
| :--- | :--- | :--- |
| **Mahasiswa** | *Primary Human Actor* | Mengakses layanan akademik mandiri: melakukan pendaftaran, pembayaran SPP/UKT, pengisian KRS semester berjalan, pengecekan jadwal & KHS, serta penerbitan transkrip nilai. |
| **Dosen** | *Primary Human Actor* | Menjalankan dua peran fungsional: (1) **Dosen Pengajar** yang menginput dan memperbarui nilai perkuliahan, serta (2) **Dosen Pembimbing Akademik / Wali** yang memvalidasi dan menyetujui/menolak pengajuan KRS mahasiswa bimbingan. |
| **Admin** | *Primary Human Actor* | Mengelola master data sistem: manajemen akun pengguna (*User*), pengelolaan kurikulum, katalog mata kuliah, alokasi ruang dan jadwal kuliah, serta monitoring sinkronisasi data PMB. |
| **Sistem PMB** | *Secondary External System* | Sistem eksternal Penerimaan Mahasiswa Baru yang bertukar data pendaftaran mahasiswa baru, validasi berkas admisi, dan sinkronisasi status kelulusan seleksi ke SIAKAD. |

---

## 3. Daftar Use Case per Modul

### 3.1 Modul Registrasi & Admisi
1. **Daftar Kuliah:** Calon mahasiswa/mahasiswa melakukan registrasi program studi dan jalur masuk terintegrasi dengan Sistem PMB.
2. **Unggah Berkas Persyaratan:** Mengunggah dokumen administrasi (Ijazah, KTP, Transkrip/SKL).
3. **Sinkronisasi Data Mahasiswa Baru:** Admin dan Sistem PMB mensinkronisasi data kelulusan calon mahasiswa menjadi data mahasiswa resmi (memperoleh NIM).

### 3.2 Modul Keuangan & Pembayaran
1. **Bayar Biaya Kuliah:** Pembayaran tagihan semester berjalan (SPP/UKT) oleh mahasiswa melalui kanal perbankan/Payment Gateway.
2. **Validasi Status Pembayaran:** Verifikasi sistem bahwa tagihan semester berjalan berstatus `LUNAS`.
3. **Ajukan Keringanan / Cicilan:** Permohonan dispensasi penundaan atau pemecahan termin pembayaran SPP.

### 3.3 Modul Rencana Studi (KRS)
1. **Isi KRS:** Pemilihan paket/mata kuliah yang diambil pada semester berjalan sesuai kuota SKS.
2. **Validasi Prasyarat Mata Kuliah:** Pengecekan otomatis kelayakan akademik (mata kuliah prasyarat yang telah lulus).
3. **Revisi / Batal-Tambah KRS:** Perubahan mata kuliah pada periode drop/add.
4. **Cetak Bukti KRS:** Pengunduhan bukti fisik/digital lembar KRS yang telah disetujui.
5. **Validasi & Persetujuan KRS:** Evaluasi dan persetujuan pengajuan KRS oleh Dosen Wali.
6. **Tolak KRS dengan Catatan:** Penolakan pengajuan KRS jika mata kuliah bentrok atau melanggar prasyarat.

### 3.4 Modul Penilaian & Hasil Studi
1. **Input Nilai Mahasiswa:** Penginputan komponen nilai (Tugas, UTS, UAS, Praktikum) oleh Dosen Pengajar.
2. **Kalkulasi Nilai Akhir & Mutu:** Perhitungan skor akhir dan konversi nilai huruf secara otomatis berdasarkan evaluator bobot.
3. **Proses Sanggah Nilai:** Penyesuaian nilai oleh Dosen jika mahasiswa mengajukan sanggahan yang valid.
4. **Lihat Kartu Hasil Studi (KHS):** Mahasiswa melihat rincian capaian indeks prestasi semester berjalan.
5. **Generate Transkrip Nilai:** Penyusunan rekam jejak nilai kumulatif seluruh semester yang telah ditempuh.
6. **Kalkulasi IPK & SKS Kumulatif:** Perhitungan total SKS lulus dan Indeks Prestasi Kumulatif (IPK).
7. **Export Transkrip Resmi (PDF):** Penerbitan berkas transkrip resmi bertandatangan digital.

### 3.5 Modul Administrasi Akademik
1. **Kelola Kurikulum & Mata Kuliah:** Pengelolaan daftar mata kuliah, bobot SKS, dan aturan prasyarat.
2. **Kelola Alokasi Jadwal:** Penataan jadwal kelas, jam, kapasitas, dan ruangan kuliah.
3. **Kelola Data Pengguna:** Manajemen akun Mahasiswa, Dosen, dan staf institusi.

---

## 4. Analisis Relasi `<<include>>` dan `<<extend>>`

Berdasarkan standar UML 2.5:
* **`<<include>>`** menandakan bahwa alur pada use case sumber (*base*) **selalu dan wajib** memanggil use case target (*included*). Arah panah: `Base -. "<<include>>" .-> Included`.
* **`<<extend>>`** menandakan perilaku opsional atau kondisional yang memperluas use case dasar pada titik perluasan (*extension point*). Arah panah: `Extension -. "<<extend>>" .-> Base`.

### 4.1 Tabel Relasi `<<include>>`

| Base Use Case | Included Use Case | Rationale / Aturan Bisnis |
| :--- | :--- | :--- |
| **Isi KRS** | **Validasi Status Pembayaran** | **Mandatory:** Mahasiswa tidak diizinkan memilih mata kuliah jika tagihan SPP semester berjalan belum `LUNAS` (prasyarat finansial mutlak). |
| **Isi KRS** | **Validasi Prasyarat Mata Kuliah** | **Mandatory:** Setiap mata kuliah yang dipilih wajib diverifikasi apakah mahasiswa telah memenuhi lulusan mata kuliah prasyaratnya. |
| **Daftar Kuliah** | **Unggah Berkas Persyaratan** | **Mandatory:** Registrasi pendaftaran kuliah tidak dapat diselesaikan tanpa pengunggahan dokumen legalitas pendaftar. |
| **Input Nilai Mahasiswa** | **Kalkulasi Nilai Akhir & Mutu** | **Mandatory:** Setiap kali dosen menyimpan nilai komponen, sistem secara otomatis mengeksekusi konversi bobot angka ke huruf mutu (*A, B, C, D, E*). |
| **Generate Transkrip Nilai** | **Kalkulasi IPK & SKS Kumulatif** | **Mandatory:** Penerbitan transkrip nilai secara inheren memerlukan perhitungan ulang total SKS lulus dan bobot IPK kumulatif. |

### 4.2 Tabel Relasi `<<extend>>`

| Extension Use Case | Base Use Case | Extension Point / Kondisi Pemicu |
| :--- | :--- | :--- |
| **Ajukan Keringanan / Cicilan** | **Bayar Biaya Kuliah** | **Kondisi:** Terpicu jika mahasiswa mengajukan skema penundaan/angsuran pembayaran UKT sebelum jatuh tempo. |
| **Revisi / Batal-Tambah KRS** | **Isi KRS** | **Kondisi:** Hanya aktif selama jendela waktu kalender akademik revisi KRS (masa *Drop/Add*). |
| **Cetak Bukti KRS** | **Isi KRS** | **Kondisi:** Opsional dipilih mahasiswa setelah formulir KRS selesai diisi dan disimpan ke basis data. |
| **Tolak KRS dengan Catatan** | **Validasi & Persetujuan KRS** | **Kondisi:** Dieksekusi Dosen Wali jika komposisi mata kuliah tidak memenuhi arahan akademik atau terjadi bentrok jadwal. |
| **Proses Sanggah Nilai** | **Input Nilai Mahasiswa** | **Kondisi:** Terpicu apabila masa sanggah dibuka dan ada pengaduan revisi nilai dari mahasiswa yang disetujui dosen. |
| **Export Transkrip Resmi (PDF)** | **Generate Transkrip Nilai** | **Kondisi:** Opsional jika mahasiswa atau staf akademik memerlukan cetakan dokumen fisik/PDF dengan stempel digital. |

---

## 5. Referensi Berkas Terkait
* Diagram Mermaid Source: [`academic_usecase_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_usecase_diagram.mmd)
* Diagram Vector SVG: [`usecase_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/usecase/usecase_diagram.svg)
* Class Diagram Arsitektur: [`academic_class_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_class_diagram.mmd)
