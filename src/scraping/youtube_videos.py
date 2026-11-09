"""Collect YouTube video metadata for a channel + query via the Data API v3.

Refactor of the original ``爬視頻_年份.py``:
  * API key is read from the environment (``YOUTUBE_API_KEY``), never hardcoded.
  * Channel, query, date range and output path are CLI arguments.
  * Handles pagination and missing statistics fields defensively.

Example:
    python -m src.scraping.youtube_videos \
        --channel UC9JZrrDHcFEUG7FQSSUj98A --query 北上求醫 \
        --start 2018-01-01 --end 2025-01-01 --out data/raw/hk01_videos.xlsx
"""
from __future__ import annotations
import argparse
import pandas as pd
from googleapiclient.discovery import build

from src import config


def fetch_videos(channel_id: str, query: str, start: str, end: str) -> pd.DataFrame:
    if not config.YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set. Copy .env.example to .env.")
    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

    rows, page_token = [], None
    while True:
        search = youtube.search().list(
            channelId=channel_id, q=query, part="snippet", maxResults=50,
            type="video", publishedAfter=f"{start}T00:00:00Z",
            publishedBefore=f"{end}T00:00:00Z", pageToken=page_token,
        ).execute()

        for item in search.get("items", []):
            vid = item["id"]["videoId"]
            detail = youtube.videos().list(
                part="snippet,statistics", id=vid).execute()["items"][0]
            stats = detail.get("statistics", {})
            rows.append({
                "Title": detail["snippet"]["title"],
                "Description": detail["snippet"]["description"],
                "URL": f"https://www.youtube.com/watch?v={vid}",
                "Publish Time": detail["snippet"]["publishedAt"],
                "Like Count": int(stats.get("likeCount", 0)),
                "Comment Count": int(stats.get("commentCount", 0)),
                "View Count": int(stats.get("viewCount", 0)),
            })

        page_token = search.get("nextPageToken")
        if not page_token:
            break
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--channel", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--start", default="2018-01-01")
    p.add_argument("--end", default="2025-01-01")
    p.add_argument("--out", default=str(config.DATA_RAW / "youtube_videos.xlsx"))
    args = p.parse_args()

    df = fetch_videos(args.channel, args.query, args.start, args.end)
    df.to_excel(args.out, index=False)
    print(f"Saved {len(df)} videos -> {args.out}")


if __name__ == "__main__":
    main()
