# Sequence Diagram - Pembayaran SPP & Denda (Versi 1)

Diagram sequence UML berbasis Mermaid untuk alur transaksi **Pembayaran SPP dan Penanganan Denda Keterlambatan** pada sistem informasi akademik **SEVIMA Mini**.

---

## 📌 Bukti Visual Diagram

![Sequence Diagram Pembayaran SPP & Denda](../perbaikan/minggu-02/payment_sequence_diagram_versi_1.png)

---

## 🛠️ Kode Sumber Mermaid

Kode sumber tersimpan di [payment-sequence-diagram.mmd](payment-sequence-diagram.mmd):

```mermaid
sequenceDiagram
    autonumber
    actor Mahasiswa
    actor Admin as Admin Akademik
    participant Payment
    participant Repository
    participant NotificationService

    %% 1. Inisiasi Pembayaran SPP
    Mahasiswa ->>+ Repository: getTagihanSPP(mahasiswaId, semester)
    Repository -->>- Mahasiswa: tagihan(jumlahSPP, tanggalJatuhTempo)

    %% 2. Evaluasi Jatuh Tempo (Use Case: Bayar SPP vs Bayar Denda Keterlambatan)
    alt Pembayaran Tepat Waktu (Use Case: Bayar SPP)
        Mahasiswa ->>+ Payment: prosesPembayaran(semester, jumlahSPP)
        Payment ->> Payment: setStatus("lunas")
        Payment -->>- Mahasiswa: buktiBayar(status: "lunas", total: jumlahSPP)

    else Pembayaran Melewati Jatuh Tempo (Extend: Bayar Denda Keterlambatan)
        Mahasiswa ->>+ Payment: prosesPembayaran(semester, jumlahSPP)
        Payment ->> Payment: hitungDendaKeterlambatan(hariTerlambat)
        Note over Payment: Biaya denda keterlambatan ditambahkan otomatis ke tagihan dasar SPP
        Payment ->> Payment: setStatus("lunas_dengan_denda")
        Payment -->>- Mahasiswa: buktiBayar(status: "lunas_dengan_denda", total: jumlahSPP + denda)
    end

    %% 3. Penyimpanan dan Validasi oleh Admin
    Mahasiswa ->>+ Repository: simpanBuktiPembayaran(paymentObj)
    Repository -->>- Mahasiswa: status OK

    Admin ->>+ Repository: getDaftarPembayaran()
    Repository -->>- Admin: listPembayaran
    Admin ->>+ Admin: validasiPembayaran(paymentObj)
    Admin ->>+ Repository: updateStatusVerifikasi(paymentId, "terverifikasi")
    Repository -->>- Admin: status OK
    Admin -) NotificationService: kirimNotifikasiAsync(mahasiswaId, "Pembayaran SPP telah diverifikasi")
    NotificationService -) Mahasiswa: terimaNotifikasi("Status SPP Semester Ini: Terverifikasi Aktif")
```

---

## 🏛️ Cakupan Use Case yang Disinkronkan
- **Use Case `Bayar SPP`**: Mahasiswa membayar biaya perkuliahan sebelum jatuh tempo dan memperoleh bukti pembayaran lunas.
- **Use Case `Bayar Denda Keterlambatan` (Relasi `<<extend>>`)**: Jika pembayaran melewati batas tanggal jatuh tempo, use case diperluas dengan kalkulasi denda penalti keterlambatan yang diakumulasikan ke total tagihan.
- **Validasi Admin**: `Admin Akademik` memvalidasi status pembayaran agar mahasiswa memenuhi syarat administrasi untuk perwalian/KRS.
