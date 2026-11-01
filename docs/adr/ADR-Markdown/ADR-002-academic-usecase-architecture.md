# ADR-002: Desain Use Case Sistem Informasi Akademik dan Relasi Include/Extend

* **Status:** Diterima (*Accepted*)
* **Tanggal:** 2026-11-01
* **Penyusun:** Arsitek Sistem (*System Architect*)
* **Konteks Sistem:** Platform Akademik Kampus (*Academic Information System / SEVIMA-Mini*)

---

## 1. Konteks & Latar Belakang (Context)

Sistem Informasi Akademik kampus memerlukan dekomposisi fungsionalitas yang jelas untuk memisahkan domain tanggung jawab pengguna, otomasi proses bisnis, dan integrasi sistem eksternal. Sistem harus melayani empat peran aktor:
1. `Mahasiswa` (kegiatan mandiri akademik dan administrasi)
2. `Dosen` (pengajaran dan perwalian akademik)
3. `Admin` (pengelolaan master data dan kurikulum)
4. `Sistem PMB` (subsistem eksternal penerimaan mahasiswa baru)

Tantangan pemodelan fungsional meliputi:
* Menghindari *use case bloat* (terlalu banyak use case mikro yang mengaburkan tujuan pengguna).
* Menentukan batasan fungsional (*system boundary*) yang jelas antara portal internal SEVIMA-Mini dan sistem eksternal PMB.
* Menerapkan relasi **`<<include>>`** dan **`<<extend>>`** secara presisi sesuai standar UML 2.5 untuk membedakan alur mutlak (*mandatory*) dan alur kondisional/ekstensi (*optional/conditional*).

---

## 2. Keputusan Arsitektur & Dekomposisi Use Case (Architectural Decision)

### 2.1 Identifikasi Aktor & Batasan Sistem

Sistem membedakan aktor primer (*human actors*) dan aktor sekunder (*system actors*):
* **`Mahasiswa`**: Bertanggung jawab atas inisiasi pendaftaran, pembayaran SPP, pengisian rencana studi (KRS), monitoring KHS, dan pencetakan transkrip.
* **`Dosen`**: Menjalankan fungsi ganda: Dosen Pengajar (input nilai perkuliahan, penanganan sanggahan nilai) dan Dosen Wali/DPA (evaluasi serta persetujuan/penolakan KRS).
* **`Admin`**: Menangani konfigurasi master kurikulum, alokasi ruang/waktu jadwal kuliah, dan audit pengguna.
* **`Sistem PMB`**: Sistem eksternal yang terhubung via API/sinkronisasi data untuk memicu transfer data calon mahasiswa yang lolos seleksi.

---

### 2.2 Dekomposisi Modul & Use Case

| Modul Fungsional | Use Case Inti | Aktor Terkait | Deskripsi Fungsional |
| :--- | :--- | :--- | :--- |
| **Registrasi & PMB** | `Daftar Kuliah` | `Mahasiswa`, `Sistem PMB` | Registrasi identitas calon mahasiswa dan pemilihan prodi. |
| | `Sinkronisasi Data Mahasiswa` | `Admin`, `Sistem PMB` | Migrasi data calon mahasiswa lulus seleksi menjadi mahasiswa resmi. |
| **Keuangan** | `Bayar Biaya Kuliah` | `Mahasiswa` | Pembayaran tagihan semester berjalan (SPP/UKT). |
| **Rencana Studi** | `Isi KRS` | `Mahasiswa` | Pemilihan paket mata kuliah pada semester aktif. |
| | `Validasi & Persetujuan KRS` | `Dosen` (Wali) | Tinjauan komposisi mata kuliah dan pengesahan KRS mahasiswa. |
| **Penilaian & Hasil** | `Input Nilai Mahasiswa` | `Dosen` (Pengajar) | Pengisian skor komponen tugas, UTS, UAS. |
| | `Lihat KHS` | `Mahasiswa` | Monitoring indeks prestasi semester berjalan. |
| | `Generate Transkrip Nilai` | `Mahasiswa`, `Dosen` | Penerbitan rekam jejak akademik kumulatif. |
| **Administrasi** | `Kelola Kurikulum` | `Admin` | Konfigurasi SKS dan mata kuliah prasyarat. |
| | `Kelola Alokasi Jadwal` | `Admin` | Penataan ruangan dan jam perkuliahan. |
| | `Kelola Data Pengguna` | `Admin` | Manajemen akun civitas akademika. |

---

### 2.3 Keputusan Penggunaan Relasi `<<include>>` vs `<<extend>>`

#### A. Relasi `<<include>>` (Ketergantungan Mutlak / Mandatory Sub-flow)
Arah panah UML: `Base Use Case -. "<<include>>" .-> Included Use Case`.

1. **`Isi KRS` $\rightarrow$ `Validasi Status Pembayaran`**:
   * **Rationale:** Mahasiswa secara mutlak dilarang memilih mata kuliah apabila tagihan biaya kuliah (SPP) semester berjalan belum berstatus `LUNAS`. Validasi finansial merupakan gerbang (*gatekeeper*) utama.
2. **`Isi KRS` $\rightarrow$ `Validasi Prasyarat Mata Kuliah`**:
   * **Rationale:** Sistem secara otomatis memvalidasi apakah mata kuliah prasyarat telah lulus di semester sebelumnya sebelum mata kuliah lanjutan dapat disimpan ke dalam draft KRS.
3. **`Daftar Kuliah` $\rightarrow$ `Unggah Berkas Persyaratan`**:
   * **Rationale:** Pendaftaran mahasiswa baru tidak sah tanpa pengunggahan berkas legalitas (Ijazah, KTP, SKL).
4. **`Input Nilai Mahasiswa` $\rightarrow$ `Kalkulasi Nilai Akhir & Mutu`**:
   * **Rationale:** Penyimpanan nilai komponen otomatis mengeksekusi algoritma pembobotan dan konversi huruf mutu (*Grade Evaluator*).
5. **`Generate Transkrip Nilai` $\rightarrow$ `Kalkulasi IPK & SKS Kumulatif`**:
   * **Rationale:** Pembuatan transkrip secara inheren mewajibkan komputasi total SKS lulus dan bobot indeks prestasi kumulatif.

#### B. Relasi `<<extend>>` (Alur Kondisional / Extension Points)
Arah panah UML: `Extending Use Case -. "<<extend>>" .-> Base Use Case`.

1. **`Revisi / Batal-Tambah KRS` $\rightarrow$ `Isi KRS`**:
   * **Extension Point:** Terpicu hanya pada masa kalender akademik revisi (*Drop/Add period*).
2. **`Cetak Bukti KRS` $\rightarrow$ `Isi KRS`**:
   * **Extension Point:** Opsional diakses mahasiswa jika membutuhkan dokumen fisik/PDF setelah KRS tersimpan.
3. **`Ajukan Keringanan / Cicilan` $\rightarrow$ `Bayar Biaya Kuliah`**:
   * **Extension Point:** Terpicu kondisional jika mahasiswa mengajukan penundaan atau pemecahan termin pembayaran UKT.
4. **`Tolak KRS dengan Catatan` $\rightarrow$ `Validasi & Persetujuan KRS`**:
   * **Extension Point:** Dieksekusi Dosen Wali jika mahasiswa melanggar batasan SKS atau terjadi bentrok jadwal.
5. **`Proses Sanggah Nilai` $\rightarrow$ `Input Nilai Mahasiswa`**:
   * **Extension Point:** Aktif kondisional jika ada komplain nilai resmi dari mahasiswa selama jendela sanggah dibuka.
6. **`Export Transkrip Resmi (PDF)` $\rightarrow$ `Generate Transkrip Nilai`**:
   * **Extension Point:** Opsional saat dokumen resmi bertandatangan digital diperlukan untuk keperluan eksternal.

---

## 3. Pertimbangan & Trade-off (Consequences)

### 3.1 Integrasi Sistem PMB (Loosely Coupled via Sync)
* **Kelebihan:** Sistem SEVIMA-Mini inti tidak terbebani oleh tingginya *traffic* seleksi pendaftar yang tidak lolos seleksi.
* **Trade-off:** Memerlukan mekanisme sinkronisasi data yang andal untuk mencegah inkonsistensi saat penerbitan NIM mahasiswa baru.

### 3.2 Granularitas Relasi `<<include>>` pada KRS
* **Kelebihan:** Menjamin kepatuhan aturan akademik dan finansial secara otomatis di tingkat perancangan use case sebelum implementasi modul servis.
* **Trade-off:** Menambah kompleksitas visual diagram; dimitigasi dengan pengelompokan modul (*subgraph packaging*).

---

## 4. Referensi Berkas Terkait
* Diagram UML Use Case Mermaid: [`academic_usecase_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_usecase_diagram.mmd)
* Vektor Diagram Use Case SVG: [`usecase_diagram.svg`](file:///home/zainun/Git/istn/sevima-mini/docs/usecase/usecase_diagram.svg)
* Class Diagram Arsitektur: [`academic_class_diagram.mmd`](file:///home/zainun/Git/istn/sevima-mini/academic_class_diagram.mmd)
