from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pmb import (
    PMBStatsResponse,
    PendaftarOut,
    PendaftarStatusOut,
    RegisterRequest,
)
from app.services.pmb import (
    PMBService,
    approve_calon_mahasiswa,
    register_calon_mahasiswa,
    reject_calon_mahasiswa,
)

router = APIRouter(prefix="/api/pmb", tags=["Penerimaan Mahasiswa Baru (PMB)"])


@router.post(
    "/register",
    response_model=PendaftarOut,
    status_code=status.HTTP_201_CREATED,
    summary="Pendaftaran Calon Mahasiswa Baru",
    description=(
        "Menerima dan memproses pendaftaran calon mahasiswa baru ke dalam sistem PMB:\n\n"
        "- **Validasi Format Input**: Nama minimal 3 karakter, nomor HP format Indonesia (+62/62/08), format email valid.\n"
        "- **Validasi Rentang Usia**: Calon mahasiswa berusia minimal 14 tahun dan maksimal 80 tahun.\n"
        "- **Verifikasi Entitas Relasi**: Program Studi dan Jalur Masuk wajib terdaftar di basis data.\n"
        "- **Status Default**: Pendaftar baru secara otomatis mendapatkan status awal `pending` tanpa NIM (`null`).\n"
        "- **Privacy by Design**: Menyaring data sensitif (alamat dan tanggal lahir tidak dikembalikan pada respons)."
    ),
    responses={
        201: {
            "description": "Pendaftaran berhasil dicatat (status: pending, privasi terlindungi)",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nama_lengkap": "Ahmad Fauzi",
                        "email": "ahmad.fauzi@example.com",
                        "phone": "081234567890",
                        "program_studi_id": 1,
                        "jalur_masuk_id": 1,
                        "status": "pending",
                        "nim": None,
                        "created_at": "2026-11-14T10:00:00Z",
                        "approved_at": None,
                    }
                }
            },
        },
        400: {
            "description": "Validasi input gagal atau referensi entitas relasi tidak ditemukan",
            "content": {
                "application/json": {
                    "examples": {
                        "validation_error": {
                            "summary": "Error Validasi Format Input",
                            "value": {
                                "detail": "Data pendaftaran yang dikirimkan tidak valid",
                                "errors": [
                                    "phone: Format nomor HP tidak valid (harus nomor Indonesia dengan awalan 08, 62, atau +62)",
                                    "tanggal_lahir: Usia calon mahasiswa minimal 14 tahun",
                                ],
                            },
                        },
                        "foreign_key_not_found": {
                            "summary": "Program Studi atau Jalur Masuk Tidak Ditemukan",
                            "value": {
                                "detail": "Program studi dengan ID 9999 tidak ditemukan dalam basis data."
                            },
                        },
                    }
                }
            },
        },
        409: {
            "description": "Konflik integritas data (email sudah terdaftar dalam sistem PMB)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email sudah terdaftar dalam sistem PMB. Silakan gunakan email lain."
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
    description=(
        "Menyetujui pendaftaran calon mahasiswa dan menerbitkan Nomor Induk Mahasiswa (NIM):\n\n"
        "- **State Machine**: Transisi status dari `pending` ke `approved`. Status `rejected` bersifat terminal dan dilarang disetujui (409).\n"
        "- **Penerbitan NIM Multi-Worker**: Menghasilkan NIM berurutan unik format 11 digit zero-padded (`YYYY` + `PPP` + `NNNN`) aman multi-worker menggunakan row-lock database InnoDB.\n"
        "- **Idempotensi**: Pemanggilan berulang pada calon yang sudah berstatus `approved` mengembalikan HTTP 200 beserta NIM yang sama tanpa memanggil ulang generator.\n"
        "- **Self-Healing**: Secara otomatis menerbitkan NIM jika mendeteksi calon berstatus `approved` namun kolom NIM masih kosong.\n"
        "- **Pencatatan Waktu**: Merekam timestamp `approved_at` berbasis waktu UTC secara atomik."
    ),
    responses={
        200: {
            "description": "Pendaftaran berhasil disetujui atau sudah approved (operasi idempotent)",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nama_lengkap": "Ahmad Fauzi",
                        "email": "ahmad.fauzi@example.com",
                        "phone": "081234567890",
                        "program_studi_id": 1,
                        "jalur_masuk_id": 1,
                        "status": "approved",
                        "nim": "20260010001",
                        "created_at": "2026-11-14T10:00:00Z",
                        "approved_at": "2026-11-14T10:05:00Z",
                    }
                }
            },
        },
        400: {
            "description": "Kode program studi tidak valid atau batas kuota tahunan 9999 terlampaui",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_prodi_code": {
                            "summary": "Kode Prodi Bukan 3 Karakter Alfanumerik",
                            "value": {
                                "detail": "Kode program studi '12' tidak valid. Kode prodi harus terdiri dari 3 karakter alfanumerik (misal 'TIF', 'SIF', atau '001')."
                            },
                        },
                        "quota_exceeded": {
                            "summary": "Batas Kuota NIM Terlampaui (Maksimal 9999)",
                            "value": {
                                "detail": "Batas nomor urut NIM untuk tahun 2026 prodi 001 telah melampaui batas maksimum (9999)."
                            },
                        },
                        "prodi_not_found": {
                            "summary": "Relasi Program Studi Hilang",
                            "value": {
                                "detail": "Program studi calon mahasiswa tidak ditemukan."
                            },
                        },
                    }
                }
            },
        },
        404: {
            "description": "Calon mahasiswa dengan ID yang diminta tidak ditemukan",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Calon mahasiswa dengan ID 9999 tidak ditemukan."
                    }
                }
            },
        },
        409: {
            "description": "Konflik status state machine (calon berstatus rejected) atau konflik integritas konkurensi",
            "content": {
                "application/json": {
                    "examples": {
                        "rejected_conflict": {
                            "summary": "Calon Sudah Berstatus Rejected",
                            "value": {
                                "detail": "Calon mahasiswa sudah berstatus rejected dan tidak dapat disetujui."
                            },
                        },
                        "concurrency_conflict": {
                            "summary": "Konflik Konkurensi Database",
                            "value": {
                                "detail": "Gagal menyetujui pendaftaran setelah beberapa kali percobaan karena konflik integritas data."
                            },
                        },
                    }
                }
            },
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
    description=(
        "Menolak pendaftaran calon mahasiswa baru:\n\n"
        "- **State Machine**: Transisi status dari `pending` ke `rejected`.\n"
        "- **Terminal State**: Calon mahasiswa yang sudah berstatus `approved` bersifat final dan tidak dapat ditolak (409 Conflict).\n"
        "- **Idempotensi**: Pemanggilan berulang pada calon yang sudah berstatus `rejected` mengembalikan HTTP 200 secara aman tanpa mengubah data.\n"
        "- **Isolasi Database**: Menggunakan row-level lock (`with_for_update`) dan commit atomik di akhir transaksi."
    ),
    responses={
        200: {
            "description": "Pendaftaran berhasil ditolak atau sudah berstatus rejected (operasi idempotent)",
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "nama_lengkap": "Siti Aminah",
                        "email": "siti.aminah@example.com",
                        "phone": "081298765432",
                        "program_studi_id": 1,
                        "jalur_masuk_id": 2,
                        "status": "rejected",
                        "nim": None,
                        "created_at": "2026-11-14T10:00:00Z",
                        "approved_at": None,
                    }
                }
            },
        },
        404: {
            "description": "Calon mahasiswa dengan ID yang diminta tidak ditemukan",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Calon mahasiswa dengan ID 9999 tidak ditemukan."
                    }
                }
            },
        },
        409: {
            "description": "Konflik status state machine (calon sudah berstatus approved)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Calon mahasiswa sudah berstatus approved dan tidak dapat ditolak."
                    }
                }
            },
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


@router.get(
    "/status/{id}",
    response_model=PendaftarStatusOut,
    status_code=status.HTTP_200_OK,
    summary="Cek Status Pendaftaran Calon Mahasiswa",
    description=(
        "Mengambil informasi status pendaftaran calon mahasiswa untuk pengecekan publik:\n\n"
        "- **Privacy by Design**: Menyaring secara ketat seluruh data pribadi yang tidak perlu (tidak menampilkan nomor telepon, email, alamat, maupun tanggal lahir).\n"
        "- **Status & NIM**: Menampilkan status seleksi (`pending`, `approved`, atau `rejected`) serta nomor NIM jika calon telah dinyatakan lulus/approved."
    ),
    responses={
        200: {
            "description": "Informasi status pendaftaran calon mahasiswa berhasil diambil",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nama_lengkap": "Ahmad Fauzi",
                        "program_studi_id": 1,
                        "jalur_masuk_id": 1,
                        "status": "approved",
                        "nim": "20260010001",
                        "created_at": "2026-11-14T10:00:00Z",
                        "approved_at": "2026-11-14T10:05:00Z",
                    }
                }
            },
        },
        404: {
            "description": "Calon mahasiswa dengan ID yang diminta tidak ditemukan",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Calon mahasiswa dengan ID 9999 tidak ditemukan."
                    }
                }
            },
        },
    },
)
def get_status(
    id: int,
    db: Session = Depends(get_db),
) -> PendaftarStatusOut:
    """Mengambil status pendaftaran calon mahasiswa (tanpa data pribadi sensitif)."""
    return PMBService.get_status(db, calon_id=id)


@router.get(
    "/stats",
    response_model=PMBStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Ringkasan Statistik Pendaftar PMB",
    description=(
        "Menyajikan ringkasan statistik agregasi pendaftar PMB yang dihitung secara efisien di level mesin basis data:\n\n"
        "- **Statistik per Status**: Jumlah pendaftar per status seleksi (`pending`, `approved`, `rejected`) menggunakan agregasi `GROUP BY` di database.\n"
        "- **Statistik per Program Studi**: Jumlah pendaftar per program studi menggunakan `outerjoin` (program studi tanpa pendaftar tetap tampil dengan angka `0`).\n"
        "- **Statistik per Jalur Masuk**: Jumlah pendaftar per jalur masuk menggunakan `outerjoin` (jalur masuk tanpa pendaftar tetap tampil dengan angka `0`)."
    ),
    responses={
        200: {
            "description": "Ringkasan statistik agregasi pendaftar PMB berhasil dihitung",
            "content": {
                "application/json": {
                    "example": {
                        "per_status": {
                            "pending": 25,
                            "approved": 10,
                            "rejected": 5,
                        },
                        "per_program_studi": [
                            {"id": 1, "kode": "001", "nama": "Teknik Informatika", "total": 20},
                            {"id": 2, "kode": "002", "nama": "Sistem Informasi", "total": 15},
                            {"id": 3, "kode": "003", "nama": "Arsitektur", "total": 5},
                            {"id": 4, "kode": "004", "nama": "Teknik Elektro", "total": 0},
                        ],
                        "per_jalur_masuk": [
                            {"id": 1, "nama": "SNBP", "total": 15},
                            {"id": 2, "nama": "SNBT", "total": 20},
                            {"id": 3, "nama": "Mandiri", "total": 5},
                        ],
                    }
                }
            },
        },
    },
)
def get_stats(
    db: Session = Depends(get_db),
) -> PMBStatsResponse:
    """
    Menyajikan agregasi statistik pendaftar PMB:
    - Jumlah pendaftar per status (GROUP BY di database)
    - Jumlah pendaftar per program studi (outerjoin agar 0 tetap muncul)
    - Jumlah pendaftar per jalur masuk (outerjoin agar 0 tetap muncul)
    """
    return PMBService.get_stats(db)


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


