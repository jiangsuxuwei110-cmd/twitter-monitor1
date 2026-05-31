"""
Twitter/X 推文抓取模块 v2
- 使用 twikit 库通过 Twitter 账号登录抓取（不需要 API Key）
- Cookie 持久化，避免每次重新登录
- 图片链接自动转换 pbs.twimg.com → pic.x.com
- 评论抓取（获取推文回复）
"""

import json
import logging
import os
import re
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

# ── 配置 ──────────────────────────────────────────────
TARGET_USER = os.environ.get("TWITTER_TARGET_USER", "aleabitoreddit")

# Cookie 文件路径（GitHub Actions 中从环境变量注入）
COOKIE_FILE = os.environ.get("COOKIE_FILE", "data/cookies.json")

# Twitter 账号（用于首次登录，之后用 Cookie）
TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME", "")
TWITTER_EMAIL = os.environ.get("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD", "")


def convert_image_url(url: str) -> str:
    """将 pbs.twimg.com 转为 pic.x.com，避免 PushPlus 拦截"""
    if not url:
        return url
    return url.replace("pbs.twimg.com", "pic.x.com")


def format_tweet_text(text: str) -> str:
    """格式化推文文本，移除末尾 t.co 短链接"""
    if not text:
        return ""
    text = re.sub(r"\s*https://t\.co/\w+\s*$", "", text)
    return text.strip()


async def _get_client():
    """获取 twikit 客户端（自动处理登录/Cookie）"""
    from twikit import Client

    client = Client("en-US")

    # 检查是否有 cookie 文件
    if os.path.exists(COOKIE_FILE):
        try:
            client.load_cookies(COOKIE_FILE)
            logger.info("从文件加载 Cookie 成功")
            return client
        except Exception as e:
            logger.warning("Cookie 加载失败，尝试重新登录: %s", e)

    # 检查环境变量中的 Cookie（GitHub Actions Secret）
    cookie_str = os.environ.get("TWITTER_COOKIES", "")
    if cookie_str:
        try:
            cookies = json.loads(cookie_str)
            # 写入临时文件
            os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
            with open(COOKIE_FILE, "w") as f:
                json.dump(cookies, f)
            client.load_cookies(COOKIE_FILE)
            logger.info("从环境变量加载 Cookie 成功")
            return client
        except Exception as e:
            logger.warning("环境变量 Cookie 解析失败: %s", e)

    # 使用账号密码登录
    if TWITTER_USERNAME and TWITTER_PASSWORD:
        logger.info("使用账号密码登录 Twitter...")
        await client.login(
            auth_info_1=TWITTER_USERNAME,
            auth_info_2=TWITTER_EMAIL if TWITTER_EMAIL else None,
            password=TWITTER_PASSWORD,
        )
        # 保存 Cookie
        os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
        client.save_cookies(COOKIE_FILE)
        logger.info("登录成功，Cookie 已保存")
        return client

    raise RuntimeError(
        "无法获取 Twitter 客户端：请配置 TWITTER_COOKIES 或 TWITTER_USERNAME/TWITTER_PASSWORD 环境变量"
    )


async def _fetch_user_tweets(last_id: Optional[str] = None) -> list[dict]:
    """使用 twikit 获取用户最新推文"""
    client = await _get_client()

    # 获取用户信息
    user = await client.get_user_by_screen_name(TARGET_USER)
    logger.info("获取用户 @%s (id=%s)", TARGET_USER, user.id)

    # 获取最新推文（取 20 条，足够找到新内容）
    tweets = await client.get_user_tweets(user.id, "Tweets", count=20)

    result = []
    for tweet in tweets:
        tweet_id = tweet.id

        # 如果遇到上次处理的推文 ID，停止
        if tweet_id == last_id:
            break

        # 提取文本
        text = format_tweet_text(tweet.text or "")

        # 提取图片
        images = []
        if hasattr(tweet, "media") and tweet.media:
            for media in tweet.media:
                if hasattr(media, "type") and media.type == "photo":
                    img_url = getattr(media, "media_url_https", "") or getattr(media, "url", "")
                    if img_url:
                        images.append(
                            {
                                "original": img_url,
                                "converted": convert_image_url(img_url),
                                "width": getattr(media, "width", 0),
                                "height": getattr(media, "height", 0),
                            }
                        )

        # 提取视频缩略图
        video_info = None
        if hasattr(tweet, "media") and tweet.media:
            for media in tweet.media:
                if hasattr(media, "type") and media.type in ("video", "animated_gif"):
                    thumb = getattr(media, "media_url_https", "")
                    video_info = {"poster": convert_image_url(thumb), "duration": 0}
                    break

        # 提取外部链接
        urls = []
        if hasattr(tweet, "urls") and tweet.urls:
            for url_entity in tweet.urls:
                urls.append(
                    {
                        "display_url": getattr(url_entity, "display_url", ""),
                        "expanded_url": getattr(url_entity, "expanded_url", ""),
                    }
                )

        # 用户信息
        tweet_user = tweet.user
        avatar_url = ""
        if tweet_user:
            avatar_url = convert_image_url(
                getattr(tweet_user, "profile_image_url_https", "") or ""
            )

        result.append(
            {
                "id": tweet_id,
                "text": text,
                "images": images,
                "video": video_info,
                "created_at": str(tweet.created_at) if hasattr(tweet, "created_at") else "",
                "user": {
                    "name": tweet_user.name if tweet_user else TARGET_USER,
                    "screen_name": tweet_user.screen_name if tweet_user else TARGET_USER,
                    "avatar": avatar_url,
                },
                "urls": urls,
                "tweet_url": f"https://twitter.com/{TARGET_USER}/status/{tweet_id}",
            }
        )

    return result


async def _fetch_tweet_comments(tweet_id: str) -> list[dict]:
    """获取推文评论（回复）"""
    try:
        client = await _get_client()
        # 获取推文详情和回复
        tweet = await client.get_tweet_by_id(tweet_id)
        if not tweet:
            return []

        comments = []
        # 获取回复
        if hasattr(tweet, "replies") and tweet.replies:
            for reply in tweet.replies[:10]:
                author = ""
                if reply.user:
                    author = reply.user.name or reply.user.screen_name or ""
                content = format_tweet_text(reply.text or "")
                if content:
                    comments.append({"author": author, "content": content})

        return comments
    except Exception as e:
        logger.warning("获取推文 %s 评论失败: %s", tweet_id, e)
        return []


def fetch_new_tweets(last_id: Optional[str] = None) -> list[dict]:
    """
    主入口：获取新推文（同步包装异步函数）
    返回：按时间倒序的新推文列表（最新的在前）
    """
    try:
        tweets = asyncio.run(_fetch_new_tweets_async(last_id))
        return tweets
    except Exception as e:
        logger.error("fetch_new_tweets 失败: %s", e)
        return []


async def _fetch_new_tweets_async(last_id: Optional[str] = None) -> list[dict]:
    """异步获取新推文"""
    # 1. 获取推文列表
    tweets = await _fetch_user_tweets(last_id)

    if not tweets:
        logger.info("没有发现新推文")
        return []

    # 首次运行（无 last_id），最多取 5 条
    if last_id is None:
        tweets = tweets[:5]

    # 2. 获取评论
    for tweet in tweets:
        tweet["comments"] = await _fetch_tweet_comments(tweet["id"])

    logger.info("成功获取 %d 条新推文", len(tweets))
    return tweets
