#!/usr/bin/env python3
"""
Skrip Pengujian Konkurensi Manual: Persetujuan Pendaftaran PMB (Multi-Worker Safe).

Tujuan:
- Mendaftarkan N pasang calon mahasiswa dummy dengan Program Studi yang sama.
- Menembakkan request PUT /api/pmb/approve/{id} secara serentak (paralel) menggunakan
  threading dan threading.Barrier untuk menyamakan milidetik request.
- Memverifikasi secara otomatis:
  1. Semua request berhasil (HTTP 200).
  2. Tidak ada NIM kembar / duplikat (Keunikan 100%).
  3. Nomor urut NIM berurutan tanpa ada celah (gapless sequential sequence).
"""

import argparse
import sys
import threading
import time
import uuid
from typing import Dict, List, Optional
import requests

# Konfigurasi Default
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_NUM_PAIRS = 5  # 5 pasang = 10 pendaftar


def daftarkan_calon(base_url: str, prodi_id: int, jalur_id: int, label: str) -> Dict:
    """Mendaftarkan satu calon mahasiswa dummy ke endpoint POST /api/pmb/register."""
    unique_suffix = uuid.uuid4().hex[:6]
    # Nomor HP valid format Indonesia (+62 / 08...)
    random_digits = "".join([str(int(c, 16) % 10) for c in unique_suffix])
    phone_number = f"08123{random_digits}".ljust(12, "0")[:12]

    payload = {
        "nama_lengkap": f"Dummy Concurrency {label} {unique_suffix}",
        "email": f"concurrency.{label}.{unique_suffix}@example.com",
        "phone": phone_number,
        "tanggal_lahir": "2005-08-17",
        "alamat": "Jl. Konkurensi No. 42, Jakarta",
        "program_studi_id": prodi_id,
        "jalur_masuk_id": jalur_id,
    }

    url = f"{base_url.rstrip('/')}/api/pmb/register"
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code != 201:
        raise RuntimeError(
            f"Gagal mendaftarkan calon dummy ({resp.status_code}): {resp.text}"
        )
    return resp.json()


def approve_worker(
    base_url: str,
    calon_id: int,
    barrier: threading.Barrier,
    results_list: List[Dict],
    worker_label: str,
):
    """Worker thread yang menunggu di Barrier sebelum serentak menembak PUT /approve/{id}."""
    url = f"{base_url.rstrip('/')}/api/pmb/approve/{calon_id}"

    # Tunggu seluruh worker siap di garis start
    barrier.wait()

    start_time = time.perf_counter()
    try:
        resp = requests.put(url, timeout=15)
        duration_ms = (time.perf_counter() - start_time) * 1000
        results_list.append({
            "worker": worker_label,
            "calon_id": calon_id,
            "status_code": resp.status_code,
            "data": resp.json() if resp.status_code == 200 else None,
            "error": resp.text if resp.status_code != 200 else None,
            "duration_ms": duration_ms,
        })
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        results_list.append({
            "worker": worker_label,
            "calon_id": calon_id,
            "status_code": 0,
            "data": None,
            "error": str(exc),
            "duration_ms": duration_ms,
        })


def main():
    parser = argparse.ArgumentParser(
        description="Uji Konkurensi Pengiriman Request Approval PMB Paralel."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL server API (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--pairs",
        type=int,
        default=DEFAULT_NUM_PAIRS,
        help=f"Jumlah pasang request paralel (default: {DEFAULT_NUM_PAIRS} pasang = {DEFAULT_NUM_PAIRS * 2} request)",
    )
    parser.add_argument(
        "--prodi-id",
        type=int,
        default=1,
        help="ID Program Studi target (default: 1)",
    )
    parser.add_argument(
        "--jalur-id",
        type=int,
        default=1,
        help="ID Jalur Masuk target (default: 1)",
    )

    args = parser.parse_args()
    base_url = args.url
    num_pairs = args.pairs
    prodi_id = args.prodi_id
    jalur_id = args.jalur_id

    total_requests = num_pairs * 2

    print("=" * 80)
    print("🚀 PENGUJIAN KONKURENSI MANUAL: MULTI-WORKER APPROVE NIM GENERATOR")
    print("=" * 80)
    print(f"Target Base URL     : {base_url}")
    print(f"Program Studi ID    : {prodi_id}")
    print(f"Jalur Masuk ID      : {jalur_id}")
    print(f"Jumlah Pasangan     : {num_pairs} pasang ({total_requests} total pendaftar)")
    print("=" * 80)

    # 1. Pengecekan Konektivitas Health Check
    try:
        health_resp = requests.get(f"{base_url.rstrip('/')}/", timeout=5)
        if health_resp.status_code != 200:
            print(f"⚠️  Peringatan: Server merespons health check dengan status {health_resp.status_code}")
    except Exception as e:
        print(f"❌ ERROR: Tidak dapat terhubung ke server di {base_url}.")
        print(f"   Pastikan server FastAPI/Uvicorn sudah berjalan: {e}")
        sys.exit(1)

    print("\n[Langkah 1] Menyiapkan dan mendaftarkan calon mahasiswa dummy...")
    pairs_data = []
    for i in range(1, num_pairs + 1):
        try:
            calon_a = daftarkan_calon(base_url, prodi_id, jalur_id, label=f"P{i}A")
            calon_b = daftarkan_calon(base_url, prodi_id, jalur_id, label=f"P{i}B")
            pairs_data.append((calon_a, calon_b))
            print(f"  ✓ Pasangan {i:02d}: ID {calon_a['id']} & ID {calon_b['id']} terdaftar (status: pending)")
        except Exception as e:
            print(f"  ❌ Gagal mendaftarkan pasangan {i}: {e}")
            sys.exit(1)

    print(f"\n[Langkah 2] Menembakkan approval paralel untuk {num_pairs} pasang calon mahasiswa...")
    all_results: List[Dict] = []

    for pair_idx, (calon_a, calon_b) in enumerate(pairs_data, start=1):
        barrier = threading.Barrier(2)
        pair_results: List[Dict] = []

        thread_a = threading.Thread(
            target=approve_worker,
            args=(base_url, calon_a["id"], barrier, pair_results, f"Pasangan {pair_idx:02d}-A"),
        )
        thread_b = threading.Thread(
            target=approve_worker,
            args=(base_url, calon_b["id"], barrier, pair_results, f"Pasangan {pair_idx:02d}-B"),
        )

        thread_a.start()
        thread_b.start()

        thread_a.join()
        thread_b.join()

        all_results.extend(pair_results)
        time.sleep(0.05)  # Jeda mikro antar-pasang

    print("\n[Langkah 3] Hasil Eksekusi Respons Endpoint:")
    print("-" * 80)
    print(f"{'Worker':<18} | {'Calon ID':<9} | {'HTTP':<5} | {'NIM Terbit':<15} | {'Latency':<10}")
    print("-" * 80)

    nims_collected: List[str] = []
    errors: List[str] = []

    for r in all_results:
        calon_id = r["calon_id"]
        status_code = r["status_code"]
        duration = f"{r['duration_ms']:.1f} ms"
        if status_code == 200 and r["data"]:
            nim = r["data"].get("nim", "NONE")
            nims_collected.append(nim)
            print(f"{r['worker']:<18} | {calon_id:<9} | {status_code:<5} | {nim:<15} | {duration:<10}")
        else:
            errors.append(f"Worker {r['worker']} (ID {calon_id}) gagal ({status_code}): {r['error']}")
            print(f"{r['worker']:<18} | {calon_id:<9} | {status_code:<5} | {'ERROR':<15} | {duration:<10}")

    print("-" * 80)

    # 4. Verifikasi Integritas Data & Konkurensi
    print("\n[Langkah 4] Verifikasi Hasil Uji Konkurensi:")
    print("-" * 80)

    success_count = len(nims_collected)
    print(f"Total Request Dikirim : {total_requests}")
    print(f"Total Berhasil (200)  : {success_count} / {total_requests}")

    if errors:
        print("\n⚠️  Ditemukan Error Selama Eksekusi:")
        for err in errors:
            print(f"  - {err}")

    # Uji 1: Keunikan NIM (No duplicates)
    unique_nims = set(nims_collected)
    is_unique = len(unique_nims) == len(nims_collected)

    if is_unique:
        print(f"✅ UJI KEUNIKAN: LOLOS (Semua {len(nims_collected)} NIM unik, TIDAK ADA NIM KEMBAR)")
    else:
        duplicates = [nim for nim in unique_nims if nims_collected.count(nim) > 1]
        print(f"❌ UJI KEUNIKAN: GAGAL (Ditemukan duplikasi NIM: {duplicates})")

    # Uji 2: Urutan Berurutan Tanpa Celah (Gapless Sequence)
    # Ekstrak 4 digit nomor urut terakhir
    sequences = sorted([int(nim[-4:]) for nim in nims_collected if nim[-4:].isdigit()])
    is_gapless = True
    gap_details = []

    for idx in range(len(sequences) - 1):
        diff = sequences[idx + 1] - sequences[idx]
        if diff != 1:
            is_gapless = False
            gap_details.append(f"Celah antara urutan {sequences[idx]} dan {sequences[idx + 1]} (selisih: {diff})")

    if sequences:
        print(f"Rentang Urutan Terbit : {sequences[0]:04d} s/d {sequences[-1]:04d} (total: {len(sequences)})")

    if is_gapless and len(sequences) == total_requests:
        print(f"✅ UJI SEKUENSIAL: LOLOS (Semua nomor urut berurutan presisi tanpa celah/gap)")
    else:
        if not is_gapless:
            print(f"❌ UJI SEKUENSIAL: GAGAL (Ditemukan celah nomor urut loncat)")
            for g in gap_details:
                print(f"   - {g}")
        else:
            print(f"⚠️  UJI SEKUENSIAL: Parsial (Jumlah berhasil {len(sequences)} != {total_requests})")

    print("=" * 80)

    if is_unique and is_gapless and (success_count == total_requests):
        print("🎉 KESIMPULAN: MEKANISME ROW-LOCK & GENERATOR NIM BERJALAN SEMPURNA!")
        print("   Database row lock (FOR UPDATE) berhasil mengisolasi request konkuren secara atomik.")
        sys.exit(0)
    else:
        print("💥 KESIMPULAN: PENGUJIAN KONKURENSI MENGINDIKASIKAN ANOMALI DATA.")
        sys.exit(1)


if __name__ == "__main__":
    main()
