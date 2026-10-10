#!/usr/bin/env python3
"""
Add or replace a lab member's portrait.

    python3 scripts/add-photo.py "Mona Moghadampanah" ~/Downloads/mona.jpg

The script crops the picture to a square (keeping the top of the frame, where
the face usually is), resizes it to at most 600 x 600, saves it as
assets/people/<slug>.jpg and sets the member's "photo" field in
data/people.json. Any common format works as input: JPEG, PNG, HEIC (with
pillow-heif installed) or WebP.

Requires Pillow:  python3 -m pip install --user Pillow
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
PEOPLE = ROOT / "data" / "people.json"
OUT_DIR = ROOT / "assets" / "people"
SIZE = 600


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    name, src = sys.argv[1], pathlib.Path(sys.argv[2]).expanduser()

    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("Pillow is missing. Run:  python3 -m pip install --user Pillow")
        return 1
    try:
        import pillow_heif  # optional, for iPhone HEIC photos
        pillow_heif.register_heif_opener()
    except ImportError:
        pass

    people = json.loads(PEOPLE.read_text(encoding="utf-8"))
    members = [m for g in people["groups"] for m in g["members"]]
    match = [m for m in members if m["name"].lower() == name.lower()]
    if not match:
        print(f'No current member named "{name}". Names in data/people.json:')
        for m in members:
            print(f"  {m['name']}")
        return 1
    person = match[0]

    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = 0 if h > w else (h - side) // 2   # portrait: keep the head
    out = min(SIZE, side)                   # never upscale a small original
    img = img.crop((left, top, left + side, top + side)).resize(
        (out, out), Image.LANCZOS)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rel = f"assets/people/{slugify(person['name'])}.jpg"
    img.save(ROOT / rel, "JPEG", quality=85, optimize=True, progressive=True)

    person["photo"] = rel
    PEOPLE.write_text(json.dumps(people, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(f"Saved {rel} and updated data/people.json for {person['name']}.")
    print("Commit both files to publish the photo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
