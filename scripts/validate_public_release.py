"""Fail if the portfolio copy contains known private-release materials."""
from __future__ import annotations

from pathlib import Path
import csv
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERN = re.compile(r"AIza[0-9A-Za-z_-]{20,}")
PROHIBITED_PROCESSED = {
    "news_articles.csv",
    "news_articles_sentiment.csv",
    "youtube_comments_anonymized.csv",
    "youtube_comments_sentiment.csv",
    "youtube_videos.csv",
}
PROHIBITED_PUBLIC_COLUMNS = {
    "comment", "content", "description", "title", "url", "video_id", "video_hash",
}


def errors() -> list[str]:
    findings: list[str] = []
    raw = ROOT / "data" / "raw"
    if raw.exists():
        for path in raw.iterdir():
            if path.name != ".gitkeep":
                findings.append(f"raw source file present: {path.relative_to(ROOT)}")

    processed = ROOT / "data" / "processed"
    if processed.exists():
        for name in PROHIBITED_PROCESSED:
            if (processed / name).exists():
                findings.append(f"full-text/identifying processed file present: data/processed/{name}")

    for path in [ROOT / "resources" / "dict.txt.big", *ROOT.glob("figures/*.html")]:
        if path.exists():
            findings.append(f"non-public asset present: {path.relative_to(ROOT)}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.name.endswith((".png", ".pyc")):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET_PATTERN.search(text):
            findings.append(f"possible Google API key present: {path.relative_to(ROOT)}")

    for path in (ROOT / "data" / "public").glob("*.csv"):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            columns = set(next(csv.reader(handle), []))
        bad = columns & PROHIBITED_PUBLIC_COLUMNS
        if bad:
            findings.append(f"prohibited public columns in {path.relative_to(ROOT)}: {sorted(bad)}")

    if not (ROOT / "src" / "config.py").exists():
        findings.append("required source file missing: src/config.py")
    return findings


if __name__ == "__main__":
    findings = errors()
    if findings:
        print("PUBLIC RELEASE CHECK: FAIL")
        print("\n".join(f"- {item}" for item in findings))
        raise SystemExit(1)
    print("PUBLIC RELEASE CHECK: PASS")
