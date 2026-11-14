from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    nama_lengkap: str = Field(
        ...,
        min_length=3,
        description="Nama lengkap minimal 3 karakter",
        examples=["Ahmad Fauzi"],
    )
    email: EmailStr = Field(
        ...,
        description="Alamat email aktif calon mahasiswa",
        examples=["ahmad.fauzi@example.com"],
    )
    phone: str = Field(
        ...,
        pattern=r"^(\+62|62|08)[0-9]{7,13}$",
        description="Nomor HP Indonesia dengan awalan 08, 62, atau +62",
        examples=["081234567890"],
    )
    tanggal_lahir: Optional[date] = Field(
        default=None,
        description="Tanggal lahir calon mahasiswa",
        examples=["2005-08-17"],
    )
    alamat: Optional[str] = Field(
        default=None,
        description="Alamat tempat tinggal",
        examples=["Jl. Lenteng Agung No. 10, Jakarta Selatan"],
    )
    program_studi_id: int = Field(
        ...,
        gt=0,
        description="ID program studi yang dipilih (harus > 0)",
        examples=[1],
    )
    jalur_masuk_id: int = Field(
        ...,
        gt=0,
        description="ID jalur masuk yang dipilih (harus > 0)",
        examples=[1],
    )


class PendaftarOut(BaseModel):
    id: int
    nama_lengkap: str
    email: EmailStr
    phone: str
    program_studi_id: int
    jalur_masuk_id: Optional[int] = None
    status: str
    nim: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None

    # Mengizinkan pemetaan otomatis dari objek SQLAlchemy (Pydantic v2)
    # Atribut tanggal_lahir dan alamat TIDAK disertakan demi perlindungan privasi
    model_config = ConfigDict(from_attributes=True)
