import datetime
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_PATH = os.path.join(ROOT, "data", "contributions.json")
OUT_PATH = os.path.join(ROOT, "stats.svg")

WIDTH = 840
HEIGHT = 880
TITLE = "GitHub Stats"
MONTH_LETTERS = "JFMAMJJASOND"


def short_date(value):
    if not value:
        return "-"
    date = datetime.date.fromisoformat(value)
    return date.strftime("%b %d, %Y").replace(" 0", " ")


def streak_range(streak):
    if not streak["length"]:
        return "no active streak"
    return f'{short_date(streak["start"])} - {short_date(streak["end"])}'


def card(x, y, label, value, unit, sub, delay):
    return (
        f'<g class="t" style="animation-delay:{delay:.2f}s">'
        f'<rect x="{x}" y="{y}" width="392" height="150" rx="10" fill="#161b22" stroke="#30363d"/>'
        f'<text x="{x + 24}" y="{y + 40}" fill="#7d8590" font-size="22">{label.title()}</text>'
        f'<text x="{x + 24}" y="{y + 100}" font-size="54" font-weight="700" fill="#39d353">{value}'
        f'<tspan font-size="24" font-weight="400" fill="#7d8590"> {unit}</tspan></text>'
        f'<text x="{x + 24}" y="{y + 130}" fill="#7d8590" font-size="16">{sub}</text>'
        f"</g>"
    )


def bar_chart(monthly, top):
    panel_x, panel_w, panel_h = 20, 800, 302
    inner_left, inner_right = 60, panel_w - 20
    base_y = top + panel_h - 50
    max_height = panel_h - 130
    peak = max((m["total"] for m in monthly), default=1) or 1
    slot = (inner_right - inner_left) / len(monthly)
    bar_w = min(38, slot * 0.6)

    parts = [
        f'<g class="t" style="animation-delay:0.90s">'
        f'<rect x="{panel_x}" y="{top}" width="{panel_w}" height="{panel_h}" rx="10" fill="#161b22" stroke="#30363d"/>'
        f'<text x="{panel_x + 24}" y="{top + 40}" fill="#7d8590" font-size="22">Monthly contributions</text>'
        f"</g>"
    ]
    for index, month in enumerate(monthly):
        height = max(4, month["total"] / peak * max_height)
        x = inner_left + index * slot + (slot - bar_w) / 2
        y = base_y - height
        letter = MONTH_LETTERS[int(month["month"][5:7]) - 1]
        delay = 1.0 + index * 0.06
        shade = "#39d353" if month["total"] == peak else "#26a641"
        parts.append(
            f'<rect class="b" x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{height:.1f}" rx="6" '
            f'fill="{shade}" style="animation-delay:{delay:.2f}s"><title>{month["month"]}: {month["total"]}</title></rect>'
            f'<text x="{x + bar_w / 2:.1f}" y="{y - 8:.1f}" fill="#e6edf3" font-size="15" text-anchor="middle">{month["total"]}</text>'
            f'<text x="{x + bar_w / 2:.1f}" y="{base_y + 28}" fill="#7d8590" font-size="16" text-anchor="middle">{letter}</text>'
        )
    return "".join(parts)


def main():
    with open(DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)

    current = data["current_streak"]
    longest = data["longest_streak"]
    best = data["best_day"]
    start = short_date(data["range"]["start"])
    end = short_date(data["range"]["end"])

    cards = [
        card(20, 54, "current streak", current["length"], "days", streak_range(current), 0.00),
        card(428, 54, "longest streak", longest["length"], "days", streak_range(longest), 0.10),
        card(20, 222, "contributions", data["total_contributions"], "total", f"{start} - {end}", 0.20),
        card(428, 222, "active days", data["active_days"], "days", "days with at least one commit", 0.30),
        card(20, 390, "best day", best["count"], "commits", short_date(best["date"]), 0.40),
        card(428, 390, "avg per active day", data["avg_per_active_day"], "commits", "on days I ship code", 0.50),
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<style>
  .t {{ animation:in 0.45s ease-out both; }}
  @keyframes in {{ 0%{{opacity:0;transform:translateY(14px)}} 100%{{opacity:1;transform:translateY(0)}} }}
  .b {{ transform-box:fill-box; transform-origin:bottom; animation:grow 0.6s ease-out both; }}
  @keyframes grow {{ 0%{{transform:scaleY(0)}} 100%{{transform:scaleY(1)}} }}
  @media (prefers-reduced-motion: reduce) {{ .t, .b {{ animation:none !important; }} }}
</style>
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="#30363d"/>
<line x1="0" y1="30" x2="{WIDTH}" y2="30" stroke="#30363d"/>
<circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="52" cy="15" r="5" fill="#27c93f"/>
<text x="{WIDTH / 2}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">{TITLE}</text>
{"".join(cards)}
{bar_chart(data["monthly"][-12:], 558)}
</svg>
"""
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
