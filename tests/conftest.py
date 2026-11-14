import sys
from pathlib import Path

# Pastikan root direktori proyek berada dalam sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.pmb import JalurMasuk, ProgramStudi

# Engine SQLite in-memory dengan StaticPool agar koneksi persisten & aman multi-thread
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Fixture db: create_all di awal, yield session, drop_all di akhir."""
    Base.metadata.create_all(bind=engine)
    session: Session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Fixture client dengan dependency_overrides untuk get_db (dibersihkan setelah tes)."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def prodi_ti(db):
    """Fixture prodi_ti: Teknik Informatika dengan kode 001."""
    prodi = ProgramStudi(
        kode="001",
        nama="Teknik Informatika",
        fakultas="Fakultas Teknologi Informasi",
    )
    db.add(prodi)
    db.commit()
    db.refresh(prodi)
    return prodi


@pytest.fixture
def jalur_snbp(db):
    """Fixture jalur_masuk default (SNBP) untuk mendukung pendaftaran calon mahasiswa."""
    jalur = JalurMasuk(nama="SNBP")
    db.add(jalur)
    db.commit()
    db.refresh(jalur)
    return jalur
