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

---

### Prompt #6 (versi: V7 - Integrasi Design Patterns: Factory, Observer, Strategy)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengintegrasikan tiga pola desain (*GoF Design Patterns*) secukupnya tanpa menambah kelas yang tidak perlu: Factory Pattern (`UserFactory` dengan invarian mutlak mahasiswa wajib ber-NIM), Observer Pattern (`KRSSubscriber` & `KRSManager`), dan Strategy Pattern (`ValidationRule` beserta 3 aturan konkret yang diagregasi oleh `KRSValidator`).
- **Prompt:**
  ```text
  Pada class diagram saya.

  Tambahkan tiga pattern secukupnya, tanpa menambah kelas yang tidak perlu:
  1. Factory: UserFactory yang membuat Mahasiswa, Dosen, Admin, dan
     CalonMahasiswa (Mahasiswa selalu punya NIM).
  2. Observer: KRSManager mengumumkan event perubahan status KRS;
     Mahasiswa, Dosen PA, dan bagian akademik adalah subscriber.
  3. Strategy: interface ValidationRule dengan implementasi
     CekPrasyaratRule, CekBatasSKSRule, CekJadwalBentrokRule, sehingga
     aturan baru (mis. CekTunggakanRule) bisa ditambah tanpa mengubah
     KRSValidator (Open/Closed).

  Output: Mermaid classDiagram yang diperbarui + penjelasan singkat
  manfaat tiap pattern di sistem ini.
  ```
- **Output ringkas:** Kode sumber Mermaid Versi 7 pada [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd), dokumentasi teknis lengkap di [class-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.md), dokumentasi evolusi di [perbaikan/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/README.md), sinkronisasi [README.md](file:///home/zainun/git/istn/sevima-mini/README.md), serta artefak visual [class_diagram_versi_7.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-02/class_diagram_versi_7.png) dan [class_diagram_design_patterns.png](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-02/class_diagram_design_patterns.png).
- **Keputusan Arsitektur Utama:**
  1. **Factory Pattern (`UserFactory`):** Memusatkan instansiasi turunan `User`. Mengunci invarian bisnis bahwa `createMahasiswa(...)` wajib menerima parameter `nim`, sehingga mustahil menciptakan objek `Mahasiswa` berstatus *invalid* (tanpa NIM) di dalam memori sistem.
  2. **Observer Pattern (`KRSSubscriber` & `KRSManager`):** `KRSManager` mempublikasikan event `onStatusKRSChanged` kepada seluruh observer (`Mahasiswa`, `Dosen`, `Admin`) yang mengimplementasikan `KRSSubscriber`. Mengeliminasi *tight coupling* antara alur persetujuan KRS dan subsistem notifikasi pihak berkepentingan.
  3. **Strategy Pattern (`ValidationRule` & `KRSValidator`):** `KRSValidator` bertindak sebagai *Rule Engine* independen yang mengeksekusi daftar `ValidationRule` (`CekPrasyaratRule`, `CekBatasSKSRule`, `CekJadwalBentrokRule`). Penambahan aturan bisnis baru (misal `CekTunggakanRule`) dapat dilakukan secara *plug-and-play* tanpa memodifikasi kode inti `KRSValidator` (*Open/Closed Principle*).
- **Commit terkait:** `02a4050` - `feat: integrate Factory, Observer, and Strategy design patterns into class diagram (version 7)` [AI-assisted]

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Meskipun sistem sudah menerapkan modularitas SOLID, proses kreasi user rawan inkonsistensi status (mahasiswa tanpa NIM), notifikasi perubahan status KRS berpotensi menimbulkan kopling langsung, dan penambahan aturan validasi KRS berisiko memodifikasi validator yang sudah stabil.
- **Plan:** Menyelaraskan arsitektur dengan 3 GoF pattern secara proporsional (*lean*): Factory untuk integritas data user, Observer untuk *loose-coupling* event KRS, dan Strategy untuk ekstensibilitas aturan validasi tanpa kelas berlebih.
- **Act:** Mengintegrasikan struktur kelas ke Mermaid, memperbarui dokumentasi teknis, menghasilkan rendering gambar resolusi tinggi melalui Kroki, serta mencatat riwayat pembaruan ke README dan log AI.
- **Reflect:** Desain pola (*design patterns*) yang diterapkan secara tepat sasaran mampu meningkatkan fleksibilitas dan ketahanan sistem tanpa menciptakan *over-engineering* atau kompleksitas yang tidak perlu.

---

## AI Usage Log: Minggu 3

### Prompt #1 (versi: V1 - Implementasi Model Data SQLAlchemy 2.0 & Migrasi Alembic PMB)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengimplementasikan model basis data modern SQLAlchemy 2.0 (`Mapped` dan `mapped_column`) dan skrip migrasi terkelola Alembic untuk 3 tabel modul PMB (`program_studi`, `jalur_masuk`, `calon_mahasiswa`) berbasis SQLite, menjamin integritas relasional via `PRAGMA foreign_keys = ON;`, dan memetakan batas penegakan constraint antara database dan aplikasi.
- **Prompt:**
  ```text
  Anda adalah backend engineer Python senior.

  Konteks: modul PMB (penerimaan mahasiswa baru) sistem akademik "SEVIMA Mini".
  Stack: Python, SQLAlchemy 2 (gaya Mapped dan mapped_column, BUKAN gaya lama
  declarative_base/Column), Alembic, database SQLite.

  Buat model SQLAlchemy dan migrasi Alembic untuk 3 tabel:
  1. program_studi: id (PK), kode (string 3 karakter, UNIQUE), nama, fakultas.
  2. jalur_masuk: id (PK), nama (UNIQUE; contoh SNBP, SNBT, Mandiri).
  3. calon_mahasiswa: id (PK), nama_lengkap (NOT NULL), email (UNIQUE, index,
     NOT NULL), phone (STRING, bukan integer), tanggal_lahir, alamat,
     program_studi_id (FK, NOT NULL), jalur_masuk_id (FK), status
     (ENUM: pending/approved/rejected, default pending, dengan CHECK constraint
     aktif), nim (nullable, UNIQUE), created_at (server_default now),
     approved_at (nullable).

  Syarat:
  - Migrasi punya fungsi upgrade DAN downgrade (downgrade menghapus
    calon_mahasiswa lebih dulu).
  - Aktifkan PRAGMA foreign_keys untuk SQLite.
  - Format nomor HP TIDAK divalidasi di database (SQLite tanpa regex bawaan);
    database cukup membatasi panjang.
  - Jelaskan singkat di mana setiap constraint ditegakkan (database atau aplikasi).

  Format output: kode per file (models, migrasi), lalu penjelasan singkat.
  ```
- **Output ringkas:**
  1. Modul engine dan koneksi basis data di `app/database.py` dengan hook listener `@event.listens_for(Engine, "connect")` untuk mengaktifkan `PRAGMA foreign_keys=ON;` secara otomatis pada setiap sesi koneksi SQLite.
  2. Model deklaratif ORM modern di `app/models/pmb.py` menggunakan `Mapped` dan `mapped_column` dengan relasi dua arah (`relationship`), pembatasan panjang kolom, dan `CheckConstraint` aktif untuk status PMB.
  3. Konfigurasi runner migrasi di `alembic/env.py` dengan penegakan SQLite pragma dan `render_as_batch=True`.
  4. Skrip migrasi terkelola di `alembic/versions/20261114_0001_create_pmb_tables.py` dengan implementasi `upgrade()` dan `downgrade()` terurut (tabel `calon_mahasiswa` dihapus lebih dulu untuk menjaga kepatuhan FK constraint).
  5. Dokumentasi dan matriks perbandingan tanggung jawab constraint antara basis data dan lapisan aplikasi di `perbaikan/minggu-03/README.md`.
- **Keputusan Arsitektur Utama:**
  1. **Aktivasi Pragma Foreign Keys SQLite:** SQLite menonaktifkan FK secara *default*. Penegakan dilakukan pada dua titik kritis: *runtime application connection* (`app/database.py`) dan *migration connection runner* (`alembic/env.py` & skrip migrasi).
  2. **Penyimpanan Nomor Telepon:** Nomor HP disimpan sebagai `VARCHAR(20)` (String, bukan Integer) untuk mempertahankan digit nol di awal (*leading zero*) dan kode negara (`+62`). Pembatasan panjang diterapkan di database, sedangkan validasi pola format diserahkan ke *application layer* (Pydantic / service layer) karena SQLite standar tidak memiliki mesin regex *native*.
  3. **Urutan Downgrade Konsisten:** Skrip migrasi `downgrade()` menghapus tabel `calon_mahasiswa` terlebih dahulu sebelum menghapus `jalur_masuk` dan `program_studi` guna mencegah pelanggaran integritas referensial.
- **Commit terkait:** `e990cec` - `feat(pmb): implement SQLAlchemy 2 models and Alembic migration for PMB module [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** SQLite memiliki karakteristik khusus di mana penegakan *foreign key* harus diaktifkan secara eksplisit per koneksi dan ketiadaan fungsi bawaan regex untuk validasi format teks kompleks.
- **Plan:** Menyusun konfigurasi SQLAlchemy 2.0 murni (`DeclarativeBase`, `Mapped`, `mapped_column`), menambahkan event listener koneksi engine SQLite, mengonfigurasi batch mode pada Alembic, dan merancang skema yang membagi peran validasi secara seimbang antara database dan domain aplikasi.
- **Act:** Mengimplementasikan kode per berkas secara modular (`app/database.py`, `app/models/pmb.py`, `alembic.ini`, `alembic/env.py`, skrip migrasi), mendokumentasikan spesifikasi di README Minggu 3, dan menyinkronkan struktur proyek.
- **Reflect:** Menegakkan aturan integritas pada level yang tepat (skema fisik di database, aturan format & siklus hidup bisnis di aplikasi) menghasilkan sistem yang tangguh, mencegah korupsi data, sekaligus menjaga efisiensi komputasi basis data.

---

### Prompt #2 (versi: V2 - Implementasi Endpoint Pendaftaran PMB FastAPI & Layered Architecture)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Membangun endpoint `POST /api/pmb/register` menggunakan FastAPI berbasis *Layered Architecture* (Router, Service, Schema/DTO, Model), menerapkan pencegahan *race condition* konkurensi email ganda, mengamankan privasi data pendaftar, dan merestrukturisasi penanganan error validasi menjadi HTTP 400 ramah pengguna.
- **Prompt:**
  ```text
  Anda adalah backend engineer Python senior.

  Konteks: berikut model SQLAlchemy dan struktur folder project saya
  (app/models, app/schemas, app/services, app/routers, app/database.py):
  [TEMPEL KODE MODEL + STRUKTUR FOLDER]

  Buat endpoint POST /api/pmb/register dengan FastAPI:
  - Skema Pydantic RegisterRequest: nama_lengkap minimal 3 karakter, email
    (EmailStr), phone (regex nomor HP Indonesia: awalan 08, 62, atau +62),
    tanggal_lahir, alamat, program_studi_id dan jalur_masuk_id lebih dari 0.
  - Skema respons PendaftarOut (jangan bocorkan alamat dan tanggal lahir).
  - Service: cek email ganda, cek program studi dan jalur masuk ada, simpan
    dengan status pending, tangani IntegrityError (race condition email).
  - Router tipis dengan dependency injection get_db (yield + finally).
  - Status code: 201 sukses, 409 email ganda, 400 referensi tidak valid,
    error validasi format -> 400 (ubah handler RequestValidationError).
  - Pesan error ramah; jangan kirim stack trace atau pesan DB mentah.

  Format output: kode per file, tanpa penjelasan panjang.
  ```
- **Output ringkas:**
  1. Generator dependency injection `get_db` pada [app/database.py](file:///home/zainun/git/istn/sevima-mini/app/database.py) dengan *lifecycle yield-finally* penutupan koneksi sesi.
  2. DTO validasi Pydantic v2 di [app/schemas/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/schemas/pmb.py) mencakup `RegisterRequest` (regex nomor HP `^(\+62|62|08)[0-9]{7,13}$`, panjang string, validasi email, `gt=0`) serta `PendaftarOut` yang menyaring atribut privat (`alamat` dan `tanggal_lahir`).
  3. Lapisan *domain service* di [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py) dengan verifikasi eksistensi referensi foreign key serta blok pencegat *race condition* `try-except IntegrityError` (HTTP 409).
  4. Pengendali tipis (*thin router*) di [app/routers/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/routers/pmb.py) mendeklarasikan rute `POST /api/pmb/register` dengan respons `status_code=201`.
  5. Pengendali exception terpusat di [app/main.py](file:///home/zainun/git/istn/sevima-mini/app/main.py) yang menimpa `RequestValidationError` bawaan FastAPI menjadi respons HTTP 400 Bad Request dengan pesan humanis terstruktur.
  6. Suite pengujian endpoint otomatis di [tests/test_api_pmb.py](file:///home/zainun/git/istn/sevima-mini/tests/test_api_pmb.py) mencakup seluruh skenario validasi, status code, dan penyaringan privasi data.
  7. Pembaruan dokumentasi perbaikan Minggu 3 pada [perbaikan/minggu-03/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-03/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Separation of Concerns (SoC):** Router hanya mengelola rute HTTP dan dependency injection, service memegang seluruh aturan transaksi dan orkestrasi integritas data, sedangkan schema mengelola serialisasi/deserialisasi.
  2. **Mitigasi Race Condition Konkurensi:** Pengecekan `db.query().filter().first()` rentan terhadap *time-of-check to time-of-use* (TOCTOU). Penambahan penanganan `IntegrityError` saat `db.commit()` menjamin keunikan email tetap aman pada level basis data.
  3. **Privacy by Design:** `PendaftarOut` tidak mengekspos atribut identitas sensitif seperti alamat tinggal dan tanggal lahir pendaftar ke publik.
  4. **Standarisasi Kontrak Error Client:** Menyelaraskan error validasi Pydantic ke standar HTTP 400 (bukan 422 default) agar seragam dengan penolakan referensi data tidak valid.
- **Commit terkait:** `32e97dd` - `docs: document PMB register endpoint implementation in perbaikan and update AI usage log [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Validasi input tidak boleh hanya mengandalkan lapisan web framework karena rawan *race condition* saat concurrent request dan rawan membocorkan *stack trace* internal basis data saat terjadi error SQL. Selain itu, FastAPI secara default menggunakan HTTP 422 untuk schema validation yang kerap tidak selaras dengan konvensi API standar (HTTP 400).
- **Plan:** Memisahkan tanggung jawab secara tegas menggunakan arsitektur berlapis, merancang DTO protektif (tanpa atribut sensitif), mengimplementasikan proteksi ganda (query check + exception interceptor), serta menimpa exception handler bawaan FastAPI.
- **Act:** Mengimplementasikan kode per berkas (`schemas/pmb.py`, `services/pmb.py`, `routers/pmb.py`, `main.py`), menambahkan automated tests dengan `TestClient`, serta mendokumentasikan matriks status code pada folder perbaikan.
- **Reflect:** Kombinasi validasi deklaratif Pydantic di pintu masuk API, verifikasi referensial di lapisan service, dan constraint unik di level basis data membentuk pertahanan berlapis (*defense in depth*) yang kokoh, aman, dan berorientasi pada pengalaman pengguna yang baik (*clean DX/UX*).

---

### Prompt #3 (versi: V3 - Prosedur Pengujian Swagger UI OpenAPI & Seeder Data Awal)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Menyediakan skrip pengisian data awal (*seeding*), panduan eksekusi server Uvicorn, dan prosedur pengujian interaktif antarmuka Swagger UI OpenAPI untuk modul PMB.
- **Prompt:**
  ```text
  cara testnya gmn agar saya bisa check via swagger
  ```
- **Output ringkas:**
  1. Skrip *seeder* otomatis di [app/seed.py](file:///home/zainun/git/istn/sevima-mini/app/seed.py) yang memuat data awal Program Studi (TIF, SIF, ARS, TEK) dan Jalur Masuk (SNBP, SNBT, Mandiri) untuk mencegah *foreign key error* saat pengujian manual.
  2. Panduan menjalankan server pengembangan Uvicorn menggunakan *virtual environment* lokal: `uvicorn app.main:app --reload --port 8000`.
  3. Prosedur pengujian interaktif melalui antarmuka Swagger UI di `http://127.0.0.1:8000/docs` lengkap dengan skenario uji payload valid (HTTP 201), validasi regex & panjang string (HTTP 400), serta email duplikat (HTTP 409).
- **Keputusan Arsitektur Utama:**
  - Swagger UI terintegrasi langsung melalui OpenAPI spec bawaan FastAPI (`/openapi.json`), mendokumentasikan skema input `RegisterRequest` dan skema output `PendaftarOut` secara otomatis dari model Pydantic.
  - Skrip *seeder* mandiri memastikan lingkungan lokal siap pakai tanpa perlu input data SQL manual.
- **Commit terkait:** `31d7f7f` - `feat(docs): add seed script, Swagger UI testing guide, and update AI usage log [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Pengujian endpoint yang memiliki ketergantungan relasi *foreign key* (seperti `program_studi_id` dan `jalur_masuk_id`) membutuhkan data referensi valid pada basis data agar tidak menghasilkan error validasi bisnis saat diuji melalui UI Swagger.
- **Plan:** Menyediakan skrip *seeder* idempotens yang mengisi data awal Program Studi dan Jalur Masuk jika belum tersedia, serta menyusun panduan langkah demi langkah menjalankan Uvicorn dan menguji skenario positif/negatif pada Swagger UI.
- **Act:** Mengimplementasikan berkas `app/seed.py`, mengeksekusi seeding ke database `sevima_mini.db`, memverifikasi endpoint `/docs` menghasilkan respons HTTP 200, dan mencatat dokumentasi ke dalam log AI.
- **Reflect:** Menyertakan instrumen data awal (*seed data*) dan dokumentasi Swagger yang interaktif sangat menyederhanakan siklus pengujian (*Developer Experience*) bagi pengembang maupun tim penguji QA.

---

### Prompt #4 (versi: V4 - Penguatan Keamanan, Eliminasi Error Masking, & Refactoring Murni SQLAlchemy 2.0)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengimplementasikan perbaikan kritis berdasarkan hasil audit arsitektur: mengeliminasi *blind exception handling* pada `IntegrityError`, mengadopsi sintaks murni SQLAlchemy 2.0 (`select`/`scalar`), memperketat regex nomor ponsel Indonesia, menambahkan validasi batas usia calon mahasiswa, serta memperbarui suite pengujian otomatis.
- **Prompt:**
  ```text
  sekarang saya mau kamu impementasikan kemudian saya mau kamu save ke AI-Usage-log dan dengan commit AI-Assited, terus saya mau kamu kasih tau cara untuk testingnya (ini hanya sebatas cari tau saja tanpa edit kode)
  ```
- **Output ringkas:**
  1. Pembaruan [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py): Bermigrasi dari `db.query()` ke `db.scalar(select(...))` murni SQLAlchemy 2.0, serta mendiferensiasi pesan `IntegrityError` berdasarkan `exc.orig` (membedakan pelanggaran unique email, foreign key, atau check constraint).
  2. Pembaruan [app/schemas/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/schemas/pmb.py): Mengetatkan pola regex nomor HP seluler Indonesia `^(?:\+628|628|08)[1-9][0-9]{6,11}$`, menambahkan `@field_validator` usia `tanggal_lahir` (14–80 tahun), dan mengikat tipe respons `status` ke `StatusPMB`.
  3. Pembersihan prefix Pydantic pada pesan humanis di [app/main.py](file:///home/zainun/git/istn/sevima-mini/app/main.py).
  4. Penambahan skenario uji pada [tests/test_api_pmb.py](file:///home/zainun/git/istn/sevima-mini/tests/test_api_pmb.py) untuk tanggal lahir masa depan dan validasi nomor HP non-seluler (14 unit test lolos 100%).
  5. Pembaruan dokumentasi perbaikan di [perbaikan/minggu-03/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-03/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Eliminasi Error Masking:** Menghilangkan asumsi salah bahwa setiap `IntegrityError` pasti berasal dari email ganda. Pengecekan spesifik pada string origin driver basis data memastikan pelanggaran foreign key atau check constraint tetap dikembalikan dengan kode dan konteks yang tepat.
  2. **Konsistensi Modern Python Stack:** Seluruh query di service layer kini patuh pada standar SQLAlchemy 2.0 (`select` statement).
  3. **Penyempurnaan Validasi Domain:** Mencegah anomali tanggal lahir di masa depan atau usia di luar rentang perkuliahan wajar secara deklaratif di lapisan Pydantic DTO.
- **Commit terkait:** `641baca` - `feat(api): implement security hardening and SQLAlchemy 2 query refactoring [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Audit teknis mengungkap celah di mana *catch-all IntegrityError* menyamarkan kegagalan constraint lain sebagai error email duplikat, dan query masih memakai gaya hybrid SQLAlchemy 1.x.
- **Plan:** Mengonversi seluruh query menjadi `db.scalar(select())`, menginspeksi error origin database untuk diferensiasi status code, memperketat regex seluler Indonesia, serta menambahkan validasi batas usia calon mahasiswa baru.
- **Act:** Mengedit berkas schema, service, exception handler, menambahkan test cases baru, mengeksekusi suite unit test (14/14 lolos), memperbarui dokumentasi perbaikan, dan mencatat riwayat ke log transparansi AI.
- **Reflect:** Kode yang baik tidak hanya berhasil menjalankan *happy path*, tetapi harus mampu menangani *edge cases* integritas dan menyajikan *error reporting* yang akurat tanpa membocorkan kelemahan sistem internal.

---

### Prompt #5 (versi: V5 - Penanganan Kasus Tepi Regex Nomor HP & Sanitasi Input Humanis)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Menyempurnakan penanganan kasus tepi nomor telepon seluler: mendukung nomor pascabayar 9 digit lawas (`081112345`), membersihkan pemisah humanis (spasi, strip, titik, kurung) via Pydantic pre-validator, serta memperluas suite pengujian otomatis hingga 17 unit test.
- **Prompt:**
  ```text
  saya mau kamu benerin terkait hal diatas, kemudian save di AI-Log dengan commit AI-Assisted
  ```
- **Output ringkas:**
  1. Sanitasi otomatis karakter pemisah pada `phone` via `@field_validator("phone", mode="before")` di [app/schemas/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/schemas/pmb.py) untuk membersihkan tanda hubung, spasi, titik, dan tanda kurung.
  2. Pembaruan pola regex menjadi `^(\+62|62|0)8[1-9][0-9]{5,10}$` yang mendukung nomor seluler 9 hingga 14 digit/karakter.
  3. Penambahan unit test baru di [tests/test_api_pmb.py](file:///home/zainun/git/istn/sevima-mini/tests/test_api_pmb.py) untuk menguji format nomor dengan tanda hubung, nomor 9 digit lawas, dan penolakan nomor dial-up `0809` (17 unit test lolos 100%).
  4. Pembaruan dokumentasi perbaikan di [perbaikan/minggu-03/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-03/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Resilient Input Handling:** Pengguna yang mengetik nomor dengan format humanis (`0812-3456-7890` atau `+62 812 3456 7890`) tetap dilayani secara mulus karena sistem membersihkan tanda baca sebelum validasi regex dan penyimpanan ke basis data.
  2. **Inclusive Validation:** Kuantifier `{5,10}` mencegah terjadinya penolakan keliru (*false negative*) bagi pemegang nomor seluler lawas 9 digit tanpa membuka celah bagi nomor PSTN/bebas pulsa.
- **Commit terkait:** `3cba6cf` - `feat(schemas): handle phone edge cases with pre-sanitizer and regex range update [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Analisis kasus tepi regex mengungkap bahwa pola ketat tanpa sanitasi memicu *false negative* pada nomor dengan spasi/strip dan nomor pascabayar 9 digit yang sah di dunia nyata.
- **Plan:** Menambahkan pre-validator pembersih karakter sebelum validasi regex berjalan di Pydantic, melonggarkan batas minimum digit dari 6 ke 5 digit, serta memperbarui unit test.
- **Act:** Mengimplementasikan regex `^(\+62|62|0)8[1-9][0-9]{5,10}$` dan validator `sanitize_phone_number` di `app/schemas/pmb.py`, menambahkan 3 kasus uji baru di `tests/test_api_pmb.py`, memperbarui pesan error di `app/main.py`, dan mengeksekusi 17 unit test.
- **Reflect:** Validasi data yang ramah pengguna (*user-friendly validation*) harus bersifat *forgiving on input, strict on storage*—menerima variasi penulisan yang wajar dari manusia, membersihkannya secara otomatis, dan memastikan format yang disimpan ke basis data selalu bersih dan terstandarisasi.

---

### Prompt #6 (versi: V6 - Keputusan Arsitektur Opsi A: Override RequestValidationError ke 400 & Sinkronisasi Swagger UI)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengadopsi Opsi A untuk penanganan validasi Pydantic (mengubah HTTP 422 bawaan menjadi HTTP 400 Bad Request) sesuai dokumen spesifikasi tugas, serta menyelaraskan dokumentasi OpenAPI/Swagger UI dengan mengeliminasi skema status 422.
- **Prompt:**
  ```text
  Di FastAPI, kegagalan validasi Pydantic secara default menghasilkan 422.
  Tes di dokumen tugas saya mengharapkan 400 untuk nomor HP salah.
  Berikan dua opsi: (A) exception handler RequestValidationError yang
  mengubah menjadi 400, (B) tetap 422 dan menyesuaikan tes. Untuk tiap
  opsi: kode lengkap, kelebihan, kekurangan, dan dampak pada Swagger.
  Jangan memilihkan; saya yang memutuskan dan menulis di ADR.
  ```
  *(Dilanjutkan dengan persetujuan pengguna untuk mengadopsi Opsi A secara permanen)*.
- **Output ringkas:**
  1. Exception handler `@app.exception_handler(RequestValidationError)` pada [app/main.py](file:///home/zainun/git/istn/sevima-mini/app/main.py) mengembalikan HTTP 400 Bad Request dengan pesan humanis tanpa *stack trace*.
  2. Modifikasi generator skema `custom_openapi` di [app/main.py](file:///home/zainun/git/istn/sevima-mini/app/main.py) yang membersihkan status 422 bawaan FastAPI agar Swagger UI `/docs` konsisten 100% dengan respons runtime (hanya menampilkan status `201`, `400`, dan `409`).
  3. Deklarasi kontrak respons eksplisit `400` dan `409` pada decorator endpoint [app/routers/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/routers/pmb.py).
  4. Pencatatan pembaruan pada [perbaikan/minggu-03/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-03/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Kepatuhan Kontrak Dokumen Tugas:** Opsi A dipilih agar sistem mematuhi ekspektasi penilaian tugas akademik yang mensyaratkan kode respons `HTTP 400` untuk input format nomor HP atau data registrasi yang salah.
  2. **Eliminasi Inkonsistensi Swagger:** Secara bawaan di FastAPI, pengubahan status melalui exception handler tidak otomatis mengubah skema OpenAPI. Dengan mengimplementasikan `custom_openapi()`, tampilan Swagger UI disinkronkan secara total sehingga tidak menampilkan status 422 yang sudah tidak lagi dipakai.
- **Commit terkait:** `11ab6a9` - `feat(api): adopt Option A overriding RequestValidationError to 400 with Swagger sync [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Terdapat diskrepansi antara konvensi modern FastAPI (HTTP 422) dengan naskah spesifikasi tugas yang mengasumsikan HTTP 400 untuk format input tidak valid. Selain itu, mengubah exception handler di FastAPI tanpa memodifikasi skema OpenAPI meninggalkan dokumentasi Swagger yang tidak sinkron.
- **Plan:** Mengimplementasikan Opsi A secara paripurna: memasang *exception interceptor* untuk runtime HTTP 400, sekaligus mengintersep generator OpenAPI agar skema dokumentasi Swagger `/docs` mencerminkan kontrak status respons yang sesungguhnya.
- **Act:** Mengonfigurasi `validation_exception_handler` dan `custom_openapi` di `app/main.py`, menambahkan metadata `responses` di `app/routers/pmb.py`, memverifikasi 17 unit test lolos 100%, serta mendokumentasikan keputusan arsitektur.
- **Reflect:** Keputusan arsitektur (ADR) yang matang harus memperhitungkan keselarasan antara *runtime behavior* dengan *documentation contracts*. Menyelaraskan skema OpenAPI saat melakukan override exception handler framework mencegah kebingungan tim frontend dan penguji API.

---

### Prompt #7 (versi: V7 - Penerbitan Dokumen Resmi ADR-003 Format PDF)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Menyusun dokumen Architecture Decision Record (ADR-003) dalam format PDF resmi untuk iterasi Minggu ke-3 yang mendokumentasikan keputusan standardisasi validasi klien (HTTP 400 vs 422), sinkronisasi Swagger UI, strategi validasi pertahanan berlapis (*Defense-in-Depth*), penegakan kunci asing SQLite, urutan aman rollback Alembic, dan privasi data calon mahasiswa (*Privacy by Design*).
- **Prompt:**
  ```text
  oke buatkan ADR dengan format PDF untuk minggu ke 3
  ```
- **Output ringkas:**
  1. Dokumen keputusan arsitektur resmi [documents/ADR-003.pdf](file:///home/zainun/git/istn/sevima-mini/documents/ADR-003.pdf) setebal 5 halaman berstandar A4 yang dihasilkan secara otomatis menggunakan engine LibreOffice headless.
  2. Struktur ADR mencakup 7 bagian komprehensif: Konteks (7 isu kritis), Alternatif & Trade-off (Opsi A terpilih vs Opsi B ditolak), Keputusan (5 pilar teknis termasuk matriks pertahanan berlapis), Konsekuensi (positif & trade-offs), Pola Desain yang Diterapkan, Catatan Peran AI & Verifikasi Kritis, serta Referensi Terkait.
  3. Pembaruan tautan dan katalog dokumentasi di [README.md](file:///home/zainun/git/istn/sevima-mini/README.md), [perbaikan/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/README.md), dan [perbaikan/minggu-03/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-03/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Dokumentasi Formal Berkelanjutan:** ADR-003 melengkapi rangkaian keputusan arsitektur sebelumnya (ADR-001 pemecahan relasi M:N Enrollment dan ADR-002 dekomposisi 7 service domain).
  2. **Justifikasi Tertulis Deviasi Framework:** Mendokumentasikan secara formal alasan pemilihan Opsi A (override 400 & penghapusan 422 pada OpenAPI) agar arsitektur tetap transparan, dapat dipelihara (*maintainable*), dan dapat diaudit oleh pihak penguji.
- **Commit terkait:** `98c2ec5` - `docs(adr): create ADR-003 PDF document for Week 3 architectural decisions [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Pengambilan keputusan teknis seperti pengubahan exception handler, konfigurasi koneksi driver basis data, dan urutan DDL migrasi memerlukan justifikasi tertulis yang kokoh agar tidak dianggap sebagai anomali kode biasa.
- **Plan:** Menyusun dokumen ADR-003 berformat PDF dengan standar tata letak profesional A4 yang memuat konteks teknis, perbandingan trade-off alternatif, keputusan implementasi berlapis, konsekuensi sistemik, pola arsitektur, dan transparansi peran AI.
- **Act:** Menulis struktur dokumen ADR lengkap, merender ke PDF menggunakan LibreOffice headless, memverifikasi keterbacaan tipografi dan pemisahan halaman (5 halaman rapi tanpa teks terputus), memperbarui daftar ADR di README, dan mencatat log penggunaan AI.
- **Reflect:** Dokumentasi arsitektur berbentuk ADR PDF yang rapi menjadi artefak audit yang sangat bernilai tinggi dalam rekayasa perangkat lunak skala enterprise, menjamin setiap keputusan teknis memiliki rekam jejak rasional yang teruji.

---

## AI Usage Log: Minggu 4

### Prompt #1 (versi: V1 - Implementasi Generator NIM Multi-Worker, Model NimCounter, Migrasi Alembic, & Penanganan Konkurensi)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengimplementasikan fungsi `generate_nim` multi-worker dengan database row lock (`SELECT ... FOR UPDATE`), model `NimCounter` berbasis SQLAlchemy 2.0, skrip migrasi terkelola Alembic, mitigasi race condition inisialisasi awal via savepoint, penanganan `IntegrityError` dengan rollback & retry hingga 3 kali, serta integrasi endpoint persetujuan pendaftar PMB.
- **Prompt:**
  ```text
  Anda adalah backend engineer Python senior.

  Konteks: modul PMB "SEVIMA Mini". Stack: FastAPI, SQLAlchemy 2 (Mapped,
  mapped_column, select() gaya 2.0), database MySQL (InnoDB) di produksi dan
  SQLite di tes. Aplikasi berjalan dengan BANYAK WORKER (bukan satu proses),
  jadi JANGAN pakai threading.Lock di Python.

  Buat fungsi generate_nim(db, tahun, kode_prodi) -> str:
  - Format: 4 digit tahun + 3 digit kode prodi + 4 digit nomor urut
    (zero padding), tanpa strip. Contoh: 2025001001.
  - Nomor urut dihitung ulang per kombinasi (tahun, kode_prodi), mulai dari 1.
  - Gunakan tabel nim_counter (PK gabungan tahun + kode_prodi, kolom last_number)
    dengan SELECT ... FOR UPDATE (row lock) di database.
  - Fungsi TIDAK melakukan commit sendiri (cukup flush); transaksi milik endpoint.
  - Batas nomor urut 9999; lewat batas -> raise error.
  - Tambahkan unique constraint pada kolom nim, dan jelaskan cara menangani
    IntegrityError dengan rollback dan retry maksimal 3 kali.
  - Jelaskan: apa yang terjadi jika dua request datang bersamaan? Kapan kunci
    dilepas?

  Format output: kode fungsi + model NimCounter + migrasi Alembic untuk
  tabel nim_counter, lalu penjelasan singkat.
  ```
- **Output ringkas:**
  1. Model deklaratif ORM `NimCounter` di [app/models/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/models/pmb.py) dengan *Composite Primary Key* `(tahun, kode_prodi)` dan kolom `last_number` (Integer, default 0).
  2. Skrip migrasi terkelola di [app/alembic/versions/20261114_0002_create_nim_counter.py](file:///home/zainun/git/istn/sevima-mini/app/alembic/versions/20261114_0002_create_nim_counter.py) dengan fungsi DDL `upgrade()` dan `downgrade()`.
  3. Implementasi fungsi `generate_nim` pada [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py) yang menggunakan kueri modern `select(NimCounter).where(...).with_for_update()` (row-level X-lock di InnoDB), penanganan inisialisasi awal konkuren via `with db.begin_nested():` (SAVEPOINT), validasi kuota 9999 (`NimLimitExceededError`), dan eksekusi `db.flush()` tanpa commit internal.
  4. Implementasi fungsi `approve_calon_mahasiswa` dan rute endpoint `POST /api/pmb/calon-mahasiswa/{calon_id}/approve` di [app/routers/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/routers/pmb.py) dengan pola penanganan `IntegrityError` / `OperationalError` melalui `db.rollback()` dan percobaan ulang (*retry*) maksimal 3 kali.
  5. Suite pengujian unit otomatis di [tests/test_nim_counter.py](file:///home/zainun/git/istn/sevima-mini/tests/test_nim_counter.py) mencakup 9 skenario uji (format 11 digit zero-padded, isolasi counter per tahun/prodi, batas 9999, non-commit flush, idempotensi approval, retry IntegrityError, dan endpoint TestClient).
  6. Dokumentasi komprehensif analisis konkurensi, siklus kunci InnoDB, dan spesifikasi arsitektur di [perbaikan/minggu-04/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-04/README.md) dan sinkronisasi [perbaikan/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/README.md) serta [README.md](file:///home/zainun/git/istn/sevima-mini/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Delegasi Serialisasi ke DBMS (Eliminasi `threading.Lock`):** Pada arsitektur multi-worker di mana tiap worker berjalan sebagai proses OS terpisah, penjaminan urutan dan keunikan harus dilakukan di level DBMS melalui row-level lock (`SELECT ... FOR UPDATE`), bukan in-memory lock aplikasi.
  2. **Boundary Transaksi Bersih (No Internal Commit):** `generate_nim` mematuhi prinsip transaksi atomik dengan hanya memanggil `db.flush()`. Endpoint pemanggil memiliki kendali penuh untuk melakukan commit atau rollback jika terjadi kegagalan pada langkah bisnis selanjutnya.
  3. **Mitigasi Race Condition Inisialisasi Counter:** Penggunaan nested transaction / savepoint saat baris counter pertama kali dimasukkan mencegah timbulnya deadlock antar-worker akibat gap-locking di MySQL InnoDB.
  4. **Resilient Retry Loop:** Mengamankan transaksi persetujuan pendaftar dengan loop retry maksimal 3 kali dan `db.rollback()` segera untuk membebaskan lock dan membersihkan state session.
- **Commit terkait:** `3d30516` - `feat(pmb): implement multi-worker NIM generator with row lock, NimCounter model, and retry mechanism [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Pada aplikasi multi-worker, penomoran berurutan rawan memicu duplikasi akibat race condition jika mengandalkan in-memory lock. Selain itu, fungsi penomoran yang melakukan commit mandiri merusak prinsip atomisitas transaksi endpoint.
- **Plan:** Merancang tabel `nim_counter` dengan composite primary key `(tahun, kode_prodi)`, memanfaatkan `SELECT ... FOR UPDATE` untuk serialisasi row-level di InnoDB (dan kompatibel aman dengan SQLite pengujian), menerapkan flush-only dalam fungsi generator, serta membungkus alur approval dengan mekanisme retry 3 kali.
- **Act:** Mengimplementasikan model deklaratif ORM `NimCounter`, membuat migrasi Alembic `20261114_0002`, menulis fungsi `generate_nim` dan `approve_calon_mahasiswa`, mengekspos endpoint FastAPI, menambahkan 9 unit test komprehensif (seluruh 26 unit test lolos 100%), serta mendokumentasikan analisis konkurensi di folder perbaikan Minggu 4.
- **Reflect:** Menyerahkan tanggung jawab penguncian konkurensi ke database engine dan menjaga boundary transaksi tetap di tangan endpoint menghasilkan sistem backend yang *robust*, terhindar dari nomor urut bolong/duplikat, serta siap dijalankan pada skala produksi multi-worker.

---

### Prompt #2 (versi: V2 - State Machine Transisi PMB: PUT Approve & Reject, Idempotensi, & Thin Router)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengimplementasikan mesin transisi status pendaftaran (*State Machine*) untuk calon mahasiswa melalui endpoint `PUT /api/pmb/approve/{id}` dan `PUT /api/pmb/reject/{id}`, menjamin idempotensi operasi, mengunci baris pendaftar via `with_for_update()`, memvalidasi format kode program studi wajib 3 digit angka, melakukan *single-commit transaction*, mengisolasi aturan bisnis pada `PMBService`, serta menyaring data pribadi pada skema output DTO.
- **Prompt:**
  ```text
  Konteks: berikut model, skema, dan generate_nim saya:

  Buat endpoint PUT /api/pmb/approve/{id} dan PUT /api/pmb/reject/{id}:
  - State machine: pending -> approved/rejected; approved dan rejected final.
  - Approve: ambil pendaftar dengan with_for_update; 404 jika tidak ada;
    jika sudah approved kembalikan 200 + NIM lama TANPA memanggil generator
    (idempotent); jika rejected -> 409; jika kode prodi bukan 3 digit atau
    prodi tidak ditemukan -> 400; catat approved_at (UTC); panggil generate_nim;
    commit SEKALI di akhir (satu transaksi).
  - Reject: hanya dari pending; approved -> 409; rejected -> 200 (idempotent).
  - Aturan transisi diletakkan di PMBService, router tetap tipis.
  - Respons memakai skema Pydantic khusus output (jangan bocorkan data pribadi).
  ```
- **Output ringkas:**
  1. Lapisan domain service `PMBService` pada [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py) yang mengimplementasikan method `approve()` dan `reject()` dengan penegakan state machine, kueri `select(CalonMahasiswa).with_for_update()`, verifikasi eksistensi dan validasi 3 digit angka kode prodi (HTTP 400), pencatatan timestamp `approved_at` berbasis UTC, pencegahan pemanggilan generator NIM ganda pada kondisi idempotent, dan *single commit* di akhir alur.
  2. Implementasi router tipis (*thin controller*) di [app/routers/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/routers/pmb.py) untuk rute `PUT /api/pmb/approve/{id}` dan `PUT /api/pmb/reject/{id}` dengan dependency injection `get_db` dan penanganan kode status 200, 400, 404, dan 409.
  3. Pemeliharaan skema Pydantic output `PendaftarOut` pada [app/schemas/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/schemas/pmb.py) yang secara ketat menyaring data privat (`alamat` dan `tanggal_lahir`).
  4. Suite pengujian otomatis baru di [tests/test_state_machine.py](file:///home/zainun/git/istn/sevima-mini/tests/test_state_machine.py) dengan 9 skenario uji (transisi pending->approved, idempotensi approve tanpa generator, penolakan approve dari rejected -> 409, penolakan kode prodi non-3 digit angka -> 400, 404 not found, transisi pending->rejected, idempotensi reject, penolakan reject dari approved -> 409, dan pengujian penyaringan data pribadi). Seluruh **35 unit test lolos 100%**.
  5. Pembaruan dokumentasi perbaikan di [perbaikan/minggu-04/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-04/README.md) dan [README.md](file:///home/zainun/git/istn/sevima-mini/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Strict State Machine (Terminal States):** Status `approved` dan `rejected` bersifat terminal. Upaya merusak state (misal menolak mahasiswa yang sudah ber-NIM atau menyetujui mahasiswa yang sudah ditolak) digagalkan di lapisan service dengan HTTP 409 Conflict.
  2. **True Idempotency:** Memanggil approve berulang kali pada calon yang sudah approved tidak akan mengonsumsi nomor urut NIM baru dari database counter (`last_number` tidak bertambah), melainkan langsung mengembalikan data dan NIM eksisting dengan HTTP 200 OK.
  3. **Integritas Format Kode Prodi:** Penegakan bahwa kode prodi wajib terdiri dari 3 digit angka (`isdigit()` dan `len == 3`) mencegah terbitnya NIM berformat salah atau tercampur huruf saat registrasi disetujui.
  4. **Pemisahan Peran Arsitektural (Separation of Concerns):** Seluruh aturan transisi dan transaksi diisolasi di dalam `PMBService`, menjaga router tetap deklaratif dan ramping.
- **Commit terkait:** `45e90b4` - `feat(pmb): implement state machine PUT approve and reject endpoints with idempotency and thin router [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Siklus hidup pendaftaran rentan terhadap inkonsistensi data jika transisi status tidak memiliki aturan terminal yang tegas (misal terjadi pergantian bolak-balik antara approved dan rejected) atau jika operasi approval berulang menyebabkan pemborosan nomor urut NIM akibat generator yang terus dipanggil tanpa proteksi idempotensi.
- **Plan:** Membangun *State Machine* terpusat pada `PMBService` dengan exclusive lock `with_for_update()`, mendefinisikan rute idempotent untuk `PUT /approve/{id}` dan `PUT /reject/{id}`, memvalidasi eksistensi dan format 3 digit kode prodi, memastikan single transaction commit, dan memverifikasi proteksi privasi pada DTO output.
- **Act:** Mengimplementasikan method `PMBService.approve` dan `PMBService.reject`, menambahkan handler route pada `app/routers/pmb.py`, menyusun 9 unit test baru di `tests/test_state_machine.py`, mengeksekusi suite unit test (35/35 lolos), serta memperbarui dokumen perbaikan dan log AI.
- **Reflect:** Mengombinasikan state machine berbasis transisi ketat, row locking, dan idempotensi menghasilkan API yang aman terhadap *concurrency bugs*, stabil saat terjadi *network retries* dari klien, serta mematuhi prinsip kebersihan arsitektur rekayasa perangkat lunak modern.

---

### Prompt #3 (versi: V3 - Penyelarasan Validasi Kode Prodi 3 Karakter Alfanumerik pada Approval PMB)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Mengatasi kendala penolakan validasi HTTP 400 saat menyetujui calon mahasiswa dengan kode prodi 'TIF' (Teknik Informatika). Menyelaraskan aturan validasi agar menerima kode prodi 3 karakter alfanumerik (`isalnum()` dan `len == 3`, seperti 'TIF', 'SIF', '001') sesuai model basis data `ProgramStudi`, sembari tetap menolak kode yang panjangnya bukan 3 karakter.
- **Prompt:**
  ```text
  terdapat error pada approve 
  {
    "detail": "Kode program studi 'TIF' tidak valid. Kode prodi harus terdiri dari 3 digit angka."
  }
  padahal saya mengguanakan data dibawah ini dan ketika register itu berhasil
  {
    "nama_lengkap": "Test tujuh",
    "email": "test.7@example.com",
    "phone": "081234567890",
    "tanggal_lahir": "2005-08-17",
    "alamat": "Jl. Lenteng Agung No. 10, Jakarta Selatan",
    "program_studi_id": 1,
    "jalur_masuk_id": 1
  }
  ```
- **Output ringkas:**
  1. Pembaruan logika validasi pada `PMBService.approve` di [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py): Mengganti pengecekan `isdigit()` menjadi `isalnum()` dan `len == 3`, sehingga kode prodi alfabetik 3 karakter seperti `'TIF'` (Teknik Informatika) diterima secara sah dan menghasilkan NIM (misal `2026TIF0001`).
  2. Penyesuaian skenario pengujian di [tests/test_state_machine.py](file:///home/zainun/git/istn/sevima-mini/tests/test_state_machine.py) untuk memastikan prodi `'TIF'` berhasil disetujui (HTTP 200 OK), sementara kode prodi non-3 karakter (misal `'12'` atau `'1234'`) tetap ditolak dengan HTTP 400 Bad Request.
  3. Pembaruan data dan eksekusi approval langsung pada ID 7 di basis data lokal `sevima_mini.db` (NIM `2026TIF0003` terbit dengan status `approved`).
  4. Pembaruan dokumentasi perbaikan di [perbaikan/minggu-04/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-04/README.md).
- **Keputusan Arsitektur Utama:**
  - **Keselarasan Domain Data (Domain Alignment):** Menghilangkan asumsi sempit bahwa "3 digit" harus selalu berupa angka desimal (`0-9`). Pada sistem informasi akademik Indonesia dan skema `ProgramStudi` proyek, kode program studi dirancang sebagai string 3 karakter alfanumerik (misal `'TIF'`, `'SIF'`, `'ARS'`). Mengizinkan `isalnum()` menjaga kompatibilitas total antara alur pendaftaran dan alur penerbitan NIM.
- **Commit terkait:** `871cc7a` - `fix(pmb): support 3-character alphanumeric prodi codes in PMB approval [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Terdapat diskrepansi di mana pendaftaran calon mahasiswa dengan `program_studi_id: 1` (`'TIF'`) berhasil disimpan pada `POST /register`, namun gagal pada `PUT /approve` karena validasi service secara kaku memeriksa `isdigit()`.
- **Plan:** Mengubah validasi pada `PMBService.approve` dari `isdigit()` menjadi `len(kode_clean) == 3 and kode_clean.isalnum()`, memperbarui pengujian otomatis, dan memvalidasi langsung pada data pengujian pengguna.
- **Act:** Mengedit `app/services/pmb.py` dan `tests/test_state_machine.py`, memverifikasi seluruh 35 unit test lolos 100%, mengeksekusi approve pada pendaftar ID 7, dan memperbarui dokumentasi log AI.
- **Reflect:** Konsistensi antarmuka (*interface consistency*) antar-tahapan proses bisnis sangat krusial. Validasi pada tahap lanjutan (seperti approval) tidak boleh menolak data yang telah dinyatakan valid dan lolos pada tahap penerimaan awal (*registration*).

---

### Prompt #4 (versi: V4 - Implementasi Endpoint GET Status Pendaftar & Agregasi Statistik PMB Database-Level)
- **Tanggal / alat AI:** 14 November 2026 / Gemini (Gemini 3.8 Flash)
- **Tujuan:** Membangun endpoint `GET /api/pmb/status/{id}` dengan penyaringan data pribadi yang ketat (`PendaftarStatusOut`) dan `GET /api/pmb/stats` yang menghitung agregasi pendaftar per status, per program studi, dan per jalur masuk langsung di level basis data menggunakan SQLAlchemy 2.0 (`select`, `func.count`, `outerjoin`), memastikan program studi dan jalur masuk tanpa pendaftar tetap tampil dengan angka 0.
- **Prompt:**
  ```text
  Buat endpoint:
  1. GET /api/pmb/status/{id}: 404 jika tidak ada; respons Pydantic khusus
     output tanpa data pribadi yang tidak perlu.
  2. GET /api/pmb/stats: jumlah pendaftar per status, per program studi,
     dan per jalur masuk. Hitung di database dengan GROUP BY (jangan ambil
     semua baris lalu hitung di Python). Gunakan outer join agar program
     studi dan jalur masuk tanpa pendaftar tetap tampil dengan angka 0.
  Gunakan SQLAlchemy 2.0 (select, func.count, outerjoin).
  ```
- **Output ringkas:**
  1. Skema DTO baru pada [app/schemas/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/schemas/pmb.py): `PendaftarStatusOut` (menghilangkan `email`, `phone`, `alamat`, dan `tanggal_lahir`) serta `PMBStatsResponse`, `ProdiStats`, dan `JalurStats`.
  2. Lapisan service pada [app/services/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/services/pmb.py):
     - `PMBService.get_status()`: kueri seleksi berdasarkan ID dengan HTTP 404 jika tidak ditemukan.
     - `PMBService.get_stats()`: eksekusi agregasi basis data dengan kueri SQLAlchemy 2.0 `select().group_by()` untuk status, serta `select(...).outerjoin(CalonMahasiswa, ...).group_by()` pada `ProgramStudi` dan `JalurMasuk` menggunakan `func.count(CalonMahasiswa.id)` untuk menjamin angka 0 pada relasi kosong.
  3. Rute controller pada [app/routers/pmb.py](file:///home/zainun/git/istn/sevima-mini/app/routers/pmb.py) untuk `GET /api/pmb/status/{id}` dan `GET /api/pmb/stats`.
  4. Suite pengujian otomatis baru di [tests/test_status_and_stats.py](file:///home/zainun/git/istn/sevima-mini/tests/test_status_and_stats.py) dengan 3 skenario uji komprehensif. Seluruh **38 unit test proyek lolos 100%**.
  5. Pembaruan dokumentasi di [perbaikan/minggu-04/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-04/README.md) dan [README.md](file:///home/zainun/git/istn/sevima-mini/README.md).
- **Keputusan Arsitektur Utama:**
  1. **Agregasi Murni Mesin Basis Data (Query Efficiency):** Menghindari pembebanan memori aplikasi dengan tidak menarik ribuan baris rekaman ke Python. Penghitungan `func.count()` langsung diolah oleh mesin SQL secara terindeks.
  2. **Penghitungan Akurat Outer Join:** Menggunakan `func.count(CalonMahasiswa.id)` dan BUKAN `func.count(*)` saat melakukan `outerjoin`. `func.count(*)` akan menghitung baris hasil join bernilai NULL sebagai 1, sedangkan `func.count(column)` secara presisi mengembalikan 0 untuk relasi tanpa record anak.
  3. **Privacy by Design pada Status Check:** Endpoint status publik tidak mengekspos nomor kontak atau alamat fisik pendaftar, hanya menampilkan nomor pendaftaran, nama, prodi, jalur, status kelulusan, dan NIM.
- **Commit terkait:** `[PENDING_COMMIT_HASH]` - `feat(pmb): implement status check and stats endpoints with database-level outerjoin aggregation [AI-Assisted]`

### Refleksi (Observe - Plan - Act - Reflect)
- **Observe:** Penarikan seluruh data tabel ke memori aplikasi untuk penghitungan analitik menimbulkan penurunan performa drastis (*memory bloating* dan O(N) komputasi aplikasi). Selain itu, pengecekan status publik rawan membocorkan privasi jika menggunakan DTO pendaftaran lengkap.
- **Plan:** Menyusun query agregasi murni database menggunakan `GROUP BY` dan `outerjoin` dengan `func.count(CalonMahasiswa.id)` agar entitas kosong bernilai 0, merancang DTO output protektif tanpa informasi kontak/alamat, dan mengisolasi logika pada `PMBService`.
- **Act:** Mengimplementasikan skema DTO, query agregasi di service layer, router tipis, 3 unit test baru (38/38 lolos), dan memperbarui dokumentasi teknis.
- **Reflect:** Mendelegasikan operasi analitik ke kemampuan relasional basis data (*push computing to data*) adalah praktik terbaik rekayasa perangkat lunak untuk menjaga skalabilitas aplikasi dan kestabilan penggunaan sumber daya server.




