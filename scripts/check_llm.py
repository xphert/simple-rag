"""Cek konfigurasi LLM dan uji satu panggilan ke endpoint yang dipakai.

Jalankan: python scripts/check_llm.py
API key selalu ditampilkan dalam bentuk tersamar.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import llm  # noqa: E402
from config import GROQ_MODEL  # noqa: E402


def mask(value):
    if not value:
        return "(kosong)"
    if len(value) <= 8:
        return value[:2] + "*" * (len(value) - 2)
    return f"{value[:4]}...{value[-4:]} (len={len(value)})"


def main():
    print("LLM_API_KEY   :", mask(os.getenv("LLM_API_KEY")))
    print("GROQ_API_KEY  :", mask(os.getenv("GROQ_API_KEY")))
    print("LLM_BASE_URL  :", llm.LLM_BASE_URL or "(kosong)")
    print("LLM_CHAT_URL  :", llm.LLM_CHAT_URL or "(mode lokal)")
    print("LLM_MODEL     :", llm.LLM_MODEL)
    print("GROQ_MODEL    :", GROQ_MODEL)
    print("LLM_TEMPERATURE:", llm.TEMPERATURE)
    print("backend       :", llm.BACKEND)
    print()

    if llm.LLM_CHAT_URL is None:
        print("Tidak ada API key -> mode lokal. Tidak ada yang perlu diuji.")
        return

    try:
        answer = asyncio.run(
            llm.generate_text(
                system_prompt="You are a helpful assistant.",
                user_prompt="Jawab satu kata: halo",
                temperature=0.0,
            )
        )
        print("OK, jawaban:", answer[:200])
    except Exception as error:  # noqa: BLE001
        print("GAGAL:", type(error).__name__)
        print(str(error)[:1500])
        status = getattr(error, "status_code", None)
        body = getattr(error, "body", None)
        if status:
            print("status_code:", status)
        if body:
            print("body:", body)


if __name__ == "__main__":
    main()
