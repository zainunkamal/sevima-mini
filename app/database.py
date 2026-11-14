from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./sevima_mini.db"

# Engine SQLite (check_same_thread=False diperlukan bila diakses multi-thread / FastAPI)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Wajib untuk SQLite: Aktifkan penegakan Foreign Key di level koneksi DB-API
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base DeclarativeBase modern (SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass
