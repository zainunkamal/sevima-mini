import os
import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.pmb import CalonMahasiswa, JalurMasuk, ProgramStudi, StatusPMB

TEST_SM_DB_PATH = "./test_state_machine.db"
test_sm_engine = create_engine(
    f"sqlite:///{TEST_SM_DB_PATH}",
    connect_args={"check_same_thread": False},
)

@event.listens_for(test_sm_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

TestSMSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_sm_engine)


def override_sm_get_db():
    db = TestSMSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestPMBStateMachine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=test_sm_engine)
        Base.metadata.create_all(bind=test_sm_engine)
        app.dependency_overrides[get_db] = override_sm_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_sm_engine)
        test_sm_engine.dispose()
        if os.path.exists(TEST_SM_DB_PATH):
            os.remove(TEST_SM_DB_PATH)

    def setUp(self):
        self.session = TestSMSessionLocal()
        self.session.query(CalonMahasiswa).delete()
        self.session.query(ProgramStudi).delete()
        self.session.query(JalurMasuk).delete()
        self.session.commit()

        # Seed program studi & jalur
        self.prodi_valid = ProgramStudi(kode="001", nama="Teknik Informatika Angka", fakultas="FTI")
        self.prodi_valid_huruf = ProgramStudi(kode="TIF", nama="Teknik Informatika", fakultas="FTI")
        self.prodi_invalid_2digit = ProgramStudi(kode="12", nama="Prodi 2 Karakter", fakultas="FTI")
        self.prodi_invalid_4digit = ProgramStudi(kode="1234", nama="Prodi 4 Karakter", fakultas="FTI")
        self.jalur = JalurMasuk(nama="Mandiri")
        self.session.add_all([
            self.prodi_valid,
            self.prodi_valid_huruf,
            self.prodi_invalid_2digit,
            self.prodi_invalid_4digit,
            self.jalur,
        ])
        self.session.commit()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def _create_calon(self, prodi_id=None, status=StatusPMB.PENDING, email="calon@example.com") -> CalonMahasiswa:
        calon = CalonMahasiswa(
            nama_lengkap="Calon Uji",
            email=email,
            phone="081234567890",
            alamat="Alamat Rahasia No. 123",
            tanggal_lahir=date(2005, 1, 1),
            program_studi_id=prodi_id or self.prodi_valid.id,
            jalur_masuk_id=self.jalur.id,
            status=status,
        )
        self.session.add(calon)
        self.session.commit()
        self.session.refresh(calon)
        return calon

    def test_01_approve_pending_success(self):
        """PUT /api/pmb/approve/{id}: Transisi pending -> approved menghasilkan NIM dan approved_at UTC."""
        calon = self._create_calon()
        res = self.client.put(f"/api/pmb/approve/{calon.id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "approved")
        self.assertIsNotNone(data["nim"])
        self.assertTrue(data["nim"].startswith(str(date.today().year) + "001"))
        self.assertIsNotNone(data["approved_at"])

        # Data pribadi TIDAK bocor pada response
        self.assertNotIn("alamat", data)
        self.assertNotIn("tanggal_lahir", data)

    def test_02_approve_idempotent_returns_old_nim_without_calling_generator(self):
        """PUT /api/pmb/approve/{id}: Jika sudah approved, kembalikan 200 + NIM lama TANPA memanggil generator."""
        calon = self._create_calon()
        res1 = self.client.put(f"/api/pmb/approve/{calon.id}")
        self.assertEqual(res1.status_code, 200)
        nim_pertama = res1.json()["nim"]

        # Mock generate_nim untuk membuktikan generator TIDAK dipanggil pada approve kedua
        with patch("app.services.pmb.generate_nim") as mock_gen:
            res2 = self.client.put(f"/api/pmb/approve/{calon.id}")
            self.assertEqual(res2.status_code, 200)
            self.assertEqual(res2.json()["nim"], nim_pertama)
            mock_gen.assert_not_called()

    def test_03_approve_rejected_returns_409(self):
        """PUT /api/pmb/approve/{id}: Calon berstatus rejected ditolak dengan status 409 Conflict."""
        calon = self._create_calon(status=StatusPMB.REJECTED)
        res = self.client.put(f"/api/pmb/approve/{calon.id}")
        self.assertEqual(res.status_code, 409)
        self.assertIn("rejected", res.json()["detail"].lower())

    def test_04_approve_prodi_kode_validation(self):
        """PUT /api/pmb/approve/{id}: Kode prodi 3 karakter (TIF atau 001) berhasil, panjang bukan 3 ditolak 400."""
        # 1. Uji prodi dengan huruf 'TIF' (3 karakter valid) -> SUKSES 200
        calon_tif = self._create_calon(prodi_id=self.prodi_valid_huruf.id, email="tif@example.com")
        res_tif = self.client.put(f"/api/pmb/approve/{calon_tif.id}")
        self.assertEqual(res_tif.status_code, 200)
        self.assertIn("TIF", res_tif.json()["nim"])

        # 2. Uji prodi 2 karakter '12' -> GAGAL 400
        calon_2digit = self._create_calon(prodi_id=self.prodi_invalid_2digit.id, email="2digit@example.com")
        res_2digit = self.client.put(f"/api/pmb/approve/{calon_2digit.id}")
        self.assertEqual(res_2digit.status_code, 400)
        self.assertIn("3 karakter alfanumerik", res_2digit.json()["detail"])

        # 3. Uji prodi 4 karakter '1234' -> GAGAL 400
        calon_4digit = self._create_calon(prodi_id=self.prodi_invalid_4digit.id, email="4digit@example.com")
        res_4digit = self.client.put(f"/api/pmb/approve/{calon_4digit.id}")
        self.assertEqual(res_4digit.status_code, 400)
        self.assertIn("3 karakter alfanumerik", res_4digit.json()["detail"])

    def test_05_approve_not_found_returns_404(self):
        """PUT /api/pmb/approve/{id}: ID tidak ada mengembalikan 404 Not Found."""
        res = self.client.put("/api/pmb/approve/999999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("tidak ditemukan", res.json()["detail"].lower())

    def test_06_reject_pending_success(self):
        """PUT /api/pmb/reject/{id}: Transisi pending -> rejected mengembalikan 200."""
        calon = self._create_calon()
        res = self.client.put(f"/api/pmb/reject/{calon.id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "rejected")
        self.assertIsNone(data["nim"])

        # Data pribadi TIDAK bocor pada response
        self.assertNotIn("alamat", data)
        self.assertNotIn("tanggal_lahir", data)

    def test_07_reject_idempotent_returns_200(self):
        """PUT /api/pmb/reject/{id}: Calon yang sudah rejected mengembalikan 200 (idempotent)."""
        calon = self._create_calon(status=StatusPMB.REJECTED)
        res = self.client.put(f"/api/pmb/reject/{calon.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "rejected")

    def test_08_reject_approved_returns_409(self):
        """PUT /api/pmb/reject/{id}: Calon berstatus approved tidak dapat ditolak (409 Conflict)."""
        calon = self._create_calon()
        # Setujui terlebih dahulu
        self.client.put(f"/api/pmb/approve/{calon.id}")

        # Upaya reject pendaftar yang sudah approved
        res = self.client.put(f"/api/pmb/reject/{calon.id}")
        self.assertEqual(res.status_code, 409)
        self.assertIn("approved", res.json()["detail"].lower())

    def test_09_reject_not_found_returns_404(self):
        """PUT /api/pmb/reject/{id}: ID tidak ada mengembalikan 404 Not Found."""
        res = self.client.put("/api/pmb/reject/999999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("tidak ditemukan", res.json()["detail"].lower())

    def test_10_approve_self_healing_when_approved_without_nim(self):
        """PUT /api/pmb/approve/{id}: Anomali data (status approved tapi nim None) diperbaiki dengan menerbitkan NIM."""
        # Arrange: buat calon berstatus approved tetapi nim masih None
        calon = self._create_calon(status=StatusPMB.APPROVED, email="anomaly@example.com")
        self.assertIsNone(calon.nim)

        # Act: panggil approve kembali
        res = self.client.put(f"/api/pmb/approve/{calon.id}")

        # Assert: sistem self-healing menerbitkan NIM baru
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "approved")
        self.assertIsNotNone(data["nim"])

