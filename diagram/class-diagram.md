# Class Diagram UML - SEVIMA Mini (Versi 3: Refactor Relasi)

Diagram kelas UML untuk sistem informasi akademik kampus kecil **SEVIMA Mini** yang mencakup modul PMB, KRS, Jadwal, Nilai, dan Pembayaran SPP setelah dilakukan evaluasi uji wadah (*lifecycle dependency*) dan uji *is-a*.

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
    Enrollment "1" *-- "0..1" Grade : memiliki
    Mahasiswa "1" *-- "0..*" Payment : memiliki
    Course "1" *-- "0..*" Schedule : memiliki
    Course "1" --> "0..*" Enrollment : didaftarkan
    Course "0..*" --> "0..*" Course : prasyarat
    Dosen "1" --> "0..*" Course : mengampu
```

## Spesifikasi & Desain OOP (Versi 3)

### 1. Prinsip SOLID & Enkapsulasi
- **Single Responsibility Principle (SRP):** Setiap kelas memiliki tanggung jawab tunggal dengan jumlah method $\le 9$ (tidak ada kelas $> 10$ method).
- **Enkapsulasi:** Seluruh atribut ber-visibility private (`-`) dengan tipe data eksplisit, dan diakses secara terkontrol melalui method public (`+`).
- **Penempatan `hitungIPK()`:** Ditempatkan khusus pada kelas `Mahasiswa` (bukan di `User`).

### 2. Hubungan Antar Kelas & Kardinalitas (Hasil Uji Wadah & Is-A)
- **Inheritance (`<|--`):** `User` sebagai abstract class diturunkan ke `Mahasiswa`, `Dosen`, `Admin`, dan `CalonMahasiswa` (lulus uji *is-a*).
- **Composition (`*--`) Relasi Kuat (Wadah hilang $\rightarrow$ Bagian ikut hilang):**
  - `Mahasiswa "1" *-- "0..*"` `Enrollment`: Riwayat enrollment terikat mutlak pada siklus hidup data mahasiswa.
  - `Enrollment "1" *-- "0..1"` `Grade`: Nilai tidak dapat berdiri sendiri tanpa enrollment.
  - `Mahasiswa "1" *-- "0..*"` `Payment`: Catatan tagihan SPP terikat pada mahasiswa.
  - `Course "1" *-- "0..*"` `Schedule`: Alokasi jadwal perkuliahan terikat pada penawaran mata kuliah (kardinalitas `0..*` mengakomodasi matkul baru di katalog).
- **Association (`-->`) Relasi Referensial/Peran (Bukan Wadah Whole-Part):**
  - `Course "1" --> "0..*"` `Enrollment`: Enrollment merujuk ke Course katalog, Course bukan wadah dari Enrollment.
  - `Course "0..*" --> "0..*"` `Course`: Relasi mata kuliah prasyarat (*self-referencing association* antar entitas setara).
  - `Dosen "1" --> "0..*"` `Course`: Asosiasi peran instruktur mengampu mata kuliah.
