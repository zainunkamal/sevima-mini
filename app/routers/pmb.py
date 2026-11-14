from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pmb import PendaftarOut, RegisterRequest
from app.services.pmb import (
    PMBService,
    approve_calon_mahasiswa,
    register_calon_mahasiswa,
    reject_calon_mahasiswa,
)

router = APIRouter(prefix="/api/pmb", tags=["PMB"])


@router.post(
    "/register",
    response_model=PendaftarOut,
    status_code=status.HTTP_201_CREATED,
    summary="Pendaftaran Calon Mahasiswa Baru",
    responses={
        400: {
            "description": "Validation Error atau Referensi Tidak Ditemukan",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Data pendaftaran yang dikirimkan tidak valid",
                        "errors": [
                            "nama_lengkap: Panjang minimal adalah 3 karakter",
                            "phone: Format nomor HP tidak valid (harus nomor Indonesia dengan awalan 08, 62, atau +62)",
                        ],
                    }
                }
            },
        },
        409: {
            "description": "Email Duplikat / Konflik Data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email sudah terdaftar. Silakan gunakan alamat email lain."
                    }
                }
            },
        },
    },
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> PendaftarOut:
    """Menerima dan memproses pendaftaran calon mahasiswa baru (Thin Controller)."""
    return PMBService.register(db, payload)


@router.put(
    "/approve/{id}",
    response_model=PendaftarOut,
    status_code=status.HTTP_200_OK,
    summary="Persetujuan Pendaftaran Calon Mahasiswa & Penerbitan NIM",
    responses={
        200: {
            "description": "Pendaftaran berhasil disetujui atau sudah approved (idempotent)",
        },
        400: {
            "description": "Kode prodi bukan 3 digit angka atau program studi tidak ditemukan",
        },
        404: {
            "description": "Calon mahasiswa tidak ditemukan",
        },
        409: {
            "description": "Konflik status pendaftaran (calon mahasiswa berstatus rejected)",
        },
    },
)
def approve(
    id: int,
    db: Session = Depends(get_db),
) -> PendaftarOut:
    """
    Menyetujui pendaftaran calon mahasiswa dan menerbitkan NIM.
    Delegasi aturan transisi state ke PMBService (Thin Controller).
    """
    return PMBService.approve(db, calon_id=id)


@router.put(
    "/reject/{id}",
    response_model=PendaftarOut,
    status_code=status.HTTP_200_OK,
    summary="Penolakan Pendaftaran Calon Mahasiswa",
    responses={
        200: {
            "description": "Pendaftaran berhasil ditolak atau sudah rejected (idempotent)",
        },
        404: {
            "description": "Calon mahasiswa tidak ditemukan",
        },
        409: {
            "description": "Konflik status pendaftaran (calon mahasiswa sudah berstatus approved)",
        },
    },
)
def reject(
    id: int,
    db: Session = Depends(get_db),
) -> PendaftarOut:
    """
    Menolak pendaftaran calon mahasiswa (hanya dari pending).
    Delegasi aturan transisi state ke PMBService (Thin Controller).
    """
    return PMBService.reject(db, calon_id=id)


@router.post(
    "/calon-mahasiswa/{calon_id}/approve",
    response_model=PendaftarOut,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def approve_alias(
    calon_id: int,
    db: Session = Depends(get_db),
) -> PendaftarOut:
    """Alias route untuk kompatibilitas pengujian."""
    return PMBService.approve(db, calon_id=calon_id)


