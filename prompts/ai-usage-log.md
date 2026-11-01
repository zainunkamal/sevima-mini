# 🤖 Log Penggunaan AI (AI Usage Log)

> **Konteks:** Dokumentasi transparansi penggunaan kecerdasan buatan (*Generative AI / LLM*) dalam perancangan arsitektur, pemodelan berorientasi objek (UML), serta penyusunan *Architectural Decision Record* (ADR) pada sistem **SEVIMA-Mini**.

---

## 📊 Ringkasan Aktivitas Perancangan

| No | Minggu | Fitur / Aktivitas | LLM / Tool | Commit Awal | Status Hasil |
| :-: | :-: | :--- | :--- | :--- | :--- |
| **1** | Minggu 1 | Perancangan UML Class Diagram Inti | Gemini 3.8 Flash | [`cd67597`](https://github.com/zainunkamal/sevima-mini/commit/cd6759791606f5facf2d09f73d7d7d092908ba16) | Selesai (Diterima) |
| **2** | Minggu 1 | Penambahan Class Inti `Payment` & Prasyarat KRS | Gemini 3.8 Flash | [`5007785`](https://github.com/zainunkamal/sevima-mini/commit/50077852cbcc06d1ad52a8f36734f10c081938dd) | Selesai (Diterima) |
| **3** | Minggu 1 | Perancangan UML Use Case Diagram | Gemini 3.8 Flash | [`b9e493f`](https://github.com/zainunkamal/sevima-mini/commit/b9e493f) | Selesai (Diterima) |
| **4** | Minggu 1 | Perancangan UML Sequence Diagram (PMB & KRS) | Gemini 3.8 Flash | [`eff27dc`](https://github.com/zainunkamal/sevima-mini/commit/eff27dc) | Selesai (Diterima) |
| **5** | Minggu 1 | Dokumentasi ADR (ADR-002, ADR-003, PDF & Restrukturisasi) | Gemini 3.8 Flash | [`35d8ca6`](https://github.com/zainunkamal/sevima-mini/commit/35d8ca6) | Selesai (Diterima) |
| **6** | Minggu 2 | Audit & Refactoring Class Diagram (OPAR) | Gemini 3.8 Flash | - | Selesai (Diterima) |
| **7** | Minggu 2 | Refactoring Use Case Diagram & Standardisasi Dosen PA (OPAR) | Gemini 3.8 Flash | - | Selesai (Diterima) |

---

## 📝 Rincian Log Prompt & Interaksi

### 🔹 Log 01: Membuat Class Diagram Inti
* **Minggu:** `1`
* **Fitur:** Membuat ClassDiagram
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`cd67597`](https://github.com/zainunkamal/sevima-mini/commit/cd6759791606f5facf2d09f73d7d7d092908ba16)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Anda adalah arsitek sistem. Buat class diagram UML untuk sistem akademik
  dengan komponen berikut:
  - User sebagai base class (Mahasiswa, Dosen, Admin, CalonMahasiswa)
  - Course dengan atribut kode, nama, SKS, prasyarat
  - Enrollment yang hubungkan Mahasiswa dan Course
  - Schedule dengan hari, jam, ruangan
  - Grade untuk nilai mahasiswa

  Terapkan prinsip SOLID. Gunakan composition untuk relasi kuat dan
  aggregation untuk relasi lemah. Output dalam format Mermaid."
  ```
* **Hasil / Luaran:**
  * Diagram Class Mermaid awal: `academic_class_diagram.mmd` (sekarang [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd)).
  * Dokumen ADR: [`docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md`](../docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md).

---

### 🔹 Log 02: Menambahkan Class Inti Payment
* **Minggu:** `1`
* **Fitur:** Menambahkan class inti payment
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`5007785`](https://github.com/zainunkamal/sevima-mini/commit/50077852cbcc06d1ad52a8f36734f10c081938dd) *(basis dari `cd67597`)*
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Saya mau menambahkan class inti payment
  Payment itu untuk sebagai syarat agar bisa mengisi KRS"
  ```
* **Hasil / Luaran:**
  * Penambahan class `Payment` dengan method `isLunas()` dan `konfirmasiPembayaran()`.
  * Integrasi validasi prasyarat pembayaran pada `Mahasiswa`, `Enrollment`, dan `Admin`.
  * Relasi agregasi `Mahasiswa o-- Payment` dan dependensi `Enrollment ..> Payment`.
  * Pembaruan dokumentasi ADR-001 dan diagram komparasi (Baseline v1.0 vs Revisi v1.1).

---

### 🔹 Log 03: Membuat Use Case Diagram
* **Minggu:** `1`
* **Fitur:** Membuat UseCase Diagram
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`b9e493f`](https://github.com/zainunkamal/sevima-mini/commit/b9e493f) *(docs: [`f47fb84`](https://github.com/zainunkamal/sevima-mini/commit/f47fb84))*
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Anda adalah arsitek sistem. Buatkan usecase diagram dengan terdiri dari 
  - aktor: mahasiswa, dosen, Admin, Sistem PMB
  - usecase: Daftar kuliah, Isi KRS, Input nilai, Generate transkrip, dll
  - Include/extend relationships"
  ```
* **Hasil / Luaran:**
  * Diagram Use Case Mermaid: [`diagrams/usecase-diagram.mmd`](../diagrams/usecase-diagram.mmd) & [`docs/usecase/usecase_diagram.svg`](../docs/usecase/usecase_diagram.svg).
  * Dokumen Spesifikasi Use Case: [`docs/usecase/USECASE-001-academic-system.md`](../docs/usecase/USECASE-001-academic-system.md).
  * Dokumen ADR Use Case: [`docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md`](../docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md).

---

### 🔹 Log 04: Membuat Sequence Diagram (PMB & Validasi KRS)
* **Minggu:** `1`
* **Fitur:** Membuat Sequence Diagram
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`eff27dc`](https://github.com/zainunkamal/sevima-mini/commit/eff27dc) *(docs: [`ae627ec`](https://github.com/zainunkamal/sevima-mini/commit/ae627ec))*
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Anda adalah arsitek sistem. Saya mau membuat sequence diagram
  - Proses pendaftaran mahasiswa baru (PMB)
  - Validasi KRS dengan pengecekan prasyarat"
  ```
* **Hasil / Luaran:**
  * Diagram Sequence PMB: [`diagrams/sequence-pmb.mmd`](../diagrams/sequence-pmb.mmd) & [`docs/sequence/pmb_sequence_diagram.svg`](../docs/sequence/pmb_sequence_diagram.svg).
  * Diagram Sequence Validasi KRS: [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd) & [`docs/sequence/krs_sequence_diagram.svg`](../docs/sequence/krs_sequence_diagram.svg).
  * Dokumen Spesifikasi Sequence: [`docs/sequence/SEQUENCE-001-pmb-and-krs.md`](../docs/sequence/SEQUENCE-001-pmb-and-krs.md).
  * Dokumen ADR Sequence: [`docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md`](../docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md).

---

### 🔹 Log 05: Dokumentasi ADR Format PDF & Restrukturisasi Diagram
* **Minggu:** `1`
* **Fitur:** Membuat Dokumen ADR format PDF & Restrukturisasi Berkas
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`35d8ca6`](https://github.com/zainunkamal/sevima-mini/commit/35d8ca6)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "untuk sequence dan usecase, buatkan document ADR dengan format PDF"
  "saya mau menambahkan ada perubahan untuk clas diagram di ADR dengan screenshoot diatas"
  "di README.md jangan sertakan file:///home/zainun/Git/istn/"
  ```
* **Hasil / Luaran:**
  * ADR PDF A4 profesional dengan diagram vektor SVG:
    * [`docs/adr/ADR-001-academic-system-class-structure.pdf`](../docs/adr/ADR-001-academic-system-class-structure.pdf)
    * [`docs/adr/ADR-002-academic-usecase-architecture.pdf`](../docs/adr/ADR-002-academic-usecase-architecture.pdf)
    * [`docs/adr/ADR-003-academic-sequence-flows.pdf`](../docs/adr/ADR-003-academic-sequence-flows.pdf)
  * Restrukturisasi direktori `diagrams/`, `docs/adr/ADR-Markdown/`, dan pembersihan path relatif [README.md](../README.md).

---

### 🔹 Log 06: Refactoring & Penguatan Class Diagram Berbasis OPAR (Observe, Plan, Act, Reflect)
* **Minggu:** `2`
* **Fitur:** Audit Konsistensi Antardiagram & Refactoring Class Diagram (SOLID & Strategy Pattern)
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** Revisi [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Audit diagram berikut terhadap konsistensi dan prinsip SOLID.
  Periksa:
  1. Participant/method di sequence yang tidak ada di class diagram
  2. Use case yang tidak punya sequence, atau sebaliknya
  3. Pelanggaran SRP (class dengan terlalu banyak tanggung jawab)
  4. Alternate flow yang hilang di tiap sequence"
  
  "Revisi class diagram berikut:
  Perubahan yang saya setujui:
  - Tambah class: KRS, KRSService, PMBService, NotificationService, ProgramStudi, NIMGenerator
  - Strategy untuk validasi KRS: ValidationRule dengan PrerequisiteRule, SksLimitRule (max 24), ScheduleConflictRule
  - Enrollment berelasi dengan Schedule dan punya semester
  - Mahasiswa punya dosenWali (Dosen); Dosen dan Mahasiswa implement observer
  - Hapus validasiSyaratPembayaran dari Enrollment, pindahkan ke ValidationRule
  Output Mermaid + daftar perubahan (Sebelum -> Sesudah).
  Catat di ai-usage-log terus tambahkan (OPAR) di ai-usage-log (observe , plan, act , reflect )"
  ```
* **Metodologi OPAR:**
  * 👁️ **Observe (Observasi):**
    * Ditemukan ketidakkonsistenan antara Sequence Diagram dan Class Diagram di mana participant service layer (`KRSService`, `PMBService`) dan boundary/storage belum dimodelkan.
    * Entitas `Enrollment` memikul beban validasi pembayaran (`validasiSyaratPembayaran`), melanggar SRP dan membuat penggandengan yang keliru dengan `Payment`.
    * Validasi pengisian KRS (prasyarat mata kuliah, batas kuota SKS, bentrok jadwal kelas) belum memiliki mekanisme extensibility yang modular.
    * Entitas `Mahasiswa` belum memiliki asosiasi dosen wali (`dosenWali`) untuk workflow persetujuan KRS, dan `Dosen` belum menjadi observer penerima notifikasi pengajuan KRS.
  * 📋 **Plan (Rencana):**
    * Memisahkan tanggung jawab orkestrasi ke dalam Service Layer: `KRSService`, `PMBService`, dan `NotificationService`.
    * Memodelkan agregat rencana studi mahasiswa dengan entitas `KRS` yang menaungi koleksi `Enrollment`.
    * Mengimplementasikan **Strategy Pattern** untuk validasi KRS melalui interface `ValidationRule` dengan 4 rule konkret: `PrerequisiteRule`, `SksLimitRule` (maksimal 24 SKS), `ScheduleConflictRule`, dan `PaymentValidationRule`.
    * Menghapus `validasiSyaratPembayaran` dari `Enrollment`, menambahkan atribut `semester`, serta menghubungkan `Enrollment` ke `Schedule`.
    * Menetapkan relasi pembimbing akademik `Mahasiswa --> Dosen` (`dosenWali`) dan menerapkan `IEnrollmentObserver` pada `Dosen` dan `Mahasiswa`.
    * Menambahkan entitas master `ProgramStudi` dan helper `NIMGenerator` yang didelegasikan oleh `UserFactory`.
  * ⚡ **Act (Tindakan / Aksi):**
    * Memperbarui [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd) dengan menambahkan 6 class baru (`KRS`, `KRSService`, `PMBService`, `NotificationService`, `ProgramStudi`, `NIMGenerator`).
    * Menambahkan interface `ValidationRule` dan concrete rules (`PrerequisiteRule`, `SksLimitRule`, `ScheduleConflictRule`, `PaymentValidationRule`).
    * Mengubah `Enrollment`: menambahkan `-int semester`, relasi ke `Schedule`, dan menghapus `validasiSyaratPembayaran()`.
    * Menghubungkan `Mahasiswa` ke `Dosen` (`dosenWali`) dan menerapkan `IEnrollmentObserver` pada `Dosen` (`onEnrollmentStatusChanged`, `onGradeUpdated`).
  * 💡 **Reflect (Refleksi):**
    * Desain class diagram kini sepenuhnya selaras (*1:1 match*) dengan sequence diagram KRS dan PMB.
    * Penerapan Strategy Pattern pada `ValidationRule` mematuhi prinsip **Open/Closed Principle (OCP)** dan **Single Responsibility Principle (SRP)**: aturan validasi baru dapat ditambahkan tanpa memodifikasi class `Enrollment` maupun `KRSService`.
    * Pemisahan Service Layer mengeliminasi anomali *God Class* pada `Mahasiswa` dan `Enrollment`, sehingga arsitektur menjadi jauh lebih modular, siap diimplementasikan ke kode produksi, dan mudah diuji (*unit testable*).
* **Hasil / Luaran:**
  * Diagram Class Mermaid yang telah direvisi: [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd).

---

### 🔹 Log 07: Penyempurnaan Use Case Diagram & Standardisasi Dosen PA Berbasis OPAR (Observe, Plan, Act, Reflect)
* **Minggu:** `2`
* **Fitur:** Perbaikan Semantik Use Case, Pemisahan Peran Aktor Dosen, Penambahan 7 Use Case Baru, dan Standardisasi Istilah Dosen PA
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** Revisi [`diagrams/usecase-diagram.mmd`](../diagrams/usecase-diagram.mmd), [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd), dan [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "bagaimana dengan permasalahan ini
  - Daftar Kuliah dikaitkan ke aktor Mahasiswa, padahal yang mendaftar adalah calon mahasiswa. Di sequence PMB aktornya “Calon Mahasiswa”, jadi tidak sinkron. Tambahkan aktor Calon Mahasiswa, atau jelaskan bahwa itu generalisasi.
  - Proses Sanggah Nilai meng-extend Input Nilai tidak masuk akal, karena sanggah dilakukan mahasiswa setelah nilai terbit. Lebih tepat extend ke Lihat KHS, dan beri asosiasi ke Mahasiswa.
  - Generate Transkrip dikaitkan ke Dosen. Biasanya aktornya Mahasiswa dan Admin.
  - Use case yang muncul di sequence tapi belum ada: Verifikasi Berkas & Seleksi, Generate NIM, Validasi Batas SKS, Cek Jadwal Bentrok (include dari Isi KRS), Login, Lihat Jadwal, dan Kirim Notifikasi.
  - Istilah tidak konsisten: use case memakai “Dosen Wali”, dokumen dosen memakai “Dosen PA”. Pilih satu. Saya mau menggunakan Dosen PA"
  
  "ya, setuju, terus jangan lupa masukin ke ai-usage-log"
  ```
* **Metodologi OPAR:**
  * 👁️ **Observe (Observasi):**
    * Pendaftaran kuliah (`UC_Daftar`) terhubung keliru ke `Mahasiswa` alih-alih `Calon Mahasiswa`, menimbulkan inkonsistensi domain dengan Sequence PMB dan Class Diagram.
    * Use case `UC_SanggahNilai` meng-extend `UC_InputNilai` yang diampu dosen, padahal secara kronologis sanggahan dipicu oleh mahasiswa setelah memeriksa Kartu Hasil Studi (`UC_LihatKHS`).
    * Use case `UC_GenTranskrip` keliru diasosiasikan dengan `Dosen`, padahal penerbitan transkrip resmi adalah otoritas institusional `Admin/BAAK` atas permohonan `Mahasiswa`.
    * Terdapat 7 use case yang telah aktif di sequence diagram atau class diagram tetapi belum terdaftar pada use case diagram: autentikasi (`UC_Login`), verifikasi seleksi PMB (`UC_VerifikasiSeleksi`), generasi NIM (`UC_GenerateNIM`), validasi kuota SKS (`UC_CekBatasSKS`), validasi bentrok jadwal (`UC_CekBentrokJadwal`), jadwal perkuliahan (`UC_LihatJadwal`), dan pengiriman notifikasi (`UC_KirimNotifikasi`).
    * Ditemukan ambiguitas terminologi pembimbing akademik: use case memakai "Dosen Wali", sedangkan dokumen resmi kampus memakai "Dosen PA" (Penasihat/Pembimbing Akademik).
  * 📋 **Plan (Rencana):**
    * Memperkenalkan aktor eksplisit `Calon Mahasiswa` (`CALON`) yang menginisiasi `UC_Daftar`.
    * Memecah aktor Dosen menjadi dua peran bisnis spesifik untuk mematuhi *Role Segregation (ISP)*: `DSN_PA` (Pembimbing Akademik) dan `DSN_Pengajar`.
    * Memperbaiki relasi sanggah nilai: `UC_SanggahNilai -. "<<extend>>" .-> UC_LihatKHS`, serta menghubungkan aktor `Mahasiswa` dan `Dosen Pengajar`.
    * Memutus relasi Dosen dari `UC_GenTranskrip` dan mengalihkannya ke `Admin` bersama `Mahasiswa`.
    * Mengintegrasikan 7 use case baru ke dalam modul yang relevan, memastikan 4 aturan validasi KRS di Use Case sinkron 1:1 dengan 4 strategi `ValidationRule` di Class Diagram.
    * Menstandarisasi istilah "Dosen PA" secara holistik pada `usecase-diagram.mmd`, `class-diagram.mmd` (atribut `dosenPA`, `getDosenPA`, `setDosenPA`), dan `sequence-krs.mmd` (`actor DosenPA`).
  * ⚡ **Act (Tindakan / Aksi):**
    * Memperbarui [`diagrams/usecase-diagram.mmd`](../diagrams/usecase-diagram.mmd) dengan seluruh restrukturisasi use case, relasi *include/extend*, dan peran aktor.
    * Mengubah istilah `dosenWali` menjadi `dosenPA` pada [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd) dan [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd).
    * Menguji kompilasi semua diagram menggunakan `mermaid-cli` (`mmdc`) untuk menjamin validitas sintaksis visual.
  * 💡 **Reflect (Refleksi):**
    * Seluruh artefak arsitektur sistem (Class Diagram, Sequence Diagram, dan Use Case Diagram) kini berada dalam keadaan **sinkron 100%** tanpa gap fungsional.
    * Model use case baru mencerminkan batasan keamanan otorisasi (*Role-Based Access Control*) yang solid, di mana hak pendaftar, mahasiswa, dosen pengajar, dosen pembimbing akademik, dan administrator terisolasi secara tegas dan kohesif.
* **Hasil / Luaran:**
  * Diagram Use Case Mermaid yang telah diperbaiki: [`diagrams/usecase-diagram.mmd`](../diagrams/usecase-diagram.mmd).
  * Diagram Class Mermaid yang telah distandarisasi: [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd).
  * Diagram Sequence KRS Mermaid yang telah distandarisasi: [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd).
