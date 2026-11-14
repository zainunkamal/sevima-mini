import os
import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.pmb import CalonMahasiswa, JalurMasuk, ProgramStudi, StatusPMB

TEST_STATS_DB_PATH = "./test_stats.db"
test_stats_engine = create_engine(
    f"sqlite:///{TEST_STATS_DB_PATH}",
    connect_args={"check_same_thread": False},
)

@event.listens_for(test_stats_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

TestStatsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_stats_engine)


def override_stats_get_db():
    db = TestStatsSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestPMBStatusAndStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=test_stats_engine)
        Base.metadata.create_all(bind=test_stats_engine)
        app.dependency_overrides[get_db] = override_stats_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_stats_engine)
        test_stats_engine.dispose()
        if os.path.exists(TEST_STATS_DB_PATH):
            os.remove(TEST_STATS_DB_PATH)

    def setUp(self):
        self.session = TestStatsSessionLocal()
        self.session.query(CalonMahasiswa).delete()
        self.session.query(ProgramStudi).delete()
        self.session.query(JalurMasuk).delete()
        self.session.commit()

        # Seed master data: 3 program studi (satu akan kosong/0 pendaftar)
        self.prodi_tif = ProgramStudi(kode="TIF", nama="Teknik Informatika", fakultas="FTI")
        self.prodi_sif = ProgramStudi(kode="SIF", nama="Sistem Informasi", fakultas="FTI")
        self.prodi_ars = ProgramStudi(kode="ARS", nama="Arsitektur", fakultas="FTSP")

        # Seed master data: 3 jalur masuk (satu akan kosong/0 pendaftar)
        self.jalur_snbp = JalurMasuk(nama="SNBP")
        self.jalur_snbt = JalurMasuk(nama="SNBT")
        self.jalur_mandiri = JalurMasuk(nama="Mandiri")

        self.session.add_all([
            self.prodi_tif, self.prodi_sif, self.prodi_ars,
            self.jalur_snbp, self.jalur_snbt, self.jalur_mandiri,
        ])
        self.session.commit()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_01_get_status_success_without_sensitive_data(self):
        """GET /api/pmb/status/{id}: Mengembalikan status pendaftaran tanpa membocorkan data pribadi."""
        calon = CalonMahasiswa(
            nama_lengkap="Budi Setiawan",
            email="budi.setiawan@example.com",
            phone="081234567890",
            alamat="Jl. Margonda Raya No. 100",
            tanggal_lahir=date(2004, 5, 12),
            program_studi_id=self.prodi_tif.id,
            jalur_masuk_id=self.jalur_snbp.id,
            status=StatusPMB.PENDING,
        )
        self.session.add(calon)
        self.session.commit()

        res = self.client.get(f"/api/pmb/status/{calon.id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Atribut yang wajib ada
        self.assertEqual(data["id"], calon.id)
        self.assertEqual(data["nama_lengkap"], "Budi Setiawan")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["program_studi_id"], self.prodi_tif.id)
        self.assertEqual(data["jalur_masuk_id"], self.jalur_snbp.id)
        self.assertIsNone(data["nim"])
        self.assertIsNotNone(data["created_at"])

        # DATA PRIBADI WAJIB TIDAK BOCOR
        self.assertNotIn("alamat", data)
        self.assertNotIn("tanggal_lahir", data)
        self.assertNotIn("phone", data)
        self.assertNotIn("email", data)

    def test_02_get_status_not_found_returns_404(self):
        """GET /api/pmb/status/{id}: Mengembalikan 404 jika ID tidak ditemukan."""
        res = self.client.get("/api/pmb/status/999999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("tidak ditemukan", res.json()["detail"].lower())

    def test_03_get_stats_aggregation_and_outer_join(self):
        """
        GET /api/pmb/stats:
        - Agregasi GROUP BY di database.
        - Outer join memastikan prodi/jalur tanpa pendaftar tetap tampil dengan angka 0.
        """
        # Buat 3 calon mahasiswa:
        # 1: TIF, SNBP, pending
        # 2: TIF, SNBP, approved (nim terbit)
        # 3: SIF, SNBT, rejected
        # ARS dan Mandiri dibiarkan KOSONG (0 pendaftar)
        calon1 = CalonMahasiswa(
            nama_lengkap="Calon 1",
            email="c1@example.com",
            phone="081234567891",
            program_studi_id=self.prodi_tif.id,
            jalur_masuk_id=self.jalur_snbp.id,
            status=StatusPMB.PENDING,
        )
        calon2 = CalonMahasiswa(
            nama_lengkap="Calon 2",
            email="c2@example.com",
            phone="081234567892",
            program_studi_id=self.prodi_tif.id,
            jalur_masuk_id=self.jalur_snbp.id,
            status=StatusPMB.APPROVED,
            nim="2026TIF0001",
        )
        calon3 = CalonMahasiswa(
            nama_lengkap="Calon 3",
            email="c3@example.com",
            phone="081234567893",
            program_studi_id=self.prodi_sif.id,
            jalur_masuk_id=self.jalur_snbt.id,
            status=StatusPMB.REJECTED,
        )
        self.session.add_all([calon1, calon2, calon3])
        self.session.commit()

        res = self.client.get("/api/pmb/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # 1. Cek per_status
        per_status = data["per_status"]
        self.assertEqual(per_status["pending"], 1)
        self.assertEqual(per_status["approved"], 1)
        self.assertEqual(per_status["rejected"], 1)

        # 2. Cek per_program_studi (outerjoin)
        per_prodi = {p["kode"]: p["total"] for p in data["per_program_studi"]}
        self.assertEqual(per_prodi["TIF"], 2)
        self.assertEqual(per_prodi["SIF"], 1)
        # ARS wajib tampil dengan total 0
        self.assertEqual(per_prodi["ARS"], 0)

        # 3. Cek per_jalur_masuk (outerjoin)
        per_jalur = {j["nama"]: j["total"] for j in data["per_jalur_masuk"]}
        self.assertEqual(per_jalur["SNBP"], 2)
        self.assertEqual(per_jalur["SNBT"], 1)
        # Mandiri wajib tampil dengan total 0
        self.assertEqual(per_jalur["Mandiri"], 0)
