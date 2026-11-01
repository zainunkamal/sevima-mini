Minggu        : 1
Fitur         : Membuat ClassDiagram
LLM/Tool      : Gemini 3.8 Flash
Promt Kunci   : "Anda adalah arsitek sistem. Buat class diagram UML untuk sistem akademik
                dengan komponen berikut:
                - User sebagai base class (Mahasiswa, Dosen, Admin, CalonMahasiswa)
                - Course dengan atribut kode, nama, SKS, prasyarat
                - Enrollment yang hubungkan Mahasiswa dan Course
                - Schedule dengan hari, jam, ruangan
                - Grade untuk nilai mahasiswa

                Terapkan prinsip SOLID. Gunakan composition untuk relasi kuat dan
                aggregation untuk relasi lemah. Output dalam format Mermaid."
Kode AI awal  : -
Revisi manual : -
---
Minggu        : 1
Fitur         : Menambahkan class inti payment
LLM/Tool      : Gemini 3.8 Flash
Promt Kunci   : "Saya mau menambahkan class inti payment
                Payment itu untuk sebagai syarat agar bisa mengisi KRS
                "
Kode AI awal  : cd67597
Revisi manual : -
---
Minggu        : 1
Fitur         : Membuat UseCase Diagram
LLM/Tool      : Gemini 3.8 Flash
Promt Kunci   : "Anda adalah arsitek sistem. Buatkan usecase diagram dengan terdiri dari 
                - aktor: mahasiswa, dosen, Admin, Sistem PMB
                - usecase: Daftar kuliah, Isi KRS, Input nilai, Generate transkrip, dll
                - Include/extend relationships"
Kode AI awal  : 50077852
Revisi manual : -
---
Minggu        : 1
Fitur         : Membuat Sequence Diagram
LLM/Tool      : Gemini 3.8 Flash
Promt Kunci   : "Anda adalah arsitek sistem. Saya mau membuat sequence diagram
                - Proses pendaftaran mahasiswa baru (PMB)
                - Validasi KRS dengan pengecekan prasyarat"
Kode AI awal  : f47fb84
Revisi manual : -
---
