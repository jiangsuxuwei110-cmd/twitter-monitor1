"""
Serenity Half-Year Report - Main Orchestrator (Cloud Version)
Runs in GitHub Actions after Task 2 completes:
1. Loads accumulated data from serenity_accumulated.json (maintained by Task 2)
2. Builds comprehensive half-year report (organized by stock/theme)
3. Pushes via PushPlus
4. Commits updated report back to repo
"""

import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_half_year_report import build_half_year_report, save_half_year_report
from push_report import push_report

# --- Config ---
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "3d9d364039ab432ead44d9725e456f7a")

BEIJING_TZ = timezone(timedelta(hours=8))


def main():
    print("=" * 60)
    print("Serenity Half-Year Comprehensive Report")
    print("=" * 60)

    today_str = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")

    # Step 1: Build comprehensive report
    print("\n[1/3] Building half-year comprehensive report...")
    html = build_half_year_report(today_str)
    save_half_year_report(html)
    print(f"  Report built: {len(html)} chars")

    # Step 2: Push via PushPlus (with auto-truncation)
    print("\n[2/3] Pushing to PushPlus...")
    try:
        result = push_report(html, f"📊 Serenity 半年综合分析 {today_str}", PUSHPLUS_TOKEN)
        print(f"  Push result: {result}")
        if isinstance(result, dict) and result.get("code") == 200:
            print("  Push SUCCESS!")
        else:
            print(f"  Push returned: {result}")
    except Exception as e:
        print(f"  ERROR pushing: {e}")

    # Step 3: Commit updated report back to repo
    print("\n[3/3] Committing report to repo...")
    import subprocess
    try:
        subprocess.run(["git", "config", "user.email", "serenity-bot@github.com"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        subprocess.run(["git", "config", "user.name", "Serenity Bot"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        subprocess.run(["git", "add", "serenity_half_year.html"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        subprocess.run(["git", "commit", "-m", f"chore: update half-year report {today_str} [skip ci]"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        subprocess.run(["git", "push", "origin", "main"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        print("  Committed and pushed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"  Git operation skipped or failed: {e}")
        print("  (This is normal if no changes or already pushed)")

    print("\nDone!")
    print("=" * 60)


if __name__ == "__main__":
    main()
