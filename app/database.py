import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Muat variabel lingkungan dari file .env (jika ada)
load_dotenv()

# Konfigurasi URL Database (prioritas dari environment variable / .env, fallback ke SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sevima_mini.db")

# Deteksi dialek basis data
is_sqlite = DATABASE_URL.startswith("sqlite")

# check_same_thread=False hanya valid untuk mesin SQLite
connect_args = {}
if is_sqlite:
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

# Wajib untuk SQLite: Aktifkan penegakan Foreign Key di level koneksi DB-API
if is_sqlite:
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base DeclarativeBase modern (SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# Dependency injection generator untuk FastAPI
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
