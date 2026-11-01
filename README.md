# Sistem Informasi Akademik (SIAKAD Mini) - Architecture Design

Dokumen arsitektur dan perancangan berorientasi objek untuk sistem informasi akademik kampus.

## 📁 Struktur Berkas

* 📊 **Diagram UML Class (Mermaid):** [`academic_class_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_class_diagram.mmd)
* 📑 **Dokumentasi ADR:** [`ADR-001: Desain Struktur Class Domain Akademik dan Relasi Entitas`](file:///home/zainun/Git/istn/sevima-mini/docs/adr/ADR-001-academic-system-class-structure.md)
* 🎯 **Diagram UML Use Case (Mermaid):** [`academic_usecase_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_usecase_diagram.mmd)
* 📑 **Spesifikasi Use Case:** [`USECASE-001: Spesifikasi & Diagram Use Case SIAKAD Mini`](file:///home/zainun/Git/istn/sevima-mini/docs/usecase/USECASE-001-academic-system.md)
* 🔄 **Diagram UML Sequence PMB (Mermaid):** [`academic_pmb_sequence_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_pmb_sequence_diagram.mmd)
* 🔄 **Diagram UML Sequence Validasi KRS (Mermaid):** [`academic_krs_sequence_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_krs_sequence_diagram.mmd)
* 📑 **Spesifikasi Sequence:** [`SEQUENCE-001: Desain Sequence Diagram PMB dan Validasi KRS`](file:///home/zainun/Git/istn/sevima-mini/docs/sequence/SEQUENCE-001-pmb-and-krs.md)

## 📌 Ringkasan Prinsip & Pola Desain

1. **SOLID Principles:**
   * **SRP:** Pemisahan ketat antara identitas (`User`), transaksi pendaftaran (`Enrollment`), evaluasi skor (`Grade`), alokasi ruang/waktu (`Schedule`), serta pengelolaan tagihan & status pelunasan biaya kuliah (`Payment`).
   * **OCP & DIP:** Perhitungan bobot nilai dinamis berbasis interface strategi (`IGradeEvaluator`).
   * **LSP:** Kontrak polimorfik kelas turunan `User` (`Mahasiswa`, `Dosen`, `Admin`, `CalonMahasiswa`).
   * **ISP:** Interface ramping (`IAuthenticatable`, `IGradeEvaluator`, `IEnrollmentObserver`).

2. **Relasi Entitas:**
   * **Composition (`*--`):** `Enrollment *-- Grade` dan `Course *-- Schedule` (keterikatan siklus hidup ketat).
   * **Aggregation (`o--`):** `Course o-- Course` (prasyarat), `Mahasiswa o-- Enrollment`, `Mahasiswa o-- Payment`, `Course o-- Enrollment`, dan `Dosen o-- Course`.
   * **Dependency (`..>`):** `Enrollment ..> Payment` (prasyarat kelayakan finansial sebelum pendaftaran/persetujuan KRS).

3. **Design Patterns:**
   * **Factory Pattern:** `UserFactory` untuk enkapsulasi instansiasi entitas turunan `User`.
   * **Strategy Pattern:** `StandardGradeEvaluator` dan `PracticumGradeEvaluator` untuk fleksibilitas formula nilai.
   * **Observer Pattern:** `IEnrollmentObserver` untuk sinkronisasi pembaruan status pendaftaran dan nilai ke mahasiswa secara reaktif.
