"""
HTML 模板模块
生成简洁大气的推送内容，包含推文原文、中文翻译、图片、评论
"""

import html as html_module
from datetime import datetime, timezone


CSS_STYLE = """
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #f5f5f5;
    color: #333;
    line-height: 1.6;
    padding: 16px;
  }
  .container { max-width: 680px; margin: 0 auto; }

  .card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #eee;
  }

  .card-header {
    display: flex;
    align-items: center;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }
  .avatar {
    width: 40px; height: 40px; border-radius: 50%;
    margin-right: 12px; background: #1da1f2;
    flex-shrink: 0;
  }
  .user-info { flex: 1; }
  .user-name { font-size: 15px; font-weight: 700; color: #14171a; }
  .user-handle { font-size: 13px; color: #657786; }
  .tweet-time {
    font-size: 12px; color: #657786; text-align: right;
    white-space: nowrap;
  }

  .section-label {
    display: inline-block;
    font-size: 11px; font-weight: 600; color: #1da1f2;
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-bottom: 6px;
    padding: 2px 8px; background: #e8f5fd; border-radius: 4px;
  }
  .tweet-text {
    font-size: 15px; color: #14171a; line-height: 1.7;
    margin-bottom: 16px; white-space: pre-wrap; word-wrap: break-word;
  }
  .tweet-translated {
    font-size: 14px; color: #555; line-height: 1.7;
    background: #f8f9fa; border-radius: 8px; padding: 12px 14px;
    margin-bottom: 16px; border-left: 3px solid #1da1f2;
  }
  .tweet-images { margin-bottom: 16px; }
  .tweet-images img {
    max-width: 100%; height: auto; border-radius: 10px;
    margin-bottom: 8px; border: 1px solid #eee;
    display: block;
  }
  .tweet-link {
    display: inline-block; font-size: 13px; color: #1da1f2;
    text-decoration: none; margin-bottom: 16px;
  }

  .comments-section { margin-top: 16px; padding-top: 14px; border-top: 1px solid #f0f0f0; }
  .comment {
    padding: 10px 0; border-bottom: 1px solid #f8f8f8;
  }
  .comment:last-child { border-bottom: none; }
  .comment-author { font-size: 13px; font-weight: 600; color: #14171a; margin-bottom: 4px; }
  .comment-original { font-size: 13px; color: #333; margin-bottom: 4px; }
  .comment-translated {
    font-size: 12px; color: #888;
    padding-left: 8px; border-left: 2px solid #e0e0e0;
  }
  .no-comments {
    font-size: 13px; color: #999; text-align: center;
    padding: 10px; font-style: italic;
  }

  .header-bar {
    text-align: center; padding: 20px 0; margin-bottom: 12px;
  }
  .header-bar h1 {
    font-size: 20px; font-weight: 700; color: #14171a;
  }
  .header-bar .subtitle {
    font-size: 13px; color: #657786; margin-top: 4px;
  }
  .footer {
    text-align: center; padding: 20px; font-size: 12px; color: #aaa;
  }
  .badge {
    display: inline-block; background: #1da1f2; color: #fff;
    font-size: 11px; padding: 2px 8px; border-radius: 10px;
    margin-left: 6px; vertical-align: middle;
  }
</style>
"""


def _escape(text: str) -> str:
    """HTML 转义"""
    return html_module.escape(text or "")


def _format_time(time_str: str) -> str:
    """格式化时间字符串"""
    if not time_str:
        return ""
    try:
        # 尝试多种格式
        for fmt in [
            "%a %b %d %H:%M:%S %z %Y",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S",
        ]:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                continue
        return time_str[:16]
    except Exception:
        return time_str[:16]


def _build_tweet_card(tweet: dict, index: int) -> str:
    """构建单条推文的 HTML 卡片"""
    parts = []

    # 卡片头部 — 用户信息
    avatar_url = tweet.get("user", {}).get("avatar", "")
    user_name = _escape(tweet.get("user", {}).get("name", "Unknown"))
    screen_name = _escape(tweet.get("user", {}).get("screen_name", ""))
    created_at = _format_time(tweet.get("created_at", ""))
    tweet_url = _escape(tweet.get("tweet_url", ""))

    parts.append('<div class="card">')

    # Header
    parts.append('<div class="card-header">')
    if avatar_url:
        parts.append(f'<img class="avatar" src="{_escape(avatar_url)}" alt="avatar" />')
    parts.append('<div class="user-info">')
    parts.append(f'<div class="user-name">{user_name}<span class="badge">#{index + 1}</span></div>')
    parts.append(f'<div class="user-handle">@{screen_name}</div>')
    parts.append("</div>")
    if created_at:
        parts.append(f'<div class="tweet-time">{created_at}</div>')
    parts.append("</div>")

    # 原文
    text = tweet.get("text", "")
    if text:
        parts.append('<div class="section-label">📝 原文</div>')
        parts.append(f'<div class="tweet-text">{_escape(text)}</div>')

    # 翻译
    translated = tweet.get("translated_text", "")
    if translated:
        parts.append('<div class="section-label">🌐 中文翻译</div>')
        parts.append(f'<div class="tweet-translated">{_escape(translated)}</div>')

    # 图片
    images = tweet.get("images", [])
    if images:
        parts.append('<div class="section-label">🖼 图片</div>')
        parts.append('<div class="tweet-images">')
        for img in images:
            src = _escape(img.get("converted", img.get("original", "")))
            if src:
                parts.append(f'<img src="{src}" alt="tweet image" loading="lazy" />')
        parts.append("</div>")

    # 视频
    video = tweet.get("video")
    if video and video.get("poster"):
        parts.append(f'<div class="section-label">🎬 视频封面</div>')
        parts.append(f'<img src="{_escape(video["poster"])}" style="max-width:100%;border-radius:10px;" />')

    # 外部链接
    urls = tweet.get("urls", [])
    if urls:
        parts.append('<div class="section-label">🔗 链接</div>')
        for u in urls:
            expanded = _escape(u.get("expanded_url", u.get("display_url", "")))
            display = _escape(u.get("display_url", ""))
            if expanded:
                parts.append(f'<div style="font-size:13px;margin-bottom:4px;">'
                             f'<a href="{expanded}" style="color:#1da1f2;">{display or expanded}</a></div>')

    # 原文链接
    if tweet_url:
        parts.append(f'<a class="tweet-link" href="{tweet_url}" target="_blank">'
                     f'🔗 在 Twitter 上查看 &rarr;</a>')

    # 评论区
    comments = tweet.get("comments", [])
    if comments:
        parts.append('<div class="comments-section">')
        parts.append(f'<div class="section-label">💬 评论 ({len(comments)})</div>')
        for c in comments:
            parts.append('<div class="comment">')
            parts.append(f'<div class="comment-author">{_escape(c.get("author", "匿名"))}</div>')
            parts.append(f'<div class="comment-original">{_escape(c.get("original", c.get("content", "")))}</div>')
            if c.get("translated"):
                parts.append(f'<div class="comment-translated">{_escape(c["translated"])}</div>')
            parts.append("</div>")
        parts.append("</div>")
    else:
        parts.append('<div class="comments-section">')
        parts.append('<div class="no-comments">暂无评论数据</div>')
        parts.append("</div>")

    parts.append("</div>")  # .card

    return "\n".join(parts)


def build_html(tweets: list[dict], username: str) -> str:
    """
    构建完整的推送 HTML 页面
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    count = len(tweets)

    parts = ["<!DOCTYPE html>", '<html lang="zh-CN">', "<head>"]
    parts.append('<meta charset="UTF-8" />')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0" />')
    parts.append(f"<title>@{_escape(username)} 推文更新</title>")
    parts.append(CSS_STYLE)
    parts.append("</head><body>")

    # 页面头部
    parts.append('<div class="container">')
    parts.append('<div class="header-bar">')
    parts.append(f"<h1>🐦 @{_escape(username)} 最新动态</h1>")
    parts.append(f'<div class="subtitle">{now} &middot; 抓取到 {count} 条新推文</div>')
    parts.append("</div>")

    # 推文卡片列表
    for i, tweet in enumerate(tweets):
        parts.append(_build_tweet_card(tweet, i))

    # 页脚
    parts.append('<div class="footer">')
    parts.append("Twitter Monitor · 自动推送 · Powered by GitHub Actions")
    parts.append("</div>")
    parts.append("</div>")

    parts.append("</body></html>")

    return "\n".join(parts)
