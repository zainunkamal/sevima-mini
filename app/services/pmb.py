import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
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


class PMBService:
    """Service pengelola siklus hidup PMB dan mesin transisi state pendaftaran."""

    @staticmethod
    def register(db: Session, request: RegisterRequest) -> CalonMahasiswa:
        return register_calon_mahasiswa(db, request)

    @staticmethod
    def approve(
        db: Session,
        calon_id: int,
        tahun: Optional[int] = None,
        max_retries: int = 3,
    ) -> CalonMahasiswa:
        """
        Menyetujui pendaftaran calon mahasiswa:
        - State machine: pending -> approved; approved final; rejected -> 409.
        - Idempotent: jika sudah approved, kembalikan 200 + NIM lama tanpa memanggil generator.
        - Menggunakan with_for_update untuk exclusive row lock.
        - Validasi kode prodi wajib 3 digit angka & prodi ditemukan -> 400 jika tidak valid.
        - Catat approved_at (UTC).
        - Commit sekali di akhir (satu transaksi atomik).
        """
        for attempt in range(1, max_retries + 1):
            try:
                # 1. Ambil pendaftar dengan exclusive row lock (with_for_update)
                stmt = (
                    select(CalonMahasiswa)
                    .where(CalonMahasiswa.id == calon_id)
                    .with_for_update()
                )
                calon = db.scalar(stmt)

                # 404 jika pendaftar tidak ditemukan
                if not calon:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Calon mahasiswa dengan ID {calon_id} tidak ditemukan.",
                    )

                # Jika sudah approved -> kembalikan 200 + NIM lama TANPA memanggil generator (idempotent)
                if calon.status == StatusPMB.APPROVED:
                    return calon

                # Jika rejected -> 409 (status final, tidak boleh transisi)
                if calon.status == StatusPMB.REJECTED:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Calon mahasiswa sudah berstatus rejected dan tidak dapat disetujui.",
                    )

                # Validasi eksistensi program studi
                prodi = calon.program_studi
                if not prodi:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Program studi calon mahasiswa tidak ditemukan.",
                    )

                # Validasi kode prodi wajib 3 karakter (digit atau huruf alfanumerik)
                kode_clean = str(prodi.kode).strip() if prodi.kode else ""
                if len(kode_clean) != 3 or not kode_clean.isalnum():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Kode program studi '{prodi.kode}' tidak valid. Kode prodi harus terdiri dari 3 karakter alfanumerik (misal 'TIF', 'SIF', atau '001').",
                    )

                # Catat approved_at (UTC)
                calon.approved_at = datetime.now(timezone.utc)

                # Panggil generator NIM
                tahun_aktif = tahun or datetime.now(timezone.utc).year
                calon.nim = generate_nim(db, tahun=tahun_aktif, kode_prodi=prodi.kode)

                # Transisi status ke approved
                calon.status = StatusPMB.APPROVED

                # Commit SEKALI di akhir (satu transaksi atomik)
                db.commit()
                db.refresh(calon)
                return calon

            except (IntegrityError, OperationalError):
                db.rollback()
                if attempt == max_retries:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Gagal menyetujui pendaftaran setelah 3 kali percobaan karena konflik integritas data.",
                    )
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

    @staticmethod
    def reject(db: Session, calon_id: int) -> CalonMahasiswa:
        """
        Menolak pendaftaran calon mahasiswa:
        - State machine: hanya boleh dari pending.
        - Idempotent: jika sudah rejected -> 200.
        - Approved final: jika sudah approved -> 409.
        - Menggunakan with_for_update untuk exclusive row lock.
        - Commit sekali di akhir (satu transaksi).
        """
        try:
            # 1. Ambil pendaftar dengan exclusive row lock (with_for_update)
            stmt = (
                select(CalonMahasiswa)
                .where(CalonMahasiswa.id == calon_id)
                .with_for_update()
            )
            calon = db.scalar(stmt)

            # 404 jika pendaftar tidak ditemukan
            if not calon:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Calon mahasiswa dengan ID {calon_id} tidak ditemukan.",
                )

            # Reject hanya dari pending; approved -> 409
            if calon.status == StatusPMB.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Calon mahasiswa sudah berstatus approved dan tidak dapat ditolak.",
                )

            # Jika sudah rejected -> kembalikan 200 (idempotent)
            if calon.status == StatusPMB.REJECTED:
                return calon

            # Transisi dari pending ke rejected
            calon.status = StatusPMB.REJECTED

            # Commit SEKALI di akhir
            db.commit()
            db.refresh(calon)
            return calon

        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_status(db: Session, calon_id: int) -> CalonMahasiswa:
        """
        Mengambil data status calon mahasiswa:
        - 404 jika tidak ditemukan.
        """
        stmt = select(CalonMahasiswa).where(CalonMahasiswa.id == calon_id)
        calon = db.scalar(stmt)
        if not calon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Calon mahasiswa dengan ID {calon_id} tidak ditemukan.",
            )
        return calon

    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        Menghitung ringkasan statistik PMB di level database menggunakan GROUP BY & outer join:
        1. Jumlah pendaftar per status (GROUP BY)
        2. Jumlah pendaftar per program studi (outerjoin agar 0 tetap muncul)
        3. Jumlah pendaftar per jalur masuk (outerjoin agar 0 tetap muncul)
        """
        # 1. Jumlah per status (GROUP BY di database)
        stmt_status = (
            select(
                CalonMahasiswa.status,
                func.count(CalonMahasiswa.id).label("total"),
            )
            .group_by(CalonMahasiswa.status)
        )
        status_counts = {s.value: 0 for s in StatusPMB}
        for row in db.execute(stmt_status):
            st_key = row.status.value if hasattr(row.status, "value") else str(row.status)
            status_counts[st_key] = row.total

        # 2. Jumlah per program studi (outerjoin agar prodi tanpa pendaftar tetap tampil angka 0)
        stmt_prodi = (
            select(
                ProgramStudi.id,
                ProgramStudi.kode,
                ProgramStudi.nama,
                func.count(CalonMahasiswa.id).label("total"),
            )
            .outerjoin(CalonMahasiswa, ProgramStudi.id == CalonMahasiswa.program_studi_id)
            .group_by(ProgramStudi.id, ProgramStudi.kode, ProgramStudi.nama)
            .order_by(ProgramStudi.id)
        )
        prodi_counts = [
            {
                "id": row.id,
                "kode": row.kode,
                "nama": row.nama,
                "total": row.total,
            }
            for row in db.execute(stmt_prodi)
        ]

        # 3. Jumlah per jalur masuk (outerjoin agar jalur tanpa pendaftar tetap tampil angka 0)
        stmt_jalur = (
            select(
                JalurMasuk.id,
                JalurMasuk.nama,
                func.count(CalonMahasiswa.id).label("total"),
            )
            .outerjoin(CalonMahasiswa, JalurMasuk.id == CalonMahasiswa.jalur_masuk_id)
            .group_by(JalurMasuk.id, JalurMasuk.nama)
            .order_by(JalurMasuk.id)
        )
        jalur_counts = [
            {
                "id": row.id,
                "nama": row.nama,
                "total": row.total,
            }
            for row in db.execute(stmt_jalur)
        ]

        return {
            "per_status": status_counts,
            "per_program_studi": prodi_counts,
            "per_jalur_masuk": jalur_counts,
        }


# Alias fungsi untuk kemudahan impor & kompatibilitas modul
approve_calon_mahasiswa = PMBService.approve
reject_calon_mahasiswa = PMBService.reject

