"""
Serenity Daily - Main Orchestrator (Cloud Version)
Runs in GitHub Actions:
1. Fetches today's tweets from RSS.app
2. Calls DeepSeek AI to analyze with Serenity methodology
3. Updates accumulated data (for half-year stats)
4. Updates cumulative HTML report (with dynamic half-year summary)
5. Pushes via PushPlus
6. Commits state changes back to repo
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_tweets import fetch_today_tweets
from analyze import call_deepseek, build_analysis_prompt
from build_report import update_report
from push_report import push_report
from accumulated import update_accumulated, get_half_year_summary, mark_shown

# --- Config ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STATE_FILE = os.path.join(DATA_DIR, "serenity_state.json")
REPORT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "serenity_report.html")

PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "3d9d364039ab432ead44d9725e456f7a")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

BEIJING_TZ = timezone(timedelta(hours=8))


def load_state() -> dict:
    """Load persistence state from JSON file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "analyzed_ids": [],      # All tweet IDs ever analyzed
        "total_days": 0,
        "total_tweets": 0,
        "all_stocks": [],        # All unique stock tickers seen
    }


def save_state(state: dict):
    """Save persistence state to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_report() -> str:
    """Load existing HTML report, or empty string if not found."""
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def save_report(html: str):
    """Save HTML report to file."""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)


def push_if_report_exists(today_str: str):
    """Fallback: update date badge and push existing report (no new analysis)."""
    state = load_state()
    report_html = load_report()
    if report_html:
        import re
        report_html = re.sub(
            r'<div class="date-badge">📅 [^<]*</div>',
            f'<div class="date-badge">📅 更新于 {today_str}</div>',
            report_html
        )
        save_report(report_html)
        result = push_report(report_html, f"🔮 Serenity 每日分析 {today_str}", PUSHPLUS_TOKEN)
        print(f"  Push result: {result}")
    return


def main():
    print("=" * 60)
    print("Serenity Daily Analysis - Cloud Version")
    print("=" * 60)

    today_str = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")

    # Step 1: Fetch tweets
    print("\n[1/6] Fetching today's tweets...")
    try:
        tweets = fetch_today_tweets()
        print(f"  Fetched {len(tweets)} tweets")
    except Exception as e:
        print(f"  ERROR fetching tweets: {e}")
        import traceback
        traceback.print_exc()
        print("  Will try to push existing report instead.")
        push_if_report_exists(today_str)
        return

    if not tweets:
        print("  No tweets today, skipping analysis.")
        push_if_report_exists(today_str)
        return

    # Step 2: Load state and filter new tweets
    state = load_state()
    new_tweets = [t for t in tweets if t["id"] not in state["analyzed_ids"]]
    print(f"  New tweets: {len(new_tweets)} / Total today: {len(tweets)}")

    if not new_tweets:
        print("  All tweets already analyzed, skipping.")
        push_if_report_exists(today_str)
        return

    # Step 3: AI Analysis
    print("\n[2/6] Calling DeepSeek AI for analysis...")
    if not DEEPSEEK_API_KEY:
        print("  ERROR: DEEPSEEK_API_KEY not set!")
        print("  Please add it as a GitHub Secret: Settings > Secrets > DEEPSEEK_API_KEY")
        sys.exit(1)

    try:
        prompt = build_analysis_prompt(new_tweets)
        analysis = call_deepseek(prompt, DEEPSEEK_API_KEY)
        print(f"  Analysis received. Summary: {analysis.get('summary', 'N/A')[:100]}...")
    except Exception as e:
        print(f"  ERROR calling DeepSeek API: {e}")
        sys.exit(1)

    # Step 4: Update accumulated data (for half-year stats)
    print("\n[3/6] Updating accumulated data...")
    changes = update_accumulated(analysis, today_str)
    accu_summary = get_half_year_summary()
    print(f"  New stocks: {changes['new_stocks']}")
    print(f"  Conviction changes: {changes['conviction_changes']}")
    print(f"  New thesis: {changes['new_thesis']}")

    # Step 5: Update HTML Report (with dynamic half-year summary)
    print("\n[4/6] Updating HTML report...")
    for t in new_tweets:
        if t["id"] not in state["analyzed_ids"]:
            state["analyzed_ids"].append(t["id"])
    state["total_days"] += 1
    state["total_tweets"] += len(new_tweets)
    for s in analysis.get("stocks", []):
        ticker = s.get("ticker", "")
        if ticker and ticker not in state["all_stocks"]:
            state["all_stocks"].append(ticker)

    existing_report = load_report()
    updated_report = update_report(
        existing_report, today_str, analysis,
        accu_summary, changes,       # <-- dynamic data + changes highlighting
    )
    save_report(updated_report)
    save_state(state)
    print(f"  Report updated.")

    # Step 6: Push via PushPlus
    print("\n[5/6] Pushing to PushPlus...")
    try:
        result = push_report(updated_report, f"🔮 Serenity 每日分析 {today_str}", PUSHPLUS_TOKEN)
        print(f"  Push result: {result}")
        if result.get("code") == 200:
            print("  Push SUCCESS!")
            # Mark all "new" flags as shown
            from accumulated import load_accumulated, mark_shown
            data = load_accumulated()
            mark_shown(data)
        else:
            print(f"  Push may have failed: {result}")
    except Exception as e:
        print(f"  ERROR pushing: {e}")

    print("\n[6/6] Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
