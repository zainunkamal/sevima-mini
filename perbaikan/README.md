# Bukti Perbandingan Diagram (Sebelum vs Sesudah Perbaikan)

Dokumen ini memuat screenshot bukti visual class diagram UML **SEVIMA Mini** sebelum dan sesudah dilakukannya perbaikan spesifikasi OOP.

---

## 1. Diagram Sebelum Dirubah (Versi Awal)
![Diagram Sebelum Dirubah](diagram_sebelum_dirubah.png)

### Karakteristik Versi Awal:
- **Visibility Atribut `User`:** Menggunakan `protected (#)` untuk `id`, `username`, dan `email`.
- **Method `User`:** Hanya memiliki `+login()` dan `+logout()`, belum memiliki accessor public (`getId()`, `getUsername()`, `getEmail()`, `setEmail()`, `ubahPassword()`).
- **Kelas `Mahasiswa`:** Belum memiliki method penghitungan IPK (`hitungIPK()`).
- **Accessor Kelas Turunan/Entitas:** Kelas `Admin`, `Enrollment`, dan `Payment` belum dilengkapi accessor eksplisit untuk atribut-atribut privatenya.

---

## 2. Diagram Sesudah Dirubah (Versi Perbaikan)
![Diagram Sesudah Dirubah](diagram_sesudah_dirubah.png)

### Karakteristik Versi Perbaikan:
- **Enkapsulasi Ketat (Strict Private):** Seluruh atribut pada semua kelas diubah menjadi `private (-)`.
- **Accessor Public Lengkap:** Disediakan getter dan setter publik pada `User`, `Admin`, `Enrollment`, dan `Payment`.
- **Penambahan `hitungIPK()`:** Method `+hitungIPK() double` ditambahkan khusus pada kelas `Mahasiswa` (tidak berada di `User`).
- **Single Responsibility Principle (SRP):** Setiap kelas tetap memiliki jumlah method $\le 9$ (di bawah batas 10 method).
- **Struktur Kelas:** Tetap 10 kelas tanpa menambah kelas baru di luar spesifikasi.

---

## 3. Ringkasan Perbedaan Detail

| Komponen / Kelas | Sebelum Perbaikan | Sesudah Perbaikan |
| :--- | :--- | :--- |
| **User (Abstract)** | `#id`, `#username`, `-password`, `#email`<br>`+login()`, `+logout()` | `-id`, `-username`, `-password`, `-email`<br>`+login()`, `+logout()`, `+getId()`, `+getUsername()`, `+getEmail()`, `+setEmail()`, `+ubahPassword()` |
| **Mahasiswa** | 8 method (tanpa hitung IPK) | 9 method (ditambahkan `+hitungIPK() double`) |
| **Admin** | 4 method (tanpa `getStaffId()`) | 5 method (ditambahkan `+getStaffId() String`) |
| **Enrollment** | 5 method (tanpa getter semester/thn) | 7 method (ditambahkan `+getSemester() int`, `+getTahunAkademik() String`) |
| **Payment** | 5 method (tanpa getter tgl bayar) | 6 method (ditambahkan `+getTanggalBayar() String`) |
