# SEVIMA Mini - Sistem Informasi Akademik Kampus Kecil

> Perancangan dan Pemodelan Arsitektur Berorientasi Objek (OOP) Berbasis Prinsip SOLID dan Standar UML Formal.

**Pengembang:** Zainun Kamal Ramadhan  
**NIM:** 263636001  
**Institusi:** Institut Sains dan Teknologi Nasional (ISTN)  

---

## 📌 Ringkasan Proyek

**SEVIMA Mini** adalah rancangan sistem informasi akademik kampus skala kecil yang dirancang untuk mengelola seluruh siklus operasional akademik mahasiswa dari proses penerimaan hingga kelulusan. Sistem ini mencakup 5 modul fungsional inti:

1. **PMB (Penerimaan Mahasiswa Baru):** Pendaftaran seleksi calon mahasiswa, pengumuman hasil seleksi, dan transisi siklus hidup (*lifecycle conversion*) menjadi mahasiswa aktif.
2. **KRS (Kartu Rencana Studi):** Pengambilan mata kuliah tiap semester, verifikasi prasyarat, validasi beban maksimal 24 SKS, serta pencegahan pendaftaran ganda.
3. **Penjadwalan Kuliah (Schedule):** Manajemen alokasi hari, jam mulai/selesai, ruangan kuliah, penugasan dosen pengajar, dan validasi bentrok jadwal riil mahasiswa.
4. **Penilaian Akademik (Grade & KHS):** Penginputan nilai angka/huruf oleh dosen, penerbitan Kartu Hasil Studi (KHS), dan kalkulasi Indeks Prestasi Kumulatif (IPK).
5. **Pembayaran SPP (Payment):** Pencatatan tagihan semesteran, validasi status pembayaran lunas/menunggak oleh Admin, serta integrasi syarat administrasi akademik.

---

## 🏛️ Prinsip Desain & Standar Arsitektur

Arsitektur kelas pada SEVIMA Mini dibangun dengan mematuhi kaidah rekayasa perangkat lunak modern:

- **SOLID Principles:**
  - *Single Responsibility Principle (SRP):* Setiap entitas hanya bertanggung jawab pada domain fungsionalnya sendiri, dengan pembatasan ketat $\le 10$ method per kelas.
  - *Dependency Inversion & Loose Coupling:* Memutus ketergantungan siklik (*circular dependency*) dua arah antara modul `Course` dan `Mahasiswa` melalui penyederhanaan antarmuka verifikasi prasyarat.
- **Enkapsulasi Ketat (*Information Hiding*):**
  - Seluruh atribut pada 10 kelas dideklarasikan sebagai `private (-)`.
  - Manipulasi dan pembacaan state objek hanya dilakukan melalui method publik (`+`) accessor/mutator yang tervalidasi.
- **Pola Kelas Perantara (*Junction Entity Pattern*):**
  - Mengurai relasi *many-to-many* antara `Mahasiswa` dan `Course` menjadi dua relasi *one-to-many* yang ternormalisasi melalui kelas perantara `Enrollment`.
  - Keputusan arsitektur ini didokumentasikan secara formal dalam [ADR-001.pdf](file:///home/zainun/git/istn/sevima-mini/documents/ADR-001.pdf).
- **Semantik Relasi UML Formal:**
  - **Komposisi (`*--`):** Relasi kepemilikan kuat berbasis siklus hidup (*lifecycle dependency*), yaitu `Mahasiswa *-- Enrollment`, `Enrollment *-- Grade`, dan `Course *-- Schedule`.
  - **Asosiasi Referensial (`-->`):** Relasi referensi antar entitas independen, yaitu `Course --> Enrollment`, `Schedule --> Enrollment`, `Dosen --> Schedule`, `CalonMahasiswa --> Mahasiswa`, dan relasi prasyarat *self-referencing* `Course --> Course`.
  - **Pewarisan / Generalisasi (`<|--`):** Pewarisan murni yang lolos uji *is-a*, yaitu `User <|-- Mahasiswa`, `User <|-- Dosen`, `User <|-- Admin`, dan `User <|-- CalonMahasiswa`.

---

## 📂 Struktur Repositori

```
sevima-mini/
├── README.md                     # Dokumentasi utama proyek
├── diagram/                      # Artefak kode diagram dan spesifikasi teknis
│   ├── class-diagram.mmd         # Kode sumber Mermaid class diagram (Versi 6 - Refactor SOLID Penuh)
│   ├── class-diagram.md          # Spesifikasi rinci atribut, method, relasi, dan aturan bisnis
│   ├── use-case-diagram.puml     # Kode sumber PlantUML Use Case Diagram (Versi 2)
│   ├── use-case-diagram.md       # Spesifikasi formal use case, aktor, dan relasi include/extend
│   ├── krs-sequence-diagram.mmd  # Kode sumber Sequence Diagram Pengisian & Validasi KRS
│   ├── krs-sequence-diagram.md   # Spesifikasi alur validasi komprehensif & error accumulator
│   ├── pmb-sequence-diagram.mmd  # Kode sumber Sequence Diagram PMB
│   ├── pmb-sequence-diagram.md   # Spesifikasi alur PMB, factory pattern, & resilient notification
│   ├── krs-approval-sequence-diagram.mmd # Kode sumber Sequence Diagram Persetujuan & Revisi KRS
│   ├── krs-approval-sequence-diagram.md  # Spesifikasi alur Approve & Revisi KRS
│   ├── payment-sequence-diagram.mmd      # Kode sumber Sequence Diagram Pembayaran SPP & Denda
│   ├── payment-sequence-diagram.md       # Spesifikasi alur transaksi keuangan & denda keterlambatan
│   ├── grading-transcript-sequence-diagram.mmd # Kode sumber Sequence Diagram Penilaian & Transkrip
│   └── grading-transcript-sequence-diagram.md  # Spesifikasi alur input nilai & penerbitan transkrip
├── perbaikan/                    # Riwayat perbaikan dan bukti visual evolusi diagram
│   ├── README.md                 # Dokumentasi komparasi perubahan antar versi
│   ├── minggu-01/                # Bukti visual evolusi Class Diagram Minggu 1 (Versi 1-4)
│   │   ├── diagram_sebelum_dirubah.png  # Versi 1 (Draft awal AI)
│   │   ├── diagram_sesudah_dirubah.png  # Versi 2 (Enkapsulasi penuh & hitungIPK)
│   │   ├── diagram_versi_3.png          # Versi 3 (Refactoring relasi & kardinalitas)
│   │   └── diagram_versi_4.png          # Versi 4 (Perbaikan arsitektur kritis 1-4)
│   └── minggu-02/                # Bukti visual pemodelan dinamis & sinkronisasi Minggu 2
│       ├── class_diagram_versi_6.png    # Screenshot Class Diagram Versi 6 (Refactor SOLID)
│       ├── use_case_versi_2.png         # Screenshot Use Case Diagram Versi 2
│       ├── krs_sequence_diagram_versi_2.png # Screenshot Sequence Validasi KRS
│       ├── pmb_sequence_diagram_versi_2.png # Screenshot Sequence PMB
│       ├── krs_approval_sequence_diagram_versi_1.png # Screenshot Sequence Approve/Revisi KRS
│       ├── payment_sequence_diagram_versi_1.png      # Screenshot Sequence Pembayaran SPP
│       └── grading_transcript_sequence_diagram_versi_1.png # Screenshot Sequence Penilaian/Transkrip
├── documents/                    # Dokumen keputusan arsitektural (ADR)
│   └── ADR-001.pdf               # ADR: Pemecahan Relasi M:N dengan Kelas Perantara Enrollment
└── logs/                         # Catatan transparansi penggunaan AI
    └── ai-usage-log.md           # Log interaksi AI dengan kerangka OPAR (Observe-Plan-Act-Reflect)
```

---

## 📊 Class Diagram Terkini (Versi 6 - Refactor Arsitektur SOLID Penuh)

Diagram kelas berikut merepresentasikan arsitektur final yang telah mematuhi prinsip **SOLID** secara menyeluruh (SRP, ISP, DIP):

```mermaid
classDiagram
    %% ==========================================
    %% 1. ROLE-BASED INTERFACES (ISP & DIP)
    %% ==========================================
    class PengisiKRS {
        <<interface>>
        +getNim() String
        +getSemester() int
        +getDaftarMatkulLulus() String[]
    }

    class PenyetujuKRS {
        <<interface>>
        +getNidn() String
        +verifikasiRencanaStudi(String krsId, boolean disetujui) boolean
    }

    class Penilai {
        <<interface>>
        +getNidn() String
        +inputNilaiMahasiswa(String enrollmentId, float nilaiAngka) boolean
    }

    class ValidationRule {
        <<interface>>
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    class NotificationChannel {
        <<interface>>
        +send(String recipient, String message) boolean
    }

    %% ==========================================
    %% 2. DOMAIN ENTITIES (POCO / High Cohesion)
    %% ==========================================
    class User {
        <<abstract>>
        -String id
        -String username
        -String password
        -String email
        +login(String username, String password) boolean
        +logout() void
        +getId() String
        +getUsername() String
        +getEmail() String
        +setEmail(String email) void
        +ubahPassword(String passwordLama, String passwordBaru) boolean
    }

    class Mahasiswa {
        -String nim
        -String programStudi
        -int semester
        +getNim() String
        +getProgramStudi() String
        +getSemester() int
        +getDaftarMatkulLulus() String[]
    }

    class Dosen {
        -String nidn
        +getNidn() String
        +verifikasiRencanaStudi(String krsId, boolean disetujui) boolean
        +inputNilaiMahasiswa(String enrollmentId, float nilaiAngka) boolean
    }

    class Admin {
        -String staffId
        +getStaffId() String
        +kelolaAkunUser(User user) void
    }

    class CalonMahasiswa {
        -String nomorPendaftaran
        -String statusSeleksi
        +getNomorPendaftaran() String
        +getStatusSeleksi() String
        +setStatusSeleksi(String status) void
    }

    class Course {
        -String kode
        -String nama
        -int sks
        +getKode() String
        +getNama() String
        +getSks() int
    }

    class Enrollment {
        -int semester
        -String tahunAkademik
        -String status
        +getSemester() int
        +getTahunAkademik() String
        +getStatus() String
        +setStatus(String status) void
    }

    class Schedule {
        -String hari
        -String jamMulai
        -String jamSelesai
        -String ruangan
        +getHari() String
        +getJamMulai() String
        +getJamSelesai() String
        +getRuangan() String
    }

    class Grade {
        -float nilaiAngka
        -String nilaiHuruf
        +getNilaiAngka() float
        +getNilaiHuruf() String
        +setNilai(float nilaiAngka, String nilaiHuruf) void
    }

    class Payment {
        -int semester
        -double jumlah
        -String tanggalBayar
        -String status
        +getJumlah() double
        +getStatus() String
        +setStatus(String status) void
    }

    class Attendance {
        -String tanggal
        -String statusKehadiran
        +getTanggal() String
        +getStatusKehadiran() String
        +setStatusKehadiran(String status) void
    }

    %% ==========================================
    %% 3. CONCRETE VALIDATION RULES (Strategy)
    %% ==========================================
    class PrerequisiteRule {
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    class MaxCreditRule {
        -int batasSKS
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    class ScheduleConflictRule {
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    %% ==========================================
    %% 4. CONCRETE NOTIFICATION CHANNELS
    %% ==========================================
    class EmailChannel {
        +send(String recipient, String message) boolean
    }

    class PushNotificationChannel {
        +send(String recipient, String message) boolean
    }

    %% ==========================================
    %% 5. MODULAR SERVICES (SRP per Modul)
    %% ==========================================
    class PMBService {
        -NotificationService notifier
        +daftar(String dataDiri, Object berkas) String
        +verifikasiBerkas(String noPendaftaran) boolean
        +nyatakanLulus(String noPendaftaran, String prodi) Mahasiswa
    }

    class KRSService {
        -KRSValidator validator
        -NotificationService notifier
        +submitKRS(PengisiKRS mhs, String[] daftarMatkul) boolean
        +ajukanRevisiKRS(PengisiKRS mhs, String[] daftarMatkul) boolean
        +prosesPersetujuan(PenyetujuKRS dosen, String krsId, boolean disetujui) boolean
    }

    class KRSValidator {
        -ValidationRule[] rules
        +registerRule(ValidationRule rule) void
        +validateAll(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrors() List
    }

    class JadwalService {
        +buatJadwal(Course course, Schedule schedule, Dosen pengajar) boolean
        +cekBentrok(Schedule s1, Schedule s2) boolean
        +getJadwalMahasiswa(String nim) List
        +getJadwalDosen(String nidn) List
    }

    class NilaiService {
        +inputNilai(Penilai dosen, String enrollmentId, float nilaiAngka) boolean
        +hitungNilaiHuruf(float nilaiAngka) String
        +hitungIPK(String nim) double
        +generateTranskrip(String nim) Object
    }

    class KeuanganService {
        +buatTagihanSPP(String nim, int semester, double nominal) Payment
        +prosesPembayaran(String paymentId, double jumlahBayar) boolean
        +hitungDenda(String paymentId) double
        +validasiStatusLunas(String nim, int semester) boolean
    }

    class PresensiService {
        +catatKehadiran(String enrollmentId, Attendance attendance) boolean
        +hitungPersentaseKehadiran(String enrollmentId) double
    }

    class NotificationService {
        -NotificationChannel channel
        +setChannel(NotificationChannel channel) void
        +kirimNotifikasi(String penerima, String pesan) boolean
    }

    %% ==========================================
    %% 6. RELASI, IMPLEMENTASI, & INJEKSI
    %% ==========================================
    User <|-- Mahasiswa
    User <|-- Dosen
    User <|-- Admin
    User <|-- CalonMahasiswa

    PengisiKRS <|.. Mahasiswa
    PenyetujuKRS <|.. Dosen
    Penilai <|.. Dosen

    ValidationRule <|.. PrerequisiteRule
    ValidationRule <|.. MaxCreditRule
    ValidationRule <|.. ScheduleConflictRule

    NotificationChannel <|.. EmailChannel
    NotificationChannel <|.. PushNotificationChannel

    Mahasiswa "1" *-- "0..*" Enrollment : memiliki
    Enrollment "1" *-- "0..1" Grade : memiliki
    Mahasiswa "1" *-- "0..*" Payment : memiliki
    Course "1" *-- "0..*" Schedule : memiliki
    Course "1" --> "0..*" Enrollment : didaftarkan
    Schedule "1" --> "0..*" Enrollment : diikuti
    Dosen "1" --> "0..*" Schedule : mengajar
    Course "0..*" --> "0..*" Course : prasyarat
    Enrollment "1" *-- "0..*" Attendance : mencatat

    KRSService --> KRSValidator : delegasi validasi
    KRSService --> NotificationService : memicu notifikasi
    KRSService ..> PengisiKRS : depends on role interface
    KRSService ..> PenyetujuKRS : depends on role interface
    KRSValidator o--> ValidationRule : agregasi aturan validasi (DIP)

    NilaiService ..> Penilai : depends on role interface
    NotificationService o--> NotificationChannel : injeksi kanal (DIP)
    PMBService --> NotificationService : memicu notifikasi
    KeuanganService ..> Payment : mengelola tagihan
    JadwalService ..> Schedule : mengelola sesi
    PresensiService ..> Attendance : mengelola kehadiran
```

---

## 🔄 Ringkasan Evolusi Arsitektur

| Evaluasi Arsitektural | Versi 1 (Draft Awal) | Versi 2 (Enkapsulasi) | Versi 3 (Relational) | Versi 4 (Final Refactor) |
| :--- | :--- | :--- | :--- | :--- |
| **Enkapsulasi Atribut** | `protected (#)` | `private (-)` | `private (-)` | `private (-)` |
| **Method `hitungIPK()`** | Belum ada | Ada di `Mahasiswa` | Ada di `Mahasiswa` | Ada di `Mahasiswa` |
| **Keterhubungan `Schedule`** | Hanya ke `Course` | Hanya ke `Course` | Hanya ke `Course` | **Terhubung ke `Enrollment` & `Dosen`** |
| **Siklus Hidup PMB** | Subclass kaku | Subclass kaku | Subclass kaku | **Asosiasi & Method Konversi ke `Mahasiswa`** |
| **Coupling `Course`-`Mahasiswa`**| Ketergantungan Siklik | Ketergantungan Siklik | Ketergantungan Siklik | **Terputus via parameter `String[]`** |
| **Tanggung Jawab KRS** | Ambigu | Ambigu | Ambigu | **Delegasi SKS via Enrollment & Validasi Semester** |

Rincian lengkap dan perbandingan visual dapat dilihat pada [perbaikan/README.md](file:///home/zainun/git/istn/sevima-mini/perbaikan/README.md).

---

## 📜 Architectural Decision Record (ADR)

Keputusan desain arsitektural penting dicatat menggunakan format ADR resmi:
- **[ADR-001: Memecah Relasi Many-to-Many Mahasiswa-Course Menggunakan Kelas Perantara Enrollment](file:///home/zainun/git/istn/sevima-mini/documents/ADR-001.pdf):** Menjelaskan analisis konteks, alternatif opsi (relasi langsung vs perantara), pertimbangan trade-off, serta catatan peran revisi manual manusia terhadap saran AI.

---

## 🤖 Catatan Transparansi Penggunaan AI

Seluruh interaksi bersama AI (Gemini 3.8 Flash) dicatat secara transparan pada [logs/ai-usage-log.md](file:///home/zainun/git/istn/sevima-mini/logs/ai-usage-log.md) dengan menerapkan siklus refleksi **OPAR (Observe - Plan - Act - Reflect)** untuk setiap iterasi prompt (Prompt #1 hingga #4).

---

## 🔗 Tautan Dokumen & Berkas Cepat

- [README Perbaikan & Screenshot Evolusi](file:///home/zainun/git/istn/sevima-mini/perbaikan/README.md)
- [Spesifikasi Class Diagram Lengkap](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.md)
- [Source Code Mermaid Class Diagram](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd)
- [Dokumen Keputusan Arsitektur ADR-001 (PDF)](file:///home/zainun/git/istn/sevima-mini/documents/ADR-001.pdf)
- [Log Penggunaan AI (OPAR)](file:///home/zainun/git/istn/sevima-mini/logs/ai-usage-log.md)
