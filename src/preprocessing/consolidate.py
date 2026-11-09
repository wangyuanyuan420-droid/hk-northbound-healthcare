"""Consolidate per-outlet, per-year YouTube video exports into one dataset.

The original project stored video metadata in ~20 separate Excel files, one
per news outlet per year (e.g. ``hk01_北上videos_2023.xlsx``). This module
merges them into a single tidy, analysis-ready table with explicit ``outlet``
and ``year`` columns, and de-duplicates by video URL.

Run:  python -m src.preprocessing.consolidate
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd

# Map filename keywords -> canonical outlet name
OUTLET_MAP = {
    "hk01": "HK01",
    "HK01": "HK01",
    "點新聞": "DotDotNews",
    "大公報": "TaKungPao",
    "星島": "SingTao",
    "TKP": "TaKungPao",
}

STD_COLS = ["Title", "Description", "URL", "Publish Time",
            "Like Count", "Comment Count", "View Count"]


def _detect_outlet(name: str) -> str:
    for key, outlet in OUTLET_MAP.items():
        if key in name:
            return outlet
    return "Unknown"


def consolidate(raw_dir: Path) -> pd.DataFrame:
    frames = []
    for f in sorted(raw_dir.glob("*videos*.xlsx")):
        try:
            df = pd.read_excel(f)
        except Exception as exc:  # noqa: BLE001
            print(f"  skip {f.name}: {exc}")
            continue
        if not set(STD_COLS).issubset(df.columns):
            continue
        df = df[STD_COLS].copy()
        df["outlet"] = _detect_outlet(f.name)
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"No *videos*.xlsx files found in {raw_dir}")

    data = pd.concat(frames, ignore_index=True)
    data["Publish Time"] = pd.to_datetime(data["Publish Time"],
                                          errors="coerce", utc=True)
    data["year"] = data["Publish Time"].dt.year
    data = data.dropna(subset=["URL"]).drop_duplicates(subset=["URL"])
    for col in ["Like Count", "Comment Count", "View Count"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0).astype(int)
    return data.reset_index(drop=True)


if __name__ == "__main__":
    from src import config

    videos = consolidate(config.DATA_RAW)
    out = config.DATA_PROCESSED / "youtube_videos.csv"
    videos.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Consolidated {len(videos)} unique videos -> {out}")
