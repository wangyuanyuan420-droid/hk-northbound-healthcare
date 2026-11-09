# Public Data Dictionary

This repository deliberately does **not** distribute raw exports, complete
news articles, comment text, URLs, video IDs, hashed identifiers, or author
information. The tables below are aggregate outputs from the original study.

## `data/public/coverage_by_quarter.csv`

| Column | Description |
|---|---|
| `quarter_end` | End date of the calendar quarter |
| `videos` | Number of collected videos in that quarter |
| `mean_views`, `mean_likes`, `mean_comments` | Mean engagement counts across collected videos |

## `data/public/outlet_summary.csv`

| Column | Description |
|---|---|
| `outlet` | Aggregate source outlet label |
| `videos` | Number of collected videos |
| `median_views`, `median_comments` | Median engagement counts |

## `data/public/comment_sentiment_summary.csv`

| Column | Description |
|---|---|
| `sentiment_category` | Automated sentiment bucket: positive, neutral, or negative |
| `comments` | Count of scored comments |
| `share_percent` | Percentage of scored comments |

## `data/sample/synthetic_video_metadata.csv`

This is an artificial 12-row example for inspecting the metadata schema. Its
record IDs and engagement values are synthetic; it is not a subset of the
research corpus and must not be used to reproduce study results.
