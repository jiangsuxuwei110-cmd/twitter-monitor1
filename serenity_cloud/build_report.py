"""
Serenity Daily - HTML Report Builder (Cloud Version)
Builds and updates the cumulative HTML report.
Today's new entries are highlighted with orange (#ff6b35) styling.
Includes half-year statistical summary section.
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

  .tweet-ref {
    background: #fefefe; border-left: 3px solid #ddd;
    padding: 10px 14px; margin: 6px 0; border-radius: 0 6px 6px 0;
    font-size: 13px; color: #666;
  }
  .day-block.new .tweet-ref { border-left-color: #ffcc80; background: #fffdf7; }
  .tweet-time { font-weight: 600; color: #888; margin-bottom: 3px; }

  /* --- Half-Year Summary Section --- */
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

  .hy-metric-row {
    display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0;
  }
  .hy-metric {
    flex: 1; min-width: 140px; background: #f5f3ff; border-radius: 8px;
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

  .footer {
    text-align: center; padding: 24px; font-size: 11px; color: #aaa;
    border-top: 1px solid #eee; margin-top: 16px;
  }
</style>
"""


# --- Half-Year Statistical Summary (static data from comprehensive analysis) ---
HALF_YEAR_SUMMARY = """
<div class="half-year-section">
  <div class="half-year-header">📊 近半年统计汇总（2025.12 — 2026.05）</div>
  <div class="half-year-body">

    <div class="section-label">📈 核心数据</div>
    <div class="hy-metric-row">
      <div class="hy-metric"><div class="hy-num">5,640</div><div class="hy-label">分析推文总数</div></div>
      <div class="hy-metric"><div class="hy-num">50+</div><div class="hy-label">覆盖股票标的</div></div>
      <div class="hy-metric"><div class="hy-num">~61%</div><div class="hy-label">30日定向准确率</div></div>
      <div class="hy-metric"><div class="hy-num">4,502%</div><div class="hy-label">自报最高YTD</div></div>
    </div>

    <div class="section-label">⭐ 最高信念持仓（⭐⭐⭐⭐⭐）</div>
    <table class="hy-table">
      <tr><th>标的</th><th>入场</th><th>涨幅</th><th>核心论点</th></tr>
      <tr><td><strong>$AXTI</strong></td><td>$12-15 / $700M MC</td><td><span class="hy-tag green">+1,057%</span></td><td>InP衬底双瓶颈垄断：上游铟/镓精炼 + 衬底制造，中国出口管制使AXTI成为西方光子学事实垄断者</td></tr>
      <tr><td><strong>$SIVE</strong></td><td>$140M MC</td><td><span class="hy-tag green">+600%</span></td><td>全球仅少数独立CW DFB激光供应商，确认供应Jabil/MRVL/Ayar/AMD CPO链路，Win Semi量产消除执行风险</td></tr>
    </table>

    <div class="section-label">🔥 高信念持仓（⭐⭐⭐⭐）</div>
    <table class="hy-table">
      <tr><th>标的</th><th>涨幅</th><th>论点</th></tr>
      <tr><td><strong>$AAOI</strong></td><td><span class="hy-tag green">+200%</span></td><td>唯一美国垂直整合光学收发器供应商，3家hyperscaler买断产出</td></tr>
      <tr><td><strong>$SOI</strong></td><td><span class="hy-tag green">+200-250%</span></td><td>CPO级SOI晶圆绝对垄断，Morgan Stanley持有6.5%</td></tr>
      <tr><td><strong>$NBIS</strong></td><td>持续积累</td><td>5合1 AI云，NVDA $2B战略投资，2026底$7-9B ARR目标</td></tr>
      <tr><td><strong>$SNDK</strong></td><td><span class="hy-tag green">+109%</span></td><td>NAND重新定价远超分析师预期，Q3收入+252% Y/Y</td></tr>
    </table>

    <div class="section-label">🔗 核心供应链全景</div>
    <div class="hy-chain">
      Hyperscaler资本开支 <span class="hy-arrow">→</span> ASIC/TPU设计 <span class="hy-arrow">→</span> 光学收发器 <span class="hy-arrow">→</span> InP外延片 <span class="hy-arrow">→</span> <strong>InP衬底 ← 核心瓶颈</strong> <span class="hy-arrow">→</span> InP原料(7N铟)
    </div>

    <div class="section-label">🏆 战绩追踪</div>
    <table class="hy-table">
      <tr><th>指标</th><th>数值</th><th>说明</th></tr>
      <tr><td>30日定向准确率</td><td>~61%（30/49）</td><td>方向判断是否正确</td></tr>
      <tr><td>严格30日±10%命中率</td><td>~41%（20/49）</td><td>是否达到有意义幅度</td></tr>
      <tr><td>60日+20%有利收盘</td><td>~54%（29/54）</td><td>更长时间窗口</td></tr>
      <tr><td>光子学/CPO验证率</td><td>~75-85%</td><td>最强论文集群</td></tr>
    </table>

    <div class="section-label">🎯 五大核心主题</div>
    <div class="insight">
      <span class="key-point">1. 光子学/CPO供应链</span> 定义性主题——构建了从hyperscaler→激光器→衬底→原料的完整BOM链条，Gen 1-4代际框架
    </div>
    <div class="insight">
      <span class="key-point">2. 内存超级周期</span> AI推理将内存从周期商品转变为产能约束产品，$SNDK前向P/E仅6.3x（2027）
    </div>
    <div class="insight">
      <span class="key-point">3. 电力/电网瓶颈</span> 数据中心用电190→980 TWh（+415%），PJM容量定价$28.92→$329.17/MW-day
    </div>
    <div class="insight">
      <span class="key-point">4. 国防/国家安全</span> OSINT驱动的国防供应链识别，$LPTH Chalcogenide玻璃替代锗
    </div>
    <div class="insight">
      <span class="key-point">5. Neocloud融资质量光谱</span> 原创框架：NVDA战略投资>纯Colo>高息债务>大额ATM稀释
    </div>

    <div class="section-label">❌ 明确看空/失败案例</div>
    <table class="hy-table">
      <tr><th>标的</th><th>问题</th></tr>
      <tr><td><strong>$IREN</strong></td><td>$6B ATM稀释≈51%股权，「数据中心的AMC」，已验证-34%</td></tr>
      <tr><td><strong>$POET</strong></td><td>$MRVL取消合作，单一客户风险暴露</td></tr>
      <tr><td><strong>$CRWV</strong></td><td>每年$1.5B+债务利息</td></tr>
    </table>

    <div class="hy-warn">
      ⚠️ <strong>重要风险提示：</strong>所有回报数为自我报告未经独立审计；策略集中小盘/微盘股单日波动可达20%+；存在幸存者偏差；本报告仅供参考不构成投资建议。
    </div>

  </div>
</div>
"""


def build_ticker_tags(stocks: list[dict]) -> str:
    """Build ticker tag HTML from stocks list, with conviction stars."""
    if not stocks:
        return '<p style="color:#999;font-size:13px;">今日无新增股票观点</p>'
    tags = []
    for s in stocks:
        conv = s.get("conviction", 3)
        stars = "⭐" * min(conv, 5)
        tags.append(
            f'<span class="ticker-tag {s["stance"]}">{s["ticker"]}'
            f' <span class="conviction-stars">{stars}</span></span>'
        )
    return " ".join(tags)


def build_stock_analysis(stocks: list[dict]) -> str:
    """Build stock analysis insights HTML with detailed analysis."""
    if not stocks:
        return ""
    html_parts = []
    for s in stocks:
        principles_str = "、".join([f"原则#{i}" for i in _principle_numbers(s.get("principles", []))])
        conv = s.get("conviction", 3)
        stars = "⭐" * min(conv, 5)
        html_parts.append(f"""<div class="insight">
      <span class="key-point">{s["ticker"]} {stars} — {principles_str}</span> {s["analysis"]}
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
      <span class="key-point">{prefix} {item["title"]}</span> {principles_str} {item["description"]}
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
    """Build a single day-block HTML with detailed summary and market context."""
    new_class = " new" if is_new else ""
    badge = '\n    <span class="badge-new">NEW</span>' if is_new else ""

    stocks_html = build_ticker_tags(analysis.get("stocks", []))
    stock_analysis_html = build_stock_analysis(analysis.get("stocks", []))

    # Summary + Market Context
    summary = analysis.get("summary", "")
    market_ctx = analysis.get("market_context", "")

    summary_block = ""
    if summary:
        summary_block = f"""<div class="day-summary">
      <span class="summary-label">📝 今日概要</span>
      {summary}
    </div>"""

    market_block = ""
    if market_ctx:
        market_block = f"""<div class="market-ctx">🌐 {market_ctx}</div>"""

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


def update_report(existing_html: str, date_str: str, analysis: dict,
                  total_days: int, total_tweets: int, today_count: int,
                  total_stocks: int) -> str:
    """
    Update the cumulative HTML report.
    - Inserts today's day-block (with 'new' class) at the top
    - Removes 'new' class and badge from previous days
    - Updates stats in hero section
    - Ensures half-year summary section is present
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
    # Restore old day-title backgrounds (new blocks have gradient, old should be default)
    html = re.sub(
        r'(<div class="day-title"[^>]*?)background:\s*linear-gradient\(135deg,\s*#fff3e0,\s*#ffe0b2\);\s*color:\s*#ff6b35;',
        r'\1background: #f5f5f5; color: #555;',
        html
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

    # Ensure half-year summary section exists (add it before footer if missing)
    if 'half-year-section' not in html:
        html = html.replace('<div class="footer">', HALF_YEAR_SUMMARY + '\n<div class="footer">')

    # Insert new day-block after the stats section
    new_block = build_day_block(date_str, analysis, is_new=True)
    insertion_marker = '<div class="content">'
    if insertion_marker in html:
        html = html.replace(insertion_marker, insertion_marker + "\n" + new_block + "\n")
    else:
        # Fallback: insert before half-year section or footer
        if 'half-year-section' in html:
            html = html.replace('<div class="half-year-section">', new_block + '\n<div class="half-year-section">')
        else:
            html = html.replace('<div class="footer">', new_block + '\n<div class="footer">')

    return html


def _build_full_report(date_str: str, analysis: dict,
                       total_days: int, total_tweets: int, today_count: int,
                       total_stocks: int) -> str:
    """Build complete HTML report from scratch, including half-year summary."""
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
{HALF_YEAR_SUMMARY}
<div class="footer">
  🔬 Serenity Daily Analysis · 每日 19:00 自动推送<br>
  Powered by GitHub Actions + DeepSeek AI · RSS.app<br>
  免责声明：本报告仅供参考分析，不构成任何投资建议
</div>
</body>
</html>"""


if __name__ == "__main__":
    # Test
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
    html = _build_full_report("2026-05-31", test_analysis, 1, 8, 8, 15)
    print(html[:500])
    # Also verify half-year section is present
    assert 'half-year-section' in html, "Half-year section missing!"
    print("\n\n[Half-year section present: OK]")
    print(f"Total HTML size: {len(html)} chars")
