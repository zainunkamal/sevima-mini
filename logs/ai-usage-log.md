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
- **Output ringkas:** Tabel analisis lengkap relasi yang mengevaluasi uji wadah dan uji *is-a*, dilanjutkan dengan penerapan refactoring relasi ke Versi 3 pada [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd) dan bukti visual [diagram_versi_3.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-01/diagram_versi_3.png).
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
- **Output ringkas:** Laporan kritik arsitektur 5 kelemahan terbesar sistem yang diurutkan berdasarkan risiko, dilanjutkan dengan penyelesaian 4 kelemahan paling kritis ke dalam diagram Versi 4 pada [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd) dan bukti visual [diagram_versi_4.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-01/diagram_versi_4.png).
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

---

## AI Usage Log: Minggu 2

### Prompt #1 (versi: Use Case Diagram V1)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Merancang Use Case Diagram formal UML 2.5 untuk sistem informasi akademik "SEVIMA Mini" dengan batasan 4 aktor, 10 use case, serta penentuan relasi `<<include>>` dan `<<extend>>` yang tepat.
- **Prompt:**
  ```text
  Anda adalah analis sistem dan arsitek OOP senior.

  Konteks: sistem informasi akademik "SEVIMA Mini".

  Buat use case diagram dengan:
  - Aktor: Mahasiswa, Dosen (PA), Admin Akademik, Sistem PMB.
  - Use case: Daftar sebagai Calon Mahasiswa, Verifikasi Berkas, Isi KRS,
    Cek Prasyarat, Approve KRS, Ajukan Revisi KRS, Input Nilai,
    Generate Transkrip, Bayar SPP, Bayar Denda Keterlambatan.
  - Tandai <<include>> dan <<extend>> yang benar:
    include = langkah wajib (panah dari use case dasar ke yang di-include);
    extend = tambahan bersyarat (panah dari use case tambahan ke use case dasar).
  - Semua use case di dalam system boundary "SEVIMA Mini"; aktor di luar.
  - Nama use case: kata kerja + objek, dari sudut pandang pengguna.

  Format output: kode PlantUML dalam satu code block (Mermaid tidak punya
  tipe use case bawaan). Setelah itu, jelaskan singkat alasan setiap
  relasi include dan extend.
  ```
- **Output ringkas:** Kode PlantUML tersimpan di [use-case-diagram.puml](file:///home/zainun/git/istn/sevima-mini/diagram/use-case-diagram.puml), spesifikasi lengkap di [use-case-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/use-case-diagram.md), dan bukti visual di [use_case_versi_1.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-02/use_case_versi_1.png).
- **Keputusan Arsitektur Utama:**
  1. `(Isi KRS) ..> (Cek Prasyarat) : <<include>>`: Langkah validasi wajib internal.
  2. `(Bayar Denda Keterlambatan) ..> (Bayar SPP) : <<extend>>`: Perluasan bersyarat jika melewati jatuh tempo.
  3. `(Ajukan Revisi KRS) ..> (Isi KRS) : <<extend>>`: Percabangan kondisional jika ditolak Dosen PA atau masa KPRS.
  4. Pemisahan domain pembayaran SPP dan pendaftaran PMB dari dependensi sinkron use case.
- **Commit terkait:** `28d7e3f` - `feat: add use case diagram (version 1) and screenshot evidence` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Standar UML 2.5 membedakan secara tegas langkah wajib (`<<include>>`) yang selalu dieksekusi dari use case dasar, dengan cabang alternatif/bersyarat (`<<extend>>`) yang mengarah balik ke use case dasar saat kondisi tertentu terpenuhi.
- **Plan:** Menyusun arsitektur use case dengan memisahkan boundary sistem, memetakan aktor manusia vs sistem eksternal, dan menerapkan relasi include/extend secara presisi tanpa anti-pattern.
- **Act:** Meng-generate kode PlantUML, merender artefak gambar PNG, menyimpannya ke `diagram/` dan `perbaikan/minggu-02/`, serta memperbarui dokumentasi proyek.
- **Reflect:** Kejelasan batasan tanggung jawab aktor (*boundaries of concern*) dan pemisahan prakondisi waktu (*temporal separation*) sangat penting agar Use Case Diagram mencerminkan interaksi pengguna nyata dan bukan sekadar diagram alir proses (flowchart).

---

### Prompt #2 (versi: Sequence Diagram Validasi KRS V1)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Merancang Sequence Diagram UML interaksi objek untuk skenario Validasi KRS dengan 6 partisipan, penerapan fragmen `loop`, `opt`, `alt`, serta pola *error accumulator* untuk menampung seluruh pesan kesalahan sekaligus.
- **Prompt:**
  ```text
  Anda adalah arsitek OOP senior.

  Buat sequence diagram validasi KRS dengan partisipan yang SAMA dengan
  class diagram saya: [DAFTAR NAMA KELAS, mis. Mahasiswa, KRSManager,
  KRSValidator, Repository, NotificationService, DosenPA].

  Alur:
  1. Mahasiswa submit KRS ke KRSManager.
  2. KRSManager mendelegasikan validasi ke KRSValidator.
  3. KRSValidator memakai fragmen loop untuk cek prasyarat setiap mata
     kuliah lewat Repository.
  4. KRSValidator (self call) menghitung total SKS, batas maksimal 24.
  5. KRSValidator cek jadwal bentrok.
  6. Jika valid: simpan KRS status "pending approval", kirim notifikasi
     ASINKRON ke DosenPA melalui NotificationService.

  Alternate flow (fragmen alt; kumpulkan SEMUA error sekaligus):
  - Prasyarat belum lulus: pesan menyebut mata kuliah prasyarat yang kurang.
  - Total SKS > 24: pesan menyebut total dan batas (mis. "SKS Anda 26, batas 24").
  - Jadwal bentrok: pesan menyebut dua mata kuliah yang bertabrakan.

  Format output: Mermaid sequenceDiagram dalam satu code block,
  tanpa penjelasan panjang.
  ```
- **Output ringkas:** Kode sumber Mermaid tersimpan di [sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/sequence-diagram.mmd), spesifikasi teknis di [sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/sequence-diagram.md), dan bukti visual tangkapan layar di [sequence_diagram_versi_1.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-02/sequence_diagram_versi_1.png).
- **Keputusan Arsitektur Utama:**
  1. Penerapan pola *Error Accumulator* pada `KRSValidator` agar validasi tidak berhenti prematur (*fail-fast*) melainkan mengevaluasi seluruh aturan (prasyarat, batas 24 SKS, dan jadwal bentrok) untuk memberikan umpan balik menyeluruh kepada mahasiswa.
  2. Penggunaan pesan asinkron (`-)`) dari `KRSManager` ke `NotificationService` untuk mencegah latensi pengiriman pesan menghambat alur respon pengajuan KRS.
- **Commit terkait:** `910b8f0` - `feat: add KRS validation sequence diagram (version 1) and screenshot evidence` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Dalam skenario validasi formulir kompleks seperti KRS, mahasiswa membutuhkan umpan balik komprehensif atas semua kesalahan yang terjadi sekaligus daripada harus memperbaiki satu per satu secara berulang.
- **Plan:** Memetakan interaksi 6 kelas/komponen secara modular dengan pembagian peran SRP (Manager sebagai orkestrator, Validator sebagai domain rule engine, Repository sebagai data access, NotificationService sebagai pemroses event asinkron).
- **Act:** Menulis diagram interaksi Mermaid yang patuh kaidah aktivasi objek dan fragmen kontrol, merender hasil grafis ke direktori perbaikan Minggu 2, serta memperbarui dokumentasi.
- **Reflect:** Sequence diagram memperjelas batasan temporal dan pesan inter-objek yang tidak terlihat pada class diagram statis, melengkapi arsitektur SEVIMA Mini menjadi siap diimplementasikan ke kode sumber.

---

### Prompt #3 (versi: Sequence Diagram PMB V1)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Merancang Sequence Diagram UML untuk alur Penerimaan Mahasiswa Baru (PMB) dengan 6 partisipan, penerapan Factory Pattern (`UserFactory`), pemanggilan notifikasi asinkron, serta penanganan *alternate flow* berkas tidak lengkap dan ketahanan kegagalan pengiriman email (*retry/log*).
- **Prompt:**
  ```text
  Buat sequence diagram pendaftaran mahasiswa baru (PMB) dengan partisipan:
  CalonMahasiswa, PMBService, Database, Admin, UserFactory,
  NotificationService.

  Alur: daftar -> PMBService simpan ke Database -> kembalikan nomor
  pendaftaran; Admin verifikasi berkas dan nyatakan lulus; PMBService
  meminta UserFactory membuat Mahasiswa lengkap dengan NIM; simpan; kirim
  pesan ASINKRON ke NotificationService; email berisi NIM dan akun.

  Tambahkan alternate flow (fragmen alt): berkas tidak lengkap, dan email
  gagal terkirim (retry/log, jangan membatalkan pendaftaran).

  Format: Mermaid sequenceDiagram dalam satu code block.
  ```
- **Output ringkas:** Kode sumber Mermaid tersimpan di [pmb-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/pmb-sequence-diagram.mmd), spesifikasi teknis di [pmb-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/pmb-sequence-diagram.md), dan bukti visual tangkapan layar di [pmb_sequence_diagram_versi_1.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-02/pmb_sequence_diagram_versi_1.png).
- **Keputusan Arsitektur Utama:**
  1. Penggunaan pola kreasi `UserFactory` untuk enkapsulasi instansiasi objek `Mahasiswa`, format kalkulasi NIM, dan kredensial akun pengguna baru.
  2. Isolasi kegagalan notifikasi email: jika pengiriman email gagal setelah 3 kali retry, error dicatat ke `Database` tanpa melakukan *rollback* terhadap status kelulusan mahasiswa baru (*non-blocking resilient notification*).
  3. Penanganan verifikasi berkas tidak lengkap dengan notifikasi revisi ke `CalonMahasiswa`.
- **Commit terkait:** `0126f14` - `feat: add PMB sequence diagram (version 1) and screenshot evidence` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Pada alur pendaftaran mahasiswa baru, proses administratif (pemberian NIM & akun) memiliki dependensi transaksi yang kritis, sementara pengiriman notifikasi email bersifat *eventual consistency*.
- **Plan:** Memisahkan alur transaksi utama dengan komunikasi asinkron (`-)`), menambahkan mekanisme retry dan logging (DLQ pattern) agar kegagalan layanan email pihak ketiga tidak membatalkan proses penerimaan mahasiswa.
- **Act:** Mengimplementasikan diagram interaksi Mermaid dengan fragmen `alt` bertingkat, mengonversi ke artefak visual beresolusi tinggi, dan menyimpannya ke direktori repositori.
- **Reflect:** Pemodelan alternate flow yang tangguh (*resilient architecture*) membedakan rancangan sistem level pemula dengan arsitektur enterprise siap produksi.

---

### Prompt #4 (versi: Penyelarasan Penuh Arsitektur & Sinkronisasi Opsi A)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Menyelaraskan seluruh ketidaksinkronan antara Class Diagram, Use Case Diagram, dan Sequence Diagrams menggunakan Opsi A (Layered Architecture), serta melengkapi sequence diagram hingga mencakup 100% use case.
- **Prompt:**
  ```text
  oke saya mau kamu sesuaikan semuanya berdasarkan temuan sinkronisasi diatas. Untuk No.1 saya ingin menggunakan Opsi A
  ```
- **Output ringkas:**
  1. Class Diagram diperbarui ke Versi 5 dengan penambahan `KRSManager`, `KRSValidator`, `PMBService`, `UserFactory`, `Repository`, dan `NotificationService`.
  2. Use Case Diagram diselaraskan dengan penambahan aktor `Calon Mahasiswa` mendampingi `Sistem PMB`.
  3. Sequence Diagram KRS dan PMB diselaraskan method dan partisipannya (`Dosen` dan `Repository`).
  4. Penambahan 3 Sequence Diagram baru: `krs-approval-sequence-diagram.mmd` (Approve/Revisi KRS), `payment-sequence-diagram.mmd` (Bayar SPP & Denda), dan `grading-transcript-sequence-diagram.mmd` (Input Nilai & Transkrip) sehingga 100% dari 10 use case terpetakan.
  5. Seluruh bukti visual tangkapan layar dirender dan disimpan di folder `perbaikan/minggu-02/`.
- **Keputusan Arsitektur Utama:**
  - Menerapkan arsitektur berlapis (Clean/Layered Architecture) yang memisahkan Controller/Manager, Domain Service, Factory, Data Access (Repository), dan Infrastructure (Notification).
  - Konsistensi 100% antara signature method di Class Diagram dan pemanggilan pesan di seluruh Sequence Diagram.
- **Commit terkait:** `177e78b` - `feat: synchronize class diagram (v5), use case (v2), and complete 100% sequence coverage` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Hasil audit komparasi silang (*cross-model verification*) mengungkap ketimpangan antara model data statis (hanya entitas) dengan model dinamis (yang membutuhkan lapisan service dan repository).
- **Plan:** Mengadopsi Opsi A secara terstruktur dengan mengekspansi Class Diagram ke Versi 5, menyelaraskan nama aktor dan method, serta menutup celah use case yang belum memiliki sequence diagram.
- **Act:** Memperbarui kode Mermaid dan PlantUML, merender 7 diagram beresolusi tinggi, dan menyinkronkan seluruh dokumentasi teknis proyek.
- **Reflect:** Model sistem perangkat lunak yang matang harus memiliki koherensi vertikal (antar-lapisan arsitektur) dan horizontal (antar-sudut pandang UML: struktural, fungsional, dan perilaku interaksi).

---

### Prompt #5 (versi: Refactor Arsitektur SOLID Penuh - Versi 6)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Melakukan audit kritis dan refactoring class diagram SEVIMA Mini terhadap prinsip SOLID, mengeliminasi God Object `Admin`, memecah layanan spesifik per modul, mengimplementasikan antarmuka peran (*role-based interfaces*), serta menerapkan *Strategy Pattern* (`ValidationRule`) dan abstraksi kanal notifikasi (`NotificationChannel`) berbasis *Dependency Injection*.
- **Prompt:**
  ```text
  Audit class diagram berikut terhadap prinsip SOLID, fokus pada
  Single Responsibility dan Dependency Inversion:

  Identifikasi kelas yang punya terlalu banyak tanggung jawab (God Object).
  Usulkan pemecahan menjadi service per modul: PMBService, KRSService +
  KRSValidator, JadwalService, NilaiService, KeuanganService, PresensiService, NotificationService. Gunakan interface kecil sesuai peran (mis. PengisiKRS, PenyetujuKRS, Penilai), NotificationChannel, dan
  ValidationRule, dengan dependency injection.
  Output: 
  (1) tabel temuan: kelas | pelanggaran | prinsip SOLID,
  (2) class diagram hasil refactor dalam Mermaid, 
  (3) alasan singkat tiap perubahan.
  ```
- **Output ringkas:** Kode sumber Mermaid Versi 6 tersimpan di [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd), dokumentasi teknis di [class-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.md), dan bukti visual tangkapan layar di [class_diagram_versi_6.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-02/class_diagram_versi_6.png).
- **Keputusan Arsitektur Utama:**
  1. Pemecahan God Object `Admin` & `Mahasiswa`: Logika operasional didelegasikan ke 7 service spesifik modul (`PMBService`, `KRSService`, `JadwalService`, `NilaiService`, `KeuanganService`, `PresensiService`, `NotificationService`).
  2. Penerapan *Interface Segregation Principle* (ISP) & *Dependency Inversion Principle* (DIP) melalui antarmuka peran: `PengisiKRS`, `PenyetujuKRS`, `Penilai`.
  3. Pemisahan aturan validasi dengan *Strategy Pattern* (`ValidationRule`) dan abstraksi komunikasi (`NotificationChannel`).
  4. Entitas domain bersih (*Clean POCO / High Cohesion*) bebas dari logika komputasi operasional.
- **Commit terkait:** `fefffa3` - `feat: refactor class diagram to version 6 adhering to full SOLID principles` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Meskipun sistem sudah memiliki lapisan service, kelas `Admin` dan entitas `Mahasiswa` masih menanggung beban tanggung jawab berlebih (God Object & bloated entities), sementara validasi dan notifikasi belum terabstraksi dengan Dependency Inversion.
- **Plan:** Memecah tanggung jawab ke service modular berbasis modul akademik, mendefinisikan antarmuka peran ramping, serta menerapkan pola Strategy dan Inversion of Control.
- **Act:** Mengimplementasikan Class Diagram Versi 6 dalam Mermaid, merender screenshot beresolusi tinggi (700 KB), memperbarui spesifikasi teknis dan dokumentasi perbaikan.
- **Reflect:** Penerapan prinsip SOLID secara ketat mengubah arsitektur monolitik prosedural menjadi sistem berorientasi objek yang fleksibel (*extensible*), mudah diuji (*testable*), dan siap diadopsi dalam skala produksi.
