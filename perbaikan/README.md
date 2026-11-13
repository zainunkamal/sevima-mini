# Dokumentasi Riwayat Perbaikan Class Diagram UML - SEVIMA Mini

Dokumen ini mencatat bukti visual dan perbandingan evolusi class diagram UML sistem informasi akademik **SEVIMA Mini** dari Versi 1 hingga Versi 3.

---

## 1. Versi 1: Versi Awal
![Versi 1 - Versi Awal](diagram_sebelum_dirubah.png)

- **Karakteristik:**
  - Menggunakan visibility `protected (#)` pada atribut `User` (`id`, `username`, `email`).
  - Belum memiliki accessor publik (`getId()`, `getUsername()`, dll) pada `User`.
  - Belum memiliki method penghitungan IPK (`hitungIPK()`) pada `Mahasiswa`.
  - Menggunakan agregasi (`o--`) untuk relasi non-komposisi.

---

## 2. Versi 2: Enkapsulasi Penuh & Penambahan `hitungIPK()`
![Versi 2 - Enkapsulasi](diagram_sesudah_dirubah.png)

- **Perubahan Utama:**
  - Enkapsulasi ketat: seluruh atribut dijadikan `private (-)`.
  - Penambahan method publik accessor/mutator pada `User`, `Admin`, `Enrollment`, dan `Payment`.
  - Penambahan method khusus `+hitungIPK() double` pada kelas `Mahasiswa` (bukan di `User`).
  - Pembatasan jumlah method tetap $\le 9$ (SRP compliant).

---

## 3. Versi 3: Refactoring Relasi (Hasil Uji Wadah & Is-A)
![Versi 3 - Refactoring Relasi](diagram_versi_3.png)

- **Perubahan Utama:**
  - **Uji Wadah-Bagian (*Lifecycle Dependency*):**
    - `Course` $\rightarrow$ `Enrollment`: Diubah dari Agregasi (`o--`) menjadi **Asosiasi (`-->`)**, karena `Course` katalog bukan wadah dari transaksi pendaftaran `Enrollment`.
    - `Dosen` $\rightarrow$ `Course`: Diubah dari Agregasi (`o--`) menjadi **Asosiasi (`-->`)**, karena relasi murni peran mengajar (bukan *whole-part*).
    - `Course` $\rightarrow$ `Course` (Prasyarat): Diubah dari Agregasi (`o--`) menjadi **Asosiasi (`-->`)** antar sesama entitas mata kuliah setara (*self-referencing association*).
  - **Koreksi Kardinalitas:**
    - `Course "1" *-- "0..*" Schedule`: Batas minimum jadwal diubah dari `1..*` menjadi `0..*` agar mata kuliah baru di katalog kurikulum dapat dibuat sebelum jadwal perkuliahan disusun.
  - **Retensi Komposisi Kuat (`*--`):**
    - `Mahasiswa "1" *-- "0..*" Enrollment` (KRS lenyap jika mahasiswa dihapus).
    - `Enrollment "1" *-- "0..1" Grade` (Nilai lenyap jika enrollment dibatalkan/dihapus).
    - `Mahasiswa "1" *-- "0..*" Payment` (Tagihan SPP terikat pada mahasiswa).
    - `Course "1" *-- "0..*" Schedule` (Jadwal kelas terikat pada mata kuliah penawaran).

---

## Tabel Komparasi Evolusi Versi

| Komponen / Relasi | Versi 1 (Awal) | Versi 2 (Enkapsulasi) | Versi 3 (Refactor Relasi) |
| :--- | :--- | :--- | :--- |
| **Atribut `User`** | `protected (#)` | `private (-)` + getter/setter | `private (-)` + getter/setter |
| **Method `Mahasiswa`** | Tanpa `hitungIPK()` | Ditambahkan `+hitungIPK() double` | Memiliki `+hitungIPK() double` |
| **`Course` - `Enrollment`** | `Course "1" o-- "0..*" Enrollment` | `Course "1" o-- "0..*" Enrollment` | **`Course "1" --> "0..*" Enrollment` (Association)** |
| **`Dosen` - `Course`** | `Dosen "1" o-- "0..*" Course` | `Dosen "1" o-- "0..*" Course` | **`Dosen "1" --> "0..*" Course` (Association)** |
| **`Course` - `Course` (Prasyarat)** | `Course "0..*" o-- "0..*" Course` | `Course "0..*" o-- "0..*" Course` | **`Course "0..*" --> "0..*" Course` (Association)** |
| **`Course` - `Schedule`** | `Course "1" *-- "1..*" Schedule` | `Course "1" *-- "1..*" Schedule` | **`Course "1" *-- "0..*" Schedule` (0..*)** |
| **Komposisi Kuat** | Ada (Enrollment, Grade, Payment) | Ada (Enrollment, Grade, Payment) | Dipertahankan & Divalidasi |
