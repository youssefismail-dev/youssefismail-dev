"""
Build a neofetch-style info card SVG to sit to the RIGHT of the ASCII
portrait: colored key/value rows for what I'm building, researching, studying
and using -- NOT GitHub stats (the contribution graph covers those).

Static content, hand-authored below. Lines fade/slide in on a short stagger so
it feels like the panel is printing alongside the portrait. STATIC=1 emits the
frozen state for Quick Look previews.

    python scripts/make_info_card.py           # writes info-card.svg
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

USER = "youssef"

# content model: tuples describing each row
# ("host",)                    -> "youssef@github"
# ("rule",)                    -> the ──── underline beneath it
# ("kv", key, value)           -> orange key + light value; key "" continues
#                                 the previous key on a new line
ROWS = [
    ("host",),
    ("rule",),
    ("kv", "Now", "Building LIMENX, a phishing-URL detector with explained verdicts"),
    ("kv", "Research", "URL Intelligence Engine: a generative model that writes"),
    ("kv", "", "realistic synthetic URLs to train and stress-test detectors"),
    ("kv", "Studying", "Computer Science & Artificial Intelligence"),
    ("kv", "Focus", "ML security · AI engineering"),
    ("kv", "Stack", "Python · PyTorch · scikit-learn · CatBoost · FastAPI"),
    ("kv", "", "Next.js · React Three Fiber · Vercel · Kaggle (GPU)"),
    ("kv", "Highlights", "LIMENX live at limnex.vercel.app"),
    ("kv", "", "4-model ensemble (lexical + CNN) with per-reason explanations"),
    ("kv", "", "IDN / homograph attack detection (97.6% recall)"),
    ("kv", "", "External-benchmark ROC 0.45 → 0.87 by fixing dataset shift"),
    ("kv", "Learning", "AI from first principles: math → models"),
    ("kv", "Contact", ": linkedin.com/in/youssef-ismail-396snow"),
]

FONT = 12.5
CHAR_W = FONT * 0.6   # monospace advance; sizes the card to the longest row
KEY_COLS = 11         # "Highlights" + one space, as in neofetch
PAD = 20
TITLEBAR_H = 30
LINE_H = 23
KEY_X = PAD
VAL_X = PAD + KEY_COLS * CHAR_W
HOST = f"{USER}@github"

W = round(VAL_X + max(len(r[2]) for r in ROWS if r[0] == "kv") * CHAR_W + PAD)
FIRST_Y = TITLEBAR_H + 30
H = round(FIRST_Y + (len(ROWS) - 1) * LINE_H + 28)   # 520 wide == portrait at 340

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"      # orange keys
GREEN = "#3fb950"
ACCENT = "#22d3ee"


def esc(s):
    return html.escape(s)


def rise(inner, i):
    """fade + slight upward slide, staggered by row index; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{USER}@github: ~$ neofetch</text>')

y = FIRST_Y
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "host":
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                 f'<tspan fill="{GREEN}">{USER}</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{ACCENT}">github</tspan></text>')
    elif kind == "rule":
        # same size as the host line, so in any monospace font it underlines
        # exactly the title's width
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{MUTED}" font-size="14">'
                 f'{"─" * len(HOST)}</text>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="{FONT}" font-weight="700">{key}</text>'
                 if key else "")
        inner += f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="{FONT}">{val}</text>'
    else:
        continue
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H)
