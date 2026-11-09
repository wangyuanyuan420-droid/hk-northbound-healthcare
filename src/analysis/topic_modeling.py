"""LDA topic modelling with coherence-based topic-number selection.

Improves on the original LDA scripts (which hardcoded ``num_topics``) by
sweeping a range of K and picking the model with the highest c_v coherence,
then saving an interactive pyLDAvis HTML. Reuses the shared noun tokenizer.

Example:
    python -m src.analysis.topic_modeling \
        --in data/processed/youtube_comments_anonymized.csv --col comment \
        --min-k 2 --max-k 8
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel

from src import config
from src.preprocessing.text_cleaning import build_corpus


def select_and_train(tokens, min_k=2, max_k=8):
    id2word = corpora.Dictionary(tokens)
    id2word.filter_extremes(no_below=3, no_above=0.5)
    corpus = [id2word.doc2bow(t) for t in tokens]

    best = None
    for k in range(min_k, max_k + 1):
        model = LdaModel(corpus=corpus, id2word=id2word, num_topics=k,
                         random_state=100, passes=10, alpha="auto")
        cm = CoherenceModel(model=model, texts=tokens,
                            dictionary=id2word, coherence="c_v")
        cv = cm.get_coherence()
        print(f"  K={k}: coherence={cv:.4f}")
        if best is None or cv > best[0]:
            best = (cv, k, model)
    return best[2], corpus, id2word, best[1], best[0]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--col", required=True)
    p.add_argument("--min-k", type=int, default=2)
    p.add_argument("--max-k", type=int, default=8)
    args = p.parse_args()

    src = Path(args.infile)
    df = pd.read_csv(src) if src.suffix == ".csv" else pd.read_excel(src)
    tokens = [t for t in build_corpus(df[args.col].dropna().astype(str)) if t]

    model, corpus, id2word, k, cv = select_and_train(
        tokens, args.min_k, args.max_k)
    print(f"\nBest K={k} (coherence={cv:.4f})")
    for tid, terms in model.print_topics(num_words=8):
        print(f"Topic {tid}: {terms}")

    try:
        import pyLDAvis, pyLDAvis.gensim
        vis = pyLDAvis.gensim.prepare(model, corpus, id2word, mds="mmd")
        out = config.FIGURES / f"lda_{src.stem}_k{k}.html"
        pyLDAvis.save_html(vis, str(out))
        print(f"Saved visualisation -> {out}")
    except Exception as exc:  # noqa: BLE001
        print(f"pyLDAvis skipped: {exc}")


if __name__ == "__main__":
    main()
