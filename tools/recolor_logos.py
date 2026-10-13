#!/usr/bin/env python3
"""
Turn a reversed (white) partner logo into a dark one, without touching any
brand colour.

Why
---
The partner wall is on a white background, but about half the logos brands
publish are the reversed version made for dark backgrounds — white ink that
disappears on white. This flips those to dark.

The rule, applied per pixel and per SVG colour:

    achromatic (white, black, grey)  ->  invert its lightness
    anything with hue               ->  left exactly as it is

So white becomes near-black and a light grey becomes a dark grey, while
Echodyne's blue, AMVIC's green, AUVSI's red and Skyfire's red come through
untouched. Inverting the whole image would turn blue into orange, which is why
this is not a CSS filter.

This edits a trademark, which is normally not ours to do — it is here because
the client asked for it explicitly. The originals are kept beside the output in
assets/img/partners/reversed/ so the authentic artwork is never lost, and any
brand that later supplies its own dark version should simply replace the file.

    python3 tools/recolor_logos.py            # list what would change
    python3 tools/recolor_logos.py --apply
"""

import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIR = ROOT / "assets" / "img" / "partners"
KEEP = DIR / "reversed"

# Below this chroma (max channel minus min, 0-1) a colour counts as
# white/black/grey and gets flipped.
#
# Chroma, not HLS saturation. Saturation is unstable at the extremes: ResilienX's
# off-white #F7F5F0 is seven values from neutral and reports a saturation of 0.30,
# which any sensible threshold would read as "this has a hue" — and the logo
# would have stayed white on a white page.
CHROMA_MAX = 0.16
# Flipped white lands here rather than pure black: it reads as ink on the page
# and matches the site's body colour.
INK = (0x10, 0x20, 0x3F)


def flip_rgb(r, g, b):
    """Invert lightness for achromatic colours; leave any hue alone."""
    hi, lo = max(r, g, b) / 255, min(r, g, b) / 255
    if hi - lo > CHROMA_MAX:
        return None                      # has hue — untouched
    l = (hi + lo) / 2
    if l >= 0.5:                         # white / light grey -> ink
        t = (l - 0.5) / 0.5              # 0 at mid grey, 1 at pure white
        return tuple(round(c + (i - c) * t)
                     for c, i in zip((128, 128, 128), INK))
    return None                          # already dark — nothing to do


def do_raster(path):
    from PIL import Image

    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    changed = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            out = flip_rgb(r, g, b)
            if out:
                px[x, y] = (*out, a)
                changed += 1
    # PNG throughout: it is lossless and keeps the alpha these all rely on.
    out_path = path.with_suffix(".png")
    im.save(out_path, "PNG", optimize=True)
    if out_path != path:
        path.unlink()
    return changed, out_path


def knockout(src, dst, ink=INK, pad=0):
    """Lift white artwork off a black panel into dark ink on transparency.

    A plain achromatic flip would turn the panel white and the type dark, which
    leaves a white rectangle sitting on the page. This instead reads the source
    luminance as coverage: where the pixel is white the artwork is solid, where
    it is black there is nothing. Antialiased edges come through as partial
    alpha rather than as a grey fringe, which is what a straight threshold would
    give.

    Only for artwork that is purely white on purely black. A panel carrying a
    coloured mark (Precision Planting's green, ANRA's teal) loses that colour
    here, so those keep their panel instead.
    """
    from PIL import Image

    im = Image.open(src).convert("RGBA")
    px = im.load()
    w, h = im.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            cov = (max(r, g, b) + min(r, g, b)) / 510          # 0 black .. 1 white
            alpha = round(cov * (a / 255) * 255)
            px[x, y] = (*ink, alpha)
            if alpha > 8:
                xs.append(x)
                ys.append(y)

    if xs:                                                     # trim the dead space
        im = im.crop((max(0, min(xs) - pad), max(0, min(ys) - pad),
                      min(w, max(xs) + 1 + pad), min(h, max(ys) + 1 + pad)))
    im.save(dst, "PNG", optimize=True)
    return im.size


HEX = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
NAMED = {"white": "#ffffff", "#fff": "#ffffff", "black": "#000000"}


def do_svg(path):
    s = path.read_text()
    changed = [0]

    def sub(m):
        v = m.group(1)
        if len(v) == 3:
            v = "".join(c * 2 for c in v)
        rgb = tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
        out = flip_rgb(*rgb)
        if not out:
            return m.group(0)
        changed[0] += 1
        return "#%02x%02x%02x" % out

    # Spell the named colours out first so one pass catches everything.
    for name, hexv in NAMED.items():
        s = re.sub(r'(fill|stroke|stop-color)\s*(=\s*"|:\s*)' + name + r'\b',
                   lambda m, h=hexv: m.group(1) + m.group(2) + h, s)
    s = HEX.sub(sub, s)
    path.write_text(s)
    return changed[0], path


def main():
    apply = "--apply" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not names:
        print("name the files to flip, e.g. "
              "python3 tools/recolor_logos.py --apply aevex.svg amvic.png")
        return

    if apply:
        KEEP.mkdir(exist_ok=True)

    for name in names:
        src = DIR / name
        if not src.exists():
            print(f"  {name:34} NOT FOUND")
            continue
        if not apply:
            print(f"  {name:34} would be flipped")
            continue
        shutil.copy2(src, KEEP / name)          # keep the authentic original
        n, out = (do_svg(src) if src.suffix == ".svg" else do_raster(src))
        print(f"  {name:34} -> {out.name:34} {n} colour(s) flipped")


if __name__ == "__main__":
    main()
