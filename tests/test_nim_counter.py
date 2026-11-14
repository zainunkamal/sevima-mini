import os
import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.pmb import CalonMahasiswa, JalurMasuk, NimCounter, ProgramStudi, StatusPMB
from app.services.pmb import (
    NimLimitExceededError,
    approve_calon_mahasiswa,
    generate_nim,
)

TEST_NIM_DB_PATH = "./test_nim_counter.db"
test_nim_engine = create_engine(
    f"sqlite:///{TEST_NIM_DB_PATH}",
    connect_args={"check_same_thread": False},
)

@event.listens_for(test_nim_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

TestNimSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_nim_engine)


def override_nim_get_db():
    db = TestNimSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestNimCounter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=test_nim_engine)
        Base.metadata.create_all(bind=test_nim_engine)
        app.dependency_overrides[get_db] = override_nim_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_nim_engine)
        test_nim_engine.dispose()
        if os.path.exists(TEST_NIM_DB_PATH):
            os.remove(TEST_NIM_DB_PATH)

    def setUp(self):
        self.session = TestNimSessionLocal()
        # Clean up tables between test runs
        self.session.query(CalonMahasiswa).delete()
        self.session.query(NimCounter).delete()
        self.session.query(ProgramStudi).delete()
        self.session.query(JalurMasuk).delete()
        self.session.commit()

        # Seed master data
        self.prodi_tif = ProgramStudi(kode="001", nama="Teknik Informatika", fakultas="FTI")
        self.prodi_sif = ProgramStudi(kode="002", nama="Sistem Informasi", fakultas="FTI")
        self.jalur = JalurMasuk(nama="SNBT")
        self.session.add_all([self.prodi_tif, self.prodi_sif, self.jalur])
        self.session.commit()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_01_generate_nim_format_and_sequence(self):
        """Memastikan format 4 digit tahun + 3 digit prodi + 4 digit nomor urut zero-padded."""
        nim1 = generate_nim(self.session, tahun=2026, kode_prodi="001")
        self.assertEqual(nim1, "20260010001")

        nim2 = generate_nim(self.session, tahun=2026, kode_prodi="001")
        self.assertEqual(nim2, "20260010002")

        nim3 = generate_nim(self.session, tahun=2026, kode_prodi="001")
        self.assertEqual(nim3, "20260010003")

        # Cek record di nim_counter
        counter = self.session.scalar(
            select(NimCounter).where(NimCounter.tahun == 2026, NimCounter.kode_prodi == "001")
        )
        self.assertIsNotNone(counter)
        self.assertEqual(counter.last_number, 3)

    def test_02_independent_counter_per_combination(self):
        """Memastikan nomor urut dihitung ulang mulai dari 1 per kombinasi (tahun, kode_prodi)."""
        nim_2026_001 = generate_nim(self.session, tahun=2026, kode_prodi="001")
        nim_2026_002 = generate_nim(self.session, tahun=2026, kode_prodi="002")
        nim_2027_001 = generate_nim(self.session, tahun=2027, kode_prodi="001")

        self.assertEqual(nim_2026_001, "20260010001")
        self.assertEqual(nim_2026_002, "20260020001")
        self.assertEqual(nim_2027_001, "20270010001")

    def test_03_numeric_prodi_zfill(self):
        """Memastikan kode prodi yang kurang dari 3 digit otomatis diisi leading zero (zfill 3)."""
        nim = generate_nim(self.session, tahun=2026, kode_prodi="5")
        self.assertEqual(nim, "20260050001")

    def test_04_limit_9999_exceeded_raises_error(self):
        """Memastikan nomor urut di atas 9999 melempar NimLimitExceededError."""
        # Buat counter yang sudah berada pada nilai 9999
        counter = NimCounter(tahun=2026, kode_prodi="001", last_number=9999)
        self.session.add(counter)
        self.session.commit()

        with self.assertRaises(NimLimitExceededError):
            generate_nim(self.session, tahun=2026, kode_prodi="001")

    def test_05_function_does_not_commit_directly(self):
        """Memastikan generate_nim hanya memanggil flush, bukan commit (rollback membatalkan kenaikan counter)."""
        counter = NimCounter(tahun=2026, kode_prodi="001", last_number=10)
        self.session.add(counter)
        self.session.commit()

        nim = generate_nim(self.session, tahun=2026, kode_prodi="001")
        self.assertEqual(nim, "20260010011")

        # Rollback transaksi sesi pemanggil
        self.session.rollback()

        # Counter kembali ke nilai sebelum generate_nim (10, bukan 11)
        reloaded = self.session.scalar(
            select(NimCounter).where(NimCounter.tahun == 2026, NimCounter.kode_prodi == "001")
        )
        self.assertEqual(reloaded.last_number, 10)

    def test_06_approve_calon_mahasiswa_success(self):
        """Memastikan alur persetujuan calon mahasiswa menerbitkan NIM dan status approved."""
        calon = CalonMahasiswa(
            nama_lengkap="Siti Rahma",
            email="siti.rahma@example.com",
            phone="081234567890",
            program_studi_id=self.prodi_tif.id,
            jalur_masuk_id=self.jalur.id,
            status=StatusPMB.PENDING,
        )
        self.session.add(calon)
        self.session.commit()

        approved_calon = approve_calon_mahasiswa(self.session, calon_id=calon.id, tahun=2026)
        self.assertEqual(approved_calon.status, StatusPMB.APPROVED)
        self.assertEqual(approved_calon.nim, "20260010001")
        self.assertIsNotNone(approved_calon.approved_at)

    def test_07_approve_idempotent(self):
        """Persetujuan berulang pada calon yang sudah disetujui tidak mengubah NIM."""
        calon = CalonMahasiswa(
            nama_lengkap="Dewi Lestari",
            email="dewi@example.com",
            phone="081234567891",
            program_studi_id=self.prodi_tif.id,
            jalur_masuk_id=self.jalur.id,
            status=StatusPMB.PENDING,
        )
        self.session.add(calon)
        self.session.commit()

        app1 = approve_calon_mahasiswa(self.session, calon_id=calon.id, tahun=2026)
        nim_pertama = app1.nim

        app2 = approve_calon_mahasiswa(self.session, calon_id=calon.id, tahun=2026)
        self.assertEqual(app2.nim, nim_pertama)

    def test_08_approve_retry_on_integrity_error(self):
        """Memastikan mekanisme retry dijalankan saat terjadi benturan IntegrityError."""
        calon = CalonMahasiswa(
            nama_lengkap="Rian Pratama",
            email="rian@example.com",
            phone="081234567892",
            program_studi_id=self.prodi_tif.id,
            jalur_masuk_id=self.jalur.id,
            status=StatusPMB.PENDING,
        )
        self.session.add(calon)
        self.session.commit()

        original_commit = self.session.commit
        attempts = 0

        def flaky_commit():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                # Simulasikan konflik integritas pada 2 percobaan pertama
                raise IntegrityError("Simulated unique conflict", None, None)
            return original_commit()

        with patch.object(self.session, "commit", side_effect=flaky_commit):
            result = approve_calon_mahasiswa(self.session, calon_id=calon.id, tahun=2026, max_retries=3)
            self.assertEqual(result.status, StatusPMB.APPROVED)
            self.assertEqual(attempts, 3)

    def test_09_api_endpoint_approve_success(self):
        """Memastikan endpoint POST /api/pmb/calon-mahasiswa/{id}/approve berfungsi via HTTP TestClient."""
        calon = CalonMahasiswa(
            nama_lengkap="Anisa Putri",
            email="anisa.putri@example.com",
            phone="081234567893",
            program_studi_id=self.prodi_tif.id,
            jalur_masuk_id=self.jalur.id,
            status=StatusPMB.PENDING,
        )
        self.session.add(calon)
        self.session.commit()

        response = self.client.post(f"/api/pmb/calon-mahasiswa/{calon.id}/approve")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "approved")
        self.assertTrue(data["nim"].startswith(str(date.today().year)))
        self.assertIsNotNone(data["approved_at"])
