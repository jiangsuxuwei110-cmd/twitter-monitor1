"""
Twitter/X 推文抓取模块 v6 (2026-05-31)
- 数据源：RSS.app RSS Feed（免费、稳定、无需 Twitter API）
- 图片：RSS <media:content> 标签 + Syndication API 双源
- RSS.app URL 通过环境变量 RSS_URL 配置
"""

import logging
import re
import os
from typing import Optional
from xml.etree import ElementTree as ET

import requests

logger = logging.getLogger(__name__)

# RSS.app Feed URL
RSS_URL = os.environ.get("RSS_URL", "https://rss.app/feeds/Z4mTJrDi96qmVhYj.xml")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# Twitter Syndication API（获取图片等详情，尽力而为）
SYNDICATION_URL = "https://cdn.syndication.twimg.com/tweet-result"

# RSS Media 命名空间
NS = {"media": "http://search.yahoo.com/mrss/"}


def _convert_image(url: str) -> str:
    """将 pbs.twimg.com 转换为 pic.x.com（中国可访问）"""
    if not url:
        return ""
    return url.replace("pbs.twimg.com", "pic.x.com")


def _fetch_syndication_images(tweet_id: str) -> list[dict]:
    """通过 Syndication API 获取推文图片（尽力而为）"""
    try:
        resp = requests.get(
            SYNDICATION_URL,
            params={"id": tweet_id, "lang": "en"},
            headers=HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            images = []
            for photo in data.get("photos", []):
                url = photo.get("url", "")
                if url:
                    images.append({
                        "original": url,
                        "converted": _convert_image(url),
                        "width": photo.get("width", 0),
                        "height": photo.get("height", 0),
                    })
            return images
    except Exception:
        pass
    return []


def _extract_rss_images(item) -> list[dict]:
    """从 RSS <media:content> 标签提取图片"""
    images = []
    for mc in item.findall("media:content", NS):
        medium = mc.get("medium", "")
        url = mc.get("url", "")
        if medium == "image" and url:
            images.append({
                "original": url,
                "converted": _convert_image(url),
                "width": int(mc.get("width", 0)),
                "height": int(mc.get("height", 0)),
            })
    return images


def fetch_via_rss_app(last_id: Optional[str] = None) -> list[dict]:
    """
    从 RSS.app Feed 抓取推文。
    返回推文列表，按时间倒序（最新在前）。
    """
    try:
        resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            logger.error("RSS.app 请求失败: HTTP %d", resp.status_code)
            return []

        root = ET.fromstring(resp.content)
        tweets = []

        for item in root.findall(".//item"):
            # 提取推文 ID
            link = item.findtext("link", "").strip()
            match = re.search(r"/status/(\d+)", link)
            if not match:
                continue
            tid = match.group(1)

            # 到达已处理推文，停止
            if tid == last_id:
                break

            # 提取正文（去除 CDATA 包装）
            title_raw = item.findtext("title", "") or ""
            text = re.sub(
                r"^\s*<!\[CDATA\[(.*?)\]\]>\s*$",
                r"\1", title_raw, flags=re.DOTALL
            ).strip()

            # 提取发布时间
            pub_date = (item.findtext("pubDate", "") or "").strip()

            # ── 图片采集：RSS media:content 优先 ──
            images = _extract_rss_images(item)

            # 如果 RSS 没有图片，尝试 Syndication API
            if not images:
                logger.debug("RSS 无图片，尝试 Syndication API: %s", tid)
                images = _fetch_syndication_images(tid)

            tweets.append({
                "id": tid,
                "text": text,
                "images": images,
                "created_at": pub_date,
                "user": {
                    "name": "Serenity",
                    "screen_name": "aleabitoreddit",
                },
                "tweet_url": link,
            })

            # 最多取 20 条
            if len(tweets) >= 20:
                break

        logger.info("RSS.app 解析完成，获得 %d 条推文", len(tweets))
        return tweets

    except Exception as e:
        logger.error("RSS.app 抓取异常: %s", e)
        return []


def fetch_comments(tweet_id: str) -> list[dict]:
    """通过 Syndication API 抓取评论（尽力而为）。"""
    try:
        resp = requests.get(
            SYNDICATION_URL,
            params={"id": tweet_id, "lang": "en", "conversation": "true"},
            headers=HEADERS,
            timeout=10,
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        comments = []
        for thread in data.get("conversationThreads", []):
            for ct in thread.get("tweets", []):
                if ct.get("id_str") == tweet_id:
                    continue
                author = ct.get("user", {}).get("name", "")
                text = ct.get("text", "")
                if author and text:
                    comments.append({"author": author, "content": text})
                if len(comments) >= 5:
                    break
            if len(comments) >= 5:
                break
        return comments
    except Exception:
        return []


def fetch_new_tweets(last_id: Optional[str] = None) -> list[dict]:
    """
    主入口：获取 @aleabitoreddit 的新推文。
    数据来源：RSS.app（稳定可用）
    """
    logger.info("开始抓取推文，last_id=%s", last_id or "None")
    tweets = fetch_via_rss_app(last_id)

    if not tweets:
        logger.warning("未获取到新推文")
        return []

    # 附上评论
    for tweet in tweets:
        tweet["comments"] = fetch_comments(tweet["id"])

    logger.info("共获得 %d 条新推文", len(tweets))
    return tweets
