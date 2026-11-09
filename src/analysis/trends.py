"""Discussion-heat and cross-outlet trend analysis (new module).

Adds analyses the original project lacked: how coverage volume and audience
engagement around 港人北上就醫 evolved over time, and how the four news
outlets differ. Consumes the consolidated ``youtube_videos.csv``.

Produces:
  * figures/trend_volume_by_quarter.png  — video count per quarter
  * figures/trend_engagement.png         — mean views/likes/comments over time
  * figures/outlet_comparison.png        — videos & median views per outlet
  * data/processed/trend_summary.csv     — the underlying table

Example:
    python -m src.analysis.trends
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import pandas as pd

from src import config

# Register a CJK font so Chinese titles render instead of tofu boxes.
if Path(config.CJK_FONT).exists():
    font_manager.fontManager.addfont(config.CJK_FONT)
    plt.rcParams["font.family"] = font_manager.FontProperties(
        fname=config.CJK_FONT).get_name()
plt.rcParams["axes.unicode_minus"] = False


def load_videos() -> pd.DataFrame:
    df = pd.read_csv(config.DATA_PROCESSED / "youtube_videos.csv")
    df["Publish Time"] = pd.to_datetime(df["Publish Time"], errors="coerce", utc=True)
    return df.dropna(subset=["Publish Time"])


def volume_by_quarter(df: pd.DataFrame) -> pd.Series:
    q = df.set_index("Publish Time").resample("QE").size()
    plt.figure(figsize=(11, 5))
    q.plot(kind="bar", color="#2b6cb0", width=0.85)
    plt.title("Coverage volume of 港人北上就醫 videos by quarter (2018–2024)")
    plt.ylabel("Number of videos")
    plt.xlabel("Quarter")
    plt.xticks([i for i in range(0, len(q), 2)],
               [str(d)[:7] for d in q.index[::2]], rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(config.FIGURES / "trend_volume_by_quarter.png", dpi=150)
    plt.close()
    return q


def engagement_over_time(df: pd.DataFrame) -> pd.DataFrame:
    eng = (df.set_index("Publish Time")
             .resample("QE")[["View Count", "Like Count", "Comment Count"]]
             .mean())
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(eng.index, eng["View Count"], marker="o", label="Mean views")
    ax.set_ylabel("Mean views")
    ax2 = ax.twinx()
    ax2.plot(eng.index, eng["Like Count"], marker="s",
             color="#dd6b20", label="Mean likes")
    ax2.plot(eng.index, eng["Comment Count"], marker="^",
             color="#38a169", label="Mean comments")
    ax2.set_ylabel("Mean likes / comments")
    ax.set_title("Audience engagement over time")
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [l.get_label() for l in lines], loc="upper left")
    plt.tight_layout()
    plt.savefig(config.FIGURES / "trend_engagement.png", dpi=150)
    plt.close()
    return eng


def outlet_comparison(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("outlet").agg(
        videos=("URL", "count"),
        median_views=("View Count", "median"),
        median_comments=("Comment Count", "median"),
    ).sort_values("videos", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    grp["videos"].plot(kind="bar", ax=axes[0], color="#2b6cb0")
    axes[0].set_title("Videos per outlet"); axes[0].set_ylabel("Count")
    grp["median_views"].plot(kind="bar", ax=axes[1], color="#dd6b20")
    axes[1].set_title("Median views per outlet"); axes[1].set_ylabel("Median views")
    for ax in axes:
        ax.set_xlabel(""); ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "outlet_comparison.png", dpi=150)
    plt.close()
    return grp


def main() -> None:
    df = load_videos()
    q = volume_by_quarter(df)
    eng = engagement_over_time(df)
    grp = outlet_comparison(df)
    grp.to_csv(config.DATA_PROCESSED / "trend_summary.csv", encoding="utf-8-sig")
    print("Videos analysed:", len(df))
    print("Peak quarter:", q.idxmax().date(), "with", int(q.max()), "videos")
    print("\nOutlet summary:\n", grp)
    print("\nFigures written to", config.FIGURES)


if __name__ == "__main__":
    main()
