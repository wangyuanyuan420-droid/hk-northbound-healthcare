# Data Ethics Statement

This project analyses **public** online discourse about Hong Kong residents
travelling north to mainland China for medical care (港人北上就醫). It was
produced for an undergraduate thesis and this public version is shared for
**academic, non-commercial portfolio purposes only**.

## Public-release boundary

This repository does not redistribute raw platform exports, complete comment
text, complete news-article text, source URLs, usernames, video identifiers,
or hashed video identifiers. It instead provides code, aggregate tables,
synthetic schema examples, and final visualisations. The full research archive
is retained only locally by the author.

## What the original research collected

- **News articles** — headlines and body text from Google News search results
  for the query 北上就醫.
- **YouTube video metadata** — titles, descriptions, publication times, and
  public engagement counts from four Hong Kong news outlets' official channels.
- **YouTube comments** — top-level public comments on collected videos.

No private messages, login-gated content, or account names were intentionally
collected.

## How the local research archive protects individuals

- The comment collector stores only comment text and a parent `video_id`; it
  does not collect usernames or author identifiers.
- Before local analysis, each `video_id` is replaced with a salted, truncated
  SHA-256 hash (`src/preprocessing/anonymize.py`).
- Comment text is passed through a redaction pass that removes e-mail addresses
  and phone-number-like digit strings. Complete text is not distributed here.
- Findings are reported in aggregate; the project does not profile or identify
  individual commenters.

## Limitations

- Platform content remains owned by its original authors and outlets.
- Automated SnowNLP sentiment classifications are noisy, especially for
  Cantonese colloquialisms, and should not be treated as ground truth.
- The study's data collection is query-based and descriptive, not a census of
  all online discussion about cross-boundary healthcare.
