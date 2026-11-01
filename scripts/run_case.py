"""Jalankan satu kasus eksperimen terhadap aplikasi FastAPI yang sebenarnya.

Skrip ini memanggil endpoint /ingest dan /ask lewat TestClient, sehingga
pipeline yang dieksekusi identik dengan aplikasi yang berjalan di uvicorn.

Input  : JSON pada stdin
         {"ingest": bool, "questions": [str], "repeats": int}
Output : JSON pada stdout
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

import config
import llm
import main

PDF_NAME = "modul-rag-dasar.pdf"
PDF_PATH = str(config.UPLOAD_DIR / PDF_NAME)


def main_case(payload: dict) -> dict:
    client = TestClient(main.app)
    result = {
        "config": {
            "temperature": llm.TEMPERATURE,
            "top_k": config.TOP_K,
            "chunk_size": config.CHUNK_SIZE,
            "chunk_overlap": config.CHUNK_OVERLAP,
            "embedding_model": config.EMBEDDING_MODEL,
            "llm_model": config.GROQ_MODEL,
            "llm_model_aktif": llm.LLM_MODEL,
            "llm_base_url": llm.LLM_BASE_URL,
            "llm_backend": llm.BACKEND,
        },
        "ingest": None,
        "answers": [],
    }

    if payload.get("ingest"):
        started = time.time()
        with open(PDF_PATH, "rb") as file:
            response = client.post(
                "/ingest",
                files={"file": (PDF_NAME, file, "application/pdf")},
            )
        response.raise_for_status()
        result["ingest"] = response.json()
        result["ingest"]["elapsed_seconds"] = round(time.time() - started, 2)

    for question in payload["questions"]:
        for repeat in range(payload.get("repeats", 1)):
            started = time.time()
            response = client.post("/ask", json={"question": question})
            response.raise_for_status()
            body = response.json()
            result["answers"].append({
                "question": question,
                "repeat": repeat,
                "answer": body["answer"],
                "sources": body["sources"],
                "elapsed_seconds": round(time.time() - started, 2),
            })
    return result


if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    # ensure_ascii=True: keluaran aman untuk stdout Windows (cp1252).
    json.dump(main_case(payload), sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.flush()
