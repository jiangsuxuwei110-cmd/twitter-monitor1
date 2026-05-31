"""
Serenity Daily - HTML Report Builder (Cloud Version)
Builds and updates the cumulative HTML report.
Today's new entries are highlighted with orange (#ff6b35) styling.
Half-year statistical summary is dynamically generated from accumulated data.
New content is highlighted in red (#dc2626) for easy visual identification.
"""

# --- CSS Styling ---
CSS = """
<style>
  * { margin:0; padding:0; box-sizing: border-box; }
  body {
    font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f0f2f5; color: #2c3e50; line-height: 1.7;
    max-width: 680px; margin:0 auto; padding: 0;
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
    flex:1; text-align: center; padding: 14px 8px; border-radius: 10px;
    background: #f8f9fa;
  }
  .stat-card.highlight { background: linear-gradient(135deg, #fff3e0, #ffe0b2); }
  .stat-num { font-size: 28px; font-weight: 800; color: #302b63; }
  .stat-card.highlight .stat-num { color: #ff6b35; }
  .stat-label { font-size: 12px; color: #888; margin-top: 4px; }

  /* --- Today's Key Insights (RED highlight block) --- */
  .today-insights {
    background: #fef2f2; border-left: 4px solid #dc2626;
    border-radius: 0 8px 8px 0; padding: 16px 18px; margin: 16px 24px;
  }
  .today-insights h3 { color: #dc2626; font-size: 14px; margin-bottom: 8px; }
  .today-insights ul { margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.9; color: #2c3e50; }
  .today-insights li { margin-bottom: 4px; }
  .today-insights .hl { color: #dc2626; font-weight: 600; }

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

  .day-summary {
    background: #f0f4ff; border-radius: 8px; padding: 14px 16px;
    margin-bottom: 16px; font-size: 14px; line-height: 1.9;
    border-left: 3px solid #302b63;
  }
  .day-block.new .day-summary { background: #fff8f2; border-left-color: #ff6b35; }
  .summary-label { font-weight: 700; color: #302b63; font-size: 13px; display: block; margin-bottom: 4px; }

  .market-ctx {
    background: #f5f0ff; border-radius: 6px; padding: 8px 12px;
    margin: 4px 0 14px; font-size: 13px; color: #5b21b6;
  }
  .day-block.new .market-ctx { background: #fff5f0; color: #c2410c; }

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
  .conviction-stars { font-size: 11px; letter-spacing: 1px; }

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
  /* NEW: red font for new content inside insight blocks */
  .insight .new-text { color: #dc2626; font-weight: 600; }

  .tweet-ref {
    background: #fefefe; border-left: 3px solid #ddd;
    padding: 10px 14px; margin: 6px 0; border-radius: 0 6px 6px 0;
    font-size: 13px; color: #666;
  }
  .day-block.new .tweet-ref { border-left-color: #ffcc80; background: #fffdf7; }
  .tweet-time { font-weight: 600; color: #888; margin-bottom: 3px; }

  /* --- Half-Year Summary Section (DYNAMIC) --- */
  .half-year-section {
    background: #fff; border-radius: 12px; margin: 20px 0; overflow: hidden;
    border-left: 4px solid #7c3aed; box-shadow: 0 2px 8px rgba(124,58,237,0.10);
  }
  .half-year-header {
    background: linear-gradient(135deg, #2e1065, #4c1d95, #5b21b6);
    color: #fff; padding: 18px 20px; font-weight: 700; font-size: 16px;
  }
  .half-year-body { padding: 18px 20px; }
  .half-year-body .section-label { color: #7c3aed; }

  .hy-table {
    width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px;
  }
  .hy-table th {
    background: #f5f3ff; padding: 8px 10px; text-align: left;
    font-weight: 600; color: #4c1d95; border-bottom: 2px solid #ddd;
  }
  .hy-table td { padding: 7px 10px; border-bottom: 1px solid #eee; }
  .hy-table tr:nth-child(even) td { background: #fafafa; }
  .hy-table tr.new-change td { background: #fef9c3 !important; }
  .hy-table tr.conviction-up td { background: #dcfce7 !important; }
  .hy-table tr.conviction-down td { background: #fee2e2 !important; }

  .hy-metric-row {
    display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0;
  }
  .hy-metric {
    flex:1; min-width: 140px; background: #f5f3ff; border-radius: 8px;
    padding: 10px 12px; text-align: center;
  }
  .hy-metric .hy-num { font-size: 22px; font-weight: 800; color: #4c1d95; }
  .hy-metric .hy-label { font-size: 11px; color: #7c3aed; margin-top: 2px; }

  .hy-tag {
    display: inline-block; padding: 1px 8px; border-radius: 3px;
    font-size: 11px; font-weight: 600; margin: 1px 3px 1px 0;
  }
  .hy-tag.green { background: #dcfce7; color: #15803d; }
  .hy-tag.red { background: #fee2e2; color: #dc2626; }
  .hy-tag.purple { background: #f3e8ff; color: #7c3aed; }
  .hy-tag.new-badge { background: #fef08a; border: 1px solid #f59e0b; color: #92400e; font-weight: 700; }

  .hy-chain {
    background: #fafafa; border-radius: 8px; padding: 12px 14px;
    margin: 8px 0; font-size: 13px; line-height: 1.9;
  }
  .hy-arrow { color: #7c3aed; font-weight: 700; margin: 0 4px; }

  .hy-warn {
    background: #fffbeb; border-left: 3px solid #f59e0b;
    padding: 10px 14px; margin: 10px 0; border-radius: 0 6px 6px 0;
    font-size: 12px; color: #92400e;
  }
  .hy-new-flash {
    display: inline-block; background: #fef08a; color: #92400e;
    padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 700;
    margin-left: 6px; animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%,100% { opacity:1; } 50% { opacity:0.5; }
  }

  .footer {
    text-align: center; padding: 24px; font-size: 11px; color: #aaa;
    border-top: 1px solid #eee; margin-top: 16px;
  }
</style>
"""


# PushPlus 2万字限制：关键文本块的长度上限
TODAY_INSIGHTS_CHARS = 200    # 「今日关键洞察」中每条总结的最大字数
STOCK_ANALYSIS_CHARS = 150    # 每只股票分析在洞察区块中的最大字数
INSIGHT_DESC_CHARS = 120      # 论点/事件描述的最大字数


DAY_SUMMARY_CHARS = 300       # day-block 概要的最长字数


def _truncate_text(text: str, max_len: int) -> str:
    """截断文本到 max_len 字符以内，超出部分用 ... 表示。"""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3].rstrip() + "..."


def build_ticker_tags(stocks: list[dict], changes: dict = None) -> str:
    """Build ticker tag HTML from stocks list, with conviction stars.
    If `changes` is provided, highlight conviction changes."""
    if not stocks:
        return '<p style="color:#999;font-size:13px;">今日无新增股票观点</p>'
    tags = []
    changed_tickers = set()
    if changes:
        for cc in changes.get("conviction_changes", []):
            changed_tickers.add(cc["ticker"])
    for s in stocks:
        conv = s.get("conviction", 3)
        stars = "⭐" * min(conv, 5)
        is_changed = s.get("ticker", "").upper() in changed_tickers
        flash = ' <span class="hy-new-flash">CHG</span>' if is_changed else ""
        tags.append(
            f'<span class="ticker-tag {s["stance"]}">{s["ticker"]}'
            f' <span class="conviction-stars">{stars}</span>{flash}</span>'
        )
    return " ".join(tags)


def build_stock_analysis(stocks: list[dict], changes: dict = None) -> str:
    """Build stock analysis insights HTML with detailed analysis.
    New stocks are marked with red font."""
    if not stocks:
        return ""
    new_tickers = set()
    if changes:
        new_tickers = set(changes.get("new_stocks", []))
        for cc in changes.get("conviction_changes", []):
            new_tickers.add(cc["ticker"])

    html_parts = []
    for s in stocks:
        ticker = s.get("ticker", "")
        principles_str = "、".join([f"原则#{i}" for i in _principle_numbers(s.get("principles", []))])
        conv = s.get("conviction", 3)
        stars = "⭐" * min(conv, 5)
        is_new = ticker.upper() in new_tickers
        red_open = '<span class="new-text">' if is_new else ""
        red_close = '</span>' if is_new else ""
        html_parts.append(f"""<div class="insight">
      <span class="key-point">{red_open}{ticker} {stars} — {principles_str}{red_close}</span> {_truncate_text(s["analysis"], STOCK_ANALYSIS_CHARS)}
    </div>""")
    return "\n".join(html_parts)


def build_insights(items: list[dict], label_class: str, new_titles: set = None) -> str:
    """Build insight divs for thesis_changes, key_events, supply_chain, risk_alerts.
    If `new_titles` is provided, highlight new items with red font."""
    if not items:
        return f'<div style="color:#999;font-size:14px;padding:8px 0;">今日该分类暂无新增内容</div>'
    if new_titles is None:
        new_titles = set()
    html_parts = []
    for item in items:
        title = item.get("title", "")
        is_new = title in new_titles or item.get("is_new", False)
        if label_class == "risk":
            red = '<span class="new-text">' if is_new else ""
            red_end = '</span>' if is_new else ""
            html_parts.append(f'<div class="insight">⚠️ <strong>{red}{title}{red_end}</strong> — {_truncate_text(item["description"], INSIGHT_DESC_CHARS)}</div>')
        else:
            prefix = "📌" if label_class == "events" else ("🔗" if label_class == "supply" else "")
            principles_str = ""
            if item.get("principles"):
                principles_str = "（" + "、".join([f"原则#{i}" for i in _principle_numbers(item["principles"])]) + "）"
            red = '<span class="new-text">' if is_new else ""
            red_end = '</span>' if is_new else ""
            html_parts.append(f"""<div class="insight">
      <span class="key-point">{prefix} {red}{title}{red_end}</span> {principles_str} {_truncate_text(item["description"], INSIGHT_DESC_CHARS)}
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
    return sorted(nums) if nums else [0]


def build_today_insights_block(analysis: dict, changes: dict) -> str:
    """Build the red '今日关键洞察' block placed at the top of the report."""
    summary = analysis.get("summary", "")
    stocks = analysis.get("stocks", [])
    new_stocks = changes.get("new_stocks", []) if changes else []
    new_thesis = changes.get("new_thesis", []) if changes else []
    new_events = changes.get("new_events", []) if changes else []
    conviction_changes = changes.get("conviction_changes", []) if changes else []

    bullets = []

    # Bullet 1: Summary (truncated for PushPlus limit)
    if summary:
        bullets.append(f'<li><span class="hl">今日概要：</span>{_truncate_text(summary, TODAY_INSIGHTS_CHARS)}</li>')

    # Bullet 2: New stocks
    for s in stocks:
        t = s.get("ticker", "")
        if t.upper() in [x.upper() for x in new_stocks]:
            stance_cn = {"bullish": "看多", "bearish": "看空", "neutral": "中性"}.get(s.get("stance", ""), "")
            stars = "⭐" * min(s.get("conviction", 3), 5)
            bullets.append(f'<li><span class="hl">新增关注：{t} {stars} {stance_cn}</span> — {_truncate_text(s.get("analysis", ""), STOCK_ANALYSIS_CHARS)}</li>')

    # Bullet 3: Conviction changes
    for cc in conviction_changes:
        direction_arrow = "🔼" if cc.get("direction") == "up" else ("🔽" if cc.get("direction") == "down" else "➡️")
        bullets.append(f'<li><span class="hl">信念变化：{cc["ticker"]} {direction_arrow} {cc.get("old","?")}→{cc.get("new","?")}⭐</span></li>')

    # Bullet 4: New thesis
    for t in new_thesis[:3]:
        bullets.append(f'<li><span class="hl">新论点：</span>{t}</li>')

    # Bullet 5: New events
    for e in new_events[:3]:
        bullets.append(f'<li><span class="hl">新事件：</span>{e}</li>')

    if not bullets:
        return ""

    bullets_html = "\n".join(bullets)
    return f"""<div class="today-insights">
  <h3>🔴 今日关键洞察</h3>
  <ul>
{bullets_html}
  </ul>
</div>"""


def build_day_block(date_str: str, analysis: dict, is_new: bool = True, changes: dict = None) -> str:
    """Build a single day-block HTML with detailed summary and market context.
    New content within the block is marked with red font via CSS class 'new-text'."""
    new_class = " new" if is_new else ""
    badge = '\n    <span class="badge-new">NEW</span>' if is_new else ""

    stocks_html = build_ticker_tags(analysis.get("stocks", []), changes)
    stock_analysis_html = build_stock_analysis(analysis.get("stocks", []), changes)

    # Summary + Market Context
    summary = analysis.get("summary", "")
    market_ctx = analysis.get("market_context", "")

    summary_block = ""
    if summary:
        summary_block = f"""<div class="day-summary">
      <span class="summary-label">📝 今日概要</span>
      {_truncate_text(summary, DAY_SUMMARY_CHARS)}
    </div>"""

    market_block = ""
    if market_ctx:
        market_block = f"""<div class="market-ctx">🌐 {market_ctx}</div>"""

    # For insights, determine which items are "new" for highlighting
    new_thesis_titles = set()
    new_event_titles = set()
    new_supply_titles = set()
    if changes:
        new_thesis_titles = set(changes.get("new_thesis", []))
        new_event_titles = set(changes.get("new_events", []))
        new_supply_titles = set(changes.get("new_supply_chain", []))

    return f"""<div class="day-block{new_class}">
  <div class="day-title">
    <span>📅 {date_str}</span>{badge}
  </div>
  <div class="day-content">
    {summary_block}
    {market_block}

    <div class="section-label stocks">📈 股票观点</div>
    <p style="margin:8px 0;">{stocks_html}</p>
    {stock_analysis_html}

    <div class="section-label thesis">🔄 论点变化</div>
    {build_insights(analysis.get("thesis_changes", []), "thesis", new_thesis_titles)}

    <div class="section-label events">📋 关键事件</div>
    {build_insights(analysis.get("key_events", []), "events", new_event_titles)}

    <div class="section-label supply">🔗 供应链洞察</div>
    {build_insights(analysis.get("supply_chain", []), "supply", new_supply_titles)}

    <div class="section-label risk">⚠️ 风险提示</div>
    {build_insights(analysis.get("risk_alerts", []), "risk")}

    <div class="section-label" style="color:#888;">💬 参考推文</div>
    {build_reference_tweets(analysis.get("reference_tweets", []))}
  </div>
</div>"""


def build_half_year_section(accu_summary: dict, changes: dict) -> str:
    """
    Dynamically build the half-year summary section from accumulated data.
    Highlights new/changing items with flash badges.
    """
    meta = accu_summary.get("meta", {})
    top_stocks = accu_summary.get("top_stocks", [])
    perf = accu_summary.get("performance", {})
    recent_thesis = accu_summary.get("recent_thesis", [])
    recent_events = accu_summary.get("recent_events", [])
    all_stocks = accu_summary.get("all_stocks", {})

    first_date = meta.get("first_date", "N/A")
    last_date = meta.get("last_date", "N/A")
    total_runs = meta.get("total_runs", 0)
    total_tweets = meta.get("total_tweets", 0)
    total_stocks_count = meta.get("total_stocks", 0)

    # Build date range display
    date_range = f"{first_date} — {last_date}" if first_date != "N/A" else "数据收集中"

    # New items for highlighting
    new_stock_set = set(changes.get("new_stocks", []))
    conviction_changes = changes.get("conviction_changes", [])
    changed_stock_set = set(cc["ticker"] for cc in conviction_changes)
    new_thesis_set = set(changes.get("new_thesis", []))
    new_event_set = set(changes.get("new_events", []))

    # --- Top conviction stocks table ---
    top_stocks_rows = ""
    for i, s in enumerate(top_stocks):
        ticker = s["ticker"]
        is_new = ticker in new_stock_set
        is_changed = ticker in changed_stock_set
        row_class = ""
        if is_changed:
            direction = next((cc["direction"] for cc in conviction_changes if cc["ticker"] == ticker), "")
            row_class = "conviction-up" if direction == "up" else ("conviction-down" if direction == "down" else "new-change")
        elif is_new:
            row_class = "new-change"
        stance_cn = {"bullish": "看多", "bearish": "看空", "neutral": "中性"}.get(s.get("stance", "neutral"), "?")
        stars = "⭐" * min(s.get("conviction", 3), 5)
        new_badge = ' <span class="hy-new-flash">NEW</span>' if is_new else ""
        change_badge = ""
        if is_changed:
            direction = next((cc["direction"] for cc in conviction_changes if cc["ticker"] == ticker), "")
            old_s = next((cc["old"] for cc in conviction_changes if cc["ticker"] == ticker), "")
            new_s = next((cc["new"] for cc in conviction_changes if cc["ticker"] == ticker), "")
            change_badge = f' <span class="hy-new-flash">{old_s}→{new_s}⭐</span>'
        top_stocks_rows += f"""<tr class="{row_class}">
      <td><strong>{ticker}</strong>{new_badge}{change_badge}</td>
      <td>{stars} {stance_cn}</td>
      <td>{s.get("first_seen", "")}</td>
      <td>{s.get("last_seen", "")}</td>
    </tr>"""

    if not top_stocks_rows:
        top_stocks_rows = '<tr><td colspan="4" style="color:#999;text-align:center;">数据收集中，暂无足够累积数据</td></tr>'

    # --- Recent thesis changes ---
    thesis_html = ""
    for t in recent_thesis[:8]:
        title = t.get("title", "")
        is_new = title in new_thesis_set
        new_badge = ' <span class="hy-new-flash">NEW</span>' if is_new else ""
        principles_str = ""
        if t.get("principles"):
            principles_str = "「" + "、".join([f"原则#{i}" for i in _principle_numbers(t["principles"])]) + "」"
        thesis_html += f'<div class="insight"><span class="key-point">🔄 {title}</span>{new_badge} {principles_str} {_truncate_text(t.get("description", ""), INSIGHT_DESC_CHARS)}</div>\n'

    if not thesis_html:
        thesis_html = '<div style="color:#999;font-size:13px;">暂无论点变化记录</div>'

    # --- Recent key events ---
    events_html = ""
    for e in recent_events[:8]:
        title = e.get("title", "")
        is_new = title in new_event_set
        new_badge = ' <span class="hy-new-flash">NEW</span>' if is_new else ""
        principles_str = ""
        if e.get("principles"):
            principles_str = "「" + "、".join([f"原则#{i}" for i in _principle_numbers(e["principles"])]) + "」"
        events_html += f'<div class="insight"><span class="key-point">📋 {title}</span>{new_badge} {principles_str} {_truncate_text(e.get("description", ""), INSIGHT_DESC_CHARS)}</div>\n'

    if not events_html:
        events_html = '<div style="color:#999;font-size:13px;">暂无关键事件记录</div>'

    # --- Performance metrics ---
    perf_html = f"""<div class="hy-metric-row">
      <div class="hy-metric"><div class="hy-num">{perf.get("directional_accuracy", 0)}%</div><div class="hy-label">定向准确率（{perf.get("directional_total", 0)}次样本）</div></div>
      <div class="hy-metric"><div class="hy-num">{perf.get("strict_accuracy", 0)}%</div><div class="hy-label">严格命中率（±10%）</div></div>
      <div class="hy-metric"><div class="hy-num">{perf.get("cpo_rate", 0)}%</div><div class="hy-label">CPO/光子学验证率</div></div>
    </div>"""

    return f"""<div class="half-year-section">
  <div class="half-year-header">📊 累积统计分析（{date_range}）</div>
  <div class="half-year-body">

    <div class="section-label">📈 核心数据快照</div>
    <div class="hy-metric-row">
      <div class="hy-metric"><div class="hy-num">{total_runs}</div><div class="hy-label">分析天数</div></div>
      <div class="hy-metric"><div class="hy-num">{total_tweets}</div><div class="hy-label">累计推文</div></div>
      <div class="hy-metric"><div class="hy-num">{total_stocks_count}</div><div class="hy-label">覆盖股票</div></div>
    </div>

    <div class="section-label">⭐ 核心持仓追踪（按信念层级排序）</div>
    <table class="hy-table">
      <tr><th>标的</th><th>信念层级</th><th>首次出现</th><th>最近提及</th></tr>
      {top_stocks_rows}
    </table>
    <div style="font-size:11px;color:#888;margin:4px 0 12px;">🟡 高亮行 = 今日新增或信念变化 | 绿色 = 信念上调 | 红色 = 信念下调</div>

    <div class="section-label">🔄 近期论点变化</div>
    {thesis_html}

    <div class="section-label">📋 近期关键事件</div>
    {events_html}

    <div class="section-label">🏆 战绩追踪</div>
    {perf_html}
    <div style="font-size:11px;color:#888;margin:4px 0 12px;">注：战绩数据随AI分析自动累积，准确率由Serenity自我报告，仅供参考</div>

    <div class="hy-warn">
      ⚠️ <strong>重要风险提示：</strong>所有回报数为自我报告未经独立审计；策略集中小盘/微盘股单日波动可达20%+；存在幸存者偏差；本报告仅供参考不构成投资建议。
    </div>

  </div>
</div>"""


def update_report(existing_html: str, date_str: str, analysis: dict,
                  accu_summary: dict, changes: dict) -> str:
    """
    Update the cumulative HTML report.
    - Inserts today's day-block (with 'new' class) at the top
    - Removes 'new' class and badge from previous days
    - Updates stats in hero section
    - Rebuilds the half-year summary section dynamically
    - Inserts today's key insights block (red highlight) at the top
    """
    import re

    # If existing is empty or placeholder, build from scratch
    if not existing_html or '<div class="hero">' not in existing_html:
        return _build_full_report(date_str, analysis, accu_summary, changes)

    # Remove 'new' class from all existing day-blocks
    html = existing_html
    html = html.replace('class="day-block new"', 'class="day-block"')
    # Remove badge-new from existing day-blocks
    html = re.sub(r'<span class="badge-new">[^<]*</span>\s*', '', html)
    # Restore old day-title backgrounds
    html = re.sub(
        r'(<div class="day-title"[^>]*?)background:\s*linear-gradient\(135deg,\s*#fff3e0,\s*#ffe0b2\);\s*color:\s*#ff6b35;',
        r'\1background: #f5f5f5; color: #555;',
        html
    )

    # Update stats (we need to compute today's tweet count)
    today_count = len(analysis.get("stocks", []))  # proxy; actual count comes from main.py
    # These are passed via accu_summary meta
    total_tweets = accu_summary.get("meta", {}).get("total_tweets", 0)
    total_stocks = accu_summary.get("meta", {}).get("total_stocks", 0)

    html = re.sub(
        r'<div class="stat-num">\d+</div>\s*<div class="stat-label">累计分析推文</div>',
        f'<div class="stat-num">{total_tweets}</div>\n    <div class="stat-label">累计分析推文</div>',
        html
    )
    html = re.sub(
        r'<div class="stat-card highlight">\s*<div class="stat-num">\d+</div>\s*<div class="stat-label">.*?今日新增</div>',
        f'<div class="stat-card highlight">\n    <div class="stat-num">{len(analysis.get("reference_tweets", []))}</div>\n    <div class="stat-label">🆕 今日新增</div>',
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

    # --- Replace or insert half-year section ---
    half_year_html = build_half_year_section(accu_summary, changes)
    if 'half-year-section' in html:
        # Replace existing section
        html = re.sub(
            r'<div class="half-year-section">.*?</div>\s*</div>\s*</div>',
            half_year_html,
            html,
            flags=re.DOTALL
        )
    else:
        # Insert before footer
        html = html.replace('<div class="footer">', half_year_html + '\n<div class="footer">')

    # --- Insert or replace today-insights block ---
    today_insights_html = build_today_insights_block(analysis, changes)
    if 'today-insights' in html:
        # Replace existing block
        html = re.sub(
            r'<div class="today-insights">.*?</div>\s*</div>',
            today_insights_html,
            html,
            flags=re.DOTALL
        )
    else:
        # Insert after stats block (before content)
        html = html.replace('<div class="content">', today_insights_html + '\n<div class="content">')

    # Insert new day-block after the content div opening
    new_block = build_day_block(date_str, analysis, is_new=True, changes=changes)
    # Remove existing new_block insertion if present
    insertion_marker = '<div class="content">'
    if insertion_marker in html:
        # Find where the first day-block is and replace it
        # Actually, just insert after content div (today-insights already handled above)
        pass  # day-block insertion handled below in _build_full_report path

    # For update_report: insert new day-block at top of content (after today-insights)
    # We need to find the right insertion point: after today-insights, before existing day-blocks
    if today_insights_html:
        # Insert after today-insights block
        html = html.replace(
            '</div>\n<div class="day-block"',
            '</div>\n' + new_block + '\n<div class="day-block"',
            1  # only first occurrence
        )
    else:
        # Fallback: insert before first day-block
        html = html.replace('<div class="day-block"', new_block + '\n<div class="day-block"', 1)

    return html


def _build_full_report(date_str: str, analysis: dict, accu_summary: dict, changes: dict = None) -> str:
    """Build complete HTML report from scratch, with dynamic half-year summary.
    Includes today's key insights block at the top (red highlight)."""
    if changes is None:
        changes = {}
    day_block = build_day_block(date_str, analysis, is_new=True, changes=changes)
    half_year_html = build_half_year_section(accu_summary, changes)
    today_insights_html = build_today_insights_block(analysis, changes)

    # Stats from accu_summary
    meta = accu_summary.get("meta", {})

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
    <div class="stat-num">{meta.get("total_tweets", 0)}</div>
    <div class="stat-label">累计分析推文</div>
  </div>
  <div class="stat-card highlight">
    <div class="stat-num">{len(analysis.get("reference_tweets", []))}</div>
    <div class="stat-label">🆕 今日新增</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{meta.get("total_stocks", 0)}</div>
    <div class="stat-label">涉及股票</div>
  </div>
</div>
{today_insights_html}
<div class="content">
{day_block}
</div>
{half_year_html}
<div class="footer">
  🔬 Serenity Daily Analysis · 每日 19:00 自动推送<br>
  Powered by GitHub Actions + DeepSeek AI · RSS.app<br>
  免责声明：本报告仅供参考分析，不构成任何投资建议
</div>
</body>
</html>"""


if __name__ == "__main__":
    # Test with mock data
    test_analysis = {
        "summary": "今日Serenity聚焦光子学供应链最新进展，$SIVE获得新的设计赢单确认，$AXTI铟价继续创新高。整体AI半导体板块维持强势，CPO路线图加速推进。",
        "market_context": "纳斯达克指数反弹1.2%，半导体ETF（SMH）上涨2.1%，AI板块资金持续流入。市场关注本周即将发布的NVDA财报。",
        "stocks": [
            {
                "ticker": "$SIVE",
                "stance": "bullish",
                "conviction": 5,
                "analysis": "Sivers Semiconductors确认新增一家hyperscaler CPO设计赢单，Win Semi量产代工进展顺利。Serenity维持$10B MC目标，认为CPO CW激光器需求远超供应能力。当前$1.4B MC对应巨大上涨空间，CHIPS Act资金进一步降低执行风险。",
                "principles": ["BottleneckHunting", "MultiHopBOM", "SmallCapAsymmetry"]
            },
            {
                "ticker": "$AXTI",
                "stance": "bullish",
                "conviction": 4,
                "analysis": "SMM 7N铟非标现货价继续创ATH，验证InP衬底需求持续超预期。AXTI作为西方唯一InP衬底供应商，定价权持续增强。但$5B+ MC限制上涨空间，Serenity明确不做空但不再推荐新入场。",
                "principles": ["BottleneckHunting", "GeopoliticalSupplyChain", "MediaValidation"]
            }
        ],
        "thesis_changes": [],
        "key_events": [
            {
                "title": "$SIVE确认新hyperscaler CPO设计赢单",
                "description": "Sivers在季度更新中确认新增一家未具名hyperscaler的CPO激光器设计赢单，进一步验证了CW DFB激光器作为CPO瓶颈的论点。Serenity将其视为Tier 2验证（公开可验证但需推理链），进一步增强了$10B MC目标的信心。",
                "principles": ["BottleneckHunting", "MediaValidation"]
            }
        ],
        "supply_chain": [],
        "risk_alerts": [],
        "reference_tweets": [
            {"time": "10:30", "summary": "$SIVE季度更新确认新hyperscaler CPO设计赢单，Win Semi量产进展顺利，CW激光器需求远超供应"},
            {"time": "14:15", "summary": "SMM 7N铟价继续ATH，$AXTI的InP衬底定价权持续增强，但$5B+ MC不再推荐新入场"},
        ]
    }
    test_accu = {
        "meta": {"first_date": "2025-12-01", "last_date": "2026-05-31", "total_runs": 42, "total_tweets": 5640, "total_stocks": 52},
        "top_stocks": [
            {"ticker": "$AXTI", "conviction": 5, "stance": "bullish", "first_seen": "2025-12-15", "last_seen": "2026-05-31"},
            {"ticker": "$SIVE", "conviction": 5, "stance": "bullish", "first_seen": "2026-01-10", "last_seen": "2026-05-31"},
            {"ticker": "$AAOI", "conviction": 4, "stance": "bullish", "first_seen": "2026-02-01", "last_seen": "2026-05-28"},
        ],
        "performance": {"directional_accuracy": 61.2, "directional_total": 49, "strict_accuracy": 40.8, "cpo_rate": 80.0},
        "recent_thesis": [],
        "recent_events": [],
        "all_stocks": {}
    }
    test_changes = {
        "new_stocks": ["$SIVE"],
        "conviction_changes": [],
        "new_thesis": [],
        "new_events": [],
    }
    html = _build_full_report("2026-05-31", test_analysis, test_accu, test_changes)
    print(html[:500])
    print("\n...\n")
    assert 'half-year-section' in html, "Half-year section missing!"
    assert 'today-insights' in html, "Today insights block missing!"
    assert 'new-text' in html, "New content red highlight missing!"
    print("[All tests passed]")
    print(f"Total HTML size: {len(html)} chars")
