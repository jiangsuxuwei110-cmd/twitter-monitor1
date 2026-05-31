"""
Serenity Daily - Tweet Fetcher (Cloud Version)
Fetches today's tweets from RSS.app RSS feed.
"""
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

import requests

# --- Config ---
RSS_URL = "https://rss.app/feeds/Z4mTJrDi96qmVhYj.xml"
BEIJING_TZ = timezone(timedelta(hours=8))

# --- XML namespaces ---
NS = {
    "media": "http://search.yahoo.com/mrss/",
}


def clean_tweet_text(description: str) -> str:
    """Strip HTML tags, trim whitespace."""
    if not description:
        return ""
    text = re.sub(r"<[^>]+>", " ", description)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_rss_date(date_str: str):
    """Parse RFC 2822 date string to UTC datetime."""
    if not date_str:
        return None
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str).replace(tzinfo=timezone.utc)
    except Exception:
        # Try ISO format fallback
        for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def fetch_today_tweets() -> list[dict]:
    """
    Fetch tweets from RSS.app posted today (Beijing time).
    Returns list of tweet dicts:
        {id, text, time_utc, time_beijing, link, images, is_new}
    """
    # Today's start in Beijing time, converted to UTC
    now_bj = datetime.now(BEIJING_TZ)
    today_start_bj = now_bj.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start_utc = today_start_bj.astimezone(timezone.utc)

    resp = requests.get(RSS_URL, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    tweets = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")

        # Extract tweet ID from link
        tid_match = re.search(r"/status/(\d+)", link)
        if not tid_match:
            continue
        tweet_id = tid_match.group(1)

        # Parse time
        pub_date_str = item.findtext("pubDate", "")
        pub_date = parse_rss_date(pub_date_str)
        if not pub_date:
            continue

        # Skip tweets before today (Beijing time)
        if pub_date < today_start_utc:
            continue

        # Clean text
        description = item.findtext("description", "")
        text = clean_tweet_text(description)

        # Extract images from media:content
        images = []
        for media in item.findall("{http://search.yahoo.com/mrss/}content"):
            url = media.get("url", "")
            if url:
                url = url.replace("pbs.twimg.com", "pic.x.com")
                images.append(url)

        tweets.append({
            "id": tweet_id,
            "title": title,
            "text": text,
            "time_utc": pub_date.isoformat(),
            "time_beijing": pub_date.astimezone(BEIJING_TZ).strftime("%m-%d %H:%M"),
            "link": link,
            "images": images,
        })

    # Sort by time oldest first
    tweets.sort(key=lambda t: t["time_utc"])
    return tweets


if __name__ == "__main__":
    tws = fetch_today_tweets()
    print(f"Fetched {len(tws)} tweets today")
    for t in tws:
        print(f"  [{t['time_beijing']}] {t['text'][:100]}...")
