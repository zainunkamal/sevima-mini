# 🤖 Log Penggunaan AI (AI Usage Log)

> **Konteks:** Dokumentasi transparansi penggunaan kecerdasan buatan (*Generative AI / LLM*) dalam perancangan arsitektur, pemodelan berorientasi objek (UML), serta penyusunan *Architectural Decision Record* (ADR) pada sistem **SIAKAD Mini**.

---

## 📊 Ringkasan Aktivitas Perancangan

| No | Minggu | Fitur / Aktivitas | LLM / Tool | Commit Awal | Status Hasil |
| :-: | :-: | :--- | :--- | :--- | :--- |
| **1** | Minggu 1 | Perancangan UML Class Diagram Inti | Gemini 3.8 Flash | [`cd67597`](https://github.com/zainunkamal/sevima-mini/commit/cd6759791606f5facf2d09f73d7d7d092908ba16) | Selesai (Diterima) |
| **2** | Minggu 1 | Penambahan Class Inti `Payment` & Prasyarat KRS | Gemini 3.8 Flash | [`5007785`](https://github.com/zainunkamal/sevima-mini/commit/50077852cbcc06d1ad52a8f36734f10c081938dd) | Selesai (Diterima) |
| **3** | Minggu 1 | Perancangan UML Use Case Diagram | Gemini 3.8 Flash | [`b9e493f`](https://github.com/zainunkamal/sevima-mini/commit/b9e493f) | Selesai (Diterima) |
| **4** | Minggu 1 | Perancangan UML Sequence Diagram (PMB & KRS) | Gemini 3.8 Flash | [`eff27dc`](https://github.com/zainunkamal/sevima-mini/commit/eff27dc) | Selesai (Diterima) |
| **5** | Minggu 1 | Dokumentasi ADR (ADR-002, ADR-003, PDF & Restrukturisasi) | Gemini 3.8 Flash | [`35d8ca6`](https://github.com/zainunkamal/sevima-mini/commit/35d8ca6) | Selesai (Diterima) |

---

## 📝 Rincian Log Prompt & Interaksi

### 🔹 Log 01: Membuat Class Diagram Inti
* **Minggu:** `1`
* **Fitur:** Membuat ClassDiagram
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`cd67597`](https://github.com/zainunkamal/sevima-mini/commit/cd6759791606f5facf2d09f73d7d7d092908ba16)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Anda adalah arsitek sistem. Buat class diagram UML untuk sistem akademik
  dengan komponen berikut:
  - User sebagai base class (Mahasiswa, Dosen, Admin, CalonMahasiswa)
  - Course dengan atribut kode, nama, SKS, prasyarat
  - Enrollment yang hubungkan Mahasiswa dan Course
  - Schedule dengan hari, jam, ruangan
  - Grade untuk nilai mahasiswa

  Terapkan prinsip SOLID. Gunakan composition untuk relasi kuat dan
  aggregation untuk relasi lemah. Output dalam format Mermaid."
  ```
* **Hasil / Luaran:**
  * Diagram Class Mermaid awal: `academic_class_diagram.mmd` (sekarang [`diagrams/class-diagram.mmd`](../diagrams/class-diagram.mmd)).
  * Dokumen ADR: [`docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md`](../docs/adr/ADR-Markdown/ADR-001-academic-system-class-structure.md).

---

### 🔹 Log 02: Menambahkan Class Inti Payment
* **Minggu:** `1`
* **Fitur:** Menambahkan class inti payment
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`5007785`](https://github.com/zainunkamal/sevima-mini/commit/50077852cbcc06d1ad52a8f36734f10c081938dd) *(basis dari `cd67597`)*
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Saya mau menambahkan class inti payment
  Payment itu untuk sebagai syarat agar bisa mengisi KRS"
  ```
* **Hasil / Luaran:**
  * Penambahan class `Payment` dengan method `isLunas()` dan `konfirmasiPembayaran()`.
  * Integrasi validasi prasyarat pembayaran pada `Mahasiswa`, `Enrollment`, dan `Admin`.
  * Relasi agregasi `Mahasiswa o-- Payment` dan dependensi `Enrollment ..> Payment`.
  * Pembaruan dokumentasi ADR-001 dan diagram komparasi (Baseline v1.0 vs Revisi v1.1).

---

### 🔹 Log 03: Membuat Use Case Diagram
* **Minggu:** `1`
* **Fitur:** Membuat UseCase Diagram
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`b9e493f`](https://github.com/zainunkamal/sevima-mini/commit/b9e493f) *(docs: [`f47fb84`](https://github.com/zainunkamal/sevima-mini/commit/f47fb84))*
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Anda adalah arsitek sistem. Buatkan usecase diagram dengan terdiri dari 
  - aktor: mahasiswa, dosen, Admin, Sistem PMB
  - usecase: Daftar kuliah, Isi KRS, Input nilai, Generate transkrip, dll
  - Include/extend relationships"
  ```
* **Hasil / Luaran:**
  * Diagram Use Case Mermaid: [`diagrams/usecase-diagram.mmd`](../diagrams/usecase-diagram.mmd) & [`docs/usecase/usecase_diagram.svg`](../docs/usecase/usecase_diagram.svg).
  * Dokumen Spesifikasi Use Case: [`docs/usecase/USECASE-001-academic-system.md`](../docs/usecase/USECASE-001-academic-system.md).
  * Dokumen ADR Use Case: [`docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md`](../docs/adr/ADR-Markdown/ADR-002-academic-usecase-architecture.md).

---

### 🔹 Log 04: Membuat Sequence Diagram (PMB & Validasi KRS)
* **Minggu:** `1`
* **Fitur:** Membuat Sequence Diagram
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`eff27dc`](https://github.com/zainunkamal/sevima-mini/commit/eff27dc) *(docs: [`ae627ec`](https://github.com/zainunkamal/sevima-mini/commit/ae627ec))*
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "Anda adalah arsitek sistem. Saya mau membuat sequence diagram
  - Proses pendaftaran mahasiswa baru (PMB)
  - Validasi KRS dengan pengecekan prasyarat"
  ```
* **Hasil / Luaran:**
  * Diagram Sequence PMB: [`diagrams/sequence-pmb.mmd`](../diagrams/sequence-pmb.mmd) & [`docs/sequence/pmb_sequence_diagram.svg`](../docs/sequence/pmb_sequence_diagram.svg).
  * Diagram Sequence Validasi KRS: [`diagrams/sequence-krs.mmd`](../diagrams/sequence-krs.mmd) & [`docs/sequence/krs_sequence_diagram.svg`](../docs/sequence/krs_sequence_diagram.svg).
  * Dokumen Spesifikasi Sequence: [`docs/sequence/SEQUENCE-001-pmb-and-krs.md`](../docs/sequence/SEQUENCE-001-pmb-and-krs.md).
  * Dokumen ADR Sequence: [`docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md`](../docs/adr/ADR-Markdown/ADR-003-academic-sequence-flows.md).

---

### 🔹 Log 05: Dokumentasi ADR Format PDF & Restrukturisasi Diagram
* **Minggu:** `1`
* **Fitur:** Membuat Dokumen ADR format PDF & Restrukturisasi Berkas
* **LLM/Tool:** `Gemini 3.8 Flash`
* **Kode AI awal:** [`35d8ca6`](https://github.com/zainunkamal/sevima-mini/commit/35d8ca6)
* **Revisi manual:** `-`
* **Prompt Kunci:**
  ```text
  "untuk sequence dan usecase, buatkan document ADR dengan format PDF"
  "saya mau menambahkan ada perubahan untuk clas diagram di ADR dengan screenshoot diatas"
  "di README.md jangan sertakan file:///home/zainun/Git/istn/"
  ```
* **Hasil / Luaran:**
  * ADR PDF A4 profesional dengan diagram vektor SVG:
    * [`docs/adr/ADR-001-academic-system-class-structure.pdf`](../docs/adr/ADR-001-academic-system-class-structure.pdf)
    * [`docs/adr/ADR-002-academic-usecase-architecture.pdf`](../docs/adr/ADR-002-academic-usecase-architecture.pdf)
    * [`docs/adr/ADR-003-academic-sequence-flows.pdf`](../docs/adr/ADR-003-academic-sequence-flows.pdf)
  * Restrukturisasi direktori `diagrams/`, `docs/adr/ADR-Markdown/`, dan pembersihan path relatif [README.md](../README.md).
