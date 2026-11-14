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
│   ├── class-diagram.mmd         # Kode sumber Mermaid class diagram (Versi 7 - GoF Design Patterns)
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
│   ├── minggu-02/                # Bukti visual pemodelan dinamis & sinkronisasi Minggu 2
│   │   ├── class_diagram_versi_7.png    # Screenshot Class Diagram Versi 7 (Factory, Observer, Strategy)
│   │   ├── use_case_versi_2.png         # Screenshot Use Case Diagram Versi 2
│   │   ├── krs_sequence_diagram_versi_2.png # Screenshot Sequence Validasi KRS
│   │   ├── pmb_sequence_diagram_versi_2.png # Screenshot Sequence PMB
│   │   ├── krs_approval_sequence_diagram_versi_1.png # Screenshot Sequence Approve/Revisi KRS
│   │   ├── payment_sequence_diagram_versi_1.png      # Screenshot Sequence Pembayaran SPP
│   │   └── grading_transcript_sequence_diagram_versi_1.png # Screenshot Sequence Penilaian/Transkrip
│   ├── minggu-03/                # Dokumentasi implementasi basis data modul PMB
│   │   └── README.md             # Spesifikasi model SQLAlchemy 2.0 & migrasi Alembic
│   └── minggu-04/                # Dokumentasi generator NIM multi-worker & konkurensi
│       └── README.md             # Spesifikasi NimCounter, row lock, dan retry mechanism
├── app/                          # Kode sumber backend aplikasi (Python/SQLAlchemy 2.0)
│   ├── database.py               # Setup engine, session, dan SQLite PRAGMA listener
│   ├── models/                   # Definisi model deklaratif ORM
│   │   ├── __init__.py           # Package registry model
│   │   └── pmb.py                # Model ProgramStudi, JalurMasuk, CalonMahasiswa, NimCounter
│   ├── schemas/                  # Skema validasi & DTO Pydantic
│   ├── services/                 # Lapisan domain service & generator NIM
│   ├── routers/                  # Router controller FastAPI
│   └── alembic/                  # Konfigurasi dan berkas migrasi skema basis data
│       ├── env.py                # Environment runner Alembic dengan SQLite PRAGMA hook
│       ├── script.py.mako        # Template migrasi
│       └── versions/             # Riwayat migrasi versi basis data
│           ├── 20261114_0001_create_pmb_tables.py # Migrasi awal 3 tabel PMB
│           └── 20261114_0002_create_nim_counter.py # Migrasi tabel nim_counter
├── alembic.ini                   # Konfigurasi utama Alembic
├── documents/                    # Dokumen keputusan arsitektural (ADR)
│   ├── ADR-001.pdf               # ADR: Pemecahan Relasi M:N dengan Kelas Perantara Enrollment
│   ├── ADR-002.pdf               # ADR: Modularitas Domain Service Layer
│   └── ADR-003.pdf               # ADR: Standardisasi Validasi Klien (HTTP 400 vs 422) & Integritas Relasional PMB
├── tests/                        # Suite pengujian otomatis (unittest & pytest)
│   ├── conftest.py               # Fixture pytest terpusat (StaticPool, db, client, prodi_ti)
│   ├── test_pmb_pytest.py        # Pengujian modul PMB berbasis pytest (AAA pattern & idempotensi)
│   ├── test_pmb.py               # Pengujian integritas basis data & constraints
│   ├── test_api_pmb.py           # Pengujian endpoint FastAPI register & DTO
│   ├── test_nim_counter.py       # Pengujian generator NIM multi-worker, row lock & retry
│   ├── test_state_machine.py     # Pengujian mesin transisi approve/reject & idempotensi
│   └── test_status_and_stats.py  # Pengujian endpoint status publik & stats agregasi outerjoin
├── pytest.ini                    # Konfigurasi runner pytest
└── logs/                         # Catatan transparansi penggunaan AI
    └── ai-usage-log.md           # Log interaksi AI dengan kerangka OPAR (Observe-Plan-Act-Reflect)
```

---

## 📊 Class Diagram Terkini (Versi 7 - Integrasi Tiga Design Patterns)

Diagram kelas berikut merepresentasikan arsitektur final yang telah mengintegrasikan pola desain **Factory**, **Observer**, dan **Strategy** tanpa redundansi:

```mermaid
classDiagram
    %% ==========================================
    %% PATTERN 2: OBSERVER INTERFACE (Subscriber)
    %% ==========================================
    class KRSSubscriber {
        <<interface>>
        +onStatusKRSChanged(String krsId, String statusBaru, String pesan) void
    }

    %% ==========================================
    %% PATTERN 3: STRATEGY INTERFACE & RULES
    %% ==========================================
    class ValidationRule {
        <<interface>>
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    class CekPrasyaratRule {
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    class CekBatasSKSRule {
        -int batasMaksimalSKS
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    class CekJadwalBentrokRule {
        +validate(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrorMessage() String
    }

    %% ==========================================
    %% CORE ENTITIES & OBSERVER IMPLEMENTATIONS
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
        +onStatusKRSChanged(String krsId, String statusBaru, String pesan) void
    }

    class Dosen {
        -String nidn
        +getNidn() String
        +lihatJadwalMengajar() void
        +verifikasiKRS(Enrollment enrollment) void
        +inputNilai(Enrollment enrollment, float nilaiAngka) void
        +onStatusKRSChanged(String krsId, String statusBaru, String pesan) void
    }

    class Admin {
        -String staffId
        +getStaffId() String
        +kelolaAkunUser(User user) void
        +validasiPembayaran(Payment payment) void
        +onStatusKRSChanged(String krsId, String statusBaru, String pesan) void
    }

    class CalonMahasiswa {
        -String nomorPendaftaran
        -String statusSeleksi
        +getNomorPendaftaran() String
        +getStatusSeleksi() String
        +daftarSeleksi() void
        +lihatPengumuman() String
        +konversiKeMahasiswa(String nimBaru, String prodi) Mahasiswa
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
        +getSks() int
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
        +prosesPembayaran() void
    }

    %% ==========================================
    %% PATTERN 1: FACTORY
    %% ==========================================
    class UserFactory {
        +createMahasiswa(String id, String username, String email, String nim, String prodi) Mahasiswa
        +createDosen(String id, String username, String email, String nidn) Dosen
        +createAdmin(String id, String username, String email, String staffId) Admin
        +createCalonMahasiswa(String id, String username, String email, String nomorPendaftaran) CalonMahasiswa
    }

    %% ==========================================
    %% OBSERVER SUBJECT & STRATEGY CONTEXT
    %% ==========================================
    class KRSManager {
        -List~KRSSubscriber~ subscribers
        +attach(KRSSubscriber subscriber) void
        +detach(KRSSubscriber subscriber) void
        +notifySubscribers(String krsId, String status, String pesan) void
        +submitKRS(String mahasiswaId, String[] daftarMatkul) boolean
        +ajukanRevisiKRS(String mahasiswaId, String[] daftarMatkul) boolean
        +approveKRS(String krsId, String dosenId, boolean disetujui) boolean
    }

    class KRSValidator {
        -List~ValidationRule~ rules
        +tambahRule(ValidationRule rule) void
        +hapusRule(ValidationRule rule) void
        +validateAll(String mahasiswaId, String[] daftarMatkul) boolean
        +getErrors() List
    }

    %% ==========================================
    %% INHERITANCE & IMPLEMENTATIONS
    %% ==========================================
    User <|-- Mahasiswa
    User <|-- Dosen
    User <|-- Admin
    User <|-- CalonMahasiswa

    KRSSubscriber <|.. Mahasiswa
    KRSSubscriber <|.. Dosen
    KRSSubscriber <|.. Admin

    ValidationRule <|.. CekPrasyaratRule
    ValidationRule <|.. CekBatasSKSRule
    ValidationRule <|.. CekJadwalBentrokRule

    %% ==========================================
    %% ASSOCIATIONS & DEPENDENCIES
    %% ==========================================
    Mahasiswa "1" *-- "0..*" Enrollment : memiliki
    Enrollment "1" *-- "0..1" Grade : memiliki
    Mahasiswa "1" *-- "0..*" Payment : memiliki
    Course "1" *-- "0..*" Schedule : memiliki
    Course "1" --> "0..*" Enrollment : didaftarkan
    Schedule "1" --> "0..*" Enrollment : diikuti
    Dosen "1" --> "0..*" Schedule : mengajar
    Course "0..*" --> "0..*" Course : prasyarat
    CalonMahasiswa "1" --> "0..1" Mahasiswa : diterimaSebagai

    UserFactory ..> Mahasiswa : instantiates (wajib NIM)
    UserFactory ..> Dosen : instantiates
    UserFactory ..> Admin : instantiates
    UserFactory ..> CalonMahasiswa : instantiates

    KRSManager o--> KRSSubscriber : mengumumkan status
    KRSManager --> KRSValidator : delegasi validasi
    KRSValidator o--> ValidationRule : mengagregasi aturan (Strategy)
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
- **[ADR-002: Memecah Arsitektur Menjadi Modular Service Layer Berbasis Modul Domain](file:///home/zainun/git/istn/sevima-mini/documents/ADR-002.pdf):** Menjelaskan eliminasi *God Object* pada `Admin` dan dekomposisi logika sistem ke dalam 7 domain service independen.
- **[ADR-003: Standardisasi Penanganan Validasi Klien (HTTP 400 vs 422) dan Integritas Relasional Modul PMB](file:///home/zainun/git/istn/sevima-mini/documents/ADR-003.pdf):** Menjelaskan adopsi Opsi A (override `RequestValidationError` ke HTTP 400 disertai sinkronisasi Swagger UI), penegakan foreign key SQLite, urutan aman rollback Alembic, dan prinsip *Privacy by Design*.

---

## 🤖 Catatan Transparansi Penggunaan AI

Seluruh interaksi bersama AI (Gemini 3.8 Flash) dicatat secara transparan pada [logs/ai-usage-log.md](file:///home/zainun/git/istn/sevima-mini/logs/ai-usage-log.md) dengan menerapkan siklus refleksi **OPAR (Observe - Plan - Act - Reflect)** untuk setiap iterasi prompt (Minggu 1 hingga Minggu 4).

---

## 🔗 Tautan Dokumen & Berkas Cepat

- [README Perbaikan & Screenshot Evolusi](file:///home/zainun/git/istn/sevima-mini/perbaikan/README.md)
- [Dokumentasi Minggu 4: Generator NIM, Konkurensi Database & Pytest PMB](file:///home/zainun/git/istn/sevima-mini/perbaikan/minggu-04/README.md)
- [Spesifikasi Class Diagram Lengkap](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.md)
- [Source Code Mermaid Class Diagram](file:///home/zainun/git/istn/sevima-mini/diagram/class-diagram.mmd)
- [Dokumen Keputusan Arsitektur ADR-001 (PDF)](file:///home/zainun/git/istn/sevima-mini/documents/ADR-001.pdf)
- [Dokumen Keputusan Arsitektur ADR-002 (PDF)](file:///home/zainun/git/istn/sevima-mini/documents/ADR-002.pdf)
- [Dokumen Keputusan Arsitektur ADR-003 (PDF)](file:///home/zainun/git/istn/sevima-mini/documents/ADR-003.pdf)
- [Log Penggunaan AI (OPAR)](file:///home/zainun/git/istn/sevima-mini/logs/ai-usage-log.md)
