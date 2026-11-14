# Sequence Diagram - Persetujuan & Revisi KRS (Versi 1)

Diagram sequence UML berbasis Mermaid untuk alur proses **Persetujuan (Approve) & Pengajuan Revisi Kartu Rencana Studi (KRS)** oleh Dosen Pembimbing Akademik (PA) dan Mahasiswa pada sistem informasi akademik **SEVIMA Mini**.

---

## 📌 Bukti Visual Diagram

![Sequence Diagram Persetujuan & Revisi KRS](../perbaikan/minggu-02/krs_approval_sequence_diagram_versi_1.png)

---

## 🛠️ Kode Sumber Mermaid

Kode sumber tersimpan di [krs-approval-sequence-diagram.mmd](krs-approval-sequence-diagram.mmd):

```mermaid
sequenceDiagram
    autonumber
    actor Dosen as Dosen (PA)
    actor Mahasiswa
    participant KRSManager
    participant KRSValidator
    participant Repository
    participant NotificationService

    %% 1. Dosen PA Meninjau Pengajuan KRS
    Dosen ->>+ KRSManager: getDaftarKRSBimbingan(dosenId)
    KRSManager ->>+ Repository: getPendingKRS(dosenId)
    Repository -->>- KRSManager: listPendingKRS
    KRSManager -->>- Dosen: tampilkanKRS(listPendingKRS)

    %% 2. Keputusan Persetujuan / Revisi KRS
    alt KRS Disetujui (Use Case: Approve KRS)
        Dosen ->>+ KRSManager: approveKRS(krsId, dosenId, true)
        KRSManager ->>+ Repository: saveKRS(krsId, "disetujui")
        Repository -->>- KRSManager: status OK
        KRSManager -) NotificationService: kirimNotifikasiAsync(mahasiswaId, "KRS Anda telah disetujui")
        NotificationService -) Mahasiswa: terimaNotifikasi("KRS Disetujui Dosen PA")
        KRSManager -->>- Dosen: konfirmasi("KRS berhasil disetujui")

    else KRS Memerlukan Perbaikan (Use Case: Ajukan Revisi KRS)
        Dosen ->>+ KRSManager: approveKRS(krsId, dosenId, false)
        KRSManager ->>+ Repository: saveKRS(krsId, "ditolak_perlu_revisi")
        Repository -->>- KRSManager: status OK
        KRSManager -) NotificationService: kirimNotifikasiAsync(mahasiswaId, "KRS ditolak: Perlu revisi")
        NotificationService -) Mahasiswa: terimaNotifikasi("Catatan Dosen PA: Ganti kelas bentrok")
        KRSManager -->>- Dosen: konfirmasi("Catatan revisi telah dikirim ke Mahasiswa")

        %% Mahasiswa Melakukan Pengajuan Revisi
        Mahasiswa ->>+ KRSManager: ajukanRevisiKRS(mahasiswaId, daftarMatkulBaru)
        KRSManager ->>+ KRSValidator: validateKRS(mahasiswaId, daftarMatkulBaru)
        KRSValidator -->>- KRSManager: validationResult(isValid, errors)
        
        alt Revisi Valid
            KRSManager ->>+ Repository: saveKRS(krsId, "pending approval")
            Repository -->>- KRSManager: status OK
            KRSManager -) NotificationService: kirimNotifikasiAsync(dosenId, "Mahasiswa telah mengajukan revisi KRS")
            NotificationService -) Dosen: terimaNotifikasi("Revisi KRS Masuk dari Mahasiswa")
            KRSManager -->>- Mahasiswa: responseSukses("Revisi KRS berhasil diajukan, menunggu persetujuan ulang")
        else Revisi Masih Invalid
            KRSManager -->> Mahasiswa: responseError("Revisi gagal, periksa aturan beban SKS dan jadwal")
        end
    end
```

---

## 🏛️ Cakupan Use Case yang Disinkronkan
- **Use Case `Approve KRS`**: Dosen PA memvalidasi rencana studi mahasiswa bimbingan, mengubah status KRS menjadi disetujui, dan memicu notifikasi asinkron ke mahasiswa.
- **Use Case `Ajukan Revisi KRS`**: Dosen PA memberikan catatan revisi jika terdapat ketidaksesuaian rencana studi. Mahasiswa mengajukan perubahan mata kuliah (`ajukanRevisiKRS`), sistem memvalidasi ulang melalui `KRSValidator`, dan mengirimkan kembali status `pending approval` ke Dosen PA.
