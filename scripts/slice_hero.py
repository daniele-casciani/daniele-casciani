"""Cut assets/hero.svg into viewBox crops so each social pill can carry its own link.

GitHub shows SVGs as <img>: links inside the SVG are dead and <map> is stripped,
so the hero is split into images that sit edge to edge, each with its own <a>.
Rewrites the hero block in README.md; safe to rerun after regenerating hero.svg.

usage: python3 -I scripts/slice_hero.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H, CUT = 860, 274, 186
# (name, x0, x1, y0, y1, link): pill boundaries must match hero.svg (pill1 46..219, pill2 231..368)
SLICES = [("top", 0, W, 0, CUT, None),
          ("pill-linkedin", 0, 225, CUT, H, "https://www.linkedin.com/in/danielecasciani/"),
          ("pill-genogra", 225, 374, CUT, H, "https://github.com/GenoGra"),
          ("rest", 374, W, CUT, H, None)]

src = (ROOT / "assets/hero.svg").read_text()
root_attrs = f'width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
assert root_attrs in src, "hero.svg size changed: update W, H and the slice boundaries"

tags = []
for name, x0, x1, y0, y1, link in SLICES:
    w, h = x1 - x0, y1 - y0
    svg = src.replace(root_attrs, f'width="{w}" height="{h}" viewBox="{x0} {y0} {w} {h}"', 1)
    (ROOT / f"assets/hero-{name}.svg").write_text(svg)
    # percentage width keeps every slice on the same scale; align=top removes the inline baseline gap
    img = f'<img src="./assets/hero-{name}.svg" alt="{name}" width="{w / W * 100:.4f}%" align="top" />'
    tags.append(f'<a href="{link}">{img}</a>' if link else img)
top, *row = tags
# no whitespace between the row images, or the browser puts a gap between them
block = f'<p align="center">\n{top}<br/>{"".join(row)}\n</p>'

readme = ROOT / "README.md"
text, n = re.subn(r'<p align="center">\n[^\n]*assets/hero(?:-top)?\.svg[^\n]*\n</p>', block, readme.read_text(), count=1)
assert n == 1, "hero block not found in README.md"
readme.write_text(text)
