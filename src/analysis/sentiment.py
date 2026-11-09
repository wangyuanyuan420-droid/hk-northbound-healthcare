"""Sentiment analysis for Chinese comments and news content (SnowNLP).

Refactor of ``Sentiment Analysis.py`` / ``情感.py``. SnowNLP returns a
probability in [0, 1]; we bucket it into positive / neutral / negative with
the same thresholds used in the original thesis (0.6 / 0.4) so results stay
comparable.

Example:
    python -m src.analysis.sentiment \
        --in data/processed/youtube_comments_anonymized.csv --col comment
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from snownlp import SnowNLP

POS_THRESHOLD = 0.6
NEG_THRESHOLD = 0.4


def score(text: str) -> float:
    text = str(text).strip()
    if not text:
        return 0.5
    try:
        return SnowNLP(text).sentiments
    except Exception:  # noqa: BLE001
        return 0.5


def categorize(s: float) -> str:
    if s > POS_THRESHOLD:
        return "positive"
    if s < NEG_THRESHOLD:
        return "negative"
    return "neutral"


def analyze(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df.copy()
    out = out.dropna(subset=[col])
    out[col] = out[col].astype(str)
    out["sentiment"] = out[col].map(score)
    out["sentiment_category"] = out["sentiment"].map(categorize)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--col", required=True, help="text column to score")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    src = Path(args.infile)
    df = pd.read_csv(src) if src.suffix == ".csv" else pd.read_excel(src)
    scored = analyze(df, args.col)
    out = args.out or str(src.with_name(src.stem + "_sentiment.csv"))
    scored.to_csv(out, index=False, encoding="utf-8-sig")
    dist = scored["sentiment_category"].value_counts().to_dict()
    print(f"Scored {len(scored)} rows -> {out}\nDistribution: {dist}")


if __name__ == "__main__":
    main()
