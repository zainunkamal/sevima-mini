# Class Diagram UML - SEVIMA Mini

Diagram kelas UML untuk sistem informasi akademik kampus kecil **SEVIMA Mini** yang mencakup modul PMB, KRS, Jadwal, Nilai, dan Pembayaran SPP.

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
        +hitungTotalSKS() int
        +validasiMaksimalSKS(int sksTambahan) boolean
        +cekPendaftaranGanda(String kodeCourse) boolean
        +tambahEnrollment(Enrollment enrollment) boolean
        +lihatKHS() void
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
    }

    class Course {
        -String kode
        -String nama
        -int sks
        +getKode() String
        +getNama() String
        +getSks() int
        +tambahPrasyarat(Course course) void
        +cekPrasyarat(Mahasiswa mhs) boolean
    }

    class Enrollment {
        -int semester
        -String tahunAkademik
        -String status
        +getSemester() int
        +getTahunAkademik() String
        +getStatus() String
        +setStatus(String status) void
        +ajukanKRS() void
        +batalkanKRS() void
        +validasiAturanKRS() boolean
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
    Course "1" o-- "0..*" Enrollment : didaftarkan
    Enrollment "1" *-- "0..1" Grade : memiliki
    Mahasiswa "1" *-- "0..*" Payment : memiliki
    Course "1" *-- "1..*" Schedule : memiliki
    Course "0..*" o-- "0..*" Course : prasyarat
    Dosen "1" o-- "0..*" Course : mengampu
```

## Spesifikasi & Desain OOP

### 1. Prinsip SOLID & Enkapsulasi
- **Single Responsibility Principle (SRP):** Setiap kelas memiliki tanggung jawab tunggal dengan jumlah method $\le 9$ (tidak ada kelas $> 10$ method).
- **Enkapsulasi:** Seluruh atribut ber-visibility private (`-`) dengan tipe data eksplisit, dan diakses secara terkontrol melalui method public (`+`).
- **Penempatan `hitungIPK()`:** Ditempatkan khusus pada kelas `Mahasiswa` (bukan di `User`).

### 2. Hubungan Antar Kelas & Kardinalitas
- **Inheritance (`<|--`):** `User` sebagai abstract class diturunkan ke `Mahasiswa`, `Dosen`, `Admin`, dan `CalonMahasiswa`.
- **Composition (`*--`) Relasi Kuat:**
  - `Mahasiswa "1" *-- "0..*"` `Enrollment`: Riwayat enrollment terikat kuat pada siklus hidup data mahasiswa.
  - `Enrollment "1" *-- "0..1"` `Grade`: Nilai tidak dapat berdiri sendiri tanpa enrollment.
  - `Mahasiswa "1" *-- "0..*"` `Payment`: Catatan tagihan SPP terikat pada mahasiswa.
  - `Course "1" *-- "1..*"` `Schedule`: Jadwal perkuliahan terikat pada penawaran mata kuliah.
- **Aggregation (`o--`) Relasi Lemah:**
  - `Course "0..*" o-- "0..*"` `Course`: Relasi mata kuliah prasyarat (independent lifecycle).
  - `Course "1" o-- "0..*"` `Enrollment`: Mata kuliah di katalog bersifat independen dari pendaftaran mahasiswa.
  - `Dosen "1" o-- "0..*"` `Course`: Dosen pengampu mengajar mata kuliah.
- **Many-to-Many Resolution:** Relasi many-to-many antara `Mahasiswa` dan `Course` dipecah melalui kelas perantara `Enrollment`.

### 3. Aturan Bisnis
- **Maksimal 24 SKS:** Diimplementasikan melalui method `validasiMaksimalSKS(int sksTambahan)` pada `Mahasiswa` dan `validasiAturanKRS()` pada `Enrollment`.
- **Pencegahan Pendaftaran Ganda:** Diimplementasikan melalui method `cekPendaftaranGanda(String kodeCourse)` pada `Mahasiswa`.
