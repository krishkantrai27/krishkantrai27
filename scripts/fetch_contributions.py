import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "krishkantrai27")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    response = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        sys.exit("no calendar cells found, GitHub markup may have changed")

    days = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        tooltip = soup.find("tool-tip", attrs={"for": cell.get("id")})
        text = tooltip.get_text(strip=True) if tooltip else ""
        match = re.match(r"(\d+)", text)
        count = int(match.group(1)) if match else 0
        days.append({"date": date, "count": count, "level": int(cell.get("data-level") or 0)})
    days.sort(key=lambda day: day["date"])
    return days


def current_streak(days):
    index = len(days) - 1
    if days[index]["count"] == 0:
        index -= 1
    end = index
    while index >= 0 and days[index]["count"] > 0:
        index -= 1
    length = end - index
    if length <= 0:
        return {"length": 0, "start": None, "end": None}
    return {"length": length, "start": days[index + 1]["date"], "end": days[end]["date"]}


def longest_streak(days):
    best = {"length": 0, "start": None, "end": None}
    run_start = None
    for index, day in enumerate(days + [{"date": None, "count": 0}]):
        if day["count"] > 0:
            if run_start is None:
                run_start = index
        elif run_start is not None:
            length = index - run_start
            if length > best["length"]:
                best = {"length": length, "start": days[run_start]["date"], "end": days[index - 1]["date"]}
            run_start = None
    return best


def monthly_totals(days):
    totals = {}
    for day in days:
        key = day["date"][:7]
        totals[key] = totals.get(key, 0) + day["count"]
    return [{"month": month, "total": total} for month, total in sorted(totals.items())]


def main():
    days = fetch_days()
    total = sum(day["count"] for day in days)
    active = sum(1 for day in days if day["count"] > 0)
    best = max(days, key=lambda day: day["count"])
    payload = {
        "username": USERNAME,
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active,
        "avg_per_active_day": round(total / active, 1) if active else 0,
        "current_streak": current_streak(days),
        "longest_streak": longest_streak(days),
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_totals(days),
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"{USERNAME}: {total} contributions, {active} active days, streak {payload['current_streak']['length']}")


if __name__ == "__main__":
    main()
