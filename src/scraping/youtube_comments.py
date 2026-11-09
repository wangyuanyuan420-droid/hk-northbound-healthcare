"""Fetch top-level comments for a list of YouTube videos (Data API v3).

Refactor of ``YouTube URL爬取Comments.py``: API key from env, input/output
paths as arguments, keeps the ``video_id`` so downstream anonymisation can
hash it (see src/preprocessing/anonymize.py).

Example:
    python -m src.scraping.youtube_comments \
        --urls data/raw/video_urls.xlsx --out data/raw/youtube_comments_raw.xlsx
"""
from __future__ import annotations
import argparse
from typing import List
import pandas as pd
from googleapiclient.discovery import build

from src import config


def video_id_from_url(url: str) -> str | None:
    url = url.strip()
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def fetch_comments(youtube, video_id: str) -> List[str]:
    comments, request = [], youtube.commentThreads().list(
        part="snippet", videoId=video_id, maxResults=100, textFormat="plainText")
    while request:
        try:
            response = request.execute()
        except Exception as exc:  # noqa: BLE001 — video may disable comments
            print(f"  {video_id}: {exc}")
            break
        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(snippet["textOriginal"])
        request = youtube.commentThreads().list_next(request, response)
    return comments


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--urls", required=True, help="xlsx/csv with a 'URL' column")
    p.add_argument("--out", default=str(config.DATA_RAW / "youtube_comments_raw.xlsx"))
    args = p.parse_args()

    if not config.YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set. Copy .env.example to .env.")
    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

    df = (pd.read_excel(args.urls) if args.urls.endswith("x")
          else pd.read_csv(args.urls))
    rows = []
    for url in df["URL"].dropna():
        vid = video_id_from_url(url)
        if not vid:
            continue
        for c in fetch_comments(youtube, vid):
            rows.append({"video_id": vid, "comment": c})

    out = pd.DataFrame(rows)
    out.to_excel(args.out, index=False)
    print(f"Saved {len(out)} comments -> {args.out}")


if __name__ == "__main__":
    main()
