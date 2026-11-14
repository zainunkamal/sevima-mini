# Sequence Diagram - Pendaftaran Mahasiswa Baru / PMB (Versi 1)

Diagram sequence UML berbasis Mermaid untuk alur proses **Penerimaan Mahasiswa Baru (PMB)** pada sistem informasi akademik kampus kecil **SEVIMA Mini**.

---

## 📌 Bukti Visual Diagram (Versi 1)

![Sequence Diagram PMB - Versi 1](../perbaikan/minggu-02/pmb_sequence_diagram_versi_1.png)

---

## 🛠️ Kode Sumber Mermaid

Kode sumber tersimpan di [pmb-sequence-diagram.mmd](pmb-sequence-diagram.mmd):

```mermaid
sequenceDiagram
    autonumber
    actor CalonMahasiswa
    participant PMBService
    participant Database
    actor Admin
    participant UserFactory
    participant NotificationService

    %% 1. Pendaftaran oleh Calon Mahasiswa
    CalonMahasiswa ->>+ PMBService: daftar(dataDiri, dokumenBerkas)
    PMBService ->>+ Database: simpanPendaftaran(calonMhs)
    Database -->>- PMBService: noPendaftaran
    PMBService -->>- CalonMahasiswa: konfirmasiPendaftaran(noPendaftaran)

    %% 2. Verifikasi Berkas oleh Admin
    Admin ->>+ PMBService: verifikasiBerkas(noPendaftaran)
    PMBService ->>+ Database: getBerkasPendaftaran(noPendaftaran)
    Database -->>- PMBService: dataBerkas
    PMBService -->>- Admin: tampilkanBerkas(dataBerkas)

    %% 3. Alternate Flow: Evaluasi Kelengkapan Berkas
    alt Berkas Lengkap & Dinyatakan Lulus
        Admin ->>+ PMBService: nyatakanLulus(noPendaftaran, prodi)
        
        %% Pembuatan Mahasiswa & Akun via UserFactory
        PMBService ->>+ UserFactory: createMahasiswa(noPendaftaran, prodi)
        UserFactory ->> UserFactory: generateNIM(prodi, tahunMasuk)
        UserFactory ->> UserFactory: createAkunUser(username, defaultPassword)
        UserFactory -->>- PMBService: mahasiswaBaru(nim, akun)

        %% Simpan data Mahasiswa ke Database
        PMBService ->>+ Database: simpanMahasiswaBaru(mahasiswaBaru)
        Database -->>- PMBService: status OK
        PMBService -->>- Admin: konfirmasiKelulusan("Calon mahasiswa resmi terdaftar dengan NIM: " + nim)

        %% Notifikasi Asinkron (Non-Blocking / Fire-and-Forget)
        PMBService -) NotificationService: kirimNotifikasiAkunAsync(email, nim, credentials)
        Note over PMBService,NotificationService: Pemanggilan asinkron: proses registrasi selesai tanpa menunggu antrean email

        %% 4. Alternate Flow: Penanganan Pengiriman Email Akun
        alt Email Berhasil Terkirim
            NotificationService ->> CalonMahasiswa: kirimEmail("Akun Mahasiswa Baru", nim, credentials)
        else Email Gagal Terkirim (Retry & Log - Tidak Membatalkan Pendaftaran)
            NotificationService ->> NotificationService: retryKirimEmail(attempt: 1..3)
            opt Tetap Gagal Setelah Batas Percobaan
                NotificationService ->>+ Database: logError("Email gagal terkirim ke " + email, nim)
                Database -->>- NotificationService: status OK
                Note over NotificationService,Database: Pendaftaran TETAP SAH. Email disimpan di DLQ (Dead Letter Queue) untuk dikirim ulang oleh worker.
            end
        end

    else Berkas Tidak Lengkap / Ditolak
        Admin ->>+ PMBService: tolakBerkas(noPendaftaran, alasan: "Ijazah belum dilegalisir")
        PMBService ->>+ Database: updateStatus(noPendaftaran, "berkas_tidak_lengkap")
        Database -->>- PMBService: status OK
        
        PMBService -) NotificationService: kirimNotifikasiRevisiAsync(email, alasan)
        NotificationService -) CalonMahasiswa: kirimEmail("Perbaikan Berkas PMB", alasan)
        PMBService -->>- Admin: konfirmasi("Status pendaftaran diperbarui: Perlu Perbaikan Berkas")
    end
```

---

## 🏛️ Partisipan & Batas Peran (*Roles & Responsibilities*)

| Partisipan | Peran Arsitektural | Tanggung Jawab Utama |
| :--- | :--- | :--- |
| **`CalonMahasiswa`** | *Actor (Initiator)* | Mengisi data diri, mengunggah berkas seleksi PMB, dan menerima nomor pendaftaran serta kredensial akun. |
| **`PMBService`** | *Application Service / Domain Facade* | Mengorkestrasikan alur pendaftaran, delegasi verifikasi berkas, pembuatan mahasiswa via factory, dan pemicu notifikasi. |
| **`Database`** | *Persistence Layer* | Menyimpan entitas pendaftaran, berkas calon mahasiswa, mutasi status, data entitas `Mahasiswa`, serta error log. |
| **`Admin`** | *Actor (Verifier & Decision Maker)* | Memeriksa validitas dokumen pendaftaran dan memutuskan kelulusan calon mahasiswa. |
| **`UserFactory`** | *Creational Pattern (GoF Factory)* | Mengenkapsulasi logika kompleks instansiasi objek `Mahasiswa`, kalkulasi format `NIM`, serta pembuatan kredensial awal akun `User`. |
| **`NotificationService`** | *Infrastructure Service* | Mengirimkan email notifikasi konfirmasi kelulusan dan kredensial akun secara asinkron dan andal (*resilient*). |

---

## 🔍 Detail Alur & Penanganan Alternate Flow

1. **Pemisahan Siklus Hidup Pendaftaran dan Penerimaan:**
   - Calon mahasiswa mendaftar dan segera memperoleh `nomor pendaftaran` sebagai tanda bukti registrasi awal.
   - Verifikasi dokumen dilakukan secara independen oleh `Admin`.

2. **Peran `UserFactory` (Pola Kreasi Berorientasi Objek):**
   - Transisi siklus hidup dari `CalonMahasiswa` menjadi `Mahasiswa` didelegasikan ke `UserFactory` untuk menjamin kepatuhan *Single Responsibility Principle* (SRP). `UserFactory` bertanggung jawab menghasilkan NIM unik berbasis tahun masuk dan kode program studi, serta akun autentikasi terenkapsulasi.

3. **Ketahanan Notifikasi Asinkron (*Resilient Notification Pattern*):**
   - Pemanggilan `NotificationService` dilakukan secara asinkron (`-)`), sehingga `PMBService` tidak terblokir oleh latensi protokol SMTP/Mail Gateway.
   - **Alternate Flow Kegagalan Email:** Jika transmisi email gagal, `NotificationService` melakukan mekanisme *retry* terencana (hingga 3 kali). Apabila tetap gagal, kegagalan dicatat ke tabel log error `Database` tanpa membatalkan transaksi pembuatan mahasiswa (*non-blocking failure isolation*). Mahasiswa tetap sah terdaftar dalam sistem akademik.

4. **Alternate Flow Berkas Tidak Lengkap:**
   - Admin memasukkan alasan spesifik (mis. *"Ijazah belum dilegalisir"*), sistem memperbarui status di `Database`, dan memicu notifikasi revisi ke calon mahasiswa untuk mengunggah ulang dokumen yang kurang.
