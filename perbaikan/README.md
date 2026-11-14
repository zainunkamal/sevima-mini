# Dokumentasi Riwayat Perbaikan Class Diagram UML - SEVIMA Mini

Dokumen ini mencatat bukti visual dan perbandingan evolusi class diagram UML sistem informasi akademik **SEVIMA Mini** dari Versi 1 hingga Versi 4 pada iterasi **Minggu 1**, serta struktur persiapan untuk iterasi berikutnya.

---

## Struktur Folder Perbaikan

- [minggu-01/](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-01): Berisi seluruh artefak tangkapan layar (*screenshot*) bukti visual evolusi class diagram Versi 1 hingga Versi 4.
- [minggu-02/](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-02): Berisi artefak visual Use Case Diagram SEVIMA Mini (Versi 1) dan perbaikan berikutnya.
- [minggu-03/](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-03): Berisi dokumentasi dan artefak implementasi basis data modul PMB (SQLAlchemy 2.0 & migrasi Alembic).
- [minggu-04/](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-04): Berisi dokumentasi generator penomoran NIM multi-worker, model `NimCounter`, migrasi Alembic, serta manajemen konkurensi row-lock database.

---

## Minggu 1: Evolusi Class Diagram (Versi 1 - Versi 4)

### 1. Versi 1: Versi Awal (Draft Awal AI)
![Versi 1 - Versi Awal](minggu-01/diagram_sebelum_dirubah.png)

- **Karakteristik & Celah:**
  - Menggunakan visibility `protected (#)` pada atribut `User` (`id`, `username`, `email`).
  - Belum memiliki accessor publik (`getId()`, `getUsername()`, dll) pada `User`.
  - Belum memiliki method penghitungan IPK (`hitungIPK()`) pada `Mahasiswa`.
  - Menggunakan notasi agregasi (`o--`) untuk relasi non-komposisi secara berlebihan.
- **Commit Terkait:** `58f6338` (*feat: initial commit with SEVIMA Mini UML class diagram*)

---

### 2. Versi 2: Enkapsulasi Penuh & Penambahan `hitungIPK()`
![Versi 2 - Enkapsulasi](minggu-01/diagram_sesudah_dirubah.png)

- **Perubahan Utama:**
  - Enkapsulasi ketat: seluruh atribut dijadikan `private (-)`.
  - Penambahan method publik accessor/mutator pada `User`, `Admin`, `Enrollment`, dan `Payment`.
  - Penambahan method khusus `+hitungIPK() double` pada kelas `Mahasiswa` (bukan di kelas `User`).
  - Pembatasan jumlah method tetap $\le 9$ per kelas (patuh prinsip *Single Responsibility Principle*).
- **Commit Terkait:** `f5d2df3` (*docs: enrich class diagram documentation with OOP specs and business rules*)

---

### 3. Versi 3: Refactoring Relasi (Hasil Uji Wadah & Is-A)
![Versi 3 - Refactoring Relasi](minggu-01/diagram_versi_3.png)

- **Perubahan Utama:**
  - **Uji Wadah-Bagian (*Lifecycle Dependency*):**
    - `Course` $\rightarrow$ `Enrollment`: Diubah dari Agregasi (`o--`) menjadi **Asosiasi (`-->`)**, karena entitas `Course` pada katalog kurikulum bukan wadah fisik/tubuh dari transaksi pendaftaran `Enrollment`.
    - `Dosen` $\rightarrow$ `Course`: Diubah dari Agregasi (`o--`) menjadi **Asosiasi (`-->`)**, karena relasi murni peran mengajar.
    - `Course` $\rightarrow$ `Course` (Prasyarat): Diubah dari Agregasi (`o--`) menjadi **Asosiasi (`-->`)** antar sesama entitas mata kuliah setara (*self-referencing association*).
  - **Koreksi Kardinalitas:**
    - `Course "1" *-- "0..*" Schedule`: Batas minimum jadwal diubah dari `1..*` menjadi `0..*` agar mata kuliah kurikulum baru dapat dibuat sebelum penawaran jadwal disusun.
- **Commit Terkait:** `46604ef` (*feat: apply relational refactoring (version 3) and add screenshot evidence*)

---

### 4. Versi 4: Perbaikan Arsitektur Kritis 1-4 (Final Refactor)
![Versi 4 - Perbaikan Arsitektur Kritis 1-4](minggu-01/diagram_versi_4.png)

- **Perubahan Utama:**
  1. **Integrasi Jadwal Riil (Mengatasi Masalah 1 - *Broken Operational Workflow*):**
     - Menghubungkan `Schedule "1" --> "0..*" Enrollment : diikuti` agar mahasiswa terdaftar pada sesi/ruangan spesifik, memungkinkan pengecekan bentrok jadwal riil via `Enrollment.cekBentrokJadwal()`.
     - Menghubungkan `Dosen "1" --> "0..*" Schedule : mengajar` agar fungsionalitas `Dosen.lihatJadwalMengajar()` memiliki sumber data jam dan ruangan yang valid.
  2. **Transisi Siklus Hidup PMB (Mengatasi Masalah 2 - *Rigid Lifecycle Inheritance*):**
     - Menambahkan method `CalonMahasiswa.konversiKeMahasiswa(nimBaru, prodi): Mahasiswa`.
     - Menambahkan relasi asosiasi transisi peran `CalonMahasiswa "1" --> "0..1" Mahasiswa : diterimaSebagai`.
  3. **Pemutusan Ketergantungan Siklik (Mengatasi Masalah 3 - *Circular Coupling*):**
     - Mengubah signature `Course.cekPrasyarat(Mahasiswa mhs)` menjadi `Course.cekPrasyarat(String[] kodeMatkulLulus): boolean`.
     - Menghapus ketergantungan langsung `Course` terhadap `Mahasiswa`, sehingga katalog kurikulum sepenuhnya independen dari model data mahasiswa.
  4. **Klarifikasi Tanggung Jawab KRS & SKS (Mengatasi Masalah 4 - *Role Ambiguity*):**
     - Menambahkan method delegasi `Enrollment.getSks(): int`.
     - Menjadikan validasi batas 24 SKS dan duplikasi matkul berbasis semester spesifik pada `Mahasiswa` (`validasiBebanKRS(int semester)`, `cekDuplikasiCourse(kodeCourse, semester)`).
- **Commit Terkait:** `a8fce29` (*feat: resolve architectural flaws 1-4 (version 4) and add screenshot evidence*)

---

## Minggu 2: Pemodelan Dinamis & Penyelarasan Penuh Arsitektur (Sinkronisasi Versi 5)

Pada iterasi ini, seluruh diagram diselaraskan secara komprehensif berdasarkan temuan evaluasi konsistensi, dengan mengadopsi **Opsi A (Layered / Clean Architecture)** dan melengkapi sequence diagram sehingga **100% dari 10 Use Case memiliki pemodelan alur dinamis**.

### 1. Class Diagram Versi 7 (Integrasi Tiga GoF Design Patterns: Factory, Observer, Strategy)
![Class Diagram Versi 7](minggu-02/class_diagram_versi_7.png)
- **Pembaruan:**
  - **Factory Pattern (`UserFactory`):** Sentralisasi instansiasi seluruh turunan `User` (`Mahasiswa`, `Dosen`, `Admin`, `CalonMahasiswa`) dengan penegakan integritas bisnis bahwa `Mahasiswa` **wajib selalu memiliki NIM**.
  - **Observer Pattern (`KRSSubscriber` & `KRSManager`):** `KRSManager` (Subject) mengumumkan event perubahan status KRS; `Mahasiswa`, `Dosen` (PA), dan `Admin` (bagian akademik) bertindak sebagai subscriber yang otomatis terbarui secara *loose-coupling*.
  - **Strategy Pattern (`ValidationRule` & `KRSValidator`):** Abstraksi antarmuka `ValidationRule` dengan implementasi strategi konkret `CekPrasyaratRule`, `CekBatasSKSRule`, dan `CekJadwalBentrokRule`. Aturan baru seperti `CekTunggakanRule` dapat ditambahkan ke `KRSValidator` tanpa mengubah kode internal (*Open/Closed Principle*).
- **Berkas Model:** [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd) & [class-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.md)

### 2. Use Case Diagram (Versi 2)
![Use Case Diagram Versi 2](minggu-02/use_case_versi_2.png)
- **Pembaruan:** Menambahkan aktor `Calon Mahasiswa` secara eksplisit mendampingi `Sistem PMB` untuk merefleksikan alur pendaftaran mandiri dan integrasi sistem.
- **Berkas Model:** [use-case-diagram.puml](file:///home/zainun/git/istn/sevima-mini/diagram/use-case-diagram.puml) & [use-case-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/use-case-diagram.md)

### 3. Sequence Diagram Pengisian & Validasi KRS (Versi 2)
![Sequence Diagram Validasi KRS](minggu-02/krs_sequence_diagram_versi_2.png)
- **Penyelarasan:** Aktor diselaraskan menjadi `Dosen as Dosen (PA)`, method tersinkron 100% dengan `KRSValidator` dan `Repository`.
- **Cakupan Use Case:** `Isi KRS` dan `Cek Prasyarat` (`<<include>>`).
- **Berkas Model:** [krs-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/krs-sequence-diagram.mmd) & [krs-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/krs-sequence-diagram.md)

### 4. Sequence Diagram Pendaftaran Mahasiswa Baru / PMB (Versi 2)
![Sequence Diagram PMB](minggu-02/pmb_sequence_diagram_versi_2.png)
- **Penyelarasan:** Partisipan `Database` digantikan oleh `Repository`, konsisten dengan `Repository` di Class Diagram dan Sequence KRS.
- **Cakupan Use Case:** `Daftar sebagai Calon Mahasiswa` dan `Verifikasi Berkas`.
- **Berkas Model:** [pmb-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/pmb-sequence-diagram.mmd) & [pmb-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/pmb-sequence-diagram.md)

### 5. Sequence Diagram Persetujuan & Revisi KRS (Versi 1)
![Sequence Diagram Persetujuan & Revisi KRS](minggu-02/krs_approval_sequence_diagram_versi_1.png)
- **Cakupan Use Case:** `Approve KRS` dan `Ajukan Revisi KRS` (`<<extend>>`).
- **Berkas Model:** [krs-approval-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/krs-approval-sequence-diagram.mmd) & [krs-approval-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/krs-approval-sequence-diagram.md)

### 6. Sequence Diagram Pembayaran SPP & Denda Keterlambatan (Versi 1)
![Sequence Diagram Pembayaran SPP](minggu-02/payment_sequence_diagram_versi_1.png)
- **Cakupan Use Case:** `Bayar SPP` dan `Bayar Denda Keterlambatan` (`<<extend>>`).
- **Berkas Model:** [payment-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/payment-sequence-diagram.mmd) & [payment-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/payment-sequence-diagram.md)

### 7. Sequence Diagram Penilaian & Penerbitan Transkrip (Versi 1)
![Sequence Diagram Penilaian & Transkrip](minggu-02/grading_transcript_sequence_diagram_versi_1.png)
- **Cakupan Use Case:** `Input Nilai` dan `Generate Transkrip`.
- **Berkas Model:** [grading-transcript-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/grading-transcript-sequence-diagram.mmd) & [grading-transcript-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/grading-transcript-sequence-diagram.md)

---

## Tabel Komparasi Riwayat Versi

| Evaluasi Arsitektural | Versi 1 | Versi 2 | Versi 3 | Versi 4 (Final Refactor) | Versi 7 (Design Patterns & SOLID) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Enkapsulasi Atribut** | `protected (#)` | `private (-)` | `private (-)` | `private (-)` | **`private (-)` ketat pada seluruh kelas** |
| **Pola Kreasi (Factory)** | Instansiasi langsung | Instansiasi langsung | Instansiasi | Transisi method | **`UserFactory`: Instansiasi terpusat & garansi Mahasiswa wajib ber-NIM** |
| **Event Transaksi (Observer)**| Tidak ada | Tidak ada | Tidak ada | Tidak ada | **`KRSSubscriber`: Notifikasi otomatis status KRS ke Mahasiswa, Dosen PA, Admin** |
| **Validasi Bisnis (Strategy)**| Hardcoded di entitas | Hardcoded di entitas | Hardcoded | Hardcoded | **`ValidationRule`: `CekPrasyarat`, `CekBatasSKS`, `CekJadwalBentrok` (Open/Closed)** |
| **Coupling Komponen** | Monolitik | Monolitik | Refactor relasi | Terputus via `String[]` | **Loose-coupling murni berbasis interface & event-driven** |

---

## Berkas Terkait

- Sequence Diagram Persetujuan & Revisi KRS: [krs-approval-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/krs-approval-sequence-diagram.mmd) & [krs-approval-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/krs-approval-sequence-diagram.md)
- Sequence Diagram Pembayaran SPP & Denda: [payment-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/payment-sequence-diagram.mmd) & [payment-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/payment-sequence-diagram.md)
- Sequence Diagram Penilaian & Transkrip: [grading-transcript-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/grading-transcript-sequence-diagram.mmd) & [grading-transcript-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/grading-transcript-sequence-diagram.md)
- Sequence Diagram PMB (Versi 2): [pmb-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/pmb-sequence-diagram.mmd) & [pmb-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/pmb-sequence-diagram.md)
- Sequence Diagram Validasi KRS (Versi 2): [krs-sequence-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/krs-sequence-diagram.mmd) & [krs-sequence-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/krs-sequence-diagram.md)
- Use Case Diagram (Versi 2): [use-case-diagram.puml](file:///home/zainun/git/istn/sevima-mini/diagram/use-case-diagram.puml) & [use-case-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/use-case-diagram.md)
- Kode Mermaid Class Diagram Versi 7: [class-diagram.mmd](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd) & [class-diagram.md](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.md)
- Dokumen Keputusan Arsitektur: [ADR-001.pdf](file:///home/zainun/git/istn/sevima-mini/documents/ADR-001.pdf), [ADR-002.pdf](file:///home/zainun/git/istn/sevima-mini/documents/ADR-002.pdf), dan [ADR-003.pdf](file:///home/zainun/git/istn/sevima-mini/documents/ADR-003.pdf)
- Dokumentasi Perbaikan Minggu 4 (NIM Generator & Concurrency): [perbaikan/minggu-04/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-04/README.md)
- Catatan Transparansi AI: [ai-usage-log.md](file:///home/zainun/git/istn/sevima-mini/logs/ai-usage-log.md)
