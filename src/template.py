"""
HTML 模板模块 v2
生成现代美观的推送内容：推文原文、精确时间、中文翻译、图片
"""

import html as html_module
from datetime import datetime


CSS_STYLE = """
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB",
                 "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    background: #f0f2f5;
    color: #1d1d1f;
    line-height: 1.6;
    padding: 12px 10px 24px;
  }
  .container { max-width: 600px; margin: 0 auto; }

  /* ── 顶部横幅 ── */
  .header-bar {
    text-align: center;
    padding: 22px 0 18px;
  }
  .header-bar .icon {
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%);
    margin: 0 auto 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; color: #fff;
    box-shadow: 0 4px 16px rgba(29, 161, 242, 0.3);
  }
  .header-bar h1 {
    font-size: 19px; font-weight: 700; color: #1d1d1f;
    letter-spacing: -0.3px;
  }
  .header-bar .subtitle {
    font-size: 12px; color: #86868b; margin-top: 4px;
  }
  .header-bar .count-badge {
    display: inline-block;
    background: #1da1f2; color: #fff;
    font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 10px;
    margin-top: 6px;
  }

  /* ── 推文卡片 ── */
  .card {
    background: #fff;
    border-radius: 14px;
    padding: 18px 16px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    border: 1px solid #e8e8ed;
  }

  /* 卡片头部：头像 + 用户名 + 时间 */
  .card-header {
    display: flex;
    align-items: flex-start;
    margin-bottom: 14px;
  }
  .avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #1da1f2, #1a91da);
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 16px; font-weight: 700;
    margin-right: 10px;
  }
  .user-info { flex: 1; min-width: 0; }
  .user-name {
    font-size: 15px; font-weight: 700; color: #1d1d1f;
    display: flex; align-items: center; gap: 6px;
  }
  .user-handle { font-size: 13px; color: #86868b; }
  .tweet-time {
    font-size: 12px; color: #86868b;
    background: #f5f5f7; border-radius: 6px;
    padding: 3px 10px; white-space: nowrap;
    flex-shrink: 0; margin-left: 10px;
    align-self: center;
  }

  /* ── 正文区域 ── */
  .text-section { margin-bottom: 14px; }
  .section-tag {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11px; font-weight: 600; color: #1da1f2;
    margin-bottom: 8px;
    padding: 2px 0;
    letter-spacing: 0.5px;
  }
  .tweet-text {
    font-size: 15px; color: #1d1d1f; line-height: 1.75;
    white-space: pre-wrap; word-wrap: break-word;
    padding: 12px 14px;
    background: #fafafc;
    border-radius: 10px;
    border: 1px solid #eeeef2;
  }

  /* ── 翻译区域 ── */
  .translated-section { margin-bottom: 14px; }
  .tweet-translated {
    font-size: 14px; color: #515154; line-height: 1.75;
    background: linear-gradient(135deg, #f0f7ff 0%, #f5f9ff 100%);
    border-radius: 10px; padding: 12px 14px;
    border-left: 3px solid #1da1f2;
  }

  /* ── 图片区域 ── */
  .images-section { margin-bottom: 14px; }
  .image-grid {
    display: grid;
    gap: 6px;
    border-radius: 10px;
    overflow: hidden;
  }
  .image-grid.single { grid-template-columns: 1fr; }
  .image-grid.multi { grid-template-columns: 1fr 1fr; }
  .image-grid img {
    width: 100%; height: auto; display: block;
    border-radius: 8px;
    border: 1px solid #eeeef2;
  }

  /* ── 原文链接 ── */
  .tweet-link-row {
    margin-bottom: 10px;
  }
  .tweet-link {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 12px; color: #1da1f2; text-decoration: none;
    font-weight: 500;
  }

  /* ── 评论区域 ── */
  .comments-section {
    margin-top: 14px; padding-top: 14px;
    border-top: 1px solid #f0f0f5;
  }
  .comment {
    padding: 8px 10px; margin-bottom: 6px;
    background: #fafafc; border-radius: 8px;
  }
  .comment:last-child { margin-bottom: 0; }
  .comment-author {
    font-size: 12px; font-weight: 600; color: #1d1d1f;
    margin-bottom: 3px;
  }
  .comment-original { font-size: 13px; color: #515154; line-height: 1.6; }
  .comment-translated {
    font-size: 12px; color: #86868b;
    margin-top: 4px; padding-left: 8px;
    border-left: 2px solid #d2d2d7;
  }
  .no-comments {
    font-size: 12px; color: #aeaeb2;
    text-align: center; padding: 8px;
  }

  /* ── 页脚 ── */
  .footer {
    text-align: center; padding: 18px 10px;
    font-size: 11px; color: #aeaeb2;
  }
  .footer .dot { margin: 0 6px; }

  /* ── 无图片时隐藏分割线 ── */
  hr { display: none; }
</style>
"""


def _escape(text: str) -> str:
    """HTML 转义"""
    return html_module.escape(text or "")


def _format_time(time_str: str) -> str:
    """
    格式化时间，精确到分钟。
    输入格式：Sun, 31 May 2026 01:31:00 GMT
    输出格式：05-31 01:31
    """
    if not time_str:
        return ""
    try:
        # RFC 2822 格式（RSS 标准）
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(time_str)
        # 转为北京时间
        from datetime import timezone, timedelta
        beijing = timezone(timedelta(hours=8))
        dt_beijing = dt.astimezone(beijing)
        return dt_beijing.strftime("%m-%d %H:%M")
    except Exception:
        pass

    # 备用：尝试常见格式
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S",
    ]:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.strftime("%m-%d %H:%M")
        except ValueError:
            continue

    # 兜底
    return time_str[:16] if len(time_str) >= 16 else time_str


def _build_tweet_card(tweet: dict, index: int) -> str:
    """构建单条推文的 HTML 卡片"""
    parts = []

    user_name = _escape(tweet.get("user", {}).get("name", "Unknown"))
    screen_name = _escape(tweet.get("user", {}).get("screen_name", ""))
    created_at = _format_time(tweet.get("created_at", ""))
    tweet_url = _escape(tweet.get("tweet_url", ""))

    parts.append('<div class="card">')

    # ── 卡片头部：头像 + 用户名 + 时间 ──
    parts.append('<div class="card-header">')
    parts.append(f'<div class="avatar">{index + 1}</div>')
    parts.append('<div class="user-info">')
    parts.append(f'<div class="user-name">{user_name}</div>')
    parts.append(f'<div class="user-handle">@{screen_name}</div>')
    parts.append('</div>')
    if created_at:
        parts.append(f'<div class="tweet-time">🕐 {created_at}</div>')
    parts.append('</div>')

    # ── 原文 ──
    text = tweet.get("text", "")
    if text:
        parts.append('<div class="text-section">')
        parts.append('<div class="section-tag">📝 原文</div>')
        parts.append(f'<div class="tweet-text">{_escape(text)}</div>')
        parts.append('</div>')

    # ── 中文翻译 ──
    translated = tweet.get("translated_text", "")
    if translated:
        parts.append('<div class="translated-section">')
        parts.append('<div class="section-tag">🌐 中文翻译</div>')
        parts.append(f'<div class="tweet-translated">{_escape(translated)}</div>')
        parts.append('</div>')

    # ── 图片 ──
    images = tweet.get("images", [])
    if images:
        parts.append('<div class="images-section">')
        parts.append('<div class="section-tag">🖼 图片</div>')
        grid_class = "image-grid single" if len(images) == 1 else "image-grid multi"
        parts.append(f'<div class="{grid_class}">')
        for img in images:
            src = img.get("converted", img.get("original", ""))
            if src:
                parts.append(f'<img src="{_escape(src)}" alt="推文图片" loading="lazy" />')
        parts.append('</div>')
        parts.append('</div>')

    # ── 视频封面 ──
    video = tweet.get("video")
    if video and video.get("poster"):
        parts.append('<div class="images-section">')
        parts.append('<div class="section-tag">🎬 视频</div>')
        parts.append(f'<img src="{_escape(video["poster"])}" '
                     f'style="max-width:100%;border-radius:10px;border:1px solid #eeeef2;" />')
        parts.append('</div>')

    # ── 外部链接 ──
    urls = tweet.get("urls", [])
    if urls:
        parts.append('<div class="tweet-link-row">')
        parts.append('<div class="section-tag">🔗 链接</div>')
        for u in urls:
            expanded = _escape(u.get("expanded_url", u.get("display_url", "")))
            display = _escape(u.get("display_url", ""))
            if expanded:
                parts.append(
                    f'<div style="font-size:12px;margin-bottom:4px;">'
                    f'<a href="{expanded}" style="color:#1da1f2;">{display or expanded}</a>'
                    f'</div>'
                )
        parts.append('</div>')

    # ── 原文链接 ──
    if tweet_url:
        parts.append('<div class="tweet-link-row">')
        parts.append(
            f'<a class="tweet-link" href="{tweet_url}" target="_blank">'
            f'🔗 在 Twitter 查看原文 &rarr;</a>'
        )
        parts.append('</div>')

    # ── 评论 ──
    comments = tweet.get("comments", [])
    parts.append('<div class="comments-section">')
    if comments:
        parts.append(f'<div class="section-tag">💬 评论 ({len(comments)})</div>')
        for c in comments:
            parts.append('<div class="comment">')
            parts.append(
                f'<div class="comment-author">{_escape(c.get("author", "匿名"))}</div>'
            )
            parts.append(
                f'<div class="comment-original">{_escape(c.get("original", c.get("content", "")))}</div>'
            )
            if c.get("translated"):
                parts.append(
                    f'<div class="comment-translated">{_escape(c["translated"])}</div>'
                )
            parts.append('</div>')
    else:
        parts.append('<div class="no-comments">暂无评论</div>')
    parts.append('</div>')

    parts.append('</div>')  # .card
    return "\n".join(parts)


def build_html(tweets: list[dict], username: str) -> str:
    """构建完整的推送 HTML 页面"""
    now = datetime.now().strftime("%m-%d %H:%M")
    count = len(tweets)

    parts = [
        '<!DOCTYPE html>',
        '<html lang="zh-CN">',
        '<head>',
        '<meta charset="UTF-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        f'<title>@{_escape(username)} 推文更新</title>',
        CSS_STYLE,
        '</head><body>',
    ]

    parts.append('<div class="container">')

    # ── 顶部横幅 ──
    parts.append('<div class="header-bar">')
    parts.append('<div class="icon">🐦</div>')
    parts.append(f'<h1>@{_escape(username)}</h1>')
    parts.append(f'<div class="subtitle">{now} 更新</div>')
    if count > 0:
        parts.append(f'<div class="count-badge">{count} 条新推文</div>')
    parts.append('</div>')

    # ── 推文卡片 ──
    for i, tweet in enumerate(tweets):
        parts.append(_build_tweet_card(tweet, i))

    # ── 页脚 ──
    parts.append('<div class="footer">')
    parts.append('Twitter Monitor<span class="dot">·</span>自动推送')
    parts.append('<br>Powered by GitHub Actions + RSS.app')
    parts.append('</div>')

    parts.append('</div>')
    parts.append('</body></html>')

    return "\n".join(parts)
