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

# The card shows the speaker at the lectern as a band under the quote, so the
# crop is landscape. That also suits the sources, which are 3:2 frames — a 4:5
# portrait crop would have thrown most of each one away and, on the one small
# file here, left nothing worth enlarging.
PORTRAIT_RATIO = 3 / 2
PORTRAIT_W = 1040         # 2x the card's rendered width at the widest layout
WIDE_W = 1600
JPEG_Q = 82

# source filename -> (output name, focal x, focal y, crop width as a fraction
# of the source width)
#
# The focal point is the centre of the speaker's FACE in the source frame, read
# off `--grid`. The crop is built around it and then nudged to stay inside the
# image, so a face near an edge still yields a full-size crop. The width sets
# how close the shot is: smaller is tighter.
#
# Do not guess these. A wrong focal point crops someone's head off.
PORTRAITS = {
    # 800x827 and the subject is small in it, so this one takes the whole
    # frame and still enlarges slightly. It is the only low-resolution source
    # here; a bigger original would be worth asking for.
    "kossack.jpg":   ("andrew-kossack.jpg", 0.50, 0.68, 0.72),
    "young.jpg":     ("todd-young.jpg",     0.60, 0.72, 0.66),
    "frazier.jpg":   ("mitch-frazier.jpg",  0.43, 0.59, 0.44),
    "braun.jpg":     ("mike-braun.jpg",     0.47, 0.29, 0.44),
}

# Wide photographs, which keep their framing and are only resized.
WIDES = {
    "team.jpg": "launch-ribbon-cutting.jpg",
}

# Where the face sits in the finished crop, measured from the top.
FACE_FROM_TOP = 0.34


def find(name):
    p = INBOX / name
    return p if p.exists() else None


def crop_portrait(im, fx, fy, wfrac):
    """A 3:2 box around (fx, fy), clamped inside the frame."""
    w = int(im.width * wfrac)
    h = int(w / PORTRAIT_RATIO)
    if h > im.height:                      # wide source: fit to height
        h, w = im.height, int(im.height * PORTRAIT_RATIO)

    cx, cy = im.width * fx, im.height * fy
    # The face sits a third of the way down, which leaves the lectern and the
    # speaker's hands in frame. Centring it vertically crops the head.
    left = int(cx - w / 2)
    top = int(cy - h * FACE_FROM_TOP)
    left = max(0, min(left, im.width - w))
    top = max(0, min(top, im.height - h))
    return im.crop((left, top, left + w, top + h))


def save(im, path, width):
    # Only ever downscale. Enlarging past the source invents detail that is
    # not there and costs bytes to carry it; a small file is better served
    # small and left to the browser than blown up here.
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

    for src_name, (out_name, fx, fy, wfrac) in PORTRAITS.items():
        src = find(src_name)
        if not src:
            print(f"  {src_name:16} not in the inbox, skipped")
            continue
        im = Image.open(src)
        cropped = crop_portrait(im, fx, fy, wfrac)
        out = (dest_dir / out_name) if dest_dir else (OUT_SPEAKERS / out_name)
        size, nbytes = save(cropped, out, PORTRAIT_W)
        scale = size[0] / cropped.width
        warn = "  ENLARGED, will be soft" if scale > 1.02 else ""
        print(f"  {src_name:16} {str(im.size):14} -> {out_name:22} "
              f"crop {cropped.width}x{cropped.height} -> {size[0]}x{size[1]}  "
              f"{nbytes // 1024} KB{warn}")

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
