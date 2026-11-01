"""Unduh model LLM lokal tanpa melalui CDN huggingface_hub (yang gagal resolve).

Dipakai hanya untuk menyiapkan mode offline. Jika GROQ_API_KEY tersedia,
skrip ini tidak diperlukan.

Output: models/Qwen2.5-0.5B-Instruct/
Jalankan: python scripts/download_local_model.py
"""

import concurrent.futures as futures
import os
import sys
import threading
import time
from pathlib import Path

import requests

REPO = os.getenv("DL_REPO", "Qwen/Qwen2.5-0.5B-Instruct")
BASE = f"https://huggingface.co/{REPO}/resolve/main/"
DEST = Path(__file__).resolve().parent.parent / "models" / REPO.split("/")[-1]
SMALL_FILES = [
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
]
BIG_FILE = "model.safetensors"
PARTS = int(os.getenv("DL_PARTS", "1"))
HEADERS = {"User-Agent": "rag-experiment-setup/1.0"}

progress = {"done": 0}
lock = threading.Lock()


def fetch_small(name: str):
    target = DEST / name
    if target.exists() and target.stat().st_size > 0:
        return
    response = requests.get(BASE + name, timeout=60, headers=HEADERS)
    response.raise_for_status()
    target.write_bytes(response.content)
    print(f"  {name}: {len(response.content)/1024:.0f} kB", flush=True)


def total_size(name: str) -> int:
    response = requests.head(BASE + name, allow_redirects=True, timeout=60, headers=HEADERS)
    response.raise_for_status()
    return int(response.headers["Content-Length"])


def fetch_part(index: int, start: int, end: int, expected: int):
    part = DEST / f"{BIG_FILE}.part{index}"
    if part.exists() and part.stat().st_size == expected:
        with lock:
            progress["done"] += expected
        return
    headers = {"Range": f"bytes={start}-{end}"}
    for attempt in range(6):
        written = part.stat().st_size if part.exists() else 0
        if written == expected:
            with lock:
                progress["done"] += expected
            return
        try:
            with requests.get(BASE + BIG_FILE, headers={**HEADERS, **headers, "Range": f"bytes={start + written}-{end}"},
                              stream=True, timeout=120) as response:
                response.raise_for_status()
                with open(part, "ab") as handle:
                    for block in response.iter_content(1 << 16):
                        handle.write(block)
                        with lock:
                            progress["done"] += len(block)
        except Exception as error:  # noqa: BLE001
            print(f"  part {index} attempt {attempt + 1} error: {error}", flush=True)
            time.sleep(3)


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"target: {DEST}", flush=True)
    for name in SMALL_FILES:
        fetch_small(name)

    marker = DEST / ".parts"
    previous = marker.read_text(encoding="utf-8").strip() if marker.exists() else ""
    if previous != str(PARTS):
        for stale in DEST.glob(f"{BIG_FILE}.part*"):
            stale.unlink()
        marker.write_text(str(PARTS), encoding="utf-8")
        print(f"  jumlah koneksi berubah ({previous or '?'} -> {PARTS}), unduhan lama dibuang", flush=True)

    size = total_size(BIG_FILE)
    print(f"  {BIG_FILE}: {size/1024/1024:.0f} MB, {PARTS} koneksi")
    chunk = size // PARTS
    ranges = []
    for index in range(PARTS):
        start = index * chunk
        end = size - 1 if index == PARTS - 1 else (index + 1) * chunk - 1
        ranges.append((index, start, end, end - start + 1))

    started = time.time()
    with futures.ThreadPoolExecutor(max_workers=PARTS) as pool:
        jobs = [pool.submit(fetch_part, *item) for item in ranges]
        while not all(job.done() for job in jobs):
            time.sleep(5)
            elapsed = time.time() - started
            speed = progress["done"] / 1024 / max(elapsed, 1)
            print(f"  {progress['done']/1024/1024:6.0f}/{size/1024/1024:.0f} MB  {speed:5.0f} kB/s")
        for job in jobs:
            job.result()

    target = DEST / BIG_FILE
    with open(target, "wb") as out:
        for index, *_ in ranges:
            out.write((DEST / f"{BIG_FILE}.part{index}").read_bytes())
    for index, *_ in ranges:
        (DEST / f"{BIG_FILE}.part{index}").unlink()

    actual = target.stat().st_size
    print(f"selesai: {actual/1024/1024:.0f} MB (harusnya {size/1024/1024:.0f} MB)")
    return 0 if actual == size else 1


if __name__ == "__main__":
    sys.exit(main())
