"""Statistik jawaban per kasus eksperimen (panjang, konsistensi antar pengulangan).

Jalankan: python scripts/answer_stats.py
"""

import difflib
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"


def main():
    files = sorted(RESULTS.glob("*.json"))
    files = [f for f in files if f.name != "run_summary.json"]
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"== {path.stem} ==")
        by_question = {}
        for answer in data["answers"]:
            text = answer["answer"].strip()
            by_question.setdefault(answer["question"], []).append(text)
            print(
                f"  q{list(by_question).index(answer['question'])+1} "
                f"run{answer['repeat']+1}: {len(text)} char, {len(text.split())} kata, "
                f"{answer['elapsed_seconds']}s | skor tertinggi "
                f"{max((s['score'] for s in answer['sources']), default=0):.4f}"
            )
        for question, texts in by_question.items():
            if len(texts) > 1:
                ratio = difflib.SequenceMatcher(None, texts[0], texts[1]).ratio()
                print(f"  kemiripan run1 vs run2: {ratio:.3f}")
        print()


if __name__ == "__main__":
    main()
