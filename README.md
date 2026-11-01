# Sistem Informasi Akademik (SIAKAD Mini) - Architecture Design

Dokumen arsitektur dan perancangan berorientasi objek untuk sistem informasi akademik kampus.

## 📁 Struktur Berkas

### 1. Diagram & Arsitektur Class
* 📊 **Diagram UML Class (Mermaid):** [`diagrams/class-diagram.mmd`](diagrams/class-diagram.mmd)
* 📑 **Dokumentasi ADR-001 (MD):** [`ADR-001: Desain Struktur Class Domain Akademik dan Relasi Entitas`](docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md)
* 📕 **Dokumentasi ADR-001 (PDF):** [`ADR-001-academic-system-class-structure.pdf`](docs/adr/ADR-001-academic-system-class-structure.pdf)

### 2. Diagram & Arsitektur Use Case
* 🎯 **Diagram UML Use Case (Mermaid):** [`diagrams/usecase-diagram.mmd`](diagrams/usecase-diagram.mmd)
* 📑 **Spesifikasi Use Case (MD):** [`USECASE-001: Spesifikasi & Diagram Use Case SIAKAD Mini`](docs/usecase/USECASE-001-academic-system.md)
* 📑 **Dokumentasi ADR-002 (MD):** [`ADR-002: Desain Use Case Sistem Informasi Akademik dan Relasi Include/Extend`](docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md)
* 📕 **Dokumentasi ADR-002 (PDF):** [`ADR-002-academic-usecase-architecture.pdf`](docs/adr/ADR-002-academic-usecase-architecture.pdf)

### 3. Diagram & Arsitektur Sequence
* 🔄 **Diagram UML Sequence PMB (Mermaid):** [`diagrams/sequence-pmb.mmd`](diagrams/sequence-pmb.mmd)
* 🔄 **Diagram UML Sequence Validasi KRS (Mermaid):** [`diagrams/sequence-krs.mmd`](diagrams/sequence-krs.mmd)
* 📑 **Spesifikasi Sequence (MD):** [`SEQUENCE-001: Desain Sequence Diagram PMB dan Validasi KRS`](docs/sequence/SEQUENCE-001-pmb-and-krs.md)
* 📑 **Dokumentasi ADR-003 (MD):** [`ADR-003: Desain Sequence Diagram PMB dan Validasi KRS Bertingkat`](docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md)
* 📕 **Dokumentasi ADR-003 (PDF):** [`ADR-003-academic-sequence-flows.pdf`](docs/adr/ADR-003-academic-sequence-flows.pdf)

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
