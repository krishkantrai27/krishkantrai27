import datetime
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_PATH = os.path.join(ROOT, "data", "contributions.json")
OUT_PATH = os.path.join(ROOT, "contrib-heatmap.svg")

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL = 13
STEP = 16
LEFT = 34
TOP = 24
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def weekday_index(date):
    return (date.weekday() + 1) % 7


def main():
    with open(DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)

    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    origin = first - datetime.timedelta(days=weekday_index(first))

    cells = []
    month_labels = []
    last_month = None
    for index, day in enumerate(days):
        date = datetime.date.fromisoformat(day["date"])
        column = (date - origin).days // 7
        row = weekday_index(date)
        x = LEFT + column * STEP
        y = TOP + row * STEP
        if row == 0 and date.month != last_month:
            month_labels.append(f'<text class="lbl" x="{x}" y="16">{MONTHS[date.month - 1]}</text>')
            last_month = date.month
        color = COLORS[min(day["level"], 4)]
        delay = round(index * 0.012, 3)
        title = f'{day["count"]} contributions on {day["date"]}'
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{color}" style="animation-delay:{delay}s"><title>{title}</title></rect>'
        )

    columns = (datetime.date.fromisoformat(days[-1]["date"]) - origin).days // 7 + 1
    width = LEFT + columns * STEP + 6
    height = TOP + 7 * STEP + 30

    weekday_labels = "".join(
        f'<text class="lbl" x="2" y="{TOP + row * STEP + 11}">{name}</text>'
        for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    legend_y = TOP + 7 * STEP + 8
    legend_x = width - 6 - 5 * STEP - 80
    legend = [f'<text class="lbl" x="{legend_x}" y="{legend_y + 11}">Less</text>']
    for level, color in enumerate(COLORS):
        legend.append(
            f'<rect x="{legend_x + 34 + level * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>'
        )
    legend.append(f'<text class="lbl" x="{legend_x + 34 + 5 * STEP + 4}" y="{legend_y + 11}">More</text>')
    total = f'<text class="total" x="{LEFT}" y="{legend_y + 12}">{data["total_contributions"]} contributions in the last year</text>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<style>
  text.lbl {{ fill:#7d8590; font-size:13px; font-weight:600; }}
  text.total {{ fill:#e6edf3; font-size:15px; font-weight:700; }}
  .c {{ transform-box:fill-box; transform-origin:center; animation:pop 0.55s ease-out both; }}
  @keyframes pop {{ 0%{{opacity:0;transform:scale(.2)}} 60%{{opacity:1;transform:scale(1.1)}} 100%{{opacity:1;transform:scale(1)}} }}
  @media (prefers-reduced-motion: reduce) {{ .c {{ animation:none !important; }} }}
</style>
<rect width="{width}" height="{height}" fill="none"/>
{"".join(month_labels)}{weekday_labels}
{"".join(cells)}
{total}{"".join(legend)}
</svg>
"""
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(svg)
    print(f"wrote {OUT_PATH} ({width}x{height})")


if __name__ == "__main__":
    main()
