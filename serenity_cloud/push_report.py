"""
Serenity Daily - PushPlus Pusher (Cloud Version)
Pushes the HTML report via PushPlus API.
Auto-truncates content if exceeding PushPlus 20k character limit.
"""
import json
import re
import urllib.request

PUSHPLUS_URL = "https://www.pushplus.plus/send"
PUSHPLUS_MAX_CHARS = 19000  # Leave 1000 char margin for JSON overhead


# Minimal CSS fallback when full CSS is too large
MINIMAL_CSS = (
    '<style>body{max-width:680px;margin:0 auto;font-family:-apple-system,"PingFang SC",sans-serif;'
    'font-size:14px;line-height:1.7;padding:8px;color:#2c3e50;background:#f0f2f5}'
    '.day-block{background:#fff;border-radius:12px;margin-bottom:16px;padding:16px;'
    'border-left:4px solid #e0e0e0;box-shadow:0 1px 3px rgba(0,0,0,.06)}'
    '.day-block.new{border-left-color:#ff6b35;box-shadow:0 2px 8px rgba(255,107,53,.15)}'
    '.badge-new{background:#ff6b35;color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600}'
    '.ticker-tag{display:inline-block;padding:2px 10px;border-radius:4px;margin:3px 4px;font-size:13px;font-weight:600}'
    '.ticker-tag.bullish{background:#dcfce7;color:#15803d}'
    '.ticker-tag.bearish{background:#fee2e2;color:#dc2626}'
    '.ticker-tag.neutral{background:#f1f5f9;color:#64748b}'
    '.insight{background:#fafafa;border-radius:8px;padding:12px;margin:8px 0;font-size:14px;line-height:1.8}'
    '.tweet-ref{border-left:3px solid #ddd;padding:8px 12px;margin:6px 0;font-size:13px;color:#666}'
    '.hy-new-flash{background:#fef08a;color:#92400e;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700}'
    '.section-label{font-size:14px;font-weight:700;padding:10px 0 6px;border-bottom:1px solid #eee;margin-top:4px}'
    '.hero{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:#fff;padding:24px;text-align:center}'
    '.footer{text-align:center;padding:16px;font-size:11px;color:#aaa}'
    '.stats{display:flex;gap:8px;padding:12px;background:#fff;flex-wrap:wrap}'
    '.stat-card{flex:1;min-width:80px;text-align:center;padding:10px;border-radius:8px;background:#f8f9fa}'
    '.stat-card.highlight{background:linear-gradient(135deg,#fff3e0,#ffe0b2)}'
    '.stat-num{font-size:22px;font-weight:800;color:#302b63}'
    '.stat-card.highlight .stat-num{color:#ff6b35}'
    '.stat-label{font-size:11px;color:#888}'
    '.day-title{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;'
    'font-weight:700;font-size:15px;background:#f5f5f5;color:#555}'
    '.day-block.new .day-title{background:linear-gradient(135deg,#fff3e0,#ffe0b2);color:#ff6b35}'
    '.day-summary{background:#f0f4ff;border-radius:8px;padding:12px;margin-bottom:12px;'
    'font-size:14px;border-left:3px solid #302b63}'
    '.day-block.new .day-summary{background:#fff8f2;border-left-color:#ff6b35}'
    '.market-ctx{background:#f5f0ff;border-radius:6px;padding:6px 10px;margin:4px 0 12px;font-size:13px}'
    '.key-point{display:inline-block;background:#302b63;color:#fff;padding:1px 8px;border-radius:3px;font-size:12px;font-weight:600}'
    '.conviction-stars{font-size:11px;letter-spacing:1px}'
    '.date-badge{display:inline-block;background:rgba(255,255,255,.12);padding:4px 14px;border-radius:20px;font-size:12px}'
    '.hy-table{width:100%;border-collapse:collapse;margin:8px 0;font-size:13px}'
    '.hy-table th{background:#f5f3ff;padding:6px 8px;text-align:left;font-weight:600;border-bottom:2px solid #ddd}'
    '.hy-table td{padding:5px 8px;border-bottom:1px solid #eee}'
    '.hy-tag{display:inline-block;padding:1px 8px;border-radius:3px;font-size:11px;font-weight:600}'
    '.hy-tag.green{background:#dcfce7;color:#15803d}'
    '.hy-tag.red{background:#fee2e2;color:#dc2626}'
    '.hy-tag.purple{background:#f3e8ff;color:#7c3aed}'
    '.hy-tag.new-badge{background:#fef08a;border:1px solid #f59e0b;color:#92400e;font-weight:700}'
    '.hy-warn{background:#fffbeb;border-left:3px solid #f59e0b;padding:8px 12px;margin:8px 0;font-size:12px;color:#92400e}'
    'table.hy-table tr.new-change td{background:#fef9c3!important}'
    'table.hy-table tr.conviction-up td{background:#dcfce7!important}'
    'table.hy-table tr.conviction-down td{background:#fee2e2!important}'
    '</style>'
)


def _truncate_html(html_content: str, max_chars: int = PUSHPLUS_MAX_CHARS) -> str:
    """Truncate HTML content to fit PushPlus limit, preserving readability."""
    content = html_content
    original_len = len(content)

    if original_len <= max_chars:
        return content

    print(f"  [push] Content too large: {original_len} chars > {max_chars} limit")

    # Step 1: Strip excess whitespace (but keep structure readable)
    content = re.sub(r'\n\s*\n', '\n', content)
    content = re.sub(r'  +', ' ', content)

    if len(content) <= max_chars:
        print(f"  [push] After whitespace trim: {len(content)} chars (OK)")
        return content

    # Step 2: Remove half-year summary section (largest static block)
    if 'half-year-section' in content:
        content = re.sub(
            r'<div class="half-year-section">.*?</div>\s*(?=<div class="footer">)',
            '',
            content,
            flags=re.DOTALL
        )
        # Insert truncation notice before footer
        note = (
            '<div style="background:#fef3c7;border-left:3px solid #f59e0b;'
            'padding:8px 12px;margin:12px 0;font-size:12px;color:#92400e;">'
            '📊 <b>累积统计已截断</b>（PushPlus 2万字限制），完整报告见 GitHub 仓库</div>'
        )
        content = content.replace('<div class="footer">', note + '\n<div class="footer">')
        print(f"  [push] Removed half-year section: {len(content)} chars")

    if len(content) <= max_chars:
        return content

    # Step 3: Replace full CSS with minimal version
    content = re.sub(r'<style>.*?</style>', MINIMAL_CSS, content, flags=re.DOTALL)
    print(f"  [push] Replaced with minimal CSS: {len(content)} chars")

    if len(content) <= max_chars:
        return content

    # Step 4: Last resort - truncate content body
    # Find last complete day-block and cut after it
    cutoff_marker = '</div>\n</div>\n</div>'
    last_pos = content.rfind(cutoff_marker)
    if last_pos > 0:
        content = content[:last_pos + len(cutoff_marker)]
        content += (
            '\n<div style="text-align:center;padding:16px;color:#999;font-size:12px;">'
            '... [内容过长已截断]</div>'
            '\n<div class="footer">'
        )
        content += '🔬 Serenity Daily · 内容过长已截断<br>完整报告见 GitHub 仓库</div>'
        print(f"  [push] Hard truncation: {len(content)} chars")

    return content


def push_report(html_content: str, title: str, token: str) -> dict:
    """Push HTML report to PushPlus. Auto-truncates if over character limit.
    Returns API response dict."""
    content = _truncate_html(html_content)

    payload = json.dumps({
        "token": token,
        "title": title,
        "content": content,
        "template": "html",
    }).encode("utf-8")

    req = urllib.request.Request(PUSHPLUS_URL, data=payload, headers={
        "Content-Type": "application/json",
    })

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    import os
    token = os.environ.get("PUSHPLUS_TOKEN", "3d9d364039ab432ead44d9725e456f7a")
    result = push_report("<h1>Test</h1>", "Test Push", token)
    print(result)
