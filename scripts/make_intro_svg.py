import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_PATH = os.path.join(ROOT, "intro.svg")

WIDTH = 840
HEIGHT = 210
FONT_SIZE = 20
CHAR_W = FONT_SIZE * 0.6
LINE_H = 34
TOP = 76
LEFT = 32
TITLE = "Welcome"

LINES = [
    ("Hi, I'm Krish Kant Rai", "#39d353", "700"),
    ("Full Stack Java Developer | Spring Boot | React.js", "#e6edf3", "400"),
    ("Secure REST APIs | JWT | RAG pipelines | Vector DBs", "#e6edf3", "400"),
    ("B.Tech CSE @ KIET | open to SDE, Backend and AI/GenAI roles", "#7d8590", "400"),
]

TYPE_SPEED = 0.04
LINE_GAP = 0.3


def main():
    elements = []
    clips = []
    clock = 0.4
    last_y = TOP
    last_end = LEFT

    for index, (text, color, weight) in enumerate(LINES):
        y = TOP + index * LINE_H
        width = len(text) * CHAR_W + 2
        duration = max(0.4, len(text) * TYPE_SPEED)

        clips.append(
            f'<clipPath id="c{index}"><rect x="{LEFT}" y="{y - FONT_SIZE}" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{width:.1f}" dur="{duration:.2f}s" begin="{clock:.2f}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        elements.append(
            f'<text x="{LEFT}" y="{y}" fill="{color}" font-weight="{weight}" clip-path="url(#c{index})" xml:space="preserve">{text}</text>'
        )
        last_y = y
        last_end = LEFT + width
        clock += duration + LINE_GAP

    cursor = (
        f'<rect x="{last_end + 4:.1f}" y="{last_y - FONT_SIZE + 3}" width="10" height="{FONT_SIZE + 2}" fill="#39d353" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.01;0.5;0.51" dur="1s" begin="{clock:.2f}s" repeatCount="indefinite"/>'
        f"</rect>"
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{FONT_SIZE}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient>
{"".join(clips)}
</defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="#30363d"/>
<line x1="0" y1="30" x2="{WIDTH}" y2="30" stroke="#30363d"/>
<circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="52" cy="15" r="5" fill="#27c93f"/>
<text x="{WIDTH / 2}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">{TITLE}</text>
{"".join(elements)}
{cursor}
</svg>
"""
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
