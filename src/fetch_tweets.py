"""
Twitter/X 推文抓取模块
- 多源 RSS 获取最新推文
- Twitter Syndication API 获取推文详情
- 图片链接自动转换 pbs.twimg.com → pic.x.com
- 评论抓取（尽力而为）
"""

import re
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── 配置 ──────────────────────────────────────────────
TARGET_USER = "aleabitoreddit"

# 多源 RSS 地址（按优先级）
RSS_SOURCES = [
    f"https://rsshub.app/twitter/user/{TARGET_USER}",
    f"https://nitter.net/{TARGET_USER}/rss",
    f"https://nitter.privacydev.net/{TARGET_USER}/rss",
    f"https://nitter.poast.org/{TARGET_USER}/rss",
    f"https://nitter.1d4.us/{TARGET_USER}/rss",
]

# Twitter Syndication API（获取推文详情）
SYNDICATION_URL = "https://cdn.syndication.twimg.com/tweet-result"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


def convert_image_url(url: str) -> str:
    """将 pbs.twimg.com 转为 pic.x.com，避免 PushPlus 拦截"""
    return url.replace("pbs.twimg.com", "pic.x.com")


def _extract_tweet_id_from_url(url: str) -> Optional[str]:
    """从推文 URL 中提取推文 ID"""
    match = re.search(r"/status/(\d+)", url)
    return match.group(1) if match else None


def _extract_tweet_id_from_guid(guid: str) -> Optional[str]:
    """从 RSS GUID 中提取推文 ID"""
    match = re.search(r"(\d{15,})$", guid)
    return match.group(1) if match else None


def _parse_rss_feed(xml_content: str) -> list[dict]:
    """解析 RSS/Atom XML，提取推文基本信息"""
    tweets = []
    try:
        root = ET.fromstring(xml_content)

        # RSS 2.0 格式
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items:
            title = (
                item.findtext("title")
                or item.findtext("{http://www.w3.org/2005/Atom}title", "")
            )
            link = (
                item.findtext("link")
                or item.findtext("{http://www.w3.org/2005/Atom}link", "")
            )
            description = (
                item.findtext("description")
                or item.findtext("{http://www.w3.org/2005/Atom}summary", "")
                or item.findtext("{http://www.w3.org/2005/Atom}content", "")
            )
            pub_date = (
                item.findtext("pubDate")
                or item.findtext("{http://www.w3.org/2005/Atom}published", "")
            )
            guid = (
                item.findtext("guid")
                or item.findtext("{http://www.w3.org/2005/Atom}id", "")
            )

            # Atom link 可能是 href 属性
            if not link or link.startswith("http"):
                pass
            else:
                link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                if link_elem is not None:
                    link = link_elem.get("href", link)

            tweet_id = _extract_tweet_id_from_url(link) or _extract_tweet_id_from_guid(guid)
            if not tweet_id:
                continue

            # 清理标题（移除可能有的用户名前缀）
            clean_title = re.sub(r"^[^:]+:\s*", "", title) if title else ""

            tweets.append(
                {
                    "id": tweet_id,
                    "title": clean_title,
                    "raw_description": description or "",
                    "link": link,
                    "pub_date": pub_date,
                    "source": "rss",
                }
            )
    except ET.ParseError as e:
        logger.warning("XML 解析失败: %s", e)

    return tweets


def fetch_tweets_via_rss() -> list[dict]:
    """通过多源 RSS 获取最新推文列表"""
    for url in RSS_SOURCES:
        try:
            logger.info("尝试 RSS 源: %s", url)
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and resp.text.strip():
                tweets = _parse_rss_feed(resp.text)
                if tweets:
                    logger.info("成功从 %s 获取 %d 条推文", url, len(tweets))
                    return tweets
            else:
                logger.warning("RSS 源 %s 返回 %d", url, resp.status_code)
        except Exception as e:
            logger.warning("RSS 源 %s 请求失败: %s", url, e)

    logger.error("所有 RSS 源均不可用")
    return []


def enrich_tweet_via_syndication(tweet_id: str) -> Optional[dict]:
    """
    通过 Twitter Syndication API 获取推文详细信息
    返回包含 text, images, video, created_at, user 等字段的字典
    """
    try:
        params = {"id": tweet_id, "lang": "en"}
        resp = requests.get(SYNDICATION_URL, params=params, headers=HEADERS, timeout=20)

        if resp.status_code != 200:
            logger.warning("Syndication API 返回 %d for tweet %s", resp.status_code, tweet_id)
            return None

        data = resp.json()

        # 提取文本
        text = data.get("text", "")

        # 提取图片
        images = []
        photos = data.get("photos", [])
        for photo in photos:
            img_url = photo.get("url", "")
            if img_url:
                images.append(
                    {
                        "original": img_url,
                        "converted": convert_image_url(img_url),
                        "width": photo.get("width", 0),
                        "height": photo.get("height", 0),
                    }
                )

        # 提取视频缩略图
        video_info = None
        if data.get("video"):
            video_info = {
                "poster": convert_image_url(data["video"].get("poster", "")),
                "duration": data["video"].get("duration", 0),
            }

        # 提取时间
        created_at = data.get("created_at", "")

        # 用户信息
        user = data.get("user", {})

        # 提取外部链接
        urls = []
        entities = data.get("entities", {})
        for url_entity in entities.get("urls", []):
            urls.append(
                {
                    "display_url": url_entity.get("display_url", ""),
                    "expanded_url": url_entity.get("expanded_url", ""),
                }
            )

        return {
            "id": tweet_id,
            "text": text,
            "images": images,
            "video": video_info,
            "created_at": created_at,
            "user": {
                "name": user.get("name", TARGET_USER),
                "screen_name": user.get("screen_name", TARGET_USER),
                "avatar": user.get("profile_image_url_https", ""),
            },
            "urls": urls,
            "tweet_url": f"https://twitter.com/{TARGET_USER}/status/{tweet_id}",
        }
    except Exception as e:
        logger.error("Syndication API 获取推文 %s 失败: %s", tweet_id, e)
        return None


def fetch_comments_via_nitter(tweet_id: str) -> list[dict]:
    """
    通过 Nitter 实例抓取推文评论/回复
    注意：此方法依赖 Nitter 可用性，可能不稳定
    """
    comments = []
    nitter_instances = [
        f"https://nitter.net/{TARGET_USER}/status/{tweet_id}",
        f"https://nitter.privacydev.net/{TARGET_USER}/status/{tweet_id}",
    ]

    for url in nitter_instances:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "lxml")

            # Nitter 评论区结构：.thread-line 之后的 .tweet-body
            reply_items = soup.select(".reply .tweet-body, .thread .tweet-body")
            if not reply_items:
                # 备用选择器
                reply_items = soup.select(".timeline-item .tweet-content")

            for item in reply_items[:10]:  # 最多取 10 条评论
                # 提取评论者
                author_elem = item.select_one(".fullname, .username")
                author = author_elem.get_text(strip=True) if author_elem else ""

                # 提取评论文本
                content_elem = item.select_one(".tweet-content, .tweet-text")
                content = content_elem.get_text(strip=True) if content_elem else ""

                if content and content != "•":
                    comments.append({"author": author, "content": content})

            if comments:
                logger.info("从 Nitter 获取到 %d 条评论", len(comments))
                break
        except Exception as e:
            logger.warning("Nitter 评论获取失败 (%s): %s", url, e)

    return comments


def format_tweet_text(text: str) -> str:
    """格式化推文文本，处理 t.co 短链接"""
    # 移除末尾的 t.co 短链接（如果有）
    text = re.sub(r"\s*https://t\.co/\w+\s*$", "", text)
    return text.strip()


def fetch_new_tweets(last_id: Optional[str] = None) -> list[dict]:
    """
    主入口：获取新推文（自 last_id 以来的所有新推文）
    返回：按时间正序排列的推文列表
    """
    # 1. 从 RSS 获取最新推文列表
    rss_tweets = fetch_tweets_via_rss()
    if not rss_tweets:
        logger.error("无法获取推文列表")
        return []

    # 2. 过滤出新推文
    new_tweets = []
    found_last = last_id is None  # 如果没有 last_id，采集所有（最多 5 条）

    for tweet in rss_tweets:
        if found_last:
            new_tweets.append(tweet)
            if len(new_tweets) >= 5:  # 最多处理 5 条新推文
                break
        if tweet["id"] == last_id:
            found_last = True

    # 如果没有 last_id 则只取最新的 5 条
    if last_id is None:
        new_tweets = new_tweets[:5]

    if not new_tweets:
        logger.info("没有发现新推文")
        return []

    # 3. 用 Syndication API 丰富每条推文信息
    enriched = []
    for tweet in new_tweets:
        detail = enrich_tweet_via_syndication(tweet["id"])
        if detail:
            detail["text"] = format_tweet_text(detail["text"])
            # 如果 syndication 没拿到文本，用 RSS 的
            if not detail["text"] and tweet.get("raw_description"):
                soup = BeautifulSoup(tweet["raw_description"], "html.parser")
                detail["text"] = format_tweet_text(soup.get_text(separator="\n"))
            enriched.append(detail)
        else:
            # Syndication 失败，构造一个基础结构
            enriched.append(
                {
                    "id": tweet["id"],
                    "text": tweet.get("title", ""),
                    "images": [],
                    "video": None,
                    "created_at": tweet.get("pub_date", ""),
                    "user": {"name": TARGET_USER, "screen_name": TARGET_USER, "avatar": ""},
                    "urls": [],
                    "tweet_url": tweet.get("link", ""),
                }
            )

    # 4. 获取每条推文的评论
    for tweet in enriched:
        tweet["comments"] = fetch_comments_via_nitter(tweet["id"])

    logger.info("成功获取 %d 条新推文（含评论）", len(enriched))
    return enriched
