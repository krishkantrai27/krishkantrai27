import os
import sys

from PIL import Image, ImageEnhance, ImageOps

ROOT = os.path.join(os.path.dirname(__file__), "..")
SOURCE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source", "avatar.png")
OUT_PATH = os.path.join(ROOT, "krish-ascii.svg")

WIDTH = 840
HEIGHT = 880
TITLE = "Krish Kant Rai"
COLS = 112
FONT_SIZE = 11.5
CHAR_W = FONT_SIZE * 0.6
ROW_H = FONT_SIZE * 1.0
RAMP = " .:-=+*#%@"
TOP = 52
LEFT = (WIDTH - COLS * CHAR_W) / 2


def load_image():
    image = Image.open(SOURCE).convert("RGBA")
    background = Image.new("RGBA", image.size, (0, 0, 0, 255))
    background.alpha_composite(image)
    image = background.convert("RGB")
    rows = int(COLS * CHAR_W / ROW_H * image.height / image.width)
    return image.resize((COLS, rows), Image.LANCZOS)


def tint(rgb, luma):
    green = (57, 211, 83)
    mix = 0.55
    base = tuple(int(c * (1 - mix) + g * mix) for c, g in zip(rgb, green))
    boost = 0.55 + 0.45 * luma
    return tuple(min(255, int(c * boost + 20)) for c in base)


def main():
    image = load_image()
    gray = ImageOps.autocontrast(image.convert("L"), cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.4)
    columns, rows = image.size
    lines = []
    for y in range(rows):
        spans = []
        for x in range(columns):
            luma = gray.getpixel((x, y)) / 255
            char = RAMP[int(luma ** 0.55 * (len(RAMP) - 1))]
            if char == " ":
                spans.append(" ")
                continue
            r, g, b = tint(image.getpixel((x, y)), luma)
            spans.append(f'<tspan fill="#{r:02x}{g:02x}{b:02x}">{char.replace("&", "&amp;").replace("<", "&lt;")}</tspan>')
        lines.append(
            f'<text x="{LEFT:.1f}" y="{TOP + y * ROW_H:.1f}" textLength="{columns * CHAR_W:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve">{"".join(spans)}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{FONT_SIZE}">
<style>
  .art {{ animation:fade 1.2s ease-out both; }}
  @keyframes fade {{ 0%{{opacity:0}} 100%{{opacity:1}} }}
  @media (prefers-reduced-motion: reduce) {{ .art {{ animation:none !important; }} }}
</style>
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="#30363d"/>
<line x1="0" y1="30" x2="{WIDTH}" y2="30" stroke="#30363d"/>
<circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="52" cy="15" r="5" fill="#27c93f"/>
<text x="{WIDTH / 2}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">{TITLE}</text>
<g class="art">{"".join(lines)}</g>
<text x="24" y="{HEIGHT - 20}" fill="#39d353" font-size="14">Krish Kant Rai</text>
<text x="{WIDTH - 24}" y="{HEIGHT - 20}" fill="#7d8590" font-size="14" text-anchor="end">Full Stack Java Developer</text>
</svg>
"""
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(svg)
    print(f"wrote {OUT_PATH} ({columns}x{rows} chars)")


if __name__ == "__main__":
    main()
