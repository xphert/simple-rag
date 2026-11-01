"""Isi placeholder README dengan keluaran asli dari results/*.json.

Placeholder yang didukung:
  {{ANS:kasus:q:run}}  -> jawaban (blockquote)
  {{SRC:kasus:q}}      -> tabel sumber + skor
  {{CHUNKS:kasus}}     -> jumlah chunk tersimpan
  {{TIME:kasus:q:run}} -> waktu tanggap

Jalankan: python scripts/build_readme.py
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
README = BASE / "README.md"
RESULTS = BASE / "results"

PATTERN = re.compile(r"\{\{(ANS|SRC|CHUNKS|TIME):([a-z0-9_.]+)(?::(\d+))?(?::(\d+))?\}\}")


def load(case: str) -> dict:
    return json.loads((RESULTS / f"{case}.json").read_text(encoding="utf-8"))


def answer_of(data: dict, question_index: int, repeat: int) -> dict:
    answers = [
        item for item in data["answers"]
        if item["question"].startswith("Berapa dimensi" if question_index == 1 else "Berapa nilai")
    ]
    return answers[repeat]


def quote(text: str) -> str:
    lines = []
    for line in text.strip().splitlines():
        lines.append(f"> {line}" if line.strip() else ">")
    return "\n".join(lines)


def sources_table(sources: list[dict]) -> str:
    if not sources:
        return "_(tidak ada sumber)_"
    rows = ["| Peringkat | Halaman | Skor kemiripan |", "| --- | --- | --- |"]
    for index, item in enumerate(sources, start=1):
        rows.append(f"| {index} | hal. {item['page']} | {item['score']:.4f} |")
    return "\n".join(rows)


def replace(match: re.Match) -> str:
    kind, case, first, second = match.groups()
    data = load(case)
    if kind == "CHUNKS":
        stored = (data["ingest"] or {}).get("chunks_stored")
        return str(stored) if stored is not None else "-"
    question_index = int(first)
    repeat = int(second or 0)
    if kind == "SRC":
        return sources_table(answer_of(data, question_index, 0)["sources"])
    answer = answer_of(data, question_index, repeat)
    if kind == "TIME":
        return f"{answer['elapsed_seconds']} detik"
    return quote(answer["answer"])


def main():
    text = README.read_text(encoding="utf-8")
    text = PATTERN.sub(replace, text)
    leftover = re.findall(r"\{\{[^}]+\}\}", text)
    if leftover:
        raise SystemExit(f"placeholder belum terisi: {sorted(set(leftover))}")
    README.write_text(text, encoding="utf-8")
    print(f"README.md diperbarui dari {len(list(RESULTS.glob('*.json')))} berkas hasil")


if __name__ == "__main__":
    main()
