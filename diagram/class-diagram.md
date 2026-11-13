# Class Diagram UML - SEVIMA Mini (Versi 4: Perbaikan Arsitektur Kritis 1-4)

Diagram kelas UML untuk sistem informasi akademik kampus kecil **SEVIMA Mini** yang telah disempurnakan berdasarkan hasil kritik arsitektural terhadap kelemahan kritis 1 hingga 4.

```mermaid
classDiagram
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
        +hitungIPK() double
        +hitungTotalSKS(int semester) int
        +validasiBebanKRS(int semester) boolean
        +cekDuplikasiCourse(String kodeCourse, int semester) boolean
        +tambahEnrollment(Enrollment enrollment) boolean
        +getDaftarMatkulLulus() String[]
        +lihatKHS(int semester) void
    }

    class Dosen {
        -String nidn
        +getNidn() String
        +inputNilai(Enrollment enrollment, float nilaiAngka) void
        +lihatJadwalMengajar() void
        +verifikasiKRS(Enrollment enrollment) void
    }

    class Admin {
        -String staffId
        +getStaffId() String
        +kelolaJadwal(Schedule jadwal) void
        +verifikasiPMB(CalonMahasiswa calon) void
        +validasiPembayaran(Payment payment) void
        +kelolaAkunUser(User user) void
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
        +tambahPrasyarat(Course course) void
        +cekPrasyarat(String[] kodeMatkulLulus) boolean
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
        +ajukanKRS() void
        +batalkanKRS() void
        +cekBentrokJadwal(Enrollment other) boolean
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
        +cekBentrok(Schedule other) boolean
    }

    class Grade {
        -float nilaiAngka
        -String nilaiHuruf
        +getNilaiAngka() float
        +getNilaiHuruf() String
        +hitungNilaiHuruf() String
        +updateNilai(float nilaiAngka) void
    }

    class Payment {
        -int semester
        -double jumlah
        -String tanggalBayar
        -String status
        +getSemester() int
        +getJumlah() double
        +getTanggalBayar() String
        +getStatus() String
        +prosesPembayaran() void
        +cekStatusSPP() boolean
    }

    User <|-- Mahasiswa
    User <|-- Dosen
    User <|-- Admin
    User <|-- CalonMahasiswa

    Mahasiswa "1" *-- "0..*" Enrollment : memiliki
    Enrollment "1" *-- "0..1" Grade : memiliki
    Mahasiswa "1" *-- "0..*" Payment : memiliki
    Course "1" *-- "0..*" Schedule : memiliki
    Course "1" --> "0..*" Enrollment : didaftarkan
    Schedule "1" --> "0..*" Enrollment : diikuti
    Dosen "1" --> "0..*" Schedule : mengajar
    Course "0..*" --> "0..*" Course : prasyarat
    CalonMahasiswa "1" --> "0..1" Mahasiswa : diterimaSebagai
```

## Spesifikasi Solusi Perbaikan Arsitektur (Versi 4)

### 1. Solusi Masalah 1: Integrasi Jadwal Riil (`Schedule`, `Enrollment`, `Dosen`)
- **`Schedule "1" --> "0..*" Enrollment : diikuti`**: `Enrollment` (KRS) kini terhubung langsung ke sesi alokasi `Schedule`. Mahasiswa mengetahui ruang dan jam perkuliahan secara pasti, dan `Enrollment.cekBentrokJadwal(other)` dapat dijalankan dengan akurat.
- **`Dosen "1" --> "0..*" Schedule : mengajar`**: Dosen terhubung langsung ke sesi jadwal, sehingga fungsionalitas `Dosen.lihatJadwalMengajar()` memiliki sumber data yang valid untuk ruang dan waktu mengajar.

### 2. Solusi Masalah 2: Penanganan Transisi Siklus Hidup `CalonMahasiswa` $\rightarrow$ `Mahasiswa`
- **Method `konversiKeMahasiswa(String nimBaru, String prodi): Mahasiswa`**: Mengakomodasi mutasi peran calon mahasiswa yang diterima menjadi mahasiswa resmi tanpa merusak identitas akun atau membuat kelas di luar requirement.
- **Relasi Asosiasi `CalonMahasiswa "1" --> "0..1" Mahasiswa : diterimaSebagai`**: Menghubungkan riwayat pendaftaran PMB dengan entitas mahasiswa yang terdaftar.

### 3. Solusi Masalah 3: Pemutusan Ketergantungan Siklik (*Circular Dependency*)
- **`Course.cekPrasyarat(String[] kodeMatkulLulus)`**: Menggantikan parameter `Mahasiswa` dengan array kode mata kuliah lulus (`String[]`).
- `Course` kini sepenuhnya terisolasi dan mandiri (tidak lagi bergantung pada representasi data kelas `Mahasiswa`).

### 4. Solusi Masalah 4: Klarifikasi Tanggung Jawab Dokumen KRS & SKS
- **Delegasi SKS pada `Enrollment` (`+getSks(): int`)**: Memungkinkan penghitungan SKS langsung dari asosiasi mata kuliah.
- **Pengaturan Tanggung Jawab Semesteran pada `Mahasiswa`**: Menambahkan parameter semester pada `hitungTotalSKS(semester)`, `validasiBebanKRS(semester)` (maks 24 SKS), dan `cekDuplikasiCourse(kodeCourse, semester)`.
