from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers.pmb import router as pmb_router

app = FastAPI(
    title="SEVIMA Mini - Sistem Informasi Akademik",
    description="Backend API untuk modul Penerimaan Mahasiswa Baru (PMB) dan Akademik",
    version="1.0.0",
)


# Ubah handler RequestValidationError agar merespons HTTP 400 (Bad Request)
# dengan pesan error yang ramah dan terstruktur (bukan HTTP 422 default)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    friendly_errors = []
    for err in exc.errors():
        # Ambil nama field dari lokasi error (mengabaikan prefix 'body')
        field_loc = [str(loc) for loc in err.get("loc", []) if loc != "body"]
        field_name = " -> ".join(field_loc) if field_loc else "input"
        msg = err.get("msg", "Format data tidak valid")

        # Bersihkan prefix bawaan Pydantic v2
        if msg.startswith("Value error, "):
            msg = msg.replace("Value error, ", "")

        # Transformasi pesan agar lebih ramah bagi pengguna
        if "string_too_short" in err.get("type", ""):
            msg = f"Panjang minimal adalah {err.get('ctx', {}).get('min_length', 3)} karakter"
        elif "value_error" in err.get("type", "") and "email" in field_name:
            msg = "Format alamat email tidak valid"
        elif "string_pattern_mismatch" in err.get("type", ""):
            msg = "Format nomor HP tidak valid (harus nomor Indonesia dengan awalan 08, 62, atau +62)"
        elif "greater_than" in err.get("type", ""):
            msg = "Nilai harus lebih besar dari 0"

        friendly_errors.append(f"{field_name}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Data pendaftaran yang dikirimkan tidak valid",
            "errors": friendly_errors,
        },
    )


# Register Routers
app.include_router(pmb_router)


@app.get("/", tags=["Health Check"])
def root():
    return {"message": "SEVIMA Mini API is running"}
