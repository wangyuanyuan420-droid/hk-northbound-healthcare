"""Central configuration and path management.

All paths are resolved relative to the project root, so the code runs on
any machine without editing hardcoded absolute paths. Secrets are read from
environment variables (see .env.example), never hardcoded.
"""
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # dotenv is optional
    pass

# ---- Paths ----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RESOURCES = PROJECT_ROOT / "resources"
FIGURES = PROJECT_ROOT / "figures"

# Traditional-Chinese jieba dictionary (download separately, see README)
JIEBA_DICT = RESOURCES / "dict.txt.big"

# Stopword list shared across topic-modelling and word-cloud modules
STOPWORDS_FILE = RESOURCES / "stopwords_zh.txt"

# ---- Secrets --------------------------------------------------------------
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# ---- CJK font for matplotlib / wordcloud ----------------------------------
# Override with the FONT_PATH env var if this default does not exist.
CJK_FONT = os.getenv("FONT_PATH", "/System/Library/Fonts/PingFang.ttc")

for _d in (DATA_RAW, DATA_PROCESSED, RESOURCES, FIGURES):
    _d.mkdir(parents=True, exist_ok=True)
