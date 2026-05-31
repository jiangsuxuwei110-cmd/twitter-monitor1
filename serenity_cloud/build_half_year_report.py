"""
Serenity - Half-Year Comprehensive Analysis Report Builder
Reads serenity_accumulated.json (maintained by Task 2) and generates
a comprehensive report organized by stock/theme instead of by day.
Newly merged content today is marked with red font.
"""

import json
import os
from datetime import datetime, timezone, timedelta

# --- Config ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ACCUM_FILE = os.path.join(DATA_DIR, "serenity_accumulated.json")
REPORT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "serenity_half_year.html")

BEIJING_TZ = timezone(timedelta(hours=8))

# Text truncation limits (for PushPlus 20000 char limit)
STOCK_ANALYSIS_CHARS = 200
THESIS_DESC_CHARS = 150
EVENT_DESC_CHARS = 150
INSIGHT_DESC_CHARS = 150


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3].rstrip() + "..."


# ─── CSS ───────────────────────────────────────────────────────────────
def _build_css() -> str:
    return """<style>
  body { font-family: -apple-system, 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 0; color: #2c3e50; }
  .hero { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
         color: #fff; padding: 28px 24px; text-align: center; }
  .hero h1 { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 1px; }
  .hero .subtitle { margin-top: 6px; font-size: 13px; opacity: 0.8; }
  .hero .date-badge { display: inline-block; background: rgba(255,255,255,0.15); padding: 4px 14px;
           border-radius: 20px; font-size: 12px; margin-top: 10px; }
  .container { max-width: 680px; margin: 0 auto; padding: 0 0 40px 0; }
  .today-insights { background: #fef2f2; border-left: 4px solid #dc2626;
                 border-radius: 0 8px 8px 0; padding: 16px 18px; margin: 16px 24px; }
  .today-insights h3 { color: #dc2626; font-size: 14px; margin: 0 0 8px 0; }
  .today-insights ul { margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.9; color: #2c3e50; }
  .today-insights li { margin-bottom: 4px; }
  .today-insights .highlight { color: #dc2626; font-weight: 600; }
  .section { background: #fff; border-radius: 10px; margin: 16px 24px; padding: 20px;
              box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .section h2 { margin: 0 0 14px 0; font-size: 16px; font-weight: 700;
                 border-bottom: 2px solid #f0f0f0; padding-bottom: 8px; }
  .stock-card { border: 1px solid #e8e8e8; border-radius: 8px; padding: 14px 16px;
                margin-bottom: 12px; }
  .stock-card:last-child { margin-bottom: 0; }
  .stock-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
  .stock-ticker { font-size: 16px; font-weight: 700; color: #1a1a2e; }
  .stock-stars { color: #f59e0b; font-size: 14px; }
  .stock-stance { font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
  .stance-bullish { background: #dcfce7; color: #16a34a; }
  .stance-bearish { background: #fee2e2; color: #dc2626; }
  .stance-neutral { background: #f3f4f6; color: #6b7280; }
  .conviction-bar { display: flex; gap: 3px; margin: 8px 0; }
  .conviction-dot { width: 18px; height: 8px; border-radius: 2px; background: #e5e7eb; }
  .conviction-dot.active { background: #3b82f6; }
  .conviction-dot.active-high { background: #dc2626; }
  .analysis-text { font-size: 13px; line-height: 1.7; color: #374151; margin-top: 6px; }
  .new-content { color: #dc2626; font-weight: 600; }
  .new-badge-red { display: inline-block; background: #fef2f2; color: #dc2626;
                    padding: 1px 8px; border-radius: 3px; font-size: 11px; font-weight: 700;
                    margin-left: 4px; border: 1px solid #fca5a5; }
  .timeline { border-left: 3px solid #e5e7eb; padding-left: 14px; margin: 10px 0; }
  .timeline-item { margin-bottom: 10px; position: relative; }
  .timeline-item::before { content: ''; position: absolute; left: -18px; top: 5px;
                          width: 8px; height: 8px; border-radius: 50%; background: #3b82f6; }
  .timeline-date { font-size: 11px; color: #9ca3af; font-weight: 600; }
  .timeline-text { font-size: 13px; line-height: 1.6; color: #374151; }
  .theme-tag { display: inline-block; background: #eff6ff; color: #2563eb; padding: 2px 10px;
                border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 4px; }
  .risk-card { background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px;
                padding: 12px 14px; margin-bottom: 8px; }
  .risk-card:last-child { margin-bottom: 0; }
  .risk-title { font-size: 13px; font-weight: 700; color: #dc2626; }
  .risk-desc { font-size: 12px; color: #6b7280; margin-top: 4px; line-height: 1.6; }
  .perf-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .perf-item { background: #f9fafb; border-radius: 8px; padding: 12px; text-align: center; }
  .perf-value { font-size: 24px; font-weight: 800; }
  .perf-label { font-size: 11px; color: #9ca3af; margin-top: 2px; }
  .footer { text-align: center; font-size: 11px; color: #9ca3af; padding: 20px; }
  .text-red { color: #dc2626; }
  .text-green { color: #16a34a; }
  .text-gray { color: #6b7280; }
</style>"""


# ─── Helpers ────────────────────────────────────────────────────────────

def _load_accumulated() -> dict:
    if os.path.exists(ACCUM_FILE):
        with open(ACCUM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _stars(n: int) -> str:
    return "★" * max(0, min(n, 5)) + "☆" * max(0, 5 - max(0, min(n, 5)))


def _stance_class(s: str) -> str:
    return {"bullish": "stance-bullish", "bearish": "stance-bearish"}.get(s, "stance-neutral")


def _build_conviction_bar(history: list) -> str:
    recent = history[-10:] if history else []
    bars = []
    for h in recent:
        c = h.get("conviction", 0)
        cls = "active-high" if c >= 4 else ("active" if c >= 2 else "")
        bars.append(f'<div class="conviction-dot {cls}"></div>')
    return f'<div class="conviction-bar">{"".join(bars)}</div>'


# ─── Section Builders ──────────────────────────────────────────────────

def _build_today_insights(accum: dict, today_str: str) -> str:
    """Reuse today's key insights from daily_summaries."""
    summaries = accum.get("daily_summaries", [])
    today_summary = None
    for s in summaries:
        if s.get("date") == today_str:
            today_summary = s
            break
    if not today_summary:
        # Fallback: use the latest summary
        today_summary = summaries[-1] if summaries else None
    if not today_summary:
        return ""

    summary_text = today_summary.get("summary", "")
    market_ctx = today_summary.get("market_context", "")

    bullets = []
    if summary_text:
        bullets.append(f'<li><span class="highlight">今日概要：</span>{_truncate(summary_text, 200)}</li>')
    if market_ctx:
        bullets.append(f'<li><span class="highlight">市场环境：</span>{_truncate(market_ctx, 150)}</li>')

    if not bullets:
        return ""

    return f"""<div class="today-insights">
  <h3>🔴 今日关键洞察</h3>
  <ul>{"".join(bullets)}</ul>
</div>"""


def _build_core_conclusions(accum: dict, today_str: str, is_first_run: bool) -> str:
    """Core conclusions: all stocks sorted by conviction, with new markers."""
    stocks = accum.get("stocks", {})
    if not stocks:
        return '<div class="section"><h2>📊 核心结论</h2><p class="text-gray">尚未积累股票数据，请等待每日分析运行。</p></div>'

    # Sort by max_conviction desc, then last_seen desc
    sorted_stocks = sorted(
        stocks.items(),
        key=lambda x: (-x[1].get("max_conviction", 0), -int(x[1].get("last_seen", "2000-01-01").replace("-", "")))
    )

    cards = []
    for ticker, info in sorted_stocks:
        is_new_today = info.get("first_seen") == today_str
        new_badge = f'<span class="new-badge-red">NEW 今日新增</span>' if is_new_today else ""

        stance = info.get("conviction_history", [{}])[-1].get("stance", "neutral")
        last_c = info.get("conviction_history", [{}])[-1].get("conviction", 3)
        max_c = info.get("max_conviction", last_c)
        stars_str = _stars(max_c)
        stance_cls = _stance_class(stance)

        # Latest analysis snippet
        analyses = info.get("analyses", [])
        latest_analysis = _truncate(analyses[-1], STOCK_ANALYSIS_CHARS) if analyses else "暂无分析"

        new_class = ' class="new-content"' if is_new_today else ""
        bar = _build_conviction_bar(info.get("conviction_history", []))

        cards.append(f"""
      <div class="stock-card">
        <div class="stock-header">
          <span class="stock-ticker"{new_class}>{ticker}</span>
          <span class="stock-stars">{stars_str}</span>
          <span class="stock-stance {stance_cls}">{stance}</span>
          {new_badge}
        </div>
        {bar}
        <div class="analysis-text"{new_class if is_new_today else ""}>{latest_analysis}</div>
      </div>""")

    return f"""<div class="section">
  <h2>📊 核心结论</h2>
  {"".join(cards)}
</div>"""


def _build_conviction_timeline(accum: dict, today_str: str) -> str:
    """Conviction change timeline for each stock."""
    stocks = accum.get("stocks", {})
    if not stocks:
        return ""

    # Only include stocks with conviction changes
    items = []
    for ticker, info in stocks.items():
        history = info.get("conviction_history", [])
        if len(history) < 2:
            continue
        # Build timeline for this stock
        timeline_items = []
        for h in history:
            d = h.get("date", "")
            c = h.get("conviction", 0)
            s = h.get("stance", "")
            is_today = d == today_str
            new_class = ' class="new-content"' if is_today else ""
            timeline_items.append(f"""
          <div class="timeline-item">
            <div class="timeline-date"{new_class if is_today else ""}>{d}</div>
            <div class="timeline-text">信念等级 <strong>{c}/5</strong> — {s} {_stars(c)}</div>
          </div>""")
        if timeline_items:
            items.append(f"""
        <div class="stock-card">
          <div class="stock-header">
            <span class="stock-ticker">{ticker}</span>
            <span class="stock-stars">{_stars(info.get("max_conviction", 3))}</span>
          </div>
          <div class="timeline">{"".join(timeline_items)}</div>
        </div>""")

    if not items:
        return '<div class="section"><h2>📈 持仓变化曲线</h2><p class="text-gray">每只股票需要至少 2 次分析记录才能显示变化曲线。</p></div>'

    return f"""<div class="section">
  <h2>📈 持仓变化曲线</h2>
  {"".join(items)}
</div>"""


def _build_thesis_timeline(accum: dict, today_str: str) -> str:
    """Thesis changes timeline, newest first."""
    theses = accum.get("thesis_changes", [])
    if not theses:
        return '<div class="section"><h2>🔄 论点演进时间线</h2><p class="text-gray">尚未记录论点变化。</p></div>'

    # Sort newest first
    sorted_t = sorted(theses, key=lambda x: x.get("date", ""), reverse=True)
    items = []
    for t in sorted_t[:20]:  # Show last 20 thesis changes
        d = t.get("date", "")
        title = t.get("title", "")
        desc = t.get("description", "")
        principles = t.get("principles", [])
        is_new = t.get("is_new", False) or d == today_str
        new_badge = f'<span class="new-badge-red">NEW</span>' if is_new else ""
        new_class = ' class="new-content"' if is_new else ""
        princ_str = " ".join(f'<span class="theme-tag">{p}</span>' for p in principles[:4])

        items.append(f"""
        <div class="stock-card">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span class="timeline-date">{d}</span>
            {new_badge}
          </div>
          <div style="font-size:13px;font-weight:600;color:#1a1a2e;{new_class if is_new else ""}">{title}</div>
          <div style="font-size:12px;color:#6b7280;margin-top:4px;line-height:1.6;">{_truncate(desc, THESIS_DESC_CHARS)}</div>
          <div style="margin-top:6px;">{princ_str}</div>
        </div>""")

    return f"""<div class="section">
  <h2>🔄 论点演进时间线</h2>
  {"".join(items)}
</div>"""


def _build_supply_chain_insights(accum: dict, today_str: str) -> str:
    """Supply chain insights aggregated by theme."""
    sc_list = accum.get("supply_chain", [])
    if not sc_list:
        return '<div class="section"><h2>🏭 供应链洞察</h2><p class="text-gray">尚未记录供应链洞察。</p></div>'

    # Aggregate by theme (principles)
    theme_map = {}  # theme → list of insights
    for sc in sc_list:
        principles = sc.get("principles", ["其他"])
        for p in principles:
            theme_map.setdefault(p, []).append(sc)

    sections = []
    for theme, items in theme_map.items():
        cards = []
        for sc in items[:5]:  # Top 5 per theme
            d = sc.get("date", "")
            title = sc.get("title", "")
            desc = sc.get("description", "")
            is_new = sc.get("is_new", False) or d == today_str
            new_badge = f'<span class="new-badge-red">NEW</span>' if is_new else ""
            new_class = ' class="new-content"' if is_new else ""
            cards.append(f"""
          <div style="padding:8px 0;border-bottom:1px solid #f0f0f0;">
            <span style="font-size:11px;color:#9ca3af;">{d}</span> {new_badge}
            <div style="font-size:13px;font-weight:600;{new_class if is_new else ""}">{title}</div>
            <div style="font-size:12px;color:#6b7280;margin-top:2px;">{_truncate(desc, INSIGHT_DESC_CHARS)}</div>
          </div>""")
        sections.append(f"""
      <div class="stock-card">
        <div style="font-size:14px;font-weight:700;color:#1a1a2e;margin-bottom:8px;">
          <span class="theme-tag">{theme}</span>
        </div>
        {"".join(cards)}
      </div>""")

    return f"""<div class="section">
  <h2>🏭 供应链洞察</h2>
  {"".join(sections)}
</div>"""


def _build_risk_section(accum: dict, today_str: str) -> str:
    """Risk alerts section."""
    risks = accum.get("risk_alerts", [])
    if not risks:
        return '<div class="section"><h2>⚠️ 风险提示</h2><p class="text-gray">当前无活跃风险预警。</p></div>'

    sorted_risks = sorted(risks, key=lambda x: x.get("date", ""), reverse=True)
    cards = []
    for r in sorted_risks[:10]:
        d = r.get("date", "")
        title = r.get("title", "")
        desc = r.get("description", "")
        is_new = r.get("is_new", False) or d == today_str
        new_badge = f'<span class="new-badge-red">NEW</span>' if is_new else ""
        new_class = ' class="new-content"' if is_new else ""
        cards.append(f"""
      <div class="risk-card">
        <div style="display:flex;align-items:center;gap:8px;">
          <span class="risk-title"{new_class if is_new else ""}>{title}</span>
          {new_badge}
        </div>
        <div class="risk-desc">{_truncate(desc, EVENT_DESC_CHARS)}</div>
        <div style="font-size:11px;color:#9ca3af;margin-top:4px;">{d}</div>
      </div>""")

    return f"""<div class="section">
  <h2>⚠️ 风险提示</h2>
  {"".join(cards)}
</div>"""


def _build_performance_section(accum: dict) -> str:
    """Performance stats section."""
    perf = accum.get("performance", {})
    meta = accum.get("meta", {})
    total_runs = meta.get("total_runs", 0)
    directional_hits = perf.get("directional_hits", 0)
    directional_total = perf.get("directional_total", 0)
    strict_hits = perf.get("strict_hits", 0)
    strict_total = perf.get("strict_total", 0)
    cpo_verified = perf.get("cpo_verified", 0)
    cpo_total = perf.get("cpo_total", 0)

    da = round(directional_hits / directional_total * 100, 1) if directional_total > 0 else 0
    sa = round(strict_hits / strict_total * 100, 1) if strict_total > 0 else 0
    cr = round(cpo_verified / cpo_total * 100, 1) if cpo_total > 0 else 0

    return f"""<div class="section">
  <h2>📊 Serenity 战绩统计</h2>
  <div class="perf-grid">
    <div class="perf-item">
      <div class="perf-value {'text-green' if da >= 60 else 'text-red'}">{da}%</div>
      <div class="perf-label">方向准确率 ({directional_hits}/{directional_total})</div>
    </div>
    <div class="perf-item">
      <div class="perf-value {'text-green' if sa >= 60 else 'text-red'}">{sa}%</div>
      <div class="perf-label">严格准确率 ({strict_hits}/{strict_total})</div>
    </div>
    <div class="perf-item">
      <div class="perf-value {'text-green' if cr >= 75 else 'text-red'}">{cr}%</div>
      <div class="perf-label">CPO 验证率 ({cpo_verified}/{cpo_total})</div>
    </div>
    <div class="perf-item">
      <div class="perf-value">{total_runs}</div>
      <div class="perf-label">累计分析天数</div>
    </div>
  </div>
</div>"""


# ─── Main ────────────────────────────────────────────────────────────────

def build_half_year_report(today_str: str = None) -> str:
    """Build the full half-year comprehensive report."""
    if today_str is None:
        today_str = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")

    accum = _load_accumulated()
    if not accum:
        return f"""<html><head><meta charset="utf-8"><title>Serenity 综合分析</title>{_build_css()}</head>
<body><div class="hero"><h1>Serenity 半年综合分析</h1><div class="subtitle">数据文件不存在或为空</div></div>
<div class="container"><div class="section"><p>请先运行 Task 2（每日分析），累积数据后此报告将自动生成。</p></div></div></body></html>"""

    meta = accum.get("meta", {})
    is_first_run = meta.get("total_runs", 0) <= 1

    # Hero
    first_date = meta.get("first_date", today_str)
    last_date = meta.get("last_date", today_str)
    total_stocks = len(accum.get("stocks", {}))

    hero = f"""<div class="hero">
  <h1>🔮 Serenity 半年综合分析</h1>
  <div class="subtitle">覆盖 {first_date} ~ {last_date} · {total_stocks} 支股票 · Serenity 12 原则框架</div>
  <div class="date-badge">📅 更新于 {today_str}</div>
</div>"""

    # Sections
    today_insights = _build_today_insights(accum, today_str)
    conclusions = _build_core_conclusions(accum, today_str, is_first_run)
    perf = _build_performance_section(accum)
    timeline = _build_conviction_timeline(accum, today_str)
    thesis = _build_thesis_timeline(accum, today_str)
    supply = _build_supply_chain_insights(accum, today_str)
    risks = _build_risk_section(accum, today_str)

    footer = f'<div class="footer">Serenity 综合分析 · 自动生成于 {today_str} · <a href="https://github.com">GitHub Actions</a></div>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🔮 Serenity 综合分析 {today_str}</title>
  {_build_css()}
</head>
<body>
  {hero}
  <div class="container">
    {today_insights}
    {conclusions}
    {perf}
    {timeline}
    {thesis}
    {supply}
    {risks}
  </div>
  {footer}
</body>
</html>"""

    return html


def save_half_year_report(html: str):
    """Save the half-year report to file."""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)


def load_half_year_report() -> str:
    """Load existing half-year report, or return empty string."""
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""


if __name__ == "__main__":
    print("Building half-year comprehensive report...")
    html = build_half_year_report()
    save_half_year_report(html)
    print(f"Report saved to {REPORT_FILE} ({len(html)} chars)")
