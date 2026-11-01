"""Orkestrasi seluruh eksperimen (temperature, TOP_K, chunk size, chunk overlap).

Setiap kasus dijalankan sebagai proses terpisah agar perubahan parameter pada
config.py / llm.py benar-benar dipakai oleh aplikasi (setara restart server).
Untuk eksperimen chunking, folder qdrant_data dihapus lebih dulu sehingga
ingestion benar-benar dimulai dari basis data kosong.

Jalankan:  python scripts/run_experiments.py [--only temperature,topk,chunk,overlap]
Hasil   :  results/<grup>_<kasus>.json
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.py"
LLM_PATH = BASE_DIR / "llm.py"
QDRANT_PATH = BASE_DIR / "qdrant_data"
RESULTS_DIR = BASE_DIR / "results"
PDF_PATH = BASE_DIR / "data" / "uploads" / "modul-rag-dasar.pdf"

QS = [
    "Berapa dimensi vektor dan batas maksimum token model embedding yang digunakan pada modul ini?",
    "Berapa nilai chunk size dan chunk overlap default pada modul ini, dan mengapa "
    "chunk overlap diperlukan?",
]

BASELINE = {
    "TEMPERATURE": 0.2,
    "TOP_K": 4,
    "CHUNK_SIZE": 100,
    "CHUNK_OVERLAP": 20,
}

CASES = [
    # Experiment 1 - temperature (tidak perlu ingestion ulang)
    {"group": "temperature", "label": "temp_0.0", "patch": {"TEMPERATURE": 0.0}, "reset": True, "ingest": True, "repeats": 2},
    {"group": "temperature", "label": "temp_0.2", "patch": {"TEMPERATURE": 0.2}, "reset": False, "ingest": False, "repeats": 2},
    {"group": "temperature", "label": "temp_0.8", "patch": {"TEMPERATURE": 0.8}, "reset": False, "ingest": False, "repeats": 2},

    # Experiment 2 - TOP_K (database tetap sama)
    {"group": "topk", "label": "topk_1", "patch": {"TOP_K": 1}, "reset": True, "ingest": True, "repeats": 1},
    {"group": "topk", "label": "topk_4", "patch": {"TOP_K": 4}, "reset": False, "ingest": False, "repeats": 1},
    {"group": "topk", "label": "topk_8", "patch": {"TOP_K": 8}, "reset": False, "ingest": False, "repeats": 1},

    # Experiment 3 - chunk size (wajib reset + ingest ulang)
    {"group": "chunk_size", "label": "chunk_50", "patch": {"CHUNK_SIZE": 50, "CHUNK_OVERLAP": 20}, "reset": True, "ingest": True, "repeats": 1},
    {"group": "chunk_size", "label": "chunk_100", "patch": {"CHUNK_SIZE": 100, "CHUNK_OVERLAP": 20}, "reset": True, "ingest": True, "repeats": 1},
    {"group": "chunk_size", "label": "chunk_120", "patch": {"CHUNK_SIZE": 120, "CHUNK_OVERLAP": 20}, "reset": True, "ingest": True, "repeats": 1},

    # Experiment 4 - chunk overlap (wajib reset + ingest ulang)
    {"group": "chunk_overlap", "label": "overlap_0", "patch": {"CHUNK_SIZE": 100, "CHUNK_OVERLAP": 0}, "reset": True, "ingest": True, "repeats": 1},
    {"group": "chunk_overlap", "label": "overlap_20", "patch": {"CHUNK_SIZE": 100, "CHUNK_OVERLAP": 20}, "reset": True, "ingest": True, "repeats": 1},
    {"group": "chunk_overlap", "label": "overlap_40", "patch": {"CHUNK_SIZE": 100, "CHUNK_OVERLAP": 40}, "reset": True, "ingest": True, "repeats": 1},
]


def patch(path: Path, name: str, value):
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^{name}\s*=.*$", re.MULTILINE)
    if not pattern.search(text):
        raise SystemExit(f"tidak menemukan variabel {name} di {path.name}")
    replacement = f"{name} = {value}" if not isinstance(value, str) else f'{name} = "{value}"'
    path.write_text(pattern.sub(replacement, text, count=1), encoding="utf-8")


def reset_qdrant():
    if QDRANT_PATH.exists():
        shutil.rmtree(QDRANT_PATH)
        print("  qdrant_data/ dihapus")


def run_case(ingest: bool, repeats: int) -> dict:
    payload = json.dumps({"ingest": ingest, "questions": QS, "repeats": repeats})
    finished = subprocess.run(
        [sys.executable, str(BASE_DIR / "scripts" / "run_case.py")],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(BASE_DIR),
    )
    if finished.returncode != 0:
        raise SystemExit(f"kasus gagal:\n{(finished.stderr or '')[-3000:]}")
    return json.loads(finished.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="temperature,topk,chunk_size,chunk_overlap")
    parser.add_argument("--force", action="store_true", help="jalankan ulang kasus yang sudah ada hasilnya")
    args = parser.parse_args()
    wanted = {item.strip() for item in args.only.split(",") if item.strip()}

    original_config = CONFIG_PATH.read_text(encoding="utf-8")
    original_llm = LLM_PATH.read_text(encoding="utf-8")
    RESULTS_DIR.mkdir(exist_ok=True)

    summary = []
    try:
        for case in CASES:
            if wanted and case["group"] not in wanted:
                continue
            out = RESULTS_DIR / f"{case['group']}_{case['label']}.json"
            if out.exists() and not args.force:
                print(f"[{case['group']}] {case['label']} - dilewati (sudah ada)")
                continue
            print(f"[{case['group']}] {case['label']}")

            # kembalikan seluruh parameter ke baseline, lalu terapkan patch kasus
            CONFIG_PATH.write_text(original_config, encoding="utf-8")
            LLM_PATH.write_text(original_llm, encoding="utf-8")
            for name, value in BASELINE.items():
                target = LLM_PATH if name == "TEMPERATURE" else CONFIG_PATH
                patch(target, name, value)
            for name, value in case["patch"].items():
                target = LLM_PATH if name == "TEMPERATURE" else CONFIG_PATH
                patch(target, name, value)

            if case["reset"]:
                reset_qdrant()

            result = run_case(case["ingest"], case["repeats"])
            result["group"] = case["group"]
            result["label"] = case["label"]
            result["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

            out = RESULTS_DIR / f"{case['group']}_{case['label']}.json"
            out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            chunks = (result["ingest"] or {}).get("chunks_stored")
            print(f"  -> {out.name} | chunks_stored={chunks} | jawaban={len(result['answers'])}")
            summary.append(result)
    finally:
        CONFIG_PATH.write_text(original_config, encoding="utf-8")
        LLM_PATH.write_text(original_llm, encoding="utf-8")
        print("config.py dan llm.py dikembalikan ke kondisi awal")

    pdf_sha = hashlib.sha256(PDF_PATH.read_bytes()).hexdigest()[:16]
    (RESULTS_DIR / "run_summary.json").write_text(
        json.dumps(
            {
                "pdf": PDF_PATH.name,
                "pdf_sha256_16": pdf_sha,
                "questions": QS,
                "baseline": BASELINE,
                "runs": [
                    {
                        "group": r["group"],
                        "label": r["label"],
                        "config": r["config"],
                        "chunks_stored": (r["ingest"] or {}).get("chunks_stored"),
                    }
                    for r in summary
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
