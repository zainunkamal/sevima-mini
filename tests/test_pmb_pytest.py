import re
from datetime import date
import pytest


def daftar(
    client,
    prodi_id: int,
    jalur_id: int,
    email: str = "calon.utama@example.com",
    phone: str = "081234567890",
    nama_lengkap: str = "Calon Mahasiswa Dummy",
):
    """Fungsi pembantu untuk mendaftarkan calon mahasiswa dengan data dummy."""
    payload = {
        "nama_lengkap": nama_lengkap,
        "email": email,
        "phone": phone,
        "tanggal_lahir": "2005-08-17",
        "alamat": "Jl. Lenteng Agung No. 10, Jakarta Selatan",
        "program_studi_id": prodi_id,
        "jalur_masuk_id": jalur_id,
    }
    return client.post("/api/pmb/register", json=payload)


def test_register_sukses(client, prodi_ti, jalur_snbp):
    """
    Uji registrasi pendaftar berhasil:
    - Status HTTP 201 Created
    - Status default: pending
    - NIM masih null
    - Data pribadi (alamat & tanggal lahir) tidak bocor pada respons
    """
    # Arrange: siapkan data pendaftar baru
    email_dummy = "ahmad.dahlan@example.com"

    # Act: eksekusi pendaftaran melalui fungsi pembantu daftar()
    response = daftar(client, prodi_id=prodi_ti.id, jalur_id=jalur_snbp.id, email=email_dummy)

    # Assert: verifikasi status code dan payload respons
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email_dummy
    assert data["status"] == "pending"
    assert data["nim"] is None
    assert data["program_studi_id"] == prodi_ti.id
    assert "alamat" not in data
    assert "tanggal_lahir" not in data


def test_register_email_ganda(client, prodi_ti, jalur_snbp):
    """
    Uji pencegahan registrasi email duplikat:
    - Pendaftar pertama sukses (201)
    - Pendaftar kedua dengan email identik ditolak (409 Conflict)
    """
    # Arrange: daftarkan mahasiswa pertama dengan email spesifik
    email_sama = "budi.santoso@example.com"
    res1 = daftar(client, prodi_id=prodi_ti.id, jalur_id=jalur_snbp.id, email=email_sama)
    assert res1.status_code == 201

    # Act: coba daftarkan mahasiswa kedua dengan email yang sama persis
    res2 = daftar(client, prodi_id=prodi_ti.id, jalur_id=jalur_snbp.id, email=email_sama)

    # Assert: wajib mengembalikan HTTP 409 Conflict
    assert res2.status_code == 409
    assert "email sudah terdaftar" in res2.json()["detail"].lower()


def test_approve_generate_nim(client, prodi_ti, jalur_snbp):
    """
    Uji persetujuan pendaftar & penerbitan NIM:
    - Status berubah menjadi approved
    - NIM diterbitkan dengan format regex 11 digit: YYYY (4) + PPP (3) + NNNN (4)
    - Nomor urut sekuensial dimulai dari 0001
    """
    # Arrange: daftarkan calon mahasiswa
    res_reg = daftar(client, prodi_id=prodi_ti.id, jalur_id=jalur_snbp.id, email="citra.lestari@example.com")
    calon_id = res_reg.json()["id"]

    # Act: setujui pendaftaran melalui endpoint PUT /api/pmb/approve/{id}
    res_approve = client.put(f"/api/pmb/approve/{calon_id}")

    # Assert: HTTP 200, status approved, dan validasi format regex 11 digit
    assert res_approve.status_code == 200
    data = res_approve.json()
    assert data["status"] == "approved"
    assert data["approved_at"] is not None

    nim = data["nim"]
    assert nim is not None
    # Regex 11 digit: 4 digit tahun sekarang + '001' + 4 digit nomor urut
    tahun_sekarang = str(date.today().year)
    pola_nim_11_digit = rf"^{tahun_sekarang}001\d{{4}}$"
    assert re.match(pola_nim_11_digit, nim) is not None
    assert nim.endswith("0001")


def test_approve_idempotent(client, prodi_ti, jalur_snbp):
    """
    Uji idempotensi approval:
    - Pendaftar A diapprove pertama kali -> NIM ...0001
    - Pendaftar A diapprove kedua kali -> tetap NIM ...0001 (generator tidak dipanggil ulang)
    - Pendaftar B diapprove -> mendapatkan nomor urut 2 (...0002), BUKAN 3!
    """
    # Arrange: daftarkan Pendaftar A dan Pendaftar B
    res_a = daftar(client, prodi_id=prodi_ti.id, jalur_id=jalur_snbp.id, email="pendaftar.a@example.com")
    res_b = daftar(client, prodi_id=prodi_ti.id, jalur_id=jalur_snbp.id, email="pendaftar.b@example.com")
    id_a = res_a.json()["id"]
    id_b = res_b.json()["id"]

    # Act 1: approve Pendaftar A pertama kali
    res_a_pertama = client.put(f"/api/pmb/approve/{id_a}")
    assert res_a_pertama.status_code == 200
    nim_a_pertama = res_a_pertama.json()["nim"]

    # Act 2: approve Pendaftar A kedua kali (uji idempotensi)
    res_a_kedua = client.put(f"/api/pmb/approve/{id_a}")
    assert res_a_kedua.status_code == 200
    nim_a_kedua = res_a_kedua.json()["nim"]

    # Act 3: approve Pendaftar B
    res_b_approve = client.put(f"/api/pmb/approve/{id_b}")
    assert res_b_approve.status_code == 200
    nim_b = res_b_approve.json()["nim"]

    # Assert:
    # 1. NIM Pendaftar A tidak berubah pada pemanggilan kedua
    assert nim_a_pertama == nim_a_kedua
    # 2. NIM Pendaftar B harus nomor urut 2 (0002), membuktikan counter tidak meloncat ke 3
    assert nim_b.endswith("0002")


def test_register_format_hp_salah(client, prodi_ti, jalur_snbp):
    """
    Uji penolakan format nomor HP tidak valid:
    - Sesuai keputusan arsitektur (ADR-003 / Opsi A), error validasi format merespons HTTP 400 Bad Request
    """
    # Arrange: siapkan nomor HP dengan format salah (misal awalan telepon kabel 021)
    hp_salah = "02178912345"

    # Act: eksekusi pendaftaran
    response = daftar(
        client,
        prodi_id=prodi_ti.id,
        jalur_id=jalur_snbp.id,
        email="dewi.safitri@example.com",
        phone=hp_salah,
    )

    # Assert: wajib mengembalikan HTTP 400 Bad Request (bukan 422 default)
    assert response.status_code == 400
    body = response.json()
    assert "tidak valid" in str(body).lower()


def test_approve_id_tidak_ada(client):
    """
    Uji approval pendaftar dengan ID fiktif:
    - Mengembalikan HTTP 404 Not Found
    """
    # Arrange: siapkan ID yang tidak ada di database
    id_fiktif = 999999

    # Act: kirim permintaan approval
    response = client.put(f"/api/pmb/approve/{id_fiktif}")

    # Assert: wajib HTTP 404 Not Found
    assert response.status_code == 404
    assert "tidak ditemukan" in response.json()["detail"].lower()


def test_approve_pendaftar_rejected(client, prodi_ti, jalur_snbp):
    """
    Uji penolakan transisi status terminal:
    - Calon mahasiswa ditolak terlebih dahulu (status: rejected)
    - Percobaan approval terhadap pendaftar rejected wajib ditolak dengan HTTP 409 Conflict
    """
    # Arrange: daftarkan calon mahasiswa lalu ubah statusnya menjadi rejected
    res_reg = daftar(client, prodi_id=prodi_ti.id, jalur_id=jalur_snbp.id, email="eko.prasetyo@example.com")
    calon_id = res_reg.json()["id"]

    res_reject = client.put(f"/api/pmb/reject/{calon_id}")
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "rejected"

    # Act: coba setujui pendaftar yang sudah berstatus rejected
    res_approve = client.put(f"/api/pmb/approve/{calon_id}")

    # Assert: wajib HTTP 409 Conflict (status terminal final)
    assert res_approve.status_code == 409
    assert "rejected" in res_approve.json()["detail"].lower()
