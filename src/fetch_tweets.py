"""
Twitter/X 推文抓取模块 v3
- 使用 Twitter 公开 Guest Token + GraphQL API（不需要登录/API Key）
- 图片链接自动转换 pbs.twimg.com → pic.x.com  
- 评论抓取
- 多层降级：GraphQL → Syndication API → Nitter 实例
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

# ── 配置 ──────────────────────────────────────────────
TARGET_USER = os.environ.get("TWITTER_TARGET_USER", "aleabitoreddit")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

# Twitter API 端点
GUEST_TOKEN_URL = "https://api.twitter.com/1.1/guest/activate.json"
GRAPHQL_URL = "https://twitter.com/i/api/graphql"

# Nitter 实例列表（作为降级方案）
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

# Syndication API
SYNDICATION_TWEET_URL = "https://cdn.syndication.twimg.com/tweet-result"

# 缓存 Guest Token
_guest_token: Optional[str] = None
_guest_token_time: float = 0
GUEST_TOKEN_TTL = 3600  # 1 小时


def convert_image_url(url: str) -> str:
    """将 pbs.twimg.com 转为 pic.x.com"""
    if not url:
        return ""
    return url.replace("pbs.twimg.com", "pic.x.com")


def format_tweet_text(text: str) -> str:
    """清理推文文本"""
    if not text:
        return ""
    text = re.sub(r"\s*https://t\.co/\w+\s*$", "", text)
    return text.strip()


def _get_guest_token() -> str:
    """获取 Twitter Guest Token（缓存 1 小时）"""
    global _guest_token, _guest_token_time
    now = time.time()
    if _guest_token and (now - _guest_token_time) < GUEST_TOKEN_TTL:
        return _guest_token

    try:
        headers = {**HEADERS, "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"}
        resp = requests.post(GUEST_TOKEN_URL, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            _guest_token = data.get("guest_token", "")
            _guest_token_time = now
            logger.info("获取 Guest Token 成功")
            return _guest_token
        logger.warning("Guest Token 请求失败: %s", resp.status_code)
    except Exception as e:
        logger.warning("Guest Token 请求异常: %s", e)

    return ""


def _get_user_id(session: requests.Session) -> Optional[str]:
    """通过 screen_name 获取用户 ID"""
    try:
        variables = json.dumps({"screen_name": TARGET_USER, "withSafetyModeUserFields": True})
        features = json.dumps({"hidden_profile_likes_enabled": True, "highlights_tweets_tab_ui_enabled": True})

        params = {"variables": variables, "features": features}

        url = f"{GRAPHQL_URL}/PrmbUoHTyOJeDKGyniHE_A/UserByScreenName"
        resp = session.get(url, params=params, timeout=20)

        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", {}).get("user", {}).get("result", {})
            user_id = result.get("rest_id")
            if user_id:
                logger.info("获取用户 ID: %s → %s", TARGET_USER, user_id)
                return user_id

            # 备用：从 legacy 获取
            legacy = result.get("legacy", {})
            if legacy:
                user_id = legacy.get("id_str")
                if user_id:
                    return user_id

        logger.warning("获取用户 ID 失败: status=%d", resp.status_code)
    except Exception as e:
        logger.warning("获取用户 ID 异常: %s", e)

    return None


def _parse_tweet_entry(entry: dict) -> Optional[dict]:
    """解析单个 Timeline Entry，提取推文信息"""
    try:
        content = entry.get("content", {})
        entry_type = content.get("entryType", "")

        if entry_type != "TimelineTimelineItem":
            return None

        item_content = content.get("itemContent", {})
        item_type = item_content.get("itemType", "")

        if item_type != "TimelineTweet":
            return None

        tweet_result = item_content.get("tweet_results", {}).get("result", {})
        # 有时推文嵌套在 "tweet" 字段里
        if "tweet" in tweet_result:
            tweet_result = tweet_result["tweet"]
        if "core" not in tweet_result:
            return None

        legacy = tweet_result.get("legacy", {})
        core = tweet_result.get("core", {})
        user_results = core.get("user_results", {}).get("result", {})
        user_legacy = user_results.get("legacy", {})

        tweet_id = legacy.get("id_str", "")
        if not tweet_id:
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

        # 扩展的媒体（含视频缩略图）
        video_info = None
        extended_media = legacy.get("extended_entities", {}).get("media", [])
        for media in extended_media:
            if media.get("type") in ("video", "animated_gif"):
                thumb = media.get("media_url_https", "")
                video_info = {"poster": convert_image_url(thumb), "duration": 0}
                break

        # 外部链接
        urls = []
        for url_entity in entities.get("urls", []):
            urls.append({
                "display_url": url_entity.get("display_url", ""),
                "expanded_url": url_entity.get("expanded_url", ""),
            })

        return {
            "id": tweet_id,
            "text": text,
            "images": images,
            "video": video_info,
            "created_at": legacy.get("created_at", ""),
            "user": {
                "name": user_legacy.get("name", TARGET_USER),
                "screen_name": user_legacy.get("screen_name", TARGET_USER),
                "avatar": convert_image_url(user_legacy.get("profile_image_url_https", "")),
            },
            "urls": urls,
            "tweet_url": f"https://twitter.com/{TARGET_USER}/status/{tweet_id}",
        }
    except Exception as e:
        logger.debug("解析推文条目失败: %s", e)
        return None


def fetch_tweets_via_graphql(last_id: Optional[str] = None) -> list[dict]:
    """
    通过 Twitter GraphQL API 获取用户最新推文
    使用 Guest Token（无需登录）
    """
    token = _get_guest_token()
    if not token:
        logger.error("无法获取 Guest Token")
        return []

    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers["x-guest-token"] = token
    session.headers["Authorization"] = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

    # 获取用户 ID
    user_id = _get_user_id(session)
    if not user_id:
        logger.error("无法获取用户 ID")
        return []

    # 获取时间线
    try:
        variables = json.dumps({
            "userId": user_id,
            "count": 20,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True,
        })
        features = json.dumps({
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": True,
            "responsive_web_jetfuel_frame": False,
            "responsive_web_grok_share_attachment_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_grok_show_grok_translated_post": False,
            "responsive_web_grok_analysis_button_from_backend": True,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_grok_image_annotation_enabled": True,
            "responsive_web_grok_show_grok_convos_with_shared_tweets": False,
            "rweb_video_timestamps_enabled": True,
            "responsive_web_enhance_cards_enabled": False,
        })

        params = {"variables": variables, "features": features}
        url = f"{GRAPHQL_URL}/VVKBXxIUo7GsUCoCctf2kQ/UserTweets"

        resp = session.get(url, params=params, timeout=30)

        if resp.status_code != 200:
            logger.error("GraphQL 时间线请求失败: %d", resp.status_code)
            return []

        data = resp.json()
    except Exception as e:
        logger.error("GraphQL 时间线请求异常: %s", e)
        return []

    # 解析推文
    instructions = data.get("data", {}).get("user", {}).get("result", {}).get("timeline_v2", {}).get("timeline", {}).get("instructions", [])
    
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

    return tweets


def fetch_tweet_detail_via_syndication(tweet_id: str) -> Optional[dict]:
    """通过 Syndication API 获取单条推文详情（用于补充信息）"""
    try:
        params = {"id": tweet_id, "lang": "en"}
        resp = requests.get(SYNDICATION_TWEET_URL, params=params, headers=HEADERS, timeout=15)
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
        logger.debug("Syndication API 获取 %s 失败: %s", tweet_id, e)
        return None


def fetch_tweets_via_nitter_rss() -> list[dict]:
    """通过 Nitter 实例 RSS 获取推文列表（降级方案）"""
    import xml.etree.ElementTree as ET

    for base_url in NITTER_INSTANCES:
        rss_url = f"{base_url}/{TARGET_USER}/rss"
        try:
            logger.info("尝试 Nitter: %s", rss_url)
            resp = requests.get(rss_url, headers=HEADERS, timeout=15)
            if resp.status_code != 200 or not resp.text.strip():
                continue

            # 检查是否是 RSS
            if "<rss" not in resp.text.lower() and "<feed" not in resp.text.lower():
                continue

            root = ET.fromstring(resp.text)
            tweets = []
            items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

            for item in items:
                link = item.findtext("link") or ""
                if hasattr(item, 'find'):
                    atom_link = item.find("{http://www.w3.org/2005/Atom}link")
                    if atom_link is not None:
                        link = atom_link.get("href", link)

                match = re.search(r"/status/(\d+)", link)
                if not match:
                    # 尝试从 guid 中提取
                    guid = item.findtext("guid") or item.findtext("{http://www.w3.org/2005/Atom}id", "")
                    match = re.search(r"(\d{15,})", guid)

                if not match:
                    continue

                tweet_id = match.group(1)
                title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title", "")
                pub_date = item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}published", "")

                tweets.append({
                    "id": tweet_id,
                    "title": re.sub(r"^[^:]+:\s*", "", title or ""),
                    "link": link,
                    "pub_date": pub_date,
                })

            if tweets:
                logger.info("Nitter RSS 获取 %d 条推文: %s", len(tweets), rss_url)
                return tweets
        except Exception as e:
            logger.debug("Nitter %s 失败: %s", rss_url, e)

    return []


def enrich_and_filter_tweets(raw_tweets: list[dict], last_id: Optional[str] = None) -> list[dict]:
    """
    用 Syndication API 丰富推文信息，并过滤出新推文
    """
    new_tweets = []
    for tweet in raw_tweets:
        tid = tweet.get("id", "")
        if tid == last_id:
            break

        detail = fetch_tweet_detail_via_syndication(tid)
        if detail:
            new_tweets.append(detail)
        else:
            # 构造基础结构
            new_tweets.append({
                "id": tid,
                "text": tweet.get("title", tweet.get("text", "")),
                "images": [],
                "video": None,
                "created_at": tweet.get("pub_date", tweet.get("created_at", "")),
                "user": {"name": TARGET_USER, "screen_name": TARGET_USER, "avatar": ""},
                "urls": [],
                "tweet_url": tweet.get("link", tweet.get("tweet_url", "")),
            })

    if last_id is None:
        new_tweets = new_tweets[:5]

    return new_tweets


def fetch_comments(tweet_id: str) -> list[dict]:
    """抓取推文评论（尝试多种方式）"""
    # 方式1: Syndication API 带 conversation
    try:
        params = {"id": tweet_id, "lang": "en", "conversation": "true"}
        resp = requests.get(SYNDICATION_TWEET_URL, params=params, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            conv_threads = data.get("conversationThreads", [])
            comments = []
            for thread in conv_threads:
                for conv_tweet in thread.get("tweets", []):
                    # 跳过原推文本身
                    if conv_tweet.get("id_str") == tweet_id:
                        continue
                    author = conv_tweet.get("user", {}).get("name", "")
                    text = format_tweet_text(conv_tweet.get("text", ""))
                    if author and text:
                        comments.append({"author": author, "content": text})
                    if len(comments) >= 10:
                        break
            if comments:
                logger.info("获取 %d 条评论 (syndication)", len(comments))
                return comments
    except Exception as e:
        logger.debug("Syndication 评论获取失败: %s", e)

    return []


def fetch_new_tweets(last_id: Optional[str] = None) -> list[dict]:
    """
    主入口：获取新推文
    三层降级：GraphQL → Nitter RSS → 空
    """
    raw_tweets = []

    # 第 1 层：GraphQL API
    logger.info("第 1 层尝试: Twitter GraphQL API")
    raw_tweets = fetch_tweets_via_graphql(last_id)

    # 第 2 层：Nitter RSS
    if not raw_tweets:
        logger.info("第 2 层尝试: Nitter RSS")
        nitter_tweets = fetch_tweets_via_nitter_rss()
        raw_tweets = nitter_tweets

    if not raw_tweets:
        logger.error("所有数据源均不可用")
        return []

    # 丰富 & 过滤
    tweets = enrich_and_filter_tweets(raw_tweets, last_id)

    if not tweets:
        logger.info("没有发现新推文")
        return []

    # 获取评论
    for tweet in tweets:
        tweet["comments"] = fetch_comments(tweet["id"])

    logger.info("成功获取 %d 条新推文", len(tweets))
    return tweets
