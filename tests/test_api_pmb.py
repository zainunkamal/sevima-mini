import unittest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.pmb import JalurMasuk, ProgramStudi


class TestPMBRegisterAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        prodi = ProgramStudi(kode="TIF", nama="Teknik Informatika", fakultas="FTI")
        jalur = JalurMasuk(nama="SNBT")
        db.add_all([prodi, jalur])
        db.commit()
        db.close()

        cls.client = TestClient(app)

    def test_01_register_success(self):
        """Memastikan pendaftaran berhasil menghasilkan status 201 dan menyembunyikan data sensitif."""
        payload = {
            "nama_lengkap": "Zainun Kamal",
            "email": "zainun@example.com",
            "phone": "081234567890",
            "tanggal_lahir": "2004-10-15",
            "alamat": "Jl. Lenteng Agung No. 5",
            "program_studi_id": 1,
            "jalur_masuk_id": 1,
        }
        response = self.client.post("/api/pmb/register", json=payload)
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data["nama_lengkap"], "Zainun Kamal")
        self.assertEqual(data["email"], "zainun@example.com")
        self.assertEqual(data["status"], "pending")
        # Validasi keamanan privasi
        self.assertNotIn("alamat", data)
        self.assertNotIn("tanggal_lahir", data)

    def test_02_register_duplicate_email(self):
        """Memastikan email yang sudah terdaftar menghasilkan HTTP 409 Conflict."""
        payload = {
            "nama_lengkap": "Zainun Kloning",
            "email": "zainun@example.com",  # Email yang sama dengan test_01
            "phone": "081233334444",
            "program_studi_id": 1,
            "jalur_masuk_id": 1,
        }
        response = self.client.post("/api/pmb/register", json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Email sudah terdaftar", response.json()["detail"])

    def test_03_invalid_program_studi_reference(self):
        """Memastikan program studi tidak ada menghasilkan HTTP 400 Bad Request."""
        payload = {
            "nama_lengkap": "Calon Baru",
            "email": "calon.baru@example.com",
            "phone": "+6281234567890",
            "program_studi_id": 9999,  # ID fiktif
            "jalur_masuk_id": 1,
        }
        response = self.client.post("/api/pmb/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Program studi dengan ID 9999 tidak ditemukan", response.json()["detail"])

    def test_04_invalid_jalur_masuk_reference(self):
        """Memastikan jalur masuk tidak ada menghasilkan HTTP 400 Bad Request."""
        payload = {
            "nama_lengkap": "Calon Baru",
            "email": "calon.baru2@example.com",
            "phone": "6281234567890",
            "program_studi_id": 1,
            "jalur_masuk_id": 9999,  # ID fiktif
        }
        response = self.client.post("/api/pmb/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Jalur masuk dengan ID 9999 tidak ditemukan", response.json()["detail"])

    def test_05_format_validation_error_status_400(self):
        """Memastikan error validasi format request menghasilkan HTTP 400 (bukan 422)."""
        # Nama < 3 karakter, nomor HP tidak sesuai awalan, dan ID <= 0
        payload = {
            "nama_lengkap": "Al",
            "email": "invalid-email-format",
            "phone": "02198765432",
            "program_studi_id": 0,
            "jalur_masuk_id": -1,
        }
        response = self.client.post("/api/pmb/register", json=payload)
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn("Data pendaftaran yang dikirimkan tidak valid", data["detail"])
        self.assertTrue(len(data["errors"]) >= 3)


if __name__ == "__main__":
    unittest.main()
