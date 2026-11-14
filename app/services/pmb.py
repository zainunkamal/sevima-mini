import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.models.pmb import (
    CalonMahasiswa,
    JalurMasuk,
    NimCounter,
    ProgramStudi,
    StatusPMB,
)
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


class NimLimitExceededError(Exception):
    """Dilempar saat nomor urut NIM melampaui batas maksimum 4 digit (9999)."""
    pass


def generate_nim(db: Session, tahun: int, kode_prodi: str) -> str:
    """
    Menghasilkan NIM baru dengan format:
      4 digit tahun + 3 digit kode prodi + 4 digit nomor urut (zero padding), tanpa strip.
      Contoh: tahun 2025, prodi 001, urut 1 -> 20250010001.

    Karakteristik & Integritas:
    - Multi-worker safe: Menggunakan SELECT ... FOR UPDATE (exclusive row lock di DB engine).
    - Database independent: SQLite saat pengujian mengabaikan with_for_update() secara aman.
    - Transaction boundary: TIDAK commit sendiri (hanya db.flush()); transaksi dikendalikan oleh endpoint.
    - Batas kuota: Membatasi nomor urut hingga 9999; jika melebihi, melempar NimLimitExceededError.
    - Zero padding: Menjamin 4 digit tahun, 3 digit kode prodi (zfill 3), dan 4 digit urut (zfill 4).
    """
    prodi_str = str(kode_prodi).strip().zfill(3)

    # 1. Kueri counter dengan row lock (FOR UPDATE)
    stmt = (
        select(NimCounter)
        .where(
            NimCounter.tahun == tahun,
            NimCounter.kode_prodi == prodi_str,
        )
        .with_for_update()
    )
    counter = db.scalar(stmt)

    # 2. Inisialisasi baris awal jika kombinasi (tahun, prodi) baru pertama kali digunakan
    if counter is None:
        try:
            # Gunakan savepoint (nested transaction) untuk mencegah kegagalan fatal
            # jika dua worker mengeksekusi inisialisasi pada waktu yang sama
            with db.begin_nested():
                counter = NimCounter(tahun=tahun, kode_prodi=prodi_str, last_number=0)
                db.add(counter)
                db.flush()
        except IntegrityError:
            # Worker lain sudah berhasil melakukan inisialisasi
            pass

        # Ambil kembali instance yang kini sudah pasti ada dan terkunci
        counter = db.scalar(stmt)

    # 3. Validasi batas kuota nomor urut (maksimal 9999)
    if counter.last_number >= 9999:
        raise NimLimitExceededError(
            f"Batas nomor urut NIM untuk tahun {tahun} prodi {prodi_str} telah melampaui batas maksimum (9999)."
        )

    # 4. Increment counter
    counter.last_number += 1

    # 5. Flush perubahan ke transaksi aktif (jangan commit!)
    db.flush()

    # 6. Format: 4 digit tahun + 3 digit kode prodi + 4 digit nomor urut (zero padding)
    return f"{tahun:04d}{prodi_str}{counter.last_number:04d}"


def approve_calon_mahasiswa(
    db: Session,
    calon_id: int,
    tahun: Optional[int] = None,
    max_retries: int = 3,
) -> CalonMahasiswa:
    """
    Menyetujui pendaftaran calon mahasiswa dan menerbitkan NIM secara atomik.
    Menangani potensi benturan IntegrityError dengan rollback dan retry maksimal 3 kali.
    """
    if tahun is None:
        tahun = datetime.now().year

    for attempt in range(1, max_retries + 1):
        try:
            # Cari calon mahasiswa
            calon = db.scalar(
                select(CalonMahasiswa).where(CalonMahasiswa.id == calon_id)
            )
            if not calon:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Calon mahasiswa dengan ID {calon_id} tidak ditemukan.",
                )

            # Jika sudah approved, kembalikan data yang ada (idempotent)
            if calon.status == StatusPMB.APPROVED:
                return calon

            if calon.status == StatusPMB.REJECTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calon mahasiswa yang telah ditolak tidak dapat disetujui kembali.",
                )

            # Validasi relasi program studi
            prodi = calon.program_studi
            if not prodi:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Program studi calon mahasiswa tidak ditemukan.",
                )

            # Terbitkan NIM baru
            calon.nim = generate_nim(db, tahun=tahun, kode_prodi=prodi.kode)
            calon.status = StatusPMB.APPROVED
            calon.approved_at = datetime.now(timezone.utc)

            # Commit transaksi pada level endpoint
            db.commit()
            db.refresh(calon)
            return calon

        except (IntegrityError, OperationalError):
            # Rollback transaksi segera untuk melepas row lock dan membersihkan state session
            db.rollback()

            if attempt == max_retries:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Gagal menerbitkan NIM setelah 3 kali percobaan karena konflik konkurensi integritas data.",
                )

            # Backoff singkat sebelum mencoba ulang
            time.sleep(0.05 * attempt)

        except NimLimitExceededError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

