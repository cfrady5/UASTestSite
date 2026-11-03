#!/usr/bin/env python3
"""Crop and size the launch photographs for the home page.

The event photographs are wide frames with the speaker small in them. Dropped
in whole they would be mostly flag: the card crops to 4:5 and would take a
band across the middle of the picture, which on these is the lectern.

So each portrait is cropped here, once, to a head-and-shoulders 4:5 at a
focal point given per file, then resized and saved. Doing it at build time in
CSS is not an option — `object-position` can only slide a crop up and down,
it cannot pull a figure out of a wide frame.

    python3 tools/prepare_photos.py --list
    python3 tools/prepare_photos.py --write

Finding a focal point
---------------------
`--grid FILE` writes a copy with a labelled 10x10 overlay to the scratch
directory. Read the fraction of the way across and down that the speaker's
face sits, put it in PORTRAITS below, and re-run. `--preview` writes the
proposed crops without touching assets/, so a bad focal point costs nothing.

Source files are read from an inbox directory and never modified.
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
INBOX = ROOT / "tools" / "photo-src"
OUT_SPEAKERS = ROOT / "assets" / "img" / "speakers"
OUT_IMG = ROOT / "assets" / "img"

PORTRAIT_RATIO = 4 / 5
PORTRAIT_W = 640          # 2x the card's widest rendered portrait
WIDE_W = 1600
JPEG_Q = 82

# source filename -> (output name, focal x, focal y)
#
# The focal point is the centre of the speaker's FACE as a fraction of the
# source frame. The crop is built around it and then nudged to stay inside
# the image, so a face near an edge still yields a full-size crop.
#
# These are placeholders until the photographs are on disk — run --grid on
# each file and replace them. A wrong focal point crops someone's head off,
# so do not guess them.
PORTRAITS = {
    "kossack.jpg":   ("andrew-kossack.jpg", 0.50, 0.42),
    "young.jpg":     ("todd-young.jpg",     0.50, 0.42),
    "frazier.jpg":   ("mitch-frazier.jpg",  0.50, 0.42),
    "braun.jpg":     ("mike-braun.jpg",     0.50, 0.42),
}

# Wide photographs, which keep their framing and are only resized.
WIDES = {
    "team.jpg": "launch-ribbon-cutting.jpg",
}

# The crop is taken this many face-heights tall. A portrait wants more than
# the head: shoulders and a little air above read as a portrait, a tight
# head crop reads as a passport photo.
FRAME_HEIGHT_FRACTION = 0.55   # of the source height


def find(name):
    p = INBOX / name
    return p if p.exists() else None


def crop_portrait(im, fx, fy):
    """A 4:5 box around (fx, fy), clamped inside the frame."""
    h = int(im.height * FRAME_HEIGHT_FRACTION)
    w = int(h * PORTRAIT_RATIO)
    if w > im.width:                       # narrow source: fit to width
        w, h = im.width, int(im.width / PORTRAIT_RATIO)

    cx, cy = im.width * fx, im.height * fy
    # Sit the face in the upper third rather than dead centre — that is where
    # a face belongs in a portrait, and it leaves room for the shoulders.
    left = int(cx - w / 2)
    top = int(cy - h * 0.33)
    left = max(0, min(left, im.width - w))
    top = max(0, min(top, im.height - h))
    return im.crop((left, top, left + w, top + h))


def save(im, path, width):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im = im.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
    return im.size, path.stat().st_size


def write_grid(name):
    src = find(name)
    if not src:
        sys.exit(f"{name} is not in {INBOX}")
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    for i in range(1, 10):
        x, y = im.width * i / 10, im.height * i / 10
        d.line([(x, 0), (x, im.height)], fill=(255, 0, 0), width=2)
        d.line([(0, y), (im.width, y)], fill=(255, 0, 0), width=2)
        d.text((x + 4, 4), f".{i}", fill=(255, 0, 0))
        d.text((4, y + 4), f".{i}", fill=(255, 0, 0))
    out = pathlib.Path("/tmp") / f"grid-{name}"
    im.save(out)
    print(f"wrote {out} — read the face's position off the labelled lines")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="save into assets/")
    ap.add_argument("--preview", action="store_true", help="save to /tmp instead")
    ap.add_argument("--grid", metavar="FILE", help="write a labelled overlay for one file")
    ap.add_argument("--list", action="store_true", help="show what is in the inbox")
    a = ap.parse_args()

    if a.grid:
        return write_grid(a.grid)

    INBOX.mkdir(parents=True, exist_ok=True)
    have = sorted(p.name for p in INBOX.iterdir() if p.is_file())
    if a.list or not (a.write or a.preview):
        print(f"inbox: {INBOX}")
        for n in have or ["(empty)"]:
            print(f"  {n}")
        print("\nexpected:", ", ".join(list(PORTRAITS) + list(WIDES)))
        print("\nnothing written — pass --preview or --write")
        return

    dest_dir = pathlib.Path("/tmp/photo-preview") if a.preview else None

    for src_name, (out_name, fx, fy) in PORTRAITS.items():
        src = find(src_name)
        if not src:
            print(f"  {src_name:16} not in the inbox, skipped")
            continue
        im = Image.open(src)
        out = (dest_dir / out_name) if dest_dir else (OUT_SPEAKERS / out_name)
        size, nbytes = save(crop_portrait(im, fx, fy), out, PORTRAIT_W)
        print(f"  {src_name:16} {str(im.size):14} -> {out_name:22} "
              f"{size[0]}x{size[1]}  {nbytes // 1024} KB")

    for src_name, out_name in WIDES.items():
        src = find(src_name)
        if not src:
            print(f"  {src_name:16} not in the inbox, skipped")
            continue
        im = Image.open(src)
        out = (dest_dir / out_name) if dest_dir else (OUT_IMG / out_name)
        size, nbytes = save(im, out, WIDE_W)
        print(f"  {src_name:16} {str(im.size):14} -> {out_name:22} "
              f"{size[0]}x{size[1]}  {nbytes // 1024} KB")

    if dest_dir:
        print(f"\npreview only — written to {dest_dir}, assets/ untouched")


if __name__ == "__main__":
    main()
