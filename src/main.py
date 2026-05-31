#!/usr/bin/env python3
"""
Twitter 推文监控主程序
- 检测 @aleabitoreddit 的新推文
- 翻译为中文
- 抓取评论
- 通过 PushPlus 推送
- 在 GitHub Actions 中定时运行
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from fetch_tweets import fetch_new_tweets
from translator import translate_text, translate_comments
from template import build_html
from pushplus import send_tweet_push

# ── 配置 ──────────────────────────────────────────────
TARGET_USER = "aleabitoreddit"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "3d9d364039ab432ead44d9725e456f7a")

# 状态文件路径（GitHub Actions 中为仓库根目录）
STATE_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = STATE_DIR / "last_id.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


def load_last_id() -> str | None:
    """加载上次处理的最新推文 ID"""
    try:
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            last_id = data.get("last_tweet_id")
            if last_id:
                logger.info("上次处理推文 ID: %s", last_id)
            return last_id
    except Exception as e:
        logger.warning("读取状态文件失败: %s", e)
    return None


def save_last_id(tweet_id: str) -> None:
    """保存最新推文 ID"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data = {"last_tweet_id": tweet_id}
    STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("已更新状态: last_tweet_id=%s", tweet_id)


def process_tweets(tweets: list[dict]) -> None:
    """处理推文：翻译 + 构建 HTML + 推送"""
    if not tweets:
        logger.info("没有新推文需要处理")
        return

    # 翻译每条推文和评论
    for tweet in tweets:
        text = tweet.get("text", "")
        if text:
            tweet["translated_text"] = translate_text(text)

        comments = tweet.get("comments", [])
        if comments:
            tweet["comments"] = translate_comments(comments)

    # 构建 HTML
    html_content = build_html(tweets, TARGET_USER)

    # 发送推送
    success = send_tweet_push(PUSHPLUS_TOKEN, TARGET_USER, html_content, len(tweets))
    if success:
        logger.info("推送成功！%d 条推文", len(tweets))
    else:
        logger.error("推送失败")


def main():
    """主流程"""
    logger.info("=" * 50)
    logger.info("开始检查 @%s 的新推文", TARGET_USER)

    # 1. 加载上次状态
    last_id = load_last_id()

    # 2. 获取新推文
    tweets = fetch_new_tweets(last_id)

    if not tweets:
        logger.info("没有发现新推文，任务结束")
        return

    # 3. 处理并推送
    process_tweets(tweets)

    # 4. 保存最新推文 ID（取最新的那条）
    latest_tweet = tweets[0]  # RSS 按时间倒序
    save_last_id(latest_tweet["id"])

    logger.info("任务完成")


if __name__ == "__main__":
    main()
