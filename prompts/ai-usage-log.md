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
| **6** | Minggu 2 | Audit & Refactoring Class Diagram (OPAR) | Gemini 3.8 Flash | [`52372f7`](https://github.com/zainunkamal/sevima-mini/commit/52372f7) | Selesai (Diterima) |
| **7** | Minggu 2 | Refactoring Use Case Diagram & Standardisasi Dosen PA (OPAR) | Gemini 3.8 Flash | [`ad28839`](https://github.com/zainunkamal/sevima-mini/commit/ad28839) | Selesai (Diterima) |
| **8** | Minggu 2 | Refactoring Sequence Diagram KRS Multi-Rule & Alt-Flows (OPAR) | Gemini 3.8 Flash | [`73781a2`](https://github.com/zainunkamal/sevima-mini/commit/73781a2) | Selesai (Diterima) |
| **9** | Minggu 2 | Refactoring Sequence Diagram PMB Multi-Alt-Flows & Pemisahan NIMGenerator (OPAR) | Gemini 3.8 Flash | [`2ec94c1`](https://github.com/zainunkamal/sevima-mini/commit/2ec94c1) | Selesai (Diterima) |
| **10** | Minggu 2 | Hardening Sequence Diagram KRS: Concurrency, ACID & Async Lifecycle (OPAR) | Gemini 3.8 Flash | [`4f04535`](https://github.com/zainunkamal/sevima-mini/commit/4f04535) | Selesai (Diterima) |
| **11** | Minggu 2 | Sinkronisasi & Pembaruan Komprehensif Dokumentasi ADR (ADR-001, ADR-002, ADR-003) | Gemini 3.8 Flash | [`459cf7e`](https://github.com/zainunkamal/sevima-mini/commit/459cf7e) | Selesai (Diterima) |

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
* **Kode AI awal:** [`52372f7`](https://github.com/zainunkamal/sevima-mini/commit/52372f7)
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
* **Kode AI awal:** [`ad28839`](https://github.com/zainunkamal/sevima-mini/commit/ad28839)
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

---

### 🔹 Log 08: Refactoring Sequence Diagram KRS Multi-Rule & Alternate Flows Berbasis OPAR (Observe, Plan, Act, Reflect)
* **Minggu:** `2`
* **Fitur:** Penyempurnaan Sequence Diagram KRS dengan Alur Multi-Rule Validation, Alternate Flows Komprehensif, dan Konsistensi Penuh Class Diagram
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`73781a2`](https://github.com/zainunkamal/sevima-mini/commit/73781a2)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "dari yang diatas saya mau menambahkan
  Alur: submit KRS -> cek pembayaran -> loop ValidationRule (prasyarat, SKS <= 24, jadwal bentrok,
  double enrollment) -> status "Pending Approval" -> notifikasi ke Dosen PA.
  Wajib alt flow: tiap rule gagal, masa KRS ditutup, kapasitas penuh, error database.
  Gunakan nama class dan method persis dari class diagram."
  ```
* **Metodologi OPAR:**
  * 👁️ **Observe (Observasi):**
    * Diagram sequence KRS sebelumnya belum memvisualisasikan seluruh alur alternatif (*alternate flows*) kritis secara granular, khususnya saat masa KRS ditutup, kapasitas kelas penuh, masing-masing rule validasi gagal, dan kegagalan transaksi basis data (*database exception*).
    * Class diagram sebelumnya baru memiliki 3 rule akademik (`PrerequisiteRule`, `SksLimitRule`, `ScheduleConflictRule`) dan 1 rule pembayaran (`PaymentValidationRule`), namun belum memiliki aturan eksplisit untuk pencegahan pendaftaran ganda (`DoubleEnrollmentRule`).
    * Alur pengiriman notifikasi persetujuan perlu menargetkan secara tepat ke `Dosen PA` melalui integrasi `Mahasiswa.getDosenPA()`, `NotificationService.kirimNotifikasi()`, dan pola Observer `IEnrollmentObserver.onEnrollmentStatusChanged()`.
  * 📋 **Plan (Rencana):**
    * Menambahkan class `DoubleEnrollmentRule` yang mengimplementasikan `ValidationRule` ke dalam [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd) dan use case `UC_CekDuplikasi` ke dalam [`diagrams/usecase-diagram.mmd`](../diagrams/usecase-diagram.mmd).
    * Menyusun ulang [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd) menjadi 8 tahapan kronologis terstruktur:
      1. Submit KRS & validasi kelayakan periode (Alt Flow: Masa KRS Ditutup).
      2. Cek pembayaran via `PaymentValidationRule.validate(krs, mahasiswa)` (Alt Flow: Tagihan SPP Belum Lunas).
      3. Cek kuota kapasitas kelas via `Schedule.getKapasitas()` (Alt Flow: Kuota Kapasitas Kelas Penuh).
      4. Loop evaluasi `ValidationRule` (Strategy Pattern) mencakup:
         - `PrerequisiteRule` (Alt Flow: Prasyarat Matakuliah Gagal).
         - `SksLimitRule` max 24 SKS (Alt Flow: Beban SKS Melebihi Batas).
         - `ScheduleConflictRule` (Alt Flow: Jadwal Kuliah Bentrok).
         - `DoubleEnrollmentRule` (Alt Flow: Matakuliah Duplikat).
      5. Penetapan status KRS dan Enrollment menjadi `"PENDING_APPROVAL"`.
      6. Persistensi ke database via `DB.simpanKRS(krs)` (Alt Flow: Terjadi Error Database).
      7. Notifikasi ke Dosen PA via `NotificationService.kirimNotifikasi(dosenPA, ...)` dan `broadcastKRSUpdate(krs, "PENDING_APPROVAL")`.
      8. Review dan evaluasi persetujuan oleh Dosen PA (`approveKRS` vs `rejectKRS`).
    * Memastikan setiap nama class, participant, dan pemanggilan method 100% identik dengan method signature pada class diagram.
  * ⚡ **Act (Tindakan / Aksi):**
    * Mengimplementasikan `DoubleEnrollmentRule` pada class diagram.
    * Menulis ulang `diagrams/sequence-krs.mmd` dengan blok `alt...else...end` dan `loop` sesuai seluruh alur utama dan alternatif yang diwajibkan.
    * Memvalidasi sintaks diagram menggunakan `@mermaid-js/mermaid-cli` dan mengekspor visualisasi SVG terbaru ke `docs/sequence/krs_sequence_diagram.svg`.
  * 💡 **Reflect (Refleksi):**
    * Sequence diagram kini mencerminkan penanganan kondisi galat secara defensif (*defensive programming* & *fail-fast architecture*), mencegah inkonsistensi status pada data akademik.
    * Penggunaan Strategy Pattern `ValidationRule` terbukti modular dan fleksibel dalam sequence flow, di mana orkestrator `KRSService` mengeksekusi polymorphic loop tanpa perlu kopling ketat ke detail implementasi aturan individual.
    * Sinkronisasi nama class, interface, method signature, dan observer event antara Class Diagram, Use Case Diagram, dan Sequence Diagram mencapai derajat kecocokan 100% (*zero discrepancy*).
* **Hasil / Luaran:**
  * Diagram Sequence KRS Mermaid yang diperbarui: [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd).
  * File visualisasi SVG: [`docs/sequence/krs_sequence_diagram.svg`](../docs/sequence/krs_sequence_diagram.svg).

---

### 🔹 Log 09: Refactoring Sequence Diagram PMB Multi-Alternate Flows & Pemisahan NIMGenerator Berbasis OPAR (Observe, Plan, Act, Reflect)
* **Minggu:** `2`
* **Fitur:** Penyempurnaan Sequence Diagram PMB dengan Validasi Form 400, Email Duplikat 409, Berkas Invalid, Calon Ditolak, Pemisahan NIMGenerator dari UserFactory (SRP), Standardisasi Status pending/approved/rejected, dan Pengiriman Tautan Aktivasi
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`2ec94c1`](https://github.com/zainunkamal/sevima-mini/commit/2ec94c1)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Audit diagram sequence-pmb berikut terhadap konsistensi dan prinsip SOLID.
  Periksa:
  1. Participant/method di sequence yang tidak ada di class diagram
  2. Use case yang tidak punya sequence, atau sebaliknya
  3. Pelanggaran SRP (class dengan terlalu banyak tanggung jawab)
  4. Alternate flow yang hilang di tiap sequence
  Format: tabel (Masalah | Diagram | Rekomendasi). Jangan ubah diagram dulu."
  
  "saya mau tambahan untuk perbaikan diatas
  Tambahkan alt/opt: validasi form gagal (400), email duplikat (409), berkas tidak valid,
  calon ditolak. Pisahkan NIMGenerator dari UserFactory. Ganti pengiriman password dengan
  tautan aktivasi. Gunakan status: pending / approved / rejected."
  ```
* **Metodologi OPAR:**
  * 👁️ **Observe (Observasi):**
    * Diagram sequence PMB sebelumnya tidak memiliki blok *alternate flows* sama sekali (100% *happy path*), mengabaikan skenario kegagalan krusial seperti validasi kelengkapan form, email terduplikasi, dokumen unggahan korup/salah format, serta penolakan calon mahasiswa oleh admin admisi.
    * Class `UserFactory` memikul tanggung jawab ganda (pelanggaran SRP): menghitung algoritma pembentukan format NIM sekaligus menginstansiasi objek `Mahasiswa`.
    * Pengiriman kredensial berupa password polos (*plain text password*) melanggar prinsip keamanan dasar; seharusnya menggunakan tautan aktivasi akun mandiri (*activation token/link*).
    * Terminologi status belum terstandarisasi seragam (`"PENDING_SELEKSI"`, `"LULUS"`).
  * 📋 **Plan (Rencana):**
    * Memisahkan class `NIMGenerator` dari `UserFactory` pada Class Diagram dan Sequence Diagram. `PMBService` memanggil `NIMGenerator.generateNIM()` lalu melewatkan hasilnya ke `UserFactory.createUser()`.
    * Menambahkan method `getAntreanSeleksi()` pada `PMBService` di Class Diagram untuk mengakomodasi akses antrean seleksi pendaftar oleh Admin Admisi.
    * Menyematkan 4 skenario *alternate flow* komprehensif:
      1. Alt Flow 1: Validasi form gagal &rarr; HTTP 400 Bad Request.
      2. Alt Flow 2: Email terduplikasi &rarr; HTTP 409 Conflict.
      3. Alt Flow 3: Berkas dokumen tidak valid (format &ne; PDF/JPG atau ukuran > 2MB).
      4. Alt Flow 4: Calon mahasiswa ditolak oleh Admin (`status="rejected"`).
    * Menstandarisasi nilai status seleksi admisi menjadi: `pending`, `approved`, `rejected`.
    * Mengganti pengiriman password dengan mekanisme generasi tautan aktivasi akun via `NotificationService.kirimNotifikasi()`.
  * ⚡ **Act (Tindakan / Aksi):**
    * Memperbarui [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd) dengan memisahkan `NIMGenerator` dari `UserFactory`, menambahkan relasi `PMBService ..> NIMGenerator`, serta menambahkan `getAntreanSeleksi()`.
    * Menulis ulang [`diagrams/sequence-pmb.mmd`](../diagrams/sequence-pmb.mmd) dengan seluruh tahapan, *alternate flows*, dan participant `NIMGenerator` serta `NotificationService`.
    * Memperbarui dokumentasi arsitektur [`docs/sequence/SEQUENCE-001-pmb-and-krs.md`](../docs/sequence/SEQUENCE-001-pmb-and-krs.md) dan meregenerasi visualisasi SVG [`docs/sequence/pmb_sequence_diagram.svg`](../docs/sequence/pmb_sequence_diagram.svg).
    * Memvalidasi sintaks diagram menggunakan `@mermaid-js/mermaid-cli` (Exit Code 0).
  * 💡 **Reflect (Refleksi):**
    * Pemisahan `NIMGenerator` mengembalikan kepatuhan penuh terhadap prinsip **Single Responsibility Principle (SRP)**: Factory murni bertugas untuk instansiasi objek, sedangkan logika algoritma penomoran institusional terisolasi di domain generator.
    * Penerapan status standar (`pending`, `approved`, `rejected`) menyederhanakan *State Machine* admisi pendaftar dan selaras dengan pola RESTful API.
    * Penggantian password polos dengan tautan aktivasi mengadopsi standar industri keamanan informasi (*Identity & Access Management - IAM*), mencegah eksfiltrasi kredensial pengguna pada log transaksi.
* **Hasil / Luaran:**
  * Diagram Class Mermaid yang diperbarui: [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd).
  * Diagram Sequence PMB Mermaid yang diperbarui: [`diagrams/sequence-pmb.mmd`](../diagrams/sequence-pmb.mmd).
  * File visualisasi SVG: [`docs/sequence/pmb_sequence_diagram.svg`](../docs/sequence/pmb_sequence_diagram.svg).

---

### 🔹 Log 10: Hardening Sequence Diagram KRS: Concurrency, ACID & Async Lifecycle Berbasis OPAR (Observe, Plan, Act, Reflect)
* **Minggu:** `2`
* **Fitur:** Mitigasi 5 Kelemahan Arsitektural Sequence KRS (Atomic Capacity Reservation, Transaction Scope & Rollback, Pemisahan Sesi Asinkron Dosen PA, Konsolidasi Event Notifikasi, dan Transaksi Kompensasi)
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`4f04535`](https://github.com/zainunkamal/sevima-mini/commit/4f04535)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Kritik diagram berikut sebagai senior architect. Sebutkan 5 kelemahan terbesar,
  urutkan dari yang paling berisiko, beri saran perbaikan"
  
  "oke kamu perbaiki dan jangan lupa masukin ke log"
  ```
* **Metodologi OPAR:**
  * 👁️ **Observe (Observasi):**
    * Ditemukan kerentanan kritis *Race Condition (TOCTOU)* pada pengecekan kuota kelas (`Schedule.getKapasitas()` pasif) yang memicu *overselling* saat beban puncak (*War KRS*).
    * Ketiadaan batasan transaksi eksplisit (*Transaction Scope*) pada proses persistensi basis data, berisiko meninggalkan *orphan records* dan inkonsistensi status rencana studi saat terjadi galat commit.
    * Terjadi *Temporal Coupling*: penggabungan siklus *synchronous request-response* pengajuan mahasiswa dengan evaluasi persetujuan Dosen PA yang pada kenyataannya berlangsung secara asinkron pada sesi waktu berbeda.
    * Terdapat *Architectural Pattern Smell* pada modul notifikasi berupa duplikasi pemanggilan direct push dan event observer ke aktor yang sama.
    * Ketiadaan mekanisme transaksi kompensasi pembatalan alokasi kuota ketika rule validasi berikutnya atau database commit mengalami kegagalan.
  * 📋 **Plan (Rencana):**
    * Menambahkan method `+reserveKapasitas() bool` dan `+releaseKapasitas() void` pada entitas `Schedule` di Class Diagram untuk mengenkapsulasi penguncian atomik dan transaksi kompensasi.
    * Mengganti pengecekan kuota pasif dengan eksekusi `reserveKapasitas()` di Tahap 3. Jika gagal, lepaskan alokasi slot kelas yang sempat di-reserve sebelumnya.
    * Menyematkan batasan transaksi eksplisit `DB.beginTransaction()`, `DB.commitTransaction()`, dan `DB.rollbackTransaction()` yang dibarengi pelepasan kuota via `releaseKapasitas()`.
    * Memisahkan Tahap 8 secara visual dan semantik menggunakan pembatas tegas: `SESI ASINKRON TERPISAH`.
    * Mengonsolidasikan pengiriman notifikasi ke `NotificationService` sebagai *Single Dispatcher*, mengeliminasi duplikasi pemanggilan manual `kirimNotifikasi` langsung dari service layer.
  * ⚡ **Act (Tindakan / Aksi):**
    * Memperbarui [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd) dengan menambahkan `reserveKapasitas()` dan `releaseKapasitas()` pada class `Schedule`.
    * Menulis ulang [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd) dengan seluruh 5 perbaikan arsitektural di atas.
    * Memperbarui dokumentasi teknis [`docs/sequence/SEQUENCE-001-pmb-and-krs.md`](../docs/sequence/SEQUENCE-001-pmb-and-krs.md) dan meregenerasi visualisasi SVG [`docs/sequence/krs_sequence_diagram.svg`](../docs/sequence/krs_sequence_diagram.svg).
    * Memvalidasi sintaks diagram menggunakan `@mermaid-js/mermaid-cli` (Exit Code 0).
  * 💡 **Reflect (Refleksi):**
    * Sequence diagram KRS kini memenuhi kualifikasi *Enterprise-Grade Architecture*: tangguh terhadap lonjakan konkurensi ekstrem, menjamin integritas data ACID melalui transaksi kompensasi, serta mengeliminasi kerancuan siklus hidup bisnis asinkron.
    * Penambahan kontrak `reserveKapasitas` dan `releaseKapasitas` memperkuat *Domain-Driven Design (DDD)*, di mana aturan integritas agregat dipertahankan langsung oleh entitas yang memiliki status tersebut.
* **Hasil / Luaran:**
  * Diagram Class Mermaid yang diperbarui: [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd).
  * Diagram Sequence KRS Mermaid yang diperbarui: [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd).
  * File visualisasi SVG: [`docs/sequence/krs_sequence_diagram.svg`](../docs/sequence/krs_sequence_diagram.svg).

---

### 🔹 Log 11: Pembaruan Komprehensif Dokumentasi ADR (ADR-001, ADR-002, ADR-003) Berbasis OPAR (Observe, Plan, Act, Reflect)
* **Minggu:** `2`
* **Fitur:** Sinkronisasi menyeluruh dokumentasi Architectural Decision Record (ADR-001, ADR-002, ADR-003) beserta kompilasi ulang artefak PDF
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`459cf7e`](https://github.com/zainunkamal/sevima-mini/commit/459cf7e)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Update dokumentasi ADF dengan revisian yang sudah dibuat"
  ```
* **Metodologi OPAR:**
  * 👁️ **Observe (Observasi):**
    * Dokumentasi ADR sebelumnya belum merefleksikan revisi arsitektur v2.1:
      * `ADR-001` belum mencakup domain core baru (`KRS`, `KRSService`, `PMBService`, `NotificationService`, `ProgramStudi`, `NIMGenerator`), 5 aturan validasi *Strategy Pattern*, metode reservasi atomik `Schedule.reserveKapasitas()`, serta matriks perbandingan evolusi 4 diagram.
      * `ADR-002` masih merujuk asosiasi lama (`Daftar Kuliah` ke `Mahasiswa`, `Generate Transkrip` ke `Dosen`, `Sanggah Nilai` ke `Input Nilai`), belum membedakan `Dosen PA` vs `Dosen Pengajar`, belum menyertakan aktor `Calon Mahasiswa`, dan belum memuat 8 use case baru yang muncul di alur sekuensial.
      * `ADR-003` belum memuat 4 alternate flow PMB, pemisahan `NIMGenerator` dari `UserFactory` (SRP), alur keamanan aktivasi tanpa kata sandi teks polos, 5 alternate flow KRS, proteksi konkurensi kapasitas kelas (`reserveKapasitas`/`releaseKapasitas`), cakupan transaksi database ACID (`beginTransaction`/`commit`/`rollback`), dan pemisahan sesi asinkron Dosen PA.
    * Berkas PDF lama di `docs/adr/` sudah usang dan tidak sinkron dengan diagram Mermaid aktif.
  * 📋 **Plan (Rencana):**
    * Menulis ulang `docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md` dengan menyertakan tabel struktur class v2.1, relasi composition vs aggregation, prinsip SOLID, design patterns, mitigasi konkurensi, matriks evolusi arsitektur, dan referensi visual diagram per versi.
    * Memperbarui `docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md` dengan dekomposisi aktor (`Calon Mahasiswa`, `Mahasiswa`, `Dosen PA`, `Dosen Pengajar`, `Admin`, `Sistem PMB`), tabel matriks use case lengkap (termasuk 8 use case baru), rationale relasi `<<include>>` dan `<<extend>>` yang telah dikoreksi, serta analisis trade-off.
    * Memperbarui `docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md` dengan dokumentasi terperinci 4 tahapan PMB (beserta 4 alternate flows dan tautan aktivasi) serta 7 tahapan KRS (beserta 5 alternate flows, reservasi atomik, scope transaksi database, dan pemisahan sesi approval Dosen PA).
    * Mengkompilasi ulang seluruh dokumen ADR menjadi berkas PDF resmi di `docs/adr/` menggunakan `md-to-pdf` dengan flag sandbox Puppeteer.
    * Melakukan commit ke Git dan mencatat ke dalam log penggunaan AI.
  * ⚡ **Act (Tindakan / Aksi):**
    * Memperbarui ketiga file markdown ADR di `docs/adr/ADR-Markdown/`.
    * Mengkompilasi ulang `ADR-001-academic-system-class-structure.pdf`, `ADR-002-academic-usecase-architecture.pdf`, dan `ADR-003-academic-sequence-flows.pdf` ke direktori `docs/adr/`.
    * Memverifikasi konsistensi nama class, method, aktor, dan relasi terhadap `diagrams/*.mmd`.
    * Meng-commit berkas dengan pesan: `docs(adr): update ADR-001, ADR-002, and ADR-003 with complete v2.1 architecture revisions and regenerate PDFs` (`459cf7e`).
  * 💡 **Reflect (Refleksi):**
    * Seluruh dokumentasi arsitektur (ADR-001, ADR-002, dan ADR-003) kini berada dalam status 100% konsisten dan tersinkronisasi penuh dengan diagram UML aktif (`class-diagram.mmd`, `usecase-diagram.mmd`, `sequence-krs.mmd`, `sequence-pmb.mmd`).
    * Rekaman riwayat evolusi perancangan terdokumentasi secara transparan dan terukur, memenuhi standar dokumentasi rekayasa perangkat lunak skala enterprise.
* **Hasil / Luaran:**
  * Dokumen ADR-001: [`docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md`](../docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md) & PDF: [`docs/adr/ADR-001-academic-system-class-structure.pdf`](../docs/adr/ADR-001-academic-system-class-structure.pdf).
  * Dokumen ADR-002: [`docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md`](../docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md) & PDF: [`docs/adr/ADR-002-academic-usecase-architecture.pdf`](../docs/adr/ADR-002-academic-usecase-architecture.pdf).
  * Dokumen ADR-003: [`docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md`](../docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md) & PDF: [`docs/adr/ADR-003-academic-sequence-flows.pdf`](../docs/adr/ADR-003-academic-sequence-flows.pdf).
