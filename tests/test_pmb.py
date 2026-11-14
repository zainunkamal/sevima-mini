import os
import unittest
from datetime import date

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base, engine, set_sqlite_pragma
from app.models.pmb import CalonMahasiswa, JalurMasuk, ProgramStudi, StatusPMB


class TestPMBModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Menggunakan koneksi database aktif
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        cls.Session = sessionmaker(bind=engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_01_create_valid_pmb_data(self):
        """Memastikan data valid berhasil disimpan."""
        prodi = ProgramStudi(kode="TIF", nama="Teknik Informatika", fakultas="FTI")
        jalur = JalurMasuk(nama="SNBT")
        self.session.add_all([prodi, jalur])
        self.session.commit()

        calon = CalonMahasiswa(
            nama_lengkap="Ahmad Fauzi",
            email="ahmad.fauzi@example.com",
            phone="081234567890",
            tanggal_lahir=date(2005, 5, 20),
            alamat="Jl. Raya Lenteng Agung No. 10",
            program_studi_id=prodi.id,
            jalur_masuk_id=jalur.id,
            status=StatusPMB.PENDING,
        )
        self.session.add(calon)
        self.session.commit()

        self.assertIsNotNone(calon.id)
        self.assertEqual(calon.status, StatusPMB.PENDING)
        self.assertEqual(calon.program_studi.kode, "TIF")
        self.assertEqual(calon.jalur_masuk.nama, "SNBT")

    def test_02_foreign_key_violation(self):
        """Uji penegakan Foreign Key SQLite: Menolak program_studi_id fiktif."""
        calon_invalid = CalonMahasiswa(
            nama_lengkap="Budi Santoso",
            email="budi@example.com",
            phone="081987654321",
            program_studi_id=999999,  # ID prodi fiktif
        )
        self.session.add(calon_invalid)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_03_unique_email_violation(self):
        """Uji Unique Constraint pada email calon mahasiswa."""
        prodi = self.session.query(ProgramStudi).first()
        calon_duplicate = CalonMahasiswa(
            nama_lengkap="Ahmad Duplikat",
            email="ahmad.fauzi@example.com",  # Email sudah ada di test_01
            phone="081299999999",
            program_studi_id=prodi.id,
        )
        self.session.add(calon_duplicate)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_04_unique_prodi_kode_violation(self):
        """Uji Unique Constraint pada kode program studi."""
        prodi_duplikat = ProgramStudi(
            kode="TIF",  # Kode TIF sudah ada di test_01
            nama="Teknologi Informasi Baru",
            fakultas="FTI",
        )
        self.session.add(prodi_duplikat)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_05_check_constraint_status(self):
        """Uji CHECK Constraint: Menolak status di luar pending/approved/rejected."""
        prodi = self.session.query(ProgramStudi).first()
        # Menggunakan raw SQL insert untuk menguji database-level CHECK constraint
        with self.assertRaises(IntegrityError):
            self.session.execute(
                sa.text(
                    """
                    INSERT INTO calon_mahasiswa 
                    (nama_lengkap, email, phone, program_studi_id, status)
                    VALUES ('Ilegal Status', 'ilegal@example.com', '081233333333', :prodi_id, 'invalid_status')
                    """
                ),
                {"prodi_id": prodi.id},
            )
            self.session.commit()

    def test_06_on_delete_restrict_prodi(self):
        """Uji ON DELETE RESTRICT: Program studi tidak boleh dihapus jika masih dirujuk calon mahasiswa."""
        prodi = self.session.query(ProgramStudi).filter_by(kode="TIF").first()
        self.session.delete(prodi)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_07_on_delete_set_null_jalur(self):
        """Uji ON DELETE SET NULL: Jalur masuk yang dihapus membuat jalur_masuk_id menjadi NULL."""
        jalur = self.session.query(JalurMasuk).filter_by(nama="SNBT").first()
        self.session.delete(jalur)
        self.session.commit()

        calon = self.session.query(CalonMahasiswa).filter_by(email="ahmad.fauzi@example.com").first()
        self.assertIsNone(calon.jalur_masuk_id)


if __name__ == "__main__":
    unittest.main()
