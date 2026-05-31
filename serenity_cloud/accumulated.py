"""
Serenity Daily - Accumulated Data Tracker

Manages persistent accumulated data across all daily runs.
Tracks stock conviction history, thesis changes, performance, and generates
dynamic half-year summary with change highlighting.
"""

import json
import os
from datetime import datetime, timezone, timedelta

# --- File paths ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ACCUM_FILE = os.path.join(DATA_DIR, "serenity_accumulated.json")

BEIJING_TZ = timezone(timedelta(hours=8))

# --- Default structure ---

DEFAULT_ACCUM = {
    "meta": {
        "created": "",
        "last_updated": "",
        "total_runs": 0,
        "first_date": "",
        "last_date": "",
    },
    # Per-stock tracking: ticker → { first_seen, conviction_history: [{date, conviction, stance}], ... }
    "stocks": {},
    # thesis_changes accumulated: [{date, title, description, principles, is_new}]
    "thesis_changes": [],
    # key_events accumulated
    "key_events": [],
    # supply_chain insights accumulated
    "supply_chain": [],
    # risk_alerts accumulated
    "risk_alerts": [],
    # Performance tracker
    "performance": {
        "directional_hits": 0,
        "directional_total": 0,
        "strict_hits": 0,
        "strict_total": 0,
        "cpo_verified": 0,
        "cpo_total": 0,
    },
    # Daily summaries for trend tracking
    "daily_summaries": [],
}


def load_accumulated() -> dict:
    """Load accumulated data from JSON file."""
    if os.path.exists(ACCUM_FILE):
        with open(ACCUM_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults for any missing keys
        for key in DEFAULT_ACCUM:
            if key not in data:
                data[key] = DEFAULT_ACCUM[key]
        return data
    # New file
    data = dict(DEFAULT_ACCUM)
    data["meta"]["created"] = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    return data


def save_accumulated(data: dict):
    """Save accumulated data to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    data["meta"]["last_updated"] = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    with open(ACCUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_accumulated(analysis: dict, date_str: str) -> dict:
    """
    Update accumulated data with today's analysis results.
    Returns a `changes` dict describing what's new/changed for highlighting.
    """
    data = load_accumulated()
    changes = {
        "new_stocks": [],       # tickers seen for the first time
        "conviction_changes": [],  # [{ticker, old, new}]
        "new_thesis": [],        # new thesis change titles
        "new_events": [],       # new key event titles
        "new_supply_chain": [], # new supply chain insight titles
        "new_risks": [],        # new risk alert titles
    }

    meta = data["meta"]
    meta["total_runs"] += 1
    if not meta["first_date"]:
        meta["first_date"] = date_str
    meta["last_date"] = date_str

    # --- Update stocks ---
    for stock in analysis.get("stocks", []):
        ticker = stock.get("ticker", "").upper().strip()
        if not ticker:
            continue
        stance = stock.get("stance", "neutral")
        conviction = stock.get("conviction", 3)
        analysis_text = stock.get("analysis", "")

        if ticker not in data["stocks"]:
            # New stock
            data["stocks"][ticker] = {
                "first_seen": date_str,
                "last_seen": date_str,
                "stance": stance,
                "max_conviction": conviction,
                "conviction_history": [{"date": date_str, "conviction": conviction, "stance": stance}],
                "principles": stock.get("principles", []),
                "analyses": [analysis_text[:200]],
            }
            changes["new_stocks"].append(ticker)
        else:
            existing = data["stocks"][ticker]
            existing["last_seen"] = date_str
            old_conviction = existing["max_conviction"]

            # Update conviction history
            existing["conviction_history"].append({
                "date": date_str,
                "conviction": conviction,
                "stance": stance,
            })

            if conviction > existing["max_conviction"]:
                existing["max_conviction"] = conviction
                changes["conviction_changes"].append({
                    "ticker": ticker,
                    "old": old_conviction,
                    "new": conviction,
                    "direction": "up",
                })
            elif conviction < old_conviction:
                changes["conviction_changes"].append({
                    "ticker": ticker,
                    "old": old_conviction,
                    "new": conviction,
                    "direction": "down",
                })

            # Merge principles
            for p in stock.get("principles", []):
                if p not in existing["principles"]:
                    existing["principles"].append(p)
            existing["analyses"].append(analysis_text[:200])
            # Keep last 10 analyses
            existing["analyses"] = existing["analyses"][-10:]

    # --- Update thesis_changes ---
    seen_thesis_titles = {t.get("title", "") for t in data["thesis_changes"]}
    for tc in analysis.get("thesis_changes", []):
        title = tc.get("title", "")
        if title and title not in seen_thesis_titles:
            entry = dict(tc)
            entry["date"] = date_str
            entry["is_new"] = True
            data["thesis_changes"].append(entry)
            changes["new_thesis"].append(title)
        elif title:
            # Mark as seen again (update date)
            for existing_tc in data["thesis_changes"]:
                if existing_tc.get("title") == title:
                    existing_tc["last_seen"] = date_str
                    break

    # --- Update key_events ---
    seen_event_titles = {e.get("title", "") for e in data["key_events"]}
    for ev in analysis.get("key_events", []):
        title = ev.get("title", "")
        if title and title not in seen_event_titles:
            entry = dict(ev)
            entry["date"] = date_str
            entry["is_new"] = True
            data["key_events"].append(entry)
            changes["new_events"].append(title)

    # --- Update supply_chain ---
    seen_sc_titles = {s.get("title", "") for s in data["supply_chain"]}
    for sc in analysis.get("supply_chain", []):
        title = sc.get("title", "")
        if title and title not in seen_sc_titles:
            entry = dict(sc)
            entry["date"] = date_str
            entry["is_new"] = True
            data["supply_chain"].append(entry)
            changes["new_supply_chain"].append(title)

    # --- Update risk_alerts ---
    seen_risk_titles = {r.get("title", "") for r in data["risk_alerts"]}
    for ra in analysis.get("risk_alerts", []):
        title = ra.get("title", "")
        if title and title not in seen_risk_titles:
            entry = dict(ra)
            entry["date"] = date_str
            entry["is_new"] = True
            data["risk_alerts"].append(entry)
            changes["new_risks"].append(title)

    # --- Update daily_summaries ---
    data["daily_summaries"].append({
        "date": date_str,
        "summary": analysis.get("summary", ""),
        "market_context": analysis.get("market_context", ""),
        "stock_count": len(analysis.get("stocks", [])),
        "tweet_count": len(analysis.get("reference_tweets", [])),
    })
    # Keep last 180 days
    data["daily_summaries"] = data["daily_summaries"][-180:]

    save_accumulated(data)
    return changes


def get_half_year_summary() -> dict:
    """
    Generate the half-year summary stats from accumulated data.
    Returns a dict suitable for rendering in the HTML report.
    """
    data = load_accumulated()
    stocks = data["stocks"]
    perf = data["performance"]
    meta = data["meta"]
    daily = data["daily_summaries"]

    # --- Core stats ---
    total_runs = meta["total_runs"]
    total_tweets = sum(d.get("tweet_count", 0) for d in daily)
    total_stocks = len(stocks)

    # --- Top conviction stocks ---
    # Sort by max_conviction desc, then by number of analyses desc
    top_stocks = sorted(
        [
            {
                "ticker": ticker,
                "conviction": info["max_conviction"],
                "first_seen": info["first_seen"],
                "last_seen": info["last_seen"],
                "stance": info["conviction_history"][-1]["stance"] if info["conviction_history"] else "neutral",
                "analyses_count": len(info["analyses"]),
            }
            for ticker, info in stocks.items()
        ],
        key=lambda x: (-x["conviction"], -x["analyses_count"]),
    )[:10]

    # --- Performance ---
    directional_accuracy = (
        round(perf["directional_hits"] / perf["directional_total"] * 100, 1)
        if perf["directional_total"] > 0 else 0
    )
    strict_accuracy = (
        round(perf["strict_hits"] / perf["strict_total"] * 100, 1)
        if perf["strict_total"] > 0 else 0
    )
    cpo_rate = (
        round(perf["cpo_verified"] / perf["cpo_total"] * 100, 1)
        if perf["cpo_total"] > 0 else 0
    )

    # --- Recent thesis changes (last 10) ---
    recent_thesis = [t for t in data["thesis_changes"] if t.get("is_new")][-10:]
    # Also include last 5 by date
    all_thesis_sorted = sorted(
        data["thesis_changes"],
        key=lambda x: x.get("date", ""),
        reverse=True,
    )[:10]

    # --- Recent key events (last 10) ---
    all_events_sorted = sorted(
        data["key_events"],
        key=lambda x: x.get("date", ""),
        reverse=True,
    )[:10]

    # --- Supply chain themes ---
    sc_themes = {}
    for sc in data["supply_chain"]:
        for p in sc.get("principles", []):
            sc_themes.setdefault(p, 0)
            sc_themes[p] += 1

    # --- Risk summary ---
    active_risks = [r for r in data["risk_alerts"] if r.get("is_new")]

    return {
        "meta": {
            "first_date": meta["first_date"] or "N/A",
            "last_date": meta["last_date"] or "N/A",
            "total_runs": total_runs,
            "total_tweets": total_tweets,
            "total_stocks": total_stocks,
        },
        "top_stocks": top_stocks,
        "performance": {
            "directional_accuracy": directional_accuracy,
            "directional_total": perf["directional_total"],
            "strict_accuracy": strict_accuracy,
            "cpo_rate": cpo_rate,
            "cpo_total": perf["cpo_total"],
        },
        "recent_thesis": all_thesis_sorted,
        "recent_events": all_events_sorted,
        "sc_themes": sc_themes,
        "active_risks": active_risks,
        "all_stocks": stocks,
    }


def mark_shown(data: dict):
    """After pushing, mark all 'is_new' flags as False."""
    for tc in data.get("thesis_changes", []):
        tc["is_new"] = False
    for ev in data.get("key_events", []):
        ev["is_new"] = False
    for sc in data.get("supply_chain", []):
        sc["is_new"] = False
    for ra in data.get("risk_alerts", []):
        ra["is_new"] = False
    save_accumulated(data)
