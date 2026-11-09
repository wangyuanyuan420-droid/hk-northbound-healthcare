"""Scrape Google News search results and article bodies with Selenium.

Consolidated refactor of ``Google News.py`` + ``Google News Content.py``:
two stages behind one CLI, project-relative output paths, and
``webdriver-manager`` for automatic ChromeDriver management.

Examples:
    python -m src.scraping.google_news search --query 北上就醫 --max 100
    python -m src.scraping.google_news content --in data/raw/news_links.csv
"""
from __future__ import annotations
import argparse
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from src import config


def _driver() -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    opts.add_argument("--lang=zh-TW")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                            options=opts)


def search(query: str, max_news: int = 100) -> pd.DataFrame:
    driver = _driver()
    rows = []
    try:
        driver.get(f"https://news.google.com/search?q={query}"
                   "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        while len(rows) < max_news:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            articles = driver.find_elements(By.CSS_SELECTOR, "article")
            for art in articles[len(rows):]:
                try:
                    title = art.find_element(By.CSS_SELECTOR, "h3, h4").text
                    link = art.find_element(By.TAG_NAME, "a").get_attribute("href")
                    when = art.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                except Exception:  # noqa: BLE001
                    continue
                if title and link:
                    rows.append({"title": title, "time": when, "url": link})
                if len(rows) >= max_news:
                    break
            if not articles:
                break
    finally:
        driver.quit()
    return pd.DataFrame(rows).drop_duplicates(subset=["title", "url"])


def content(links: pd.DataFrame) -> pd.DataFrame:
    driver = _driver()
    rows = []
    try:
        for _, r in links.iterrows():
            try:
                driver.get(r["url"])
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body")))
                paras = driver.find_elements(By.TAG_NAME, "p")
                body = "\n".join(p.text for p in paras)
                title = driver.find_elements(By.TAG_NAME, "h1")
                rows.append({"title": title[0].text if title else r.get("title", ""),
                             "content": body, "url": r["url"], "time": r.get("time")})
            except Exception as exc:  # noqa: BLE001
                rows.append({"title": "错误", "content": str(exc),
                             "url": r["url"], "time": r.get("time")})
    finally:
        driver.quit()
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("--query", required=True)
    s.add_argument("--max", type=int, default=100)
    s.add_argument("--out", default=str(config.DATA_RAW / "news_links.csv"))
    c = sub.add_parser("content")
    c.add_argument("--in", dest="infile", default=str(config.DATA_RAW / "news_links.csv"))
    c.add_argument("--out", default=str(config.DATA_RAW / "news_articles_raw.csv"))
    args = p.parse_args()

    if args.cmd == "search":
        df = search(args.query, args.max)
        df.to_csv(args.out, index=False, encoding="utf-8-sig")
        print(f"Saved {len(df)} links -> {args.out}")
    else:
        df = content(pd.read_csv(args.infile))
        df.to_csv(args.out, index=False, encoding="utf-8-sig")
        print(f"Saved {len(df)} articles -> {args.out}")


if __name__ == "__main__":
    main()
