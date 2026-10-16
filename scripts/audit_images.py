#!/usr/bin/env python3
"""Audit which images the site actually references, with sizes and pixel dims.
Also lists unreferenced (orphan) images under assets/img."""
import os, re, pathlib
from PIL import Image

ROOT = pathlib.Path("/Users/Jack/Documents/GitHub/jianwu-atlas-private")
SKIP_DIRS = {"private-notes", ".git", ".wrangler", "__pycache__", "pdfjs"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
Image.MAX_IMAGE_PIXELS = None


def iter_files(base):
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            yield pathlib.Path(dp) / fn


# 1) collect referenced images from static html + data js + templates
# NOTE: allow spaces inside the path (Chinese filenames often contain them);
# only stop at a delimiter that cannot appear inside an HTML/JS attribute.
refs = set()
pat = re.compile(r'assets/img/[^"\'<>]+?\.(?:png|jpe?g|webp|gif|svg)')
for p in iter_files(ROOT):
    if p.suffix in (".html", ".js", ".css"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in pat.finditer(txt):
            refs.add(m.group(0).strip())

rows = []
for r in sorted(refs):
    fp = ROOT / r
    if not fp.is_file():
        rows.append((0, 0, 0, "MISSING", r))
        continue
    size = int(fp.stat().st_size)
    try:
        with Image.open(fp) as im:
            w, h = int(im.size[0]), int(im.size[1])
    except Exception:
        w, h = 0, 0
    rows.append((size, w, h, "", r))

rows.sort(key=lambda x: -x[0])
print("referenced images:", len(rows))
print("%9s %13s  %s" % ("size", "pixels", "path"))
for size, w, h, flag, r in rows:
    px = "%dx%d" % (w, h) if w else (flag or "?")
    mark = ""
    if size > 2_000_000:
        mark = "   <== >2MB"
    elif size > 500_000:
        mark = "   <== >500KB"
    print("%8.2fM %13s  %s%s" % (size / 1048576.0, px, r, mark))
print("referenced total: %.1f MB" % (sum(r[0] for r in rows) / 1048576.0))

# 2) orphans under assets/img
allimg = []
for p in iter_files(ROOT / "assets/img"):
    if p.suffix.lower() in IMG_EXT:
        allimg.append(str(p.relative_to(ROOT)))
orph = [a for a in allimg if a not in refs]
orph.sort(key=lambda a: -int((ROOT / a).stat().st_size))
print("\nassets/img total %d images; unreferenced %d images, %.1f MB" %
      (len(allimg), len(orph), sum(int((ROOT / a).stat().st_size) for a in orph) / 1048576.0))
for a in orph[:15]:
    print("  %7.2f MB  %s" % (int((ROOT / a).stat().st_size) / 1048576.0, a))
