from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.pmb import StatusPMB


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
    # Regex nomor HP Indonesia presisi: diawali 08, 628, atau +628 diikuti digit 1-9 dan 7-11 digit berikutnya
    phone: str = Field(
        ...,
        pattern=r"^(?:\+628|628|08)[1-9][0-9]{6,11}$",
        description="Nomor HP Indonesia valid (awalan 08, 628, atau +628)",
        examples=["081234567890"],
    )
    tanggal_lahir: Optional[date] = Field(
        default=None,
        description="Tanggal lahir calon mahasiswa (rentang umur 14 - 80 tahun)",
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

    @field_validator("tanggal_lahir")
    @classmethod
    def validate_umur_calon_mahasiswa(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            today = date.today()
            if v >= today:
                raise ValueError("Tanggal lahir tidak boleh di masa depan")
            umur = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if umur < 14:
                raise ValueError("Usia calon mahasiswa minimal 14 tahun")
            if umur > 80:
                raise ValueError("Usia calon mahasiswa melebihi batas wajar (maksimal 80 tahun)")
        return v


class PendaftarOut(BaseModel):
    id: int
    nama_lengkap: str
    email: EmailStr
    phone: str
    program_studi_id: int
    jalur_masuk_id: Optional[int] = None
    status: StatusPMB
    nim: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None

    # Mengizinkan pemetaan otomatis dari objek SQLAlchemy (Pydantic v2)
    # Atribut tanggal_lahir dan alamat TIDAK disertakan demi perlindungan privasi
    model_config = ConfigDict(from_attributes=True)
