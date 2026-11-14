"""Script untuk mengisi data awal (seeding) Program Studi dan Jalur Masuk ke database."""

import os
import sys

# Pastikan direktori root proyek berada di sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.pmb import JalurMasuk, ProgramStudi


def seed_data():
    db = SessionLocal()
    try:
        # 1. Seed Program Studi
        prodi_list = [
            {"kode": "TIF", "nama": "Teknik Informatika", "fakultas": "Fakultas Teknik Industri"},
            {"kode": "SIF", "nama": "Sistem Informasi", "fakultas": "Fakultas Teknik Industri"},
            {"kode": "ARS", "nama": "Arsitektur", "fakultas": "Fakultas Teknik Sipil & Perencanaan"},
            {"kode": "TEK", "nama": "Teknik Elektro", "fakultas": "Fakultas Teknik Industri"},
        ]
        for p in prodi_list:
            if not db.query(ProgramStudi).filter_by(kode=p["kode"]).first():
                db.add(ProgramStudi(**p))

        # 2. Seed Jalur Masuk
        jalur_list = ["SNBP", "SNBT", "Mandiri"]
        for j in jalur_list:
            if not db.query(JalurMasuk).filter_by(nama=j).first():
                db.add(JalurMasuk(nama=j))

        db.commit()
        print("Data awal (Program Studi & Jalur Masuk) berhasil di-seed!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
