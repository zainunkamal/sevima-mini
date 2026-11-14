# Sequence Diagram - Validasi KRS (Versi 1)

Diagram sequence UML berbasis Mermaid untuk alur proses **Validasi Kartu Rencana Studi (KRS)** pada sistem informasi akademik kampus kecil **SEVIMA Mini**.

---

## 📌 Bukti Visual Diagram (Versi 1)

![Sequence Diagram Validasi KRS - Versi 1](../perbaikan/minggu-02/sequence_diagram_versi_1.png)

---

## 🛠️ Kode Sumber Mermaid

Kode sumber tersimpan di [krs-sequence-diagram.mmd](krs-sequence-diagram.mmd):

```mermaid
sequenceDiagram
    autonumber
    actor Mahasiswa
    participant KRSManager
    participant KRSValidator
    participant Repository
    participant NotificationService
    actor DosenPA

    Mahasiswa ->>+ KRSManager: submitKRS(mahasiswaId, daftarMatkul)
    KRSManager ->>+ KRSValidator: validateKRS(mahasiswaId, daftarMatkul)
    Note over KRSValidator: Inisialisasi koleksi penampung error (listError = [])

    %% 1. Pengecekan Prasyarat Mata Kuliah (Loop)
    loop Untuk setiap mata kuliah dalam daftarMatkul
        KRSValidator ->>+ Repository: getPrasyarat(kodeMK)
        Repository -->>- KRSValidator: daftarPrasyarat
        KRSValidator ->>+ Repository: getRiwayatLulus(mahasiswaId)
        Repository -->>- KRSValidator: riwayatLulus
        opt Prasyarat belum terpenuhi
            KRSValidator ->> KRSValidator: catatError("Prasyarat " + namaMK + " kurang: " + prasyaratKurang)
        end
    end

    %% 2. Penghitungan Total SKS (Self Call)
    KRSValidator ->>+ KRSValidator: hitungTotalSKS(daftarMatkul)
    KRSValidator -->>- KRSValidator: totalSKS
    opt totalSKS > 24
        KRSValidator ->> KRSValidator: catatError("SKS Anda " + totalSKS + ", batas 24")
    end

    %% 3. Pengecekan Jadwal Bentrok
    KRSValidator ->>+ Repository: getJadwalKuliah(daftarMatkul)
    Repository -->>- KRSValidator: daftarJadwal
    KRSValidator ->>+ KRSValidator: cekBentrokJadwal(daftarJadwal)
    KRSValidator -->>- KRSValidator: daftarBentrok
    opt Terdapat jadwal bertabrakan
        KRSValidator ->> KRSValidator: catatError("Jadwal bentrok: " + matkulA + " dan " + matkulB + " bertabrakan")
    end

    KRSValidator -->>- KRSManager: validationResult(isValid, listError)

    %% Alternate Flow: Evaluasi Hasil Validasi (Kumpulkan Semua Error Sekaligus)
    alt isValid == true (Validasi Berhasil - Tanpa Error)
        KRSManager ->>+ Repository: saveKRS(krsId, "pending approval")
        Repository -->>- KRSManager: status OK
        
        KRSManager -) NotificationService: kirimNotifikasiAsync(dosenId, krsId)
        Note over KRSManager,NotificationService: Pemanggilan asinkron (fire-and-forget)
        NotificationService -) DosenPA: notifikasiKRSMasuk(krsId, mahasiswaId)
        
        KRSManager -->>- Mahasiswa: responseSukses("KRS berhasil diajukan dengan status pending approval")
    else isValid == false (Validasi Gagal - Mengembalikan SEMUA Error)
        KRSManager -->> Mahasiswa: responseError("Pengajuan KRS ditolak:\n- Prasyarat Algoritma Lanjut kurang: Struktur Data\n- SKS Anda 26, batas 24\n- Jadwal bentrok: Basis Data II dan Jaringan Komputer bertabrakan")
    end
```

---

## 🏛️ Partisipan & Batas Peran (*Roles & Responsibilities*)

| Partisipan | Peran Arsitektural | Tanggung Jawab Utama |
| :--- | :--- | :--- |
| **`Mahasiswa`** | *Actor (Initiator)* | Menginisiasi pengajuan rencana studi dengan mengirim daftar mata kuliah pilihan. |
| **`KRSManager`** | *Application Controller / Service Facade* | Mengorkestrasikan alur pengajuan, mendelegasikan validasi, menyimpan data, dan memicu notifikasi. |
| **`KRSValidator`** | *Domain Service (Business Rules)* | Menjalankan logika validasi komprehensif (prasyarat, batas 24 SKS, jadwal bentrok) dan menampung semua error (*error accumulator*). |
| **`Repository`** | *Persistence Layer (Data Access)* | Menyediakan query prasyarat matkul, riwayat kelulusan mahasiswa, jadwal kuliah, serta penyimpanan status KRS. |
| **`NotificationService`** | *Infrastructure / Integration Service* | Menangani pengiriman notifikasi antar-aktor secara non-blocking (*asynchronous*). |
| **`DosenPA`** | *Actor (Recipient / Approver)* | Menerima pemberitahuan pengajuan KRS mahasiswa bimbingan untuk ditinjau (*pending approval*). |

---

## 🔍 Detail Alur & Logika Validasi

1. **Pengumpulan Semua Error (*Error Accumulator Pattern*):**
   - Validasi tidak langsung berhenti (*fail-fast*) pada error pertama, melainkan mengevaluasi seluruh aturan dan mengumpulkan semua pesan kesalahan dalam satu koleksi (`listError`).
   - Dengan pendekatan ini, mahasiswa mendapatkan umpan balik komprehensif dalam satu kali pengajuan.

2. **Tiga Lapisan Validasi Mandatori:**
   - **Cek Prasyarat (Fragmen `loop`):** Melakukan iterasi terhadap setiap mata kuliah yang dipilih dan mencocokkan prasyaratnya dengan riwayat mata kuliah yang telah lulus di `Repository`.
   - **Batas Beban SKS (Fragmen `opt` via *Self Call*):** Menghitung total akumulasi SKS semester berjalan. Jika melebihi batas maksimal 24 SKS, mencatat error dengan rincian total dan batasnya (mis. *"SKS Anda 26, batas 24"*).
   - **Cek Bentrok Jadwal (Fragmen `opt`):** Memeriksa tumpang tindih waktu (hari, jam mulai, jam selesai) antar alokasi kelas yang dipilih.

3. **Notifikasi Asinkron (`-)`):**
   - Menggunakan pemanggilan asinkron (*fire-and-forget*) dari `KRSManager` ke `NotificationService` agar *response time* pengajuan KRS mahasiswa tidak terhambat oleh proses pengiriman pesan ke Dosen PA.
