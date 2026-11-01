# Sistem Informasi Akademik (SIAKAD Mini) - Architecture Design

Dokumen arsitektur dan perancangan berorientasi objek untuk sistem informasi akademik kampus.

## 📁 Struktur Berkas

* 📊 **Diagram UML Class (Mermaid):** [`academic_class_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_class_diagram.mmd)
* 📑 **Dokumentasi ADR:** [`ADR-001: Desain Struktur Class Domain Akademik dan Relasi Entitas`](file:///home/zainun/Git/istn/sevima-mini/docs/adr/ADR-001-academic-system-class-structure.md)

## 📌 Ringkasan Prinsip & Pola Desain

1. **SOLID Principles:**
   * **SRP:** Pemisahan ketat antara identitas (`User`), transaksi pendaftaran (`Enrollment`), evaluasi skor (`Grade`), dan alokasi ruang/waktu (`Schedule`).
   * **OCP & DIP:** Perhitungan bobot nilai dinamis berbasis interface strategi (`IGradeEvaluator`).
   * **LSP:** Kontrak polimorfik kelas turunan `User` (`Mahasiswa`, `Dosen`, `Admin`, `CalonMahasiswa`).
   * **ISP:** Interface ramping (`IAuthenticatable`, `IGradeEvaluator`, `IEnrollmentObserver`).

2. **Relasi Entitas:**
   * **Composition (`*--`):** `Enrollment *-- Grade` dan `Course *-- Schedule` (keterikatan siklus hidup ketat).
   * **Aggregation (`o--`):** `Course o-- Course` (prasyarat), `Mahasiswa o-- Enrollment`, `Course o-- Enrollment`, dan `Dosen o-- Course`.

3. **Design Patterns:**
   * **Factory Pattern:** `UserFactory` untuk enkapsulasi instansiasi entitas turunan `User`.
   * **Strategy Pattern:** `StandardGradeEvaluator` dan `PracticumGradeEvaluator` untuk fleksibilitas formula nilai.
   * **Observer Pattern:** `IEnrollmentObserver` untuk sinkronisasi pembaruan status pendaftaran dan nilai ke mahasiswa secara reaktif.
