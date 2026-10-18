#!/usr/bin/env python3
"""Render every static image asset straight from the particle data.

Keeps the little squares in the tab bar, the no-JS fallback and the social
card identical in colour to the canvas on the page.

    python tools/make-icons.py
"""
import base64
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "particles.js"

INK = (6, 7, 10)
SS = 4  # supersampling factor


def load():
    source = DATA.read_text(encoding="utf-8")
    match = re.search(r"window\.SCNU_PARTICLES\s*=\s*(\{.*\});", source, re.S)
    if not match:
        sys.exit("could not find window.SCNU_PARTICLES in %s" % DATA)
    blob = json.loads(match.group(1))
    raw = base64.b64decode(blob["data"])
    cells = []
    for i in range(0, len(raw), 4):
        cells.append((raw[i], raw[i + 1], tuple(blob["palette"][raw[i + 2]][1])))
    return blob["grid"], cells


def render(grid, cells, width, height=None, stride=1, pad=0.13, dot=0.3):
    """Dot-matrix emblem on a transparent canvas."""
    height = height or width
    big = (width * SS, height * SS)
    img = Image.new("RGB", big, (0, 0, 0))
    mask = Image.new("L", big, 0)
    draw = ImageDraw.Draw(img)
    pain = ImageDraw.Draw(mask)

    span = min(big) * (1 - 2 * pad)
    pitch = span / grid * stride
    radius = max(1.0, pitch * dot)
    origin_x = (big[0] - span) / 2
    origin_y = (big[1] - span) / 2

    for gx, gy, rgb in cells:
        if gx % stride or gy % stride:
            continue
        x = origin_x + (gx / stride + 0.5) * pitch
        y = origin_y + (gy / stride + 0.5) * pitch
        box = [x - radius, y - radius, x + radius, y + radius]
        draw.ellipse(box, fill=rgb)
        pain.ellipse(box, fill=255)

    img = img.resize((width, height), Image.LANCZOS)
    mask = mask.resize((width, height), Image.LANCZOS)
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def vignette(width, height):
    """Same radial wash as the page background in css/style.css."""
    ys, xs = np.mgrid[0:height, 0:width].astype(np.float32)
    cx, cy = width * 0.5, height * 0.44
    rx, ry = width * 1.15, height * 0.85
    t = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2) / 0.7071
    t = np.clip(t, 0.0, 1.0)
    stops = [(0.0, (20, 26, 36)), (0.34, (11, 14, 20)), (0.74, (5, 6, 10)), (1.0, (4, 5, 8))]
    out = np.zeros((height, width, 3), dtype=np.float32)
    for i in range(len(stops) - 1):
        a, ca = stops[i]
        b, cb = stops[i + 1]
        f = np.clip((t - a) / (b - a), 0, 1)
        band = np.array(ca, np.float32) * (1 - f[..., None]) + np.array(cb, np.float32) * f[..., None]
        out = np.where((t >= a)[..., None] & (t <= b)[..., None], band, out)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGB")


def tracked(draw, centre, y, text, font, fill, tracking):
    """Draw letter-spaced text centred on x=centre."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = centre - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def square(size, emblem):
    tile = Image.new("RGBA", (size, size), INK + (255,))
    tile.paste(emblem, (0, 0), emblem)
    return tile


def main():
    grid, cells = load()
    saved = []

    for name, size, stride in (("icon-64.png", 64, 2), ("icon-180.png", 180, 1)):
        square(size, render(grid, cells, size, stride=stride)).convert("RGB").save(
            ROOT / "assets" / name, optimize=True
        )
        saved.append(name)

    emblem = render(grid, cells, 640)
    emblem.save(ROOT / "assets" / "emblem-640.png", optimize=True)
    saved.append("emblem-640.png")

    card = vignette(1200, 630)
    art = render(grid, cells, 440, stride=2, pad=0.02)
    card.paste(art, ((1200 - 440) // 2, (630 - 440) // 2 - 26), art)

    font_path = Path("C:/Windows/Fonts/segoeuil.ttf")
    if font_path.exists():
        font = ImageFont.truetype(str(font_path), 27)
        tracked(ImageDraw.Draw(card), 600, 528, "SCNU PIONEER", font, (214, 220, 229), 9.5)

    card.save(ROOT / "assets" / "og.png", optimize=True)
    saved.append("og.png")

    for name in saved:
        path = ROOT / "assets" / name
        print("%-16s %5.1f KB" % (name, path.stat().st_size / 1024))


if __name__ == "__main__":
    main()
