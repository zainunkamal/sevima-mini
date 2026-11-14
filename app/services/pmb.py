from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.pmb import CalonMahasiswa, JalurMasuk, ProgramStudi, StatusPMB
from app.schemas.pmb import RegisterRequest


def register_calon_mahasiswa(db: Session, request: RegisterRequest) -> CalonMahasiswa:
    """Mendaftarkan calon mahasiswa baru dengan validasi integritas data & referensi."""
    # 1. Cek email ganda menggunakan query modern SQLAlchemy 2.0 (Fast pre-check) -> 409
    stmt_email = select(CalonMahasiswa).where(CalonMahasiswa.email == request.email)
    existing_calon = db.scalar(stmt_email)
    if existing_calon:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar. Silakan gunakan alamat email lain.",
        )

    # 2. Cek referensi Program Studi (SQLAlchemy 2.0 select) -> 400
    stmt_prodi = select(ProgramStudi).where(ProgramStudi.id == request.program_studi_id)
    prodi = db.scalar(stmt_prodi)
    if not prodi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Program studi dengan ID {request.program_studi_id} tidak ditemukan.",
        )

    # 3. Cek referensi Jalur Masuk (SQLAlchemy 2.0 select) -> 400
    stmt_jalur = select(JalurMasuk).where(JalurMasuk.id == request.jalur_masuk_id)
    jalur = db.scalar(stmt_jalur)
    if not jalur:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Jalur masuk dengan ID {request.jalur_masuk_id} tidak ditemukan.",
        )

    # 4. Buat objek calon mahasiswa dengan status awal 'pending'
    calon_mahasiswa = CalonMahasiswa(
        nama_lengkap=request.nama_lengkap,
        email=request.email,
        phone=request.phone,
        tanggal_lahir=request.tanggal_lahir,
        alamat=request.alamat,
        program_studi_id=request.program_studi_id,
        jalur_masuk_id=request.jalur_masuk_id,
        status=StatusPMB.PENDING,
    )

    db.add(calon_mahasiswa)

    # 5. Commit dengan penanganan spesifik IntegrityError untuk menghindari blind masking
    try:
        db.commit()
        db.refresh(calon_mahasiswa)
        return calon_mahasiswa
    except IntegrityError as exc:
        db.rollback()
        error_info = str(exc.orig).lower() if exc.orig else ""

        # Deteksi spesifik jika kegagalan disebabkan oleh unique constraint email
        if "unique" in error_info and "email" in error_info:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email sudah terdaftar dalam sistem PMB. Silakan gunakan email lain.",
            )
        elif "foreign key" in error_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referensi program studi atau jalur masuk tidak valid pada basis data.",
            )
        elif "check constraint" in error_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data yang dimasukkan melanggar batasan constraint basis data.",
            )

        # Fallback conflict umum jika terjadi race condition tak terduga
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Terjadi konflik integritas data pendaftaran. Silakan periksa kembali data Anda.",
        )
