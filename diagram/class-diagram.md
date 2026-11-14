# Class Diagram UML - SEVIMA Mini (Versi 5: Integrasi Arsitektur Berlapis)

Diagram kelas UML untuk sistem informasi akademik kampus kecil **SEVIMA Mini** yang telah disempurnakan berdasarkan temuan sinkronisasi pemodelan dinamis (Opsi A: Integrasi Layered Architecture, Application Service, Factory, Data Access, dan Infrastructure).

---

## 🛠️ Kode Sumber Mermaid (Versi 5)

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
        +terimaNotifikasi(String pesan) void
    }

    class Dosen {
        -String nidn
        +getNidn() String
        +inputNilai(Enrollment enrollment, float nilaiAngka) void
        +lihatJadwalMengajar() void
        +verifikasiKRS(Enrollment enrollment) void
        +terimaNotifikasi(String pesan) void
    }

    class Admin {
        -String staffId
        +getStaffId() String
        +kelolaJadwal(Schedule jadwal) void
        +verifikasiPMB(CalonMahasiswa calon) void
        +validasiPembayaran(Payment payment) void
        +kelolaAkunUser(User user) void
        +cetakTranskripResmi(Object recordAkademik) void
    }

    class CalonMahasiswa {
        -String nomorPendaftaran
        -String statusSeleksi
        +getNomorPendaftaran() String
        +getStatusSeleksi() String
        +daftarSeleksi() void
        +lihatPengumuman() String
        +konversiKeMahasiswa(String nimBaru, String prodi) Mahasiswa
        +terimaNotifikasi(String subjek, String pesan) void
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
        +setStatus(String status) void
        +prosesPembayaran(int semester, double jumlah) void
        +hitungDendaKeterlambatan(int hariTerlambat) double
        +cekStatusSPP() boolean
    }

    class KRSManager {
        +submitKRS(String mahasiswaId, String[] daftarMatkul) boolean
        +ajukanRevisiKRS(String mahasiswaId, String[] daftarMatkul) boolean
        +approveKRS(String krsId, String dosenId, boolean disetujui) boolean
        +getDaftarKRSBimbingan(String dosenId) List
    }

    class KRSValidator {
        +validateKRS(String mahasiswaId, String[] daftarMatkul) boolean
        +hitungTotalSKS(String[] daftarMatkul) int
        +cekBentrokJadwal(Schedule[] daftarJadwal) boolean
    }

    class PMBService {
        +daftar(String dataDiri, Object dokumenBerkas) String
        +verifikasiBerkas(String noPendaftaran) Object
        +nyatakanLulus(String noPendaftaran, String prodi) boolean
        +tolakBerkas(String noPendaftaran, String alasan) boolean
    }

    class UserFactory {
        +createMahasiswa(String noPendaftaran, String prodi) Mahasiswa
        +generateNIM(String prodi, int tahunMasuk) String
        +createAkunUser(String username, String defaultPassword) User
    }

    class Repository {
        +getPrasyarat(String kodeMK) String[]
        +getRiwayatLulus(String mahasiswaId) String[]
        +getJadwalKuliah(String[] daftarMatkul) Schedule[]
        +saveKRS(String krsId, String status) boolean
        +simpanPendaftaran(CalonMahasiswa calon) String
        +getBerkasPendaftaran(String noPendaftaran) Object
        +simpanMahasiswaBaru(Mahasiswa mhs) boolean
        +updateStatusPMB(String noPendaftaran, String status) boolean
        +getTagihanSPP(String mahasiswaId, int semester) Payment
        +simpanGrade(String enrollmentId, Grade grade) boolean
        +logError(String pesan, String id) void
    }

    class NotificationService {
        +kirimNotifikasiAsync(String penerimaId, String pesan) void
        +kirimEmail(String email, String subjek, String pesan) boolean
        +retryKirimEmail(String email, String subjek, String pesan, int attempt) boolean
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

    KRSManager --> KRSValidator : delegasi validasi
    KRSManager --> Repository : persistensi
    KRSManager --> NotificationService : memicu notifikasi
    KRSValidator --> Repository : query aturan
    PMBService --> UserFactory : delegasi pembuatan
    PMBService --> Repository : persistensi
    PMBService --> NotificationService : memicu notifikasi
    UserFactory ..> Mahasiswa : instansiasi
    Admin --> PMBService : mengelola kelulusan
    Mahasiswa ..> KRSManager : mengirim permohonan
    Dosen ..> KRSManager : menyetujui
```

---

## 🏛️ Spesifikasi Komponen Layered Architecture (Opsi A)

1. **Application Service / Controller Layer (`KRSManager`, `PMBService`):**
   - Bertindak sebagai orkestrator transaksi use case antara antarmuka pengguna (aktor) dan model domain.
   - Mengisolasi kompleksitas transaksi pengajuan KRS dan alur seleksi berkas PMB.
2. **Domain Service Layer (`KRSValidator`):**
   - Menjalankan logika validasi lintas entitas (prasyarat kelulusan, batasan 24 SKS, pencegahan tabrakan jam kuliah).
   - Mengumpulkan seluruh catatan kegagalan aturan (*Error Accumulator Pattern*).
3. **Creational Factory Layer (`UserFactory`):**
   - Mengenkapsulasi instansiasi objek `Mahasiswa`, kalkulasi algoritma format `NIM`, serta pembuatan akun `User` baru secara aman.
4. **Data Access / Persistence Layer (`Repository`):**
   - Mengabstraksikan penyimpanan dan pengambilan entitas `Enrollment`, `Course`, `Grade`, `Payment`, dan `CalonMahasiswa`.
5. **Infrastructure Layer (`NotificationService`):**
   - Menangani pengiriman email dan notifikasi push antarmuka secara asinkron (*non-blocking fire-and-forget*).
