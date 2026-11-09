"""Word-frequency and word-cloud generation from Chinese text.

Refactor of ``詞雲及詞頻.py`` / ``正负词云.py``. Uses the shared tokenizer,
can filter by a sentiment category, and writes both a frequency bar chart
and a word cloud to ``figures/``.

Example:
    python -m src.analysis.wordfreq \
        --in data/processed/youtube_comments_anonymized.csv --col comment \
        --top 25 --label comments
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

from src import config
from src.preprocessing.text_cleaning import build_corpus


def _cjk_font():
    if Path(config.CJK_FONT).exists():
        font_manager.fontManager.addfont(config.CJK_FONT)
        return font_manager.FontProperties(fname=config.CJK_FONT)
    return None


def word_counts(texts) -> Counter:
    counter = Counter()
    for tokens in build_corpus(texts):
        counter.update(tokens)
    return counter


def bar_chart(counter: Counter, top: int, label: str) -> Path:
    font = _cjk_font()
    items = counter.most_common(top)
    words, freqs = zip(*items)
    plt.figure(figsize=(10, 7))
    plt.barh(range(len(words)), freqs, color="#2b6cb0")
    plt.yticks(range(len(words)), words,
               fontproperties=font if font else None)
    plt.gca().invert_yaxis()
    plt.xlabel("Frequency")
    plt.title(f"Top {top} keywords — {label}",
              fontproperties=font if font else None)
    plt.tight_layout()
    out = config.FIGURES / f"wordfreq_{label}.png"
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def word_cloud(counter: Counter, label: str) -> Path | None:
    try:
        from wordcloud import WordCloud
    except ImportError:
        return None
    wc = WordCloud(background_color="white", font_path=config.CJK_FONT,
                   width=1600, height=800, max_words=200)
    wc.generate_from_frequencies(dict(counter))
    out = config.FIGURES / f"wordcloud_{label}.png"
    wc.to_file(str(out))
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--col", required=True)
    p.add_argument("--top", type=int, default=25)
    p.add_argument("--label", default="corpus")
    p.add_argument("--sentiment", choices=["positive", "negative", "neutral"])
    args = p.parse_args()

    src = Path(args.infile)
    df = pd.read_csv(src) if src.suffix == ".csv" else pd.read_excel(src)
    if args.sentiment and "sentiment_category" in df.columns:
        df = df[df["sentiment_category"] == args.sentiment]
    counter = word_counts(df[args.col].dropna().astype(str))
    print(f"Vocabulary: {len(counter)} unique tokens")
    print("Bar chart ->", bar_chart(counter, args.top, args.label))
    wc = word_cloud(counter, args.label)
    if wc:
        print("Word cloud ->", wc)


if __name__ == "__main__":
    main()
