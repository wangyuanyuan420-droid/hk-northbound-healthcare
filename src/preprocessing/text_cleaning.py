"""Shared Chinese text-cleaning utilities.

Centralises the jieba setup, stopword loading, and noun-extraction logic
that was previously copy-pasted (with a ~1,000-word inline stopword list)
across the topic-modelling and word-cloud scripts.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Iterable, List
import jieba
import jieba.posseg as pseg

from src import config


@lru_cache(maxsize=1)
def load_stopwords() -> frozenset:
    """Load the curated stopword file, merged with PyCantonese stopwords."""
    words = set()
    if config.STOPWORDS_FILE.exists():
        for line in config.STOPWORDS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                words.add(line)
    try:
        from pycantonese import stop_words
        words |= set(stop_words())
    except Exception:  # pycantonese optional
        pass
    return frozenset(words)


@lru_cache(maxsize=1)
def _ensure_dict() -> None:
    """Point jieba at the Traditional-Chinese dictionary if available."""
    if config.JIEBA_DICT.exists():
        jieba.set_dictionary(str(config.JIEBA_DICT))


def tokenize_nouns(text: str, stopwords: Iterable[str] | None = None) -> List[str]:
    """Return nouns from *text*, excluding proper names (nr) and stopwords.

    Keeps tokens whose POS tag starts with ``n`` (nouns) but drops ``nr``
    (person names), mirroring the original analysis while being reusable.
    """
    _ensure_dict()
    stop = set(stopwords) if stopwords is not None else load_stopwords()
    tokens = []
    for word, flag in pseg.cut(str(text)):
        if flag.startswith("n") and flag != "nr" and word not in stop:
            tokens.append(word)
    return tokens


def build_corpus(texts: Iterable[str]) -> List[List[str]]:
    """Tokenise an iterable of documents into lists of noun tokens."""
    stop = load_stopwords()
    return [tokenize_nouns(t, stop) for t in texts]
