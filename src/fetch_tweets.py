"""
Twitter/X 推文抓取模块 v4 (2026-05-31 验证通过)
- Twitter Guest Token + GraphQL API（无需登录/API Key）
- 图片链接自动转换 pbs.twimg.com → pic.x.com
- 评论抓取（通过 Syndication API）
- 多层降级：GraphQL → Nitter RSS
"""

import json
import logging
import os
import re
import time
from typing import Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

TARGET_USER = os.environ.get("TWITTER_TARGET_USER", "aleabitoreddit")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

BEARER_TOKEN = (
    "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
    "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)

# ── Query IDs（2026-05 验证有效） ──────────────────────
QUERY_USER_BY_SCREEN_NAME = "7mjxD3-C6BxitPMVQ6w0-Q"
QUERY_USER_TWEETS = "LNhjy8t3XpIrBYM-ms7sPQ"

GRAPHQL_BASE = "https://twitter.com/i/api/graphql"
GUEST_TOKEN_URL = "https://api.twitter.com/1.1/guest/activate.json"
SYNDICATION_TWEET_URL = "https://cdn.syndication.twimg.com/tweet-result"

# Nitter 降级实例
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.tiekoetter.com",
    "https://nitter.privacyredirect.com",
    "https://nitter.space",
    "https://nitter.catsarch.com",
    "https://nuku.trabun.org",
    "https://lightbrd.com",
    "https://xcancel.com",
]

# Guest Token 缓存
_guest_token: Optional[str] = None
_guest_token_time: float = 0
GUEST_TOKEN_TTL = 3600


def convert_image_url(url: str) -> str:
    if not url:
        return ""
    return url.replace("pbs.twimg.com", "pic.x.com")


def format_tweet_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s*https://t\.co/\w+\s*$", "", text)
    return text.strip()


# ── Guest Token ────────────────────────────────────────

def _get_guest_token() -> str:
    global _guest_token, _guest_token_time
    now = time.time()
    if _guest_token and (now - _guest_token_time) < GUEST_TOKEN_TTL:
        return _guest_token
    try:
        h = {**HEADERS, "Authorization": BEARER_TOKEN}
        resp = requests.post(GUEST_TOKEN_URL, headers=h, timeout=15)
        if resp.status_code == 200:
            _guest_token = resp.json().get("guest_token", "")
            _guest_token_time = now
            logger.info("Guest Token 获取成功")
            return _guest_token
        logger.warning("Guest Token 失败: %d", resp.status_code)
    except Exception as e:
        logger.warning("Guest Token 异常: %s", e)
    return ""


def _make_session() -> requests.Session:
    token = _get_guest_token()
    s = requests.Session()
    s.headers.update(HEADERS)
    s.headers["Authorization"] = BEARER_TOKEN
    if token:
        s.headers["x-guest-token"] = token
    return s


# ── GraphQL 抓取 ───────────────────────────────────────

def _get_user_id(session: requests.Session) -> Optional[str]:
    """通过 screen_name 获取用户 rest_id"""
    try:
        variables = json.dumps({
            "screen_name": TARGET_USER,
            "withSafetyModeUserFields": True,
            "withSuperFollowsUserFields": True,
        })
        features = json.dumps({
            "hidden_profile_likes_enabled": True,
            "highlights_tweets_tab_ui_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
        })
        params = {"variables": variables, "features": features}
        url = f"{GRAPHQL_BASE}/{QUERY_USER_BY_SCREEN_NAME}/UserByScreenName"
        resp = session.get(url, params=params, timeout=20)

        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", {}).get("user", {}).get("result", {})
            uid = result.get("rest_id")
            if not uid:
                uid = result.get("legacy", {}).get("id_str")
            if uid:
                logger.info("用户 ID: %s → %s", TARGET_USER, uid)
                return uid
        logger.warning("获取用户 ID 失败: %d", resp.status_code)
    except Exception as e:
        logger.warning("获取用户 ID 异常: %s", e)
    return None


def _parse_tweet_entry(entry: dict) -> Optional[dict]:
    """解析 Timeline Entry → 推文字典"""
    try:
        content = entry.get("content", {})
        if content.get("entryType") != "TimelineTimelineItem":
            return None
        item_content = content.get("itemContent", {})
        if item_content.get("itemType") != "TimelineTweet":
            return None

        tweet_result = item_content.get("tweet_results", {}).get("result", {})
        if "tweet" in tweet_result:
            tweet_result = tweet_result["tweet"]
        if "core" not in tweet_result:
            return None

        legacy = tweet_result.get("legacy", {})
        core = tweet_result.get("core", {})
        user_results = core.get("user_results", {}).get("result", {})
        user_legacy = user_results.get("legacy", {})

        tid = legacy.get("id_str", "")
        if not tid:
            return None

        text = format_tweet_text(legacy.get("full_text", ""))

        # 图片
        images = []
        entities = legacy.get("entities", {})
        for media in entities.get("media", []):
            if media.get("type") == "photo":
                img_url = media.get("media_url_https", "")
                if img_url:
                    images.append({
                        "original": img_url,
                        "converted": convert_image_url(img_url),
                        "width": media.get("original_info", {}).get("width", 0),
                        "height": media.get("original_info", {}).get("height", 0),
                    })

        # 扩展媒体（视频缩略图）
        video_info = None
        for media in legacy.get("extended_entities", {}).get("media", []):
            if media.get("type") in ("video", "animated_gif"):
                thumb = convert_image_url(media.get("media_url_https", ""))
                video_info = {"poster": thumb}
                break

        # 外部链接
        urls = []
        for ue in entities.get("urls", []):
            urls.append({
                "display_url": ue.get("display_url", ""),
                "expanded_url": ue.get("expanded_url", ""),
            })

        return {
            "id": tid,
            "text": text,
            "images": images,
            "video": video_info,
            "created_at": legacy.get("created_at", ""),
            "user": {
                "name": user_legacy.get("name", TARGET_USER),
                "screen_name": user_legacy.get("screen_name", TARGET_USER),
                "avatar": convert_image_url(
                    user_legacy.get("profile_image_url_https", "")
                ),
            },
            "urls": urls,
            "tweet_url": f"https://twitter.com/{TARGET_USER}/status/{tid}",
        }
    except Exception as e:
        logger.debug("解析条目异常: %s", e)
        return None


def fetch_tweets_via_graphql(last_id: Optional[str] = None) -> list[dict]:
    """通过 Twitter GraphQL API 抓取用户时间线"""
    session = _make_session()
    if not session.headers.get("x-guest-token"):
        logger.error("无 Guest Token，GraphQL 不可用")
        return []

    user_id = _get_user_id(session)
    if not user_id:
        return []

    try:
        variables = json.dumps({
            "userId": user_id,
            "count": 20,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True,
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "withSuperFollowsTweetFields": True,
            "withSuperFollowsUserFields": True,
            "withCommunityTweetFields": True,
            "withBirdwatchPivots": False,
            "withReplaysMetadata": False,
        })

        features = json.dumps({
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_enhance_cards_enabled": False,
        })

        params = {"variables": variables, "features": features}
        url = f"{GRAPHQL_BASE}/{QUERY_USER_TWEETS}/UserTweets"
        resp = session.get(url, params=params, timeout=30)

        if resp.status_code != 200:
            logger.error("GraphQL 时间线失败: %d", resp.status_code)
            return []

        data = resp.json()
    except Exception as e:
        logger.error("GraphQL 时间线异常: %s", e)
        return []

    instructions = (
        data.get("data", {})
        .get("user", {})
        .get("result", {})
        .get("timeline_v2", {})
        .get("timeline", {})
        .get("instructions", [])
    )

    tweets = []
    for instruction in instructions:
        if instruction.get("type") != "TimelineAddEntries":
            continue
        for entry in instruction.get("entries", []):
            tweet_data = _parse_tweet_entry(entry)
            if not tweet_data:
                continue
            if tweet_data["id"] == last_id:
                break
            tweets.append(tweet_data)
            if len(tweets) >= 20:
                break
        if len(tweets) >= 20:
            break

    return tweets


# ── Syndication API（详情补充）─────────────────────────

def fetch_tweet_detail_via_syndication(tweet_id: str) -> Optional[dict]:
    """通过 Syndication API 获取单条推文详情"""
    try:
        params = {"id": tweet_id, "lang": "en"}
        resp = requests.get(
            SYNDICATION_TWEET_URL, params=params, headers=HEADERS, timeout=15
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        text = format_tweet_text(data.get("text", ""))

        images = []
        for photo in data.get("photos", []):
            img_url = photo.get("url", "")
            if img_url:
                images.append({
                    "original": img_url,
                    "converted": convert_image_url(img_url),
                    "width": photo.get("width", 0),
                    "height": photo.get("height", 0),
                })

        user = data.get("user", {})
        return {
            "id": tweet_id,
            "text": text,
            "images": images,
            "created_at": data.get("created_at", ""),
            "user": {
                "name": user.get("name", TARGET_USER),
                "screen_name": user.get("screen_name", TARGET_USER),
                "avatar": user.get("profile_image_url_https", ""),
            },
            "tweet_url": f"https://twitter.com/{TARGET_USER}/status/{tweet_id}",
        }
    except Exception as e:
        logger.debug("Syndication %s 失败: %s", tweet_id, e)
        return None


# ── Nitter RSS（降级）──────────────────────────────────

def fetch_tweets_via_nitter_rss() -> list[dict]:
    """Nitter RSS 降级方案"""
    import xml.etree.ElementTree as ET

    for base_url in NITTER_INSTANCES:
        rss_url = f"{base_url}/{TARGET_USER}/rss"
        try:
            logger.info("尝试 Nitter: %s", rss_url)
            resp = requests.get(rss_url, headers=HEADERS, timeout=15)
            if resp.status_code != 200 or not resp.text.strip():
                continue
            if "<rss" not in resp.text.lower() and "<feed" not in resp.text.lower():
                continue

            root = ET.fromstring(resp.text)
            tweets = []
            ns_atom = "{http://www.w3.org/2005/Atom}"
            items = root.findall(".//item") or root.findall(f".//{ns_atom}entry")

            for item in items:
                link = item.findtext("link") or ""
                atom_link = item.find(f"{ns_atom}link")
                if atom_link is not None:
                    link = atom_link.get("href", link)

                match = re.search(r"/status/(\d+)", link)
                if not match:
                    guid = item.findtext("guid") or item.findtext(f"{ns_atom}id", "")
                    match = re.search(r"(\d{15,})", guid)
                if not match:
                    continue

                tid = match.group(1)
                title = item.findtext("title") or item.findtext(f"{ns_atom}title", "")
                pub_date = item.findtext("pubDate") or item.findtext(f"{ns_atom}published", "")

                tweets.append({
                    "id": tid,
                    "title": re.sub(r"^[^:]+:\s*", "", title or ""),
                    "link": link,
                    "pub_date": pub_date,
                })

            if tweets:
                logger.info("Nitter RSS 获取 %d 条: %s", len(tweets), rss_url)
                return tweets
        except Exception as e:
            logger.debug("Nitter %s 失败: %s", rss_url, e)
    return []


# ── 评论抓取 ──────────────────────────────────────────

def fetch_comments(tweet_id: str) -> list[dict]:
    """抓取推文评论（Syndication API）"""
    try:
        params = {"id": tweet_id, "lang": "en", "conversation": "true"}
        resp = requests.get(
            SYNDICATION_TWEET_URL, params=params, headers=HEADERS, timeout=15
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
                text = format_tweet_text(ct.get("text", ""))
                if author and text:
                    comments.append({"author": author, "content": text})
                if len(comments) >= 10:
                    break
            if len(comments) >= 10:
                break

        if comments:
            logger.info("获取 %d 条评论", len(comments))
        return comments
    except Exception as e:
        logger.debug("评论抓取失败: %s", e)
        return []


# ── 主入口 ────────────────────────────────────────────

def fetch_new_tweets(last_id: Optional[str] = None) -> list[dict]:
    """
    主入口：获取新推文
    策略：GraphQL（主）→ Nitter RSS（降级）
    """
    raw_tweets = []

    # 第 1 层：GraphQL
    logger.info("第 1 层: Twitter GraphQL API")
    raw_tweets = fetch_tweets_via_graphql(last_id)

    # 第 2 层：Nitter RSS
    if not raw_tweets:
        logger.info("第 2 层: Nitter RSS")
        raw_tweets = fetch_tweets_via_nitter_rss()

    if not raw_tweets:
        logger.error("所有数据源均不可用")
        return []

    # 过滤 & 丰富
    tweets = []
    for tweet in raw_tweets:
        tid = tweet.get("id", "")
        if tid == last_id:
            break

        detail = fetch_tweet_detail_via_syndication(tid)
        if detail:
            tweets.append(detail)
        else:
            tweets.append({
                "id": tid,
                "text": tweet.get("title", tweet.get("text", "")),
                "images": tweet.get("images", []),
                "video": tweet.get("video"),
                "created_at": tweet.get("pub_date", tweet.get("created_at", "")),
                "user": tweet.get("user", {
                    "name": TARGET_USER,
                    "screen_name": TARGET_USER,
                    "avatar": ""}),
                "urls": tweet.get("urls", []),
                "tweet_url": tweet.get("link", tweet.get("tweet_url", "")),
            })

    if last_id is None:
        tweets = tweets[:5]

    # 获取评论
    for tweet in tweets:
        tweet["comments"] = fetch_comments(tweet["id"])

    logger.info("成功获取 %d 条新推文", len(tweets))
    return tweets
