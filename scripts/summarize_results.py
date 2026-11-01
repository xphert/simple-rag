"""Ringkas hasil eksperimen di folder results/ menjadi tabel Markdown.

Jalankan: python scripts/summarize_results.py
Output  : results/summary.md
"""

import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"

import hashlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_experiments import (  # noqa: E402
    BASELINE,
    PDF_PATH,
    QS as QUESTIONS,
)

GROUPS = [
    ("temperature", "Experiment 1 - Temperature"),
    ("topk", "Experiment 2 - TOP_K"),
    ("chunk_size", "Experiment 3 - Chunk Size"),
    ("chunk_overlap", "Experiment 4 - Chunk Overlap"),
]

PARAM = {
    "temperature": "temperature",
    "topk": "top_k",
    "chunk_size": "chunk_size",
    "chunk_overlap": "chunk_overlap",
}


def load(group: str):
    files = sorted(RESULTS.glob(f"{group}_*.json"))
    return [(path.stem, json.loads(path.read_text(encoding="utf-8"))) for path in files]


def sources_cell(sources) -> str:
    if not sources:
        return "-"
    return "<br>".join(
        f"hal. {item['page']} ({item['score']:.4f})" for item in sources
    )


def main():
    lines = ["# Ringkasan Hasil Eksperimen", ""]
    for group, title in GROUPS:
        runs = load(group)
        if not runs:
            continue
        key = PARAM[group]
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| {key} | chunks_stored | pertanyaan | jawaban | sumber (halaman / skor) |")
        lines.append("| --- | --- | --- | --- | --- |")
        for _, run in runs:
            value = run["config"][key]
            chunks = (run["ingest"] or {}).get("chunks_stored", "-")
            for answer in run["answers"]:
                label = answer["question"][:38] + "..."
                if answer["repeat"]:
                    label += f" (ulang {answer['repeat']})"
                text = answer["answer"].replace("\n", " ").replace("|", "/")
                lines.append(
                    f"| {value} | {chunks} | {label} | {text} | {sources_cell(answer['sources'])} |"
                )
        lines.append("")
    out = RESULTS / "summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: {out}")

    runs = []
    for group, _ in GROUPS:
        for _, run in load(group):
            runs.append({
                "group": run["group"],
                "label": run["label"],
                "config": run["config"],
                "chunks_stored": (run["ingest"] or {}).get("chunks_stored"),
                "timestamp": run.get("timestamp"),
            })
    summary = RESULTS / "run_summary.json"
    summary.write_text(
        json.dumps(
            {
                "pdf": PDF_PATH.name,
                "pdf_sha256_16": hashlib.sha256(PDF_PATH.read_bytes()).hexdigest()[:16],
                "questions": QUESTIONS,
                "baseline": BASELINE,
                "runs": runs,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"written: {summary} ({len(runs)} kasus)")


if __name__ == "__main__":
    main()
