from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.pmb import CalonMahasiswa, JalurMasuk, ProgramStudi, StatusPMB
from app.schemas.pmb import RegisterRequest


def register_calon_mahasiswa(db: Session, request: RegisterRequest) -> CalonMahasiswa:
    """Mendaftarkan calon mahasiswa baru dengan validasi integritas data & referensi."""
    # 1. Cek email ganda (Fast pre-check)
    existing_calon = (
        db.query(CalonMahasiswa)
        .filter(CalonMahasiswa.email == request.email)
        .first()
    )
    if existing_calon:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar. Silakan gunakan alamat email lain.",
        )

    # 2. Cek referensi Program Studi
    prodi = (
        db.query(ProgramStudi)
        .filter(ProgramStudi.id == request.program_studi_id)
        .first()
    )
    if not prodi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Program studi dengan ID {request.program_studi_id} tidak ditemukan.",
        )

    # 3. Cek referensi Jalur Masuk
    jalur = (
        db.query(JalurMasuk)
        .filter(JalurMasuk.id == request.jalur_masuk_id)
        .first()
    )
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

    # 5. Commit dengan penanganan IntegrityError untuk mengatasi race condition
    try:
        db.commit()
        db.refresh(calon_mahasiswa)
        return calon_mahasiswa
    except IntegrityError:
        db.rollback()
        # Mengantisipasi race condition concurrent insert dengan email yang sama
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar dalam sistem PMB. Silakan gunakan email lain.",
        )
