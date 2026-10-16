#!/usr/bin/env python3
"""optimize_gallery.py — generate WebP thumbnails for the gallery photos.

What it does
------------
1. Scans assets/img/gallery/ (skipping the thumbs/ output directory) for
   bitmap images and writes a WebP thumbnail into assets/img/gallery/thumbs/
   with the same basename. The long edge is capped at MAX_EDGE pixels and the
   output is encoded with quality QUALITY.
2. Rewrites assets/js/data/gallery.js so that:
     - every local photo entry gains a `thumb:` field pointing at the
       thumbnail (`src:` keeps the original full-resolution path, which the
       lightbox uses);
     - video entries whose cover is a local gallery image get their existing
       `thumb:` value repointed at the thumbnail.

Why this shape
--------------
render.js renders photos with `g.thumb || g.src` and the lightbox uses
`item.src`, so a photo without a `thumb` field simply falls back to the
original image -- no broken images, and new photos work before this script
is re-run.

Idempotent: unchanged sources are skipped, and gallery.js is only rewritten
when it actually changes.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
GALLERY_DIR = REPO_ROOT / "assets" / "img" / "gallery"
THUMB_DIR = GALLERY_DIR / "thumbs"
GALLERY_JS = REPO_ROOT / "assets" / "js" / "data" / "gallery.js"

MAX_EDGE = 1200
QUALITY = 80

SRC_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

# Preferred thumbnail format. WebP is ~30% smaller than JPEG at equivalent
# quality, so use the reference `cwebp` encoder when it is installed; fall
# back to plain JPEG so the script keeps working on machines without it.
THUMB_EXT, THUMB_MIME = ("webp", "image/webp") if shutil.which("cwebp") else ("jpg", "image/jpeg")

# A photo entry inside gallery.js, e.g.
#   { type: "photo", category: "Research", date: "...", source: "local",
#     src: "assets/img/gallery/X.jpg", caption: "..." },
PHOTO_ENTRY_RE = re.compile(r'(\{\s*type:\s*"photo"\s*,)(.*?)(\})', re.DOTALL)
LOCAL_SRC_RE = re.compile(r'src:\s*"(assets/img/gallery/([^"]+))"')
ANY_THUMB_RE = re.compile(r'thumb:\s*"(assets/img/gallery/[^"]+)"')


def thumb_rel_for(filename: str) -> str:
    """assets/img/gallery/<name>.<ext> -> assets/img/gallery/thumbs/<name>.<THUMB_EXT>"""
    stem = Path(filename).stem
    return f"assets/img/gallery/thumbs/{stem}.{THUMB_EXT}"


def make_thumb(src: Path, dest: Path) -> tuple[int, int]:
    """Write dest (thumbnail, long edge capped). Returns (src_bytes, dest_bytes)."""
    with Image.open(src) as im:
        im = im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im
        w, h = im.size
        scale = min(1.0, MAX_EDGE / float(max(w, h)))
        if scale < 1.0:
            im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))),
                           Image.LANCZOS)
        THUMB_DIR.mkdir(parents=True, exist_ok=True)
        if THUMB_EXT == "webp":
            # cwebp needs an intermediate file (it does not read stdin)
            tmp = dest.with_suffix(".tmp.png")
            im.save(tmp, "PNG")
            subprocess.run(
                ["cwebp", "-quiet", "-q", str(QUALITY), "-mt",
                 str(tmp), "-o", str(dest)],
                check=True,
            )
            tmp.unlink(missing_ok=True)
        else:
            im.save(dest, "JPEG", quality=QUALITY, optimize=True,
                    progressive=True)
    return src.stat().st_size, dest.stat().st_size


def process_images() -> dict[str, str]:
    """Generate thumbnails. Returns {original_rel_path: thumb_rel_path}."""
    mapping: dict[str, str] = {}
    src_before = 0
    thumb_after = 0
    made = skipped = 0

    for path in sorted(GALLERY_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SRC_EXTS:
            continue
        rel = f"assets/img/gallery/{path.name}"
        thumb_rel = thumb_rel_for(path.name)
        thumb_path = REPO_ROOT / thumb_rel

        if thumb_path.exists() and thumb_path.stat().st_mtime >= path.stat().st_mtime:
            skipped += 1
            mapping[rel] = thumb_rel
            continue

        s, d = make_thumb(path, thumb_path)
        src_before += s
        thumb_after += d
        made += 1
        with Image.open(thumb_path) as im:
            tw, th = im.size
        print(f"[ok] {path.name}: {s/1048576:.2f}MB -> {d/1024:.0f}KB "
              f"({tw}x{th})")
        mapping[rel] = thumb_rel

    if skipped:
        print(f"[skip] {skipped} thumbnail(s) already up to date")
    if made:
        print(f"[sum] {made} thumbnail(s): {src_before/1048576:.2f}MB -> "
              f"{thumb_after/1048576:.2f}MB "
              f"({100 - thumb_after*100/max(src_before,1):.1f}% smaller)")
    return mapping


def update_gallery_js(mapping: dict[str, str]) -> int:
    """Add/update `thumb:` fields in gallery.js. Returns number of edits."""
    if not GALLERY_JS.exists():
        print(f"[warn] {GALLERY_JS} not found, skipped")
        return 0

    text = GALLERY_JS.read_text(encoding="utf-8")
    edits = 0

    def fix_entry(m: re.Match) -> str:
        nonlocal edits
        head, body, tail = m.group(1), m.group(2), m.group(3)
        src_m = LOCAL_SRC_RE.search(body)
        if not src_m:
            return m.group(0)
        rel_src = src_m.group(1)
        thumb_rel = mapping.get(rel_src)
        if not thumb_rel:
            return m.group(0)
        if re.search(r'thumb:\s*"', body):
            # already has a thumb field: repoint it if it still points at the source
            new_body = ANY_THUMB_RE.sub(lambda t: f'thumb: "{thumb_rel}"', body, count=1)
            if new_body != body:
                edits += 1
            return head + new_body + tail
        new_body = " " + f'thumb: "{thumb_rel}",' + body
        edits += 1
        return head + new_body + tail

    new_text = PHOTO_ENTRY_RE.sub(fix_entry, text)

    # Video entries whose cover lives in assets/img/gallery/
    def fix_video_thumb(m: re.Match) -> str:
        nonlocal edits
        current = m.group(1)
        thumb_rel = mapping.get(current)
        if not thumb_rel:
            return m.group(0)
        edits += 1
        return f'thumb: "{thumb_rel}"'

    new_text = ANY_THUMB_RE.sub(fix_video_thumb, new_text)

    if new_text != text:
        GALLERY_JS.write_text(new_text, encoding="utf-8")
        print(f"[ok] updated {GALLERY_JS.relative_to(REPO_ROOT)} ({edits} thumb field(s))")
    else:
        print("[skip] gallery.js already up to date")
    return edits


def main() -> int:
    if not GALLERY_DIR.exists():
        print(f"[ERROR] gallery directory not found: {GALLERY_DIR}")
        return 1
    print(f"[info] thumbnail format: {THUMB_EXT} ({THUMB_MIME}), "
          f"max edge {MAX_EDGE}px, quality {QUALITY}")
    mapping = process_images()
    update_gallery_js(mapping)
    return 0


if __name__ == "__main__":
    sys.exit(main())
