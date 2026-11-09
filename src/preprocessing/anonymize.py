"""Anonymise YouTube comment data for public release.

Even though comments are publicly visible, re-publishing them keyed to a
specific video re-identifies commenters. This module:

  1. Replaces the raw ``video_id`` with a salted, truncated SHA-256 hash so
     rows can no longer be traced back to a specific video/commenter.
  2. Redacts e-mail addresses and phone-number-like digit strings that users
     sometimes paste into comments.

Run:  python -m src.preprocessing.anonymize
"""
from __future__ import annotations
import hashlib
import re
import pandas as pd

# A project-level salt. Change it for a fresh, non-reversible mapping.
_SALT = "hk-northbound-2025"

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s-]{6,}\d)(?!\d)")


def hash_id(value: str) -> str:
    """Return a short, non-reversible hash of an identifier."""
    digest = hashlib.sha256((_SALT + str(value)).encode("utf-8")).hexdigest()
    return "vid_" + digest[:12]


def redact_text(text: str) -> str:
    """Remove e-mails and long digit strings from free text."""
    text = _EMAIL.sub("[EMAIL]", str(text))
    text = _PHONE.sub("[NUMBER]", text)
    return text


def anonymize_comments(df: pd.DataFrame,
                       id_col: str = "video_id",
                       text_col: str = "comment") -> pd.DataFrame:
    """Return a copy of *df* with the id hashed and the text redacted."""
    out = df.copy()
    if id_col in out.columns:
        out["video_hash"] = out[id_col].map(hash_id)
        out = out.drop(columns=[id_col])
    if text_col in out.columns:
        out[text_col] = out[text_col].map(redact_text)
    return out


if __name__ == "__main__":
    from src import config

    src_file = config.DATA_RAW / "youtube_comments_raw.xlsx"
    df = pd.read_excel(src_file)
    anon = anonymize_comments(df)
    out_file = config.DATA_PROCESSED / "youtube_comments_anonymized.csv"
    anon.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"Anonymised {len(anon)} comments -> {out_file}")
