#!/usr/bin/env python3
"""Trim transparent margins from the partner logo bitmaps.

Several of the supplied files are artwork floating on a much larger
transparent canvas — thales.png is 31% artwork, pierce-aerospace.png 64%.
logo_box() in build_pages.py sizes each logo from its file dimensions, so
that padding is read as part of the mark: the logo is scaled as though the
empty space were ink, and it lands on the page noticeably smaller than its
neighbours, with a ratio that is not its own.

Trimming to the alpha bounding box fixes both at once and is idempotent —
a file already tight against its artwork is left alone.

A logo drawn on a solid plate (Precision Planting's green box, Indiana
University's red square) has no transparency, so getbbox() returns the whole
canvas and the file is untouched. That is correct: the plate is the mark.

    python3 tools/trim_logos.py          # report only
    python3 tools/trim_logos.py --write  # trim in place
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "img" / "partners"

# Leave a hair of margin so nothing sits hard against the edge of its box.
PAD_FRACTION = 0.01


def trim(path, write):
    im = Image.open(path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    bbox = im.getbbox()
    if not bbox:
        return f"{path.name}: fully transparent, skipped"

    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    fill = (tw * th) / (im.width * im.height)

    pad = max(1, round(max(tw, th) * PAD_FRACTION))
    box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
           min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))

    # Idempotence has to be judged on the crop box, not on how much ink the
    # canvas holds: the pad put back above means a trimmed file never reaches
    # a "full enough" threshold, so a fill test would rewrite it every run.
    if box == (0, 0, im.width, im.height):
        return None

    out = im.crop(box)

    before = f"{im.width}x{im.height} ({im.width / im.height:.2f})"
    after = f"{out.width}x{out.height} ({out.width / out.height:.2f})"
    if write:
        # Keep the original format; the page references these paths by name.
        out.save(path, **({"lossless": True} if path.suffix == ".webp" else {}))
    return f"{path.name:34} {fill * 100:5.1f}% ink   {before:>18} -> {after}"


def main():
    write = "--write" in sys.argv
    changed = 0
    for p in sorted(LOGOS.iterdir()):
        if p.is_dir() or p.suffix.lower() not in (".png", ".webp"):
            continue
        line = trim(p, write)
        if line:
            print(line)
            changed += 1
    print(f"\n{changed} file(s) {'trimmed' if write else 'would be trimmed'}"
          f"{'' if write else ' — re-run with --write'}")


if __name__ == "__main__":
    main()
