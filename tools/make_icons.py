#!/usr/bin/env python3
"""Draw the launcher icons from one description, rather than keeping binaries by hand.

A home-screen icon for a signalling lamp should read as a lit lens at 48 px on a
dark dock, so the mark is the lens alone — bezel, fresnel rings and the light —
and not the whole lamp, whose grip and barrel turn to mud at that size.

Everything is drawn at 4x and downsampled, which is what keeps the circle edges
clean without any anti-aliasing work of our own.

    python3 tools/make_icons.py

Maskable variants keep the lens inside the 80% safe circle, because a launcher
is free to crop a circle, a squircle or a rounded rectangle out of it.
"""

import pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
SS = 4                      # supersample factor

BG = (5, 5, 5)              # --bg
BEZEL = (29, 29, 29)
BEZEL_EDGE = (74, 74, 74)
RING = (150, 110, 20)       # the fresnel lines, as on the lamp in the page

# Centre to rim: the lit lens, cream through gold to deep amber.
STOPS = [(0.00, (255, 248, 220)), (0.35, (253, 224, 71)), (0.72, (234, 179, 8)), (1.00, (146, 64, 14))]


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def lens_colour(t):
    """Colour at fraction t from the centre of the lens to its rim."""
    for i in range(len(STOPS) - 1):
        t0, c0 = STOPS[i]
        t1, c1 = STOPS[i + 1]
        if t <= t1:
            return lerp(c0, c1, 0 if t1 == t0 else (t - t0) / (t1 - t0))
    return STOPS[-1][1]


def draw(size, lens_r, bezel_r):
    """One icon. Radii are fractions of the canvas, so the two variants agree."""
    px = size * SS
    img = Image.new('RGB', (px, px), BG)
    d = ImageDraw.Draw(img)
    c = px / 2

    def circle(r, fill):
        d.ellipse([c - r, c - r, c + r, c + r], fill=fill)

    bezel = bezel_r * px
    lens = lens_r * px

    circle(bezel, BEZEL_EDGE)
    circle(bezel * 0.955, BEZEL)
    circle(lens * 1.06, (10, 10, 10))

    # The light: concentric fills from the rim inwards. At 4x, one step per
    # supersampled pixel of radius is already finer than the output can show.
    for i in range(int(lens), 0, -1):
        circle(i, lens_colour(i / lens))

    # Fresnel rings, faint enough to read as glass rather than as targets.
    for frac in (0.45, 0.75):
        r = lens * frac
        d.ellipse([c - r, c - r, c + r, c + r], outline=RING, width=max(1, int(px / 220)))

    return img.resize((size, size), Image.LANCZOS)


def main():
    # A normal icon may use the full square; a maskable one must survive a crop
    # to the central 80%, so its lens is pulled in rather than scaled down.
    for name, size, lens_r, bezel_r in [
        ('icon-512.png', 512, 0.345, 0.45),
        ('icon-192.png', 192, 0.345, 0.45),
        ('apple-touch-icon.png', 180, 0.345, 0.45),
        ('icon-512-maskable.png', 512, 0.26, 0.34),
    ]:
        draw(size, lens_r, bezel_r).save(ROOT / name, optimize=True)
        print('wrote', name)


if __name__ == '__main__':
    main()
