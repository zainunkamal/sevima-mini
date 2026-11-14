from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pmb import PendaftarOut, RegisterRequest
from app.services.pmb import register_calon_mahasiswa

router = APIRouter(prefix="/api/pmb", tags=["PMB"])


@router.post(
    "/register",
    response_model=PendaftarOut,
    status_code=status.HTTP_201_CREATED,
    summary="Pendaftaran Calon Mahasiswa Baru",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> PendaftarOut:
    """Menerima dan memproses pendaftaran calon mahasiswa baru (Thin Controller)."""
    return register_calon_mahasiswa(db, payload)
