## AI Usage Log: Minggu 1

### Prompt #1 (versi: V1)
- **Tanggal / alat AI:** 13 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Membuat rancangan awal (*draft*) class diagram UML sistem informasi akademik "SEVIMA Mini" sesuai komponen dan batasan spesifikasi awal.
- **Prompt:**
  ```text
  Anda adalah arsitek sistem dan pakar OOP senior.

  Konteks:
  Buat class diagram UML untuk sistem informasi akademik kampus kecil
  bernama "SEVIMA Mini" dengan modul PMB, KRS, jadwal, nilai, dan pembayaran SPP.

  Komponen:
  - User sebagai abstract base class (id, username, password, email;
    method login dan logout) dengan 4 turunan:
    Mahasiswa (NIM, program studi, semester), Dosen (NIDN),
    Admin, dan CalonMahasiswa (nomor pendaftaran, status seleksi).
  - Course: kode, nama, jumlah SKS, daftar prasyarat (relasi ke Course lain).
  - Enrollment: penghubung Mahasiswa dan Course; atribut semester,
    tahun akademik, status (draft, pending, disetujui).
  - Schedule: hari, jam mulai, jam selesai, ruangan.
  - Grade: nilai angka dan nilai huruf, terhubung ke Enrollment.
  - Payment: tagihan SPP per semester, jumlah, tanggal bayar,
    status (lunas, menunggak).

  Batasan:
  - Terapkan prinsip SOLID, terutama Single Responsibility
    (tidak ada kelas dengan lebih dari 10 method).
  - Gunakan composition untuk relasi kuat dan aggregation untuk relasi lemah.
  - Wajib tulis visibility modifier (+, -, #); password harus private.
  - Wajib tulis kardinalitas pada setiap relasi.
  - Relasi many-to-many harus dipecah dengan kelas perantara.
  - Aturan bisnis: maksimal 24 SKS per KRS, cegah pendaftaran ganda.
  - Jangan membuat kelas di luar komponen di atas.

  Format output:
  Hanya kode Mermaid classDiagram dalam satu code block,
  tanpa penjelasan panjang.
  ```
- **Output ringkas:** Kode Mermaid class diagram awal berisi 10 kelas lengkap dengan pemecahan relasi many-to-many melalui `Enrollment`, disimpan di [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd).
- **Masalah ditemukan:**
  1. Atribut pada kelas `User` (`id`, `username`, `email`) masih menggunakan visibility `protected (#)`.
  2. Belum ada accessor public (getter/setter) pada kelas `User`.
  3. Fungsionalitas penghitungan IPK (`hitungIPK()`) belum ada pada kelas `Mahasiswa`.
  4. Belum ada method accessor pada beberapa entitas turunan (`Admin`, `Enrollment`, `Payment`).
- **Revisi manual saya:** Meminta AI memperketat enkapsulasi dengan mengubah semua atribut menjadi `private (-)`, menyediakan method akses publik (`+`), dan menempatkan method `hitungIPK()` khusus pada kelas `Mahasiswa`.
- **Alasan revisi:** Menerapkan prinsip enkapsulasi OOP secara ketat (*information hiding*) dan memastikan tanggung jawab penghitungan IPK berada pada pemegang data nilai mahasiswa (*Information Expert*).
- **Commit terkait:** `58f6338` - `feat: initial commit with SEVIMA Mini UML class diagram` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** AI mampu memetakan 10 kelas requirement dan memecah relasi M:N secara tepat dengan kardinalitas, namun visibilitas atribut `User` masih berstatus protected (`#`) dan fungsionalitas `hitungIPK()` belum terdefinisi.
- **Plan:** Menginstruksikan AI untuk memperketat enkapsulasi (semua atribut private), menambahkan getter/setter publik, dan menambahkan method `hitungIPK()` eksklusif di `Mahasiswa`.
- **Act:** Memberikan prompt perbaikan spesifikasi atribut/method dan meminta inisialisasi repositori Git beserta commit awal.
- **Reflect:** AI sangat efektif menyusun kerangka diagram secara cepat, namun instruksi enkapsulasi perlu dipertegas agar tidak menggunakan akses `protected` yang berlebihan.

---

### Prompt #2 (versi: V2)
- **Tanggal / alat AI:** 13 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Menyempurnakan visibilitas atribut menjadi private penuh, melengkapi method accessor publik, menambahkan method `hitungIPK()` pada `Mahasiswa`, serta menyusun dokumentasi spesifikasi OOP.
- **Prompt:**
  ```text
  Lengkapi atribut dan method setiap kelas dengan tipe data dan visibility (+, -, #). Aturan: atribut sebanyak mungkin private, akses lewat method public; hitungIPK() hanya di Mahasiswa (bukan di User); tidak ada kelas dengan lebih dari 10 method. Jangan menambah kelas baru. Output: kode Mermaid classDiagram lengkap dalam satu code block, lalu daftar singkat perubahan yang Anda buat.
  ```
- **Output ringkas:** Diagram Versi 2 dengan atribut private penuh, method `+hitungIPK() double` pada `Mahasiswa`, accessor publik lengkap, dan dokumentasi detail di [class-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.md).
- **Masalah ditemukan:**
  1. Relasi `Course` ke `Enrollment`, `Dosen` ke `Course`, dan `Course` ke `Course (Prasyarat)` masih memakai notasi agregasi (`o--`), padahal secara semantik OOP bukan relasi kepemilikan wadah-bagian (*whole-part*).
  2. Kardinalitas `Course` ke `Schedule` tertulis `1..*`, padahal mata kuliah baru di katalog kurikulum belum tentu langsung memiliki jadwal penawaran semester.
- **Revisi manual saya:** Melakukan pengujian arsitektur relasi menggunakan uji wadah-bagian (*lifecycle dependency*) dan uji *is-a* pada tabel perbandingan sebelum mengubah diagram.
- **Alasan revisi:** Mencegah kekeliruan klasifikasi relasi antara Asosiasi, Agregasi, dan Komposisi agar representasi UML benar-benar presisi secara formal.
- **Commit terkait:** `f5d2df3` - `docs: enrich class diagram documentation with OOP specs and business rules` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Enkapsulasi privat dan pembatasan $\le 10$ method per kelas telah terpenuhi dengan baik di Versi 2, namun semantik relasi agregasi masih rancu dengan asosiasi biasa.
- **Plan:** Menganalisis seluruh relasi dengan kriteria ketat: "Jika wadahnya dihapus, apakah bagiannya ikut hilang?" dan menyajikannya dalam tabel evaluasi.
- **Act:** Meminta AI meninjau relasi dan menyajikan hasil analisis tabel tanpa langsung mengubah diagram.
- **Reflect:** Pendekatan *review-first* via tabel analisis sangat membantu memvalidasi konsep sebelum mengubah kode/artefak desain.

---

### Prompt #3 (versi: V3)
- **Tanggal / alat AI:** 13 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Meninjau dan menentukan jenis relasi yang tepat (*association*, *aggregation*, *composition*, *inheritance*) melalui uji wadah-bagian (*lifecycle dependency*) dan uji *is-a*, yang kemudian diterapkan pada diagram Versi 3.
- **Prompt:**
  ```text
  Tinjau relasi pada class diagram tersebut:
  Untuk setiap relasi, tentukan jenis yang tepat (association, aggregation, composition, inheritance) dengan uji: "jika wadahnya dihapus, apakah bagiannya ikut hilang?". Periksa juga kardinalitas dan uji is-a pada setiap pewarisan. Sajikan dalam tabel: relasi | jenis sekarang | jenis seharusnya | alasan. Jangan mengubah diagram dulu.
  ```
- **Output ringkas:** Tabel analisis lengkap relasi yang mengevaluasi uji wadah dan uji *is-a*, dilanjutkan dengan penerapan refactoring relasi ke Versi 3 pada [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd) dan bukti visual [diagram_versi_3.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/diagram_versi_3.png).
- **Masalah ditemukan:**
  1. Relasi `Course - Enrollment`, `Dosen - Course`, dan `Course - Course (Prasyarat)` tidak memenuhi kriteria wadah-bagian (*whole-part*) sehingga salah diklasifikasikan sebagai agregasi (`o--`), seharusnya asosiasi referensial (`-->`).
  2. Kardinalitas minimum jadwal `Course` ke `Schedule` terlalu restriktif (`1..*`), seharusnya `0..*` agar mata kuliah kurikulum baru dapat dibuat sebelum jadwal disusun.
- **Revisi manual saya:** Menyetujui rekomendasi tabel analisis dan meminta AI menerapkan perubahan relasi tersebut ke diagram, membuat screenshot Versi 3, dan melakukan commit.
- **Alasan revisi:** Memastikan seluruh relasi diagram patuh pada semantik UML formal dan mencerminkan siklus hidup objek sesungguhnya.
- **Commit terkait:** `46604ef` - `feat: apply relational refactoring (version 3) and add screenshot evidence` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Uji wadah membuktikan bahwa banyak relasi yang sebelumnya dianggap agregasi sebenarnya hanyalah asosiasi referensial biasa karena entitas target memiliki siklus hidup independen.
- **Plan:** Mengubah notasi agregasi (`o--`) menjadi asosiasi (`-->`) pada relasi non-wadah dan melonggarkan batas minimum kardinalitas jadwal.
- **Act:** Meminta AI mengimplementasikan hasil tabel analisis ke dalam file Mermaid, menghasilkan screenshot pembuktian, dan melakukan commit Versi 3.
- **Reflect:** Uji "jika wadah dihapus, apakah bagian ikut hilang?" adalah instrumen verifikasi yang sangat konkret untuk membedakan komposisi, agregasi, dan asosiasi secara objektif.

---

### Prompt #4 (versi: V4)
- **Tanggal / alat AI:** 13 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengidentifikasi dan membedah 5 kelemahan arsitektural terbesar pada sistem (fokus pada God Object, circular dependency, rigid inheritance, dll) sebagai landasan perbaikan Versi 4.
- **Prompt:**
  ```text
  Tinjau class diagram di atas. Sebutkan 5 kelemahan terbesar, diurutkan dari yang paling berisiko. Periksa khusus: God Object (kelas dengan terlalu banyak tanggung jawab), circular dependency, inheritance yang tidak lolos uji is-a, aggregation/composition tertukar, atribut yang seharusnya private tetapi public, kardinalitas yang salah, dan kelas yang tidak ada di requirement. Jangan memperbaiki dulu, hanya berikan kritik.
  ```
- **Output ringkas:** Laporan kritik arsitektur 5 kelemahan terbesar sistem yang diurutkan berdasarkan risiko, dilanjutkan dengan penyelesaian 4 kelemahan paling kritis ke dalam diagram Versi 4 pada [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd) dan bukti visual [diagram_versi_4.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/diagram_versi_4.png).
- **Masalah ditemukan:**
  1. Terputusnya relasi jadwal: `Schedule` tidak terhubung ke `Enrollment` dan `Dosen` (*broken operational workflow*).
  2. Anti-pattern *subclassing a lifecycle state* pada `CalonMahasiswa` vs `Mahasiswa` (tidak ada transisi peran saat diterima).
  3. Ketergantungan siklik (*circular dependency*) dua arah antara `Course` dan `Mahasiswa`.
  4. Ambiguitas peran `Enrollment` dan penumpukan tanggung jawab KRS semesteran pada kelas `Mahasiswa`.
- **Revisi manual saya:** Meminta AI memperbaiki 4 kelemahan kritis tersebut dengan: menghubungkan `Schedule` ke `Enrollment` dan `Dosen`, menambahkan method konversi peran PMB, memutus *circular dependency* dengan signature `String[]`, serta menata delegasi SKS.
- **Alasan revisi:** Menyelamatkan alur kerja fungsional operasional akademik (KRS & Jadwal) dan mengeliminasi kopling antarmodul agar sistem memenuhi standar arsitektur tingkat lanjut.
- **Commit terkait:** `a8fce29` - `feat: resolve architectural flaws 1-4 (version 4) and add screenshot evidence` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Kritik arsitektur mengungkap bahwa meskipun diagram sudah rapi secara visual dan enkapsulasi, ada celah fatal pada alur data operasional (jadwal tidak terhubung ke KRS) dan kopling melingkar.
- **Plan:** Menyusun solusi arsitektural untuk 4 isu kritis tanpa menambah kelas di luar requirement 10 kelas awal.
- **Act:** Meminta AI mengaplikasikan solusi perbaikan 1–4, meregenerasi screenshot bukti visual Versi 4, dan melakukan commit final.
- **Reflect:** Siklus evaluasi kritis berbasis risiko (*risk-driven refinement*) menghasilkan rancangan arsitektur yang tidak hanya patuh pada sintaks OOP, tetapi juga kokoh secara logika domain operasional.
