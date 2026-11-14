"""Suite pengujian komprehensif untuk mencapai high coverage pada modul PMB.

Mencakup:
- Error handling edge cases (400, 404, 409, kuota 9999, retry exhaustion).
- Boundary validation umur calon mahasiswa (<14 tahun, >80 tahun, null).
- Dialek database MySQL & fallback dialect pada fungsi generator NIM.
- Batas transaksi auto_commit=False (Unit of Work composability).
- Sanitizer & validator Pydantic PMBRegisterRequest.
- OpenAPI generator kustom (ADR-003) & Root health check.
- Lifecycle Session DB get_db() & script seed_data().
- Model representation (__repr__).
"""

from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app, custom_openapi
from app.models.pmb import CalonMahasiswa, JalurMasuk, NimCounter, ProgramStudi, StatusPMB
from app.schemas.pmb import RegisterRequest
from app.seed import seed_data
from app.services.pmb import PMBService, generate_nim


# ==============================================================================
# 1. DATABASE LIFECYCLE & CLI SEEDING
# ==============================================================================

def test_database_get_db_lifecycle():
    """Menguji siklus hidup generator get_db() hingga blok finally: db.close()."""
    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)
    # Menutup generator memicu blok finally
    with pytest.raises(StopIteration):
        next(gen)


def test_seed_data_execution_and_idempotency():
    """Menguji eksekusi script seed_data() dan memastikan operasi idempotent aman."""
    # Eksekusi pada database aktual
    seed_data()
    seed_data()


def test_seed_data_initial_insert_and_exception():
    """Menguji branch insert pertama kali dan penanganan error rollback pada seed_data()."""
    # 1. Uji kondisi data belum ada (db.add terpanggil)
    with patch("app.seed.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_session_local.return_value = mock_db
        seed_data()
        assert mock_db.add.called
        assert mock_db.commit.called

    # 2. Uji kondisi exception saat seeding (db.rollback terpanggil)
    with patch("app.seed.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_db.query.side_effect = RuntimeError("DB error")
        mock_session_local.return_value = mock_db
        seed_data()
        assert mock_db.rollback.called


# ==============================================================================
# 2. MAIN APP: ROOT ENDPOINT & CUSTOM OPENAPI SCHEMA (ADR-003)
# ==============================================================================

def test_root_endpoint_health_check(client):
    """GET /: Endpoint root health check mengembalikan pesan sukses."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "SEVIMA Mini API is running"}


def test_custom_openapi_schema_caching_and_removal_of_422():
    """Menguji generator custom_openapi() menghapus respon 422 dan mendukung caching."""
    # Reset schema cache
    app.openapi_schema = None

    schema = custom_openapi()
    assert schema is not None
    assert "paths" in schema

    # Pastikan kode respons 422 telah dihapus dari seluruh rute
    for path, methods in schema["paths"].items():
        for method, spec in methods.items():
            if "responses" in spec:
                assert "422" not in spec["responses"]

    # Pemanggilan kedua harus mengembalikan schema yang tersimpan di cache
    cached_schema = custom_openapi()
    assert cached_schema is schema


# ==============================================================================
# 3. MODEL REPRESENTATIONS (__repr__)
# ==============================================================================

def test_models_repr():
    """Menguji representasi string (__repr__) pada seluruh model PMB."""
    prodi = ProgramStudi(id=1, kode="001", nama="Teknik Informatika")
    assert "<ProgramStudi(id=1, kode='001', nama='Teknik Informatika')>" == repr(prodi)

    jalur = JalurMasuk(id=1, nama="SNBP")
    assert "<JalurMasuk(id=1, nama='SNBP')>" == repr(jalur)

    calon = CalonMahasiswa(id=10, email="test@example.com", status=StatusPMB.PENDING)
    assert "<CalonMahasiswa(id=10, email='test@example.com', status='StatusPMB.PENDING')>" == repr(calon)

    counter = NimCounter(tahun=2026, kode_prodi="001", last_number=42)
    assert "<NimCounter(tahun=2026, kode_prodi='001', last_number=42)>" == repr(counter)


# ==============================================================================
# 4. SCHEMAS: PHONE SANITIZER & AGE BOUNDARY VALIDATION
# ==============================================================================

def test_schema_phone_sanitizer_non_string():
    """Validator nomor HP mengembalikan nilai apa adanya jika tipe data bukan string."""
    assert RegisterRequest.sanitize_phone_number(12345) == 12345


def test_schema_age_validator_none():
    """Validator umur mengizinkan nilai None jika tanggal lahir tidak diisi."""
    assert RegisterRequest.validate_umur_calon_mahasiswa(None) is None


def test_schema_age_validation_boundaries(client, prodi_ti, jalur_snbp):
    """Menguji penolakan usia calon mahasiswa < 14 tahun dan > 80 tahun (HTTP 400)."""
    today = date.today()

    # 1. Usia di bawah 14 tahun (misal lahir 10 tahun lalu)
    dob_terlalu_muda = f"{today.year - 10}-01-01"
    payload_muda = {
        "nama_lengkap": "Calon Bocil",
        "email": "bocil@example.com",
        "phone": "081234567890",
        "tanggal_lahir": dob_terlalu_muda,
        "program_studi_id": prodi_ti.id,
        "jalur_masuk_id": jalur_snbp.id,
    }
    res_muda = client.post("/api/pmb/register", json=payload_muda)
    assert res_muda.status_code == 400
    assert "minimal 14 tahun" in str(res_muda.json()["errors"])

    # 2. Usia di atas 80 tahun (misal lahir 85 tahun lalu)
    dob_terlalu_tua = f"{today.year - 85}-01-01"
    payload_tua = {
        "nama_lengkap": "Calon Sepuh",
        "email": "sepuh@example.com",
        "phone": "081234567890",
        "tanggal_lahir": dob_terlalu_tua,
        "program_studi_id": prodi_ti.id,
        "jalur_masuk_id": jalur_snbp.id,
    }
    res_tua = client.post("/api/pmb/register", json=payload_tua)
    assert res_tua.status_code == 400
    assert "maksimal 80 tahun" in str(res_tua.json()["errors"])

    # 3. Tanggal lahir None / Null -> registrasi tetap sukses (201 Created)
    payload_null_dob = {
        "nama_lengkap": "Calon Tanpa DOB",
        "email": "nodob@example.com",
        "phone": "081234567890",
        "tanggal_lahir": None,
        "program_studi_id": prodi_ti.id,
        "jalur_masuk_id": jalur_snbp.id,
    }
    res_null = client.post("/api/pmb/register", json=payload_null_dob)
    assert res_null.status_code == 201


# ==============================================================================
# 5. GENERATOR NIM: DIALECTS & RUNTIME ERROR
# ==============================================================================

def test_generate_nim_mysql_dialect(db):
    """Menguji alur UPSERT native saat terhubung ke database dengan dialek MySQL."""
    # Simulasikan dialect name 'mysql'
    mock_dialect = MagicMock()
    mock_dialect.name = "mysql"
    mock_bind = MagicMock()
    mock_bind.dialect = mock_dialect

    with patch.object(db, "bind", mock_bind), \
         patch.object(db, "execute") as mock_exec, \
         patch.object(db, "scalar") as mock_scalar:
        mock_counter = NimCounter(tahun=2026, kode_prodi="001", last_number=5)
        mock_scalar.return_value = mock_counter

        nim = generate_nim(db, tahun=2026, kode_prodi="001")
        assert nim == "20260010006"
        assert mock_counter.last_number == 6
        assert mock_exec.called


def test_generate_nim_other_dialect(db):
    """Menguji alur fallback savepoint (nested transaction) untuk dialek lain (PostgreSQL dll)."""
    with patch.object(db, "bind") as mock_bind:
        mock_bind.dialect.name = "postgresql"
        mock_counter = NimCounter(tahun=2026, kode_prodi="002", last_number=0)
        with patch.object(db, "begin_nested"), \
             patch.object(db, "add"), \
             patch.object(db, "flush"), \
             patch.object(db, "scalar", return_value=mock_counter):
            nim = generate_nim(db, tahun=2026, kode_prodi="002")
            assert nim == "20260020001"
            assert mock_counter.last_number == 1


def test_generate_nim_other_dialect_integrity_error(db):
    """Menguji fallback savepoint menangani IntegrityError jika worker lain sudah menginisialisasi baris."""
    with patch.object(db, "bind") as mock_bind:
        mock_bind.dialect.name = "postgresql"
        mock_counter = NimCounter(tahun=2026, kode_prodi="003", last_number=0)
        with patch.object(db, "begin_nested", side_effect=IntegrityError("Conflict", None, None)), \
             patch.object(db, "scalar", return_value=mock_counter):
            nim = generate_nim(db, tahun=2026, kode_prodi="003")
            assert nim == "20260030001"
            assert mock_counter.last_number == 1


def test_generate_nim_counter_none_raises_runtime_error(db):
    """Menguji pelemparan RuntimeError jika kueri record lock mengembalikan None setelah upsert."""
    with patch.object(db, "scalar", return_value=None):
        with pytest.raises(RuntimeError, match="Gagal menginisialisasi atau mengunci baris counter"):
            generate_nim(db, tahun=2026, kode_prodi="001")


# ==============================================================================
# 6. REGISTRATION SERVICE: RACE CONDITION INTEGRITY ERRORS (SAFETY NET)
# ==============================================================================

def test_register_commit_race_condition_unique_email(db, prodi_ti, jalur_snbp):
    """Menguji penanganan IntegrityError akibat race condition unique email saat commit (HTTP 409)."""
    req = RegisterRequest(
        nama_lengkap="Calon Balapan",
        email="balapan.email@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
    )
    mock_orig = Exception("UNIQUE constraint failed: calon_mahasiswa.email")
    with patch.object(db, "commit", side_effect=IntegrityError("Conflict", None, mock_orig)):
        with pytest.raises(HTTPException) as exc_info:
            PMBService.register(db, req)
        assert exc_info.value.status_code == 409
        assert "Email sudah terdaftar" in exc_info.value.detail


def test_register_commit_race_condition_foreign_key(db, prodi_ti, jalur_snbp):
    """Menguji penanganan IntegrityError akibat pelanggaran foreign key saat commit (HTTP 400)."""
    req = RegisterRequest(
        nama_lengkap="Calon FK Error",
        email="fk.error@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
    )
    mock_orig = Exception("FOREIGN KEY constraint failed")
    with patch.object(db, "commit", side_effect=IntegrityError("Conflict", None, mock_orig)):
        with pytest.raises(HTTPException) as exc_info:
            PMBService.register(db, req)
        assert exc_info.value.status_code == 400
        assert "Referensi program studi atau jalur masuk tidak valid" in exc_info.value.detail


def test_register_commit_race_condition_check_constraint(db, prodi_ti, jalur_snbp):
    """Menguji penanganan IntegrityError akibat pelanggaran check constraint saat commit (HTTP 400)."""
    req = RegisterRequest(
        nama_lengkap="Calon Check Error",
        email="check.error@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
    )
    mock_orig = Exception("CHECK constraint failed")
    with patch.object(db, "commit", side_effect=IntegrityError("Conflict", None, mock_orig)):
        with pytest.raises(HTTPException) as exc_info:
            PMBService.register(db, req)
        assert exc_info.value.status_code == 400
        assert "melanggar batasan constraint basis data" in exc_info.value.detail


def test_register_commit_race_condition_fallback_conflict(db, prodi_ti, jalur_snbp):
    """Menguji penanganan IntegrityError fallback umum jika terjadi race condition tak terduga (HTTP 409)."""
    req = RegisterRequest(
        nama_lengkap="Calon Fallback Error",
        email="fallback.error@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
    )
    mock_orig = Exception("database is locked")
    with patch.object(db, "commit", side_effect=IntegrityError("Conflict", None, mock_orig)):
        with pytest.raises(HTTPException) as exc_info:
            PMBService.register(db, req)
        assert exc_info.value.status_code == 409
        assert "konflik integritas data" in exc_info.value.detail.lower()


# ==============================================================================
# 7. APPROVAL SERVICE: RETRY EXHAUSTION, KUOTA 9999, ORPHAN PRODI, AUTO_COMMIT
# ==============================================================================

def test_approve_retry_exhaustion_raises_409(db, prodi_ti, jalur_snbp):
    """Memastikan bahwa jika seluruh percobaan retry gagal karena IntegrityError, sistem melempar HTTP 409."""
    calon = CalonMahasiswa(
        nama_lengkap="Calon Gagal Retry",
        email="fail.retry@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
        status=StatusPMB.PENDING,
    )
    db.add(calon)
    db.commit()

    with patch.object(db, "commit", side_effect=IntegrityError("Always fail", None, None)), \
         patch.object(db, "rollback", wraps=db.rollback) as spy_rollback:
        with pytest.raises(HTTPException) as exc_info:
            PMBService.approve(db, calon_id=calon.id, max_retries=3)

        assert exc_info.value.status_code == 409
        assert "Gagal menyetujui pendaftaran setelah beberapa kali percobaan" in exc_info.value.detail
        # Memastikan rollback dipanggil pada setiap iterasi (3 kali)
        assert spy_rollback.call_count == 3


def test_approve_quota_9999_exceeded_via_endpoint(client, db, prodi_ti, jalur_snbp):
    """PUT /api/pmb/approve/{id}: Menolak dengan HTTP 400 jika batas nomor urut NIM 9999 telah terlampaui."""
    # 1. Daftarkan calon
    calon = CalonMahasiswa(
        nama_lengkap="Calon Kuota Penuh",
        email="penuh@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
        status=StatusPMB.PENDING,
    )
    db.add(calon)
    db.commit()

    # 2. Atur counter prodi mencapai 9999
    tahun_ini = date.today().year
    counter = NimCounter(tahun=tahun_ini, kode_prodi=prodi_ti.kode, last_number=9999)
    db.merge(counter)
    db.commit()

    # 3. Panggil endpoint approval
    res = client.put(f"/api/pmb/approve/{calon.id}")
    assert res.status_code == 400
    assert "9999" in res.json()["detail"]


def test_approve_calon_orphan_prodi_raises_400(db, jalur_snbp):
    """PMBService.approve: Melempar HTTP 400 jika relasi program studi tidak ditemukan."""
    calon = CalonMahasiswa(
        id=8888,
        nama_lengkap="Calon Tanpa Prodi",
        email="tanpaprodi@example.com",
        phone="081234567890",
        program_studi_id=9999,
        jalur_masuk_id=jalur_snbp.id,
        status=StatusPMB.PENDING,
    )
    # Mock calon dengan program_studi = None
    calon.program_studi = None

    with patch.object(db, "scalar", return_value=calon):
        with pytest.raises(HTTPException) as exc_info:
            PMBService.approve(db, calon_id=calon.id)
        assert exc_info.value.status_code == 400
        assert "Program studi calon mahasiswa tidak ditemukan" in exc_info.value.detail


def test_approve_and_reject_with_auto_commit_false(db, prodi_ti, jalur_snbp):
    """Menguji composability unit-of-work: auto_commit=False hanya melakukan flush tanpa commit permanen."""
    calon1 = CalonMahasiswa(
        nama_lengkap="Calon Unit of Work 1",
        email="uow1@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
        status=StatusPMB.PENDING,
    )
    calon2 = CalonMahasiswa(
        nama_lengkap="Calon Unit of Work 2",
        email="uow2@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
        status=StatusPMB.PENDING,
    )
    db.add_all([calon1, calon2])
    db.commit()

    with patch.object(db, "commit") as mock_commit:
        # Act 1: approve calon1 dengan auto_commit=False
        app1 = PMBService.approve(db, calon_id=calon1.id, auto_commit=False)
        assert app1.status == StatusPMB.APPROVED
        assert app1.nim is not None

        # Act 2: reject calon2 dengan auto_commit=False
        rej2 = PMBService.reject(db, calon_id=calon2.id, auto_commit=False)
        assert rej2.status == StatusPMB.REJECTED

        # Assert: db.commit tidak pernah dipanggil
        assert not mock_commit.called


def test_approve_and_reject_generic_exception_handling(db, prodi_ti, jalur_snbp):
    """Menguji blok penanganan exception tak terduga pada approve dan reject (rollback & re-raise)."""
    calon = CalonMahasiswa(
        nama_lengkap="Calon Crash",
        email="crash@example.com",
        phone="081234567890",
        program_studi_id=prodi_ti.id,
        jalur_masuk_id=jalur_snbp.id,
        status=StatusPMB.PENDING,
    )
    db.add(calon)
    db.commit()

    # 1. Approve generic crash
    with patch("app.services.pmb.generate_nim", side_effect=ZeroDivisionError("Unexpected")), \
         patch.object(db, "rollback") as mock_rollback:
        with pytest.raises(ZeroDivisionError):
            PMBService.approve(db, calon_id=calon.id)
        assert mock_rollback.called

    # 2. Reject generic crash
    with patch.object(db, "commit", side_effect=ValueError("Unexpected reject error")), \
         patch.object(db, "rollback") as mock_rollback2:
        with pytest.raises(ValueError):
            PMBService.reject(db, calon_id=calon.id)
        assert mock_rollback2.called
