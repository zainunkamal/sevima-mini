import enum
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class StatusPMB(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProgramStudi(Base):
    __tablename__ = "program_studi"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Kode prodi 3 karakter unik (misal: 'TIF', 'SIF', 'ARS')
    kode: Mapped[str] = mapped_column(String(3), unique=True, nullable=False, index=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)
    fakultas: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relasi 1:N ke CalonMahasiswa
    calon_mahasiswa: Mapped[List["CalonMahasiswa"]] = relationship(
        back_populates="program_studi",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<ProgramStudi(id={self.id}, kode='{self.kode}', nama='{self.nama}')>"


class JalurMasuk(Base):
    __tablename__ = "jalur_masuk"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Contoh jalur: SNBP, SNBT, Mandiri
    nama: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Relasi 1:N ke CalonMahasiswa
    calon_mahasiswa: Mapped[List["CalonMahasiswa"]] = relationship(
        back_populates="jalur_masuk"
    )

    def __repr__(self) -> str:
        return f"<JalurMasuk(id={self.id}, nama='{self.nama}')>"


class CalonMahasiswa(Base):
    __tablename__ = "calon_mahasiswa"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nama_lengkap: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # Phone disimpan sebagai STRING (bukan integer untuk mempertahankan leading zero dan kode negara).
    # Format nomor HP tidak divalidasi di SQLite DB (cukup batas panjang String 20).
    # Validasi regex dilakukan di lapisan aplikasi (Pydantic validator/service layer).
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    tanggal_lahir: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    alamat: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Foreign Keys
    program_studi_id: Mapped[int] = mapped_column(
        ForeignKey("program_studi.id", ondelete="RESTRICT"),
        nullable=False,
    )
    jalur_masuk_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jalur_masuk.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Status PMB: ENUM dengan default 'pending' dan CHECK constraint aktif di database
    status: Mapped[StatusPMB] = mapped_column(
        String(20),
        default=StatusPMB.PENDING,
        server_default=StatusPMB.PENDING.value,
        nullable=False,
    )

    # NIM: nullable (hanya terbit saat approved), UNIQUE
    nim: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relasi ORM
    program_studi: Mapped["ProgramStudi"] = relationship(back_populates="calon_mahasiswa")
    jalur_masuk: Mapped[Optional["JalurMasuk"]] = relationship(back_populates="calon_mahasiswa")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_calon_mahasiswa_status",
        ),
    )

    def __repr__(self) -> str:
        return f"<CalonMahasiswa(id={self.id}, email='{self.email}', status='{self.status}')>"


class NimCounter(Base):
    __tablename__ = "nim_counter"

    # Composite Primary Key: kombinasi unik per tahun & kode prodi
    tahun: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode_prodi: Mapped[str] = mapped_column(String(3), primary_key=True)
    last_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    def __repr__(self) -> str:
        return f"<NimCounter(tahun={self.tahun}, kode_prodi='{self.kode_prodi}', last_number={self.last_number})>"

