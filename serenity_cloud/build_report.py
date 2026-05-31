"""
Serenity Daily - HTML Report Builder (Cloud Version)
Builds and updates the cumulative HTML report.
Today's new entries are highlighted with orange (#ff6b35) styling.
"""
from datetime import datetime

BEIJING_TZ_OFFSET = 8

# --- CSS Styling ---
CSS = """
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f0f2f5; color: #2c3e50; line-height: 1.7;
    max-width: 680px; margin: 0 auto; padding: 0;
  }
  .hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #fff; padding: 32px 24px 28px; text-align: center;
  }
  .hero h1 { font-size: 22px; font-weight: 700; letter-spacing: 1px; }
  .hero p { font-size: 13px; color: #a8b2d1; margin-top: 6px; }
  .date-badge {
    display: inline-block; background: rgba(255,255,255,0.12); padding: 4px 14px;
    border-radius: 20px; font-size: 12px; margin-top: 10px;
  }
  .stats { display: flex; gap: 12px; padding: 20px 24px; background: #fff; }
  .stat-card {
    flex: 1; text-align: center; padding: 14px 8px; border-radius: 10px;
    background: #f8f9fa;
  }
  .stat-card.highlight { background: linear-gradient(135deg, #fff3e0, #ffe0b2); }
  .stat-num { font-size: 28px; font-weight: 800; color: #302b63; }
  .stat-card.highlight .stat-num { color: #ff6b35; }
  .stat-label { font-size: 12px; color: #888; margin-top: 4px; }

  .content { padding: 16px 24px 32px; }
  .day-block {
    background: #fff; border-radius: 12px; margin-bottom: 16px; overflow: hidden;
    border-left: 4px solid #e0e0e0; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  .day-block.new {
    border-left: 4px solid #ff6b35;
    box-shadow: 0 2px 8px rgba(255,107,53,0.15);
  }
  .day-title {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 20px; font-weight: 700; font-size: 15px;
    background: #f5f5f5; color: #555;
  }
  .day-block.new .day-title {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2); color: #ff6b35;
  }
  .badge-new {
    font-size: 11px; padding: 2px 10px; border-radius: 12px;
    background: #ff6b35; color: #fff; font-weight: 600;
  }
  .day-content { padding: 16px 20px; }
  .section-label {
    font-size: 14px; font-weight: 700; padding: 10px 0 6px;
    margin-top: 4px; border-bottom: 1px solid #eee;
  }
  .section-label.stocks { color: #2563eb; }
  .section-label.thesis { color: #ea580c; }
  .section-label.events { color: #16a34a; }
  .section-label.supply { color: #7c3aed; }
  .section-label.risk { color: #dc2626; }

  .ticker-tag {
    display: inline-block; padding: 2px 10px; border-radius: 4px;
    margin: 3px 4px 3px 0; font-size: 13px; font-weight: 600;
    font-family: "SF Mono", "Menlo", monospace;
  }
  .ticker-tag.bullish { background: #dcfce7; color: #15803d; }
  .ticker-tag.bearish { background: #fee2e2; color: #dc2626; }
  .ticker-tag.neutral { background: #f1f5f9; color: #64748b; }

  .insight {
    background: #fafafa; border-radius: 8px; padding: 12px 14px;
    margin: 8px 0; font-size: 14px; line-height: 1.8;
  }
  .day-block.new .insight { background: #fff8f2; }
  .key-point {
    display: inline-block; background: #302b63; color: #fff;
    padding: 1px 8px; border-radius: 3px; font-size: 12px;
    font-weight: 600; margin-right: 6px;
  }

  .tweet-ref {
    background: #fefefe; border-left: 3px solid #ddd;
    padding: 10px 14px; margin: 6px 0; border-radius: 0 6px 6px 0;
    font-size: 13px; color: #666;
  }
  .day-block.new .tweet-ref { border-left-color: #ffcc80; background: #fffdf7; }
  .tweet-time { font-weight: 600; color: #888; margin-bottom: 3px; }

  .footer {
    text-align: center; padding: 24px; font-size: 11px; color: #aaa;
    border-top: 1px solid #eee; margin-top: 16px;
  }
</style>
"""


def build_ticker_tags(stocks: list[dict]) -> str:
    """Build ticker tag HTML from stocks list."""
    if not stocks:
        return '<p style="color:#999;font-size:13px;">今日无新增股票观点</p>'
    tags = []
    for s in stocks:
        tags.append(f'<span class="ticker-tag {s["stance"]}">{s["ticker"]}</span>')
    return " ".join(tags)


def build_stock_analysis(stocks: list[dict]) -> str:
    """Build stock analysis insights HTML."""
    if not stocks:
        return ""
    html_parts = []
    for s in stocks:
        principles_str = "、".join([f"原则#{i}" for i in _principle_numbers(s.get("principles", []))])
        html_parts.append(f"""<div class="insight">
      <span class="key-point">{s["ticker"]} — {principles_str}</span> {s["analysis"]}
    </div>""")
    return "\n".join(html_parts)


def build_insights(items: list[dict], label_class: str) -> str:
    """Build insight divs for thesis_changes, key_events, supply_chain, risk_alerts."""
    if not items:
        return f'<div style="color:#999;font-size:14px;padding:8px 0;">今日该分类暂无新增内容</div>'
    html_parts = []
    for item in items:
        if label_class == "risk":
            html_parts.append(f'<div class="insight">⚠️ <strong>{item["title"]}</strong> — {item["description"]}</div>')
        else:
            prefix = "📌" if label_class == "events" else ("🔗" if label_class == "supply" else "")
            principles_str = ""
            if item.get("principles"):
                principles_str = "（" + "、".join([f"原则#{i}" for i in _principle_numbers(item["principles"])]) + "）"
            html_parts.append(f"""<div class="insight">
      <span class="key-point">{item["title"]}</span> {principles_str} {item["description"]}
    </div>""")
    return "\n".join(html_parts)


def build_reference_tweets(refs: list[dict]) -> str:
    """Build reference tweet HTML."""
    if not refs:
        return ""
    html_parts = []
    for r in refs:
        html_parts.append(f"""<div class="tweet-ref">
      <div class="tweet-time">🕐 {r.get("time", "")}</div>
      <div>{r.get("summary", "")}</div>
    </div>""")
    return "\n".join(html_parts)


def _principle_numbers(names: list[str]) -> list[int]:
    """Map principle names to numbers."""
    mapping = {
        "BottleneckHunting": 1, "MultiHopBOM": 2, "SmallCapAsymmetry": 3,
        "InstitutionalLag": 4, "TAMExpansion": 5, "GeopoliticalSupplyChain": 6,
        "PowerCooling": 7, "CounterpartyFunding": 8, "ShortSqueeze": 9,
        "EarningsQualification": 10, "MediaValidation": 11, "BayesianUpdating": 12,
        "瓶颈狩猎": 1, "多跳BOM映射": 2, "小盘不对称": 3,
        "机构滞后": 4, "TAM扩张": 5, "地缘供应链": 6,
        "电力冷却": 7, "融资质量": 8, "逼空": 9,
        "资格认证": 10, "媒体验证": 11, "贝叶斯更新": 12,
    }
    nums = []
    for n in names:
        num = mapping.get(n, 0)
        if num > 0:
            nums.append(num)
    return nums if nums else [0]


def build_day_block(date_str: str, analysis: dict, is_new: bool = True) -> str:
    """Build a single day-block HTML."""
    new_class = " new" if is_new else ""
    badge = '\n    <span class="badge-new">NEW</span>' if is_new else ""

    stocks_html = build_ticker_tags(analysis.get("stocks", []))
    stock_analysis_html = build_stock_analysis(analysis.get("stocks", []))

    return f"""<div class="day-block{new_class}">
  <div class="day-title">
    <span>📅 {date_str}</span>{badge}
  </div>
  <div class="day-content">
    <div class="section-label stocks">📈 股票观点</div>
    <p style="margin:8px 0;">{stocks_html}</p>
    {stock_analysis_html}

    <div class="section-label thesis">🔄 论点变化</div>
    {build_insights(analysis.get("thesis_changes", []), "thesis")}

    <div class="section-label events">📋 关键事件</div>
    {build_insights(analysis.get("key_events", []), "events")}

    <div class="section-label supply">🔗 供应链洞察</div>
    {build_insights(analysis.get("supply_chain", []), "supply")}

    <div class="section-label risk">⚠️ 风险提示</div>
    {build_insights(analysis.get("risk_alerts", []), "risk")}

    <div class="section-label" style="color:#888;">💬 参考推文</div>
    {build_reference_tweets(analysis.get("reference_tweets", []))}
  </div>
</div>"""
    return html


def update_report(existing_html: str, date_str: str, analysis: dict,
                  total_days: int, total_tweets: int, today_count: int,
                  total_stocks: int) -> str:
    """
    Update the cumulative HTML report.
    - Inserts today's day-block (with 'new' class) at the top
    - Removes 'new' class and badge from previous days
    - Updates stats in hero section
    """
    import re

    # If existing is empty or placeholder, build from scratch
    if not existing_html or "<div class=\"hero\">" not in existing_html:
        return _build_full_report(date_str, analysis, total_days, total_tweets, today_count, total_stocks)

    # Remove 'new' class from all existing day-blocks
    html = existing_html
    html = html.replace('class="day-block new"', 'class="day-block"')
    # Remove badge-new from existing day-blocks
    html = re.sub(r'<span class="badge-new">[^<]*</span>', '', html)
    # Remove day-title gradient from existing blocks (restore to default)
    html = re.sub(
        r'(<div class="day-title">\s*<span>📅 [^<]*</span>)\s*</div>',
        r'\1</div>',
        html
    )

    # Fix: restore day-title background for old blocks
    # Find all day-block (non-new) and ensure their day-title has default background
    def fix_old_day_titles(m):
        block = m.group(0)
        # Replace any orange gradient background with default
        block = block.replace(
            'background: linear-gradient(135deg, #fff3e0, #ffe0b2); color: #ff6b35;',
            'background: #f5f5f5; color: #555;'
        )
        return block

    html = re.sub(
        r'<div class="day-block"[^>]*>.*?</div>\s*</div>\s*</div>',
        fix_old_day_titles,
        html,
        flags=re.DOTALL
    )

    # Update stats
    html = re.sub(
        r'<div class="stat-num">\d+</div>\s*<div class="stat-label">累计分析推文</div>',
        f'<div class="stat-num">{total_tweets}</div>\n    <div class="stat-label">累计分析推文</div>',
        html
    )
    html = re.sub(
        r'<div class="stat-card highlight">\s*<div class="stat-num">\d+</div>\s*<div class="stat-label">.*?今日新增</div>',
        f'<div class="stat-card highlight">\n    <div class="stat-num">{today_count}</div>\n    <div class="stat-label">🆕 今日新增</div>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<div class="stat-num">\d+</div>\s*<div class="stat-label">涉及股票</div>',
        f'<div class="stat-num">{total_stocks}</div>\n    <div class="stat-label">涉及股票</div>',
        html
    )

    # Update date badge
    html = re.sub(
        r'<div class="date-badge">📅 [^<]*</div>',
        f'<div class="date-badge">📅 更新于 {date_str}</div>',
        html
    )

    # Insert new day-block after the stats section (before first day-block or content div)
    new_block = build_day_block(date_str, analysis, is_new=True)
    # Find insertion point: right after </div>\n</div>\n\n<div class="content">
    insertion_marker = '<div class="content">'
    if insertion_marker in html:
        html = html.replace(insertion_marker, insertion_marker + "\n" + new_block + "\n")
    else:
        # Fallback: insert before footer
        html = html.replace('<div class="footer">', new_block + '\n<div class="footer">')

    return html


def _build_full_report(date_str: str, analysis: dict,
                       total_days: int, total_tweets: int, today_count: int,
                       total_stocks: int) -> str:
    """Build complete HTML report from scratch."""
    day_block = build_day_block(date_str, analysis, is_new=True)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Serenity 每日分析</title>
{CSS}
</head>
<body>
<div class="hero">
  <h1>🔬 Serenity 每日分析</h1>
  <p>@aleabitoreddit · AI/半导体供应链深度分析 · 云端自动化</p>
  <div class="date-badge">📅 更新于 {date_str}</div>
</div>
<div class="stats">
  <div class="stat-card">
    <div class="stat-num">{total_tweets}</div>
    <div class="stat-label">累计分析推文</div>
  </div>
  <div class="stat-card highlight">
    <div class="stat-num">{today_count}</div>
    <div class="stat-label">🆕 今日新增</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{total_stocks}</div>
    <div class="stat-label">涉及股票</div>
  </div>
</div>
<div class="content">
{day_block}
</div>
<div class="footer">
  🔬 Serenity Daily Analysis · 每日 19:00 自动推送<br>
  Powered by GitHub Actions + DeepSeek AI · RSS.app
</div>
</body>
</html>"""


if __name__ == "__main__":
    # Test
    test_analysis = {
        "summary": "Test analysis",
        "stocks": [],
        "thesis_changes": [],
        "key_events": [],
        "supply_chain": [],
        "risk_alerts": [],
        "reference_tweets": [],
    }
    html = _build_full_report("2026-05-31", test_analysis, 1, 8, 8, 15)
    print(html[:500])
