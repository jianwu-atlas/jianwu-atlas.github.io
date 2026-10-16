#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tutorials.py
===================================================================
Tutorials & Podcast Build Pipeline

NOTE: This file uses English-only comments/docstrings intentionally.
Previous versions with large blocks of Chinese comments repeatedly
suffered from UTF-8 byte corruption ("invalid continuation byte")
during heredoc paste operations in the local terminal. Since the file
content is now pure ASCII, this entire class of encoding bugs is
structurally impossible going forward.

What this script does:
  1. Scan all Markdown source files (with YAML front matter) under
     tutorials-src/
  2. Render each Markdown file into a standalone static HTML page
     -> tutorials/{slug}.html
  3. Fully rebuild (not append) assets/js/data/tutorials.js
     -- avoids the historical "appending text causes missing comma" bug
  4. Automatically clean up orphan HTML files (when a source .md file
     is renamed/deleted/marked draft, the old html is removed)

v3 -> v4 change log:

  [FIX-1] Cascading-delete safety valve:
      If tutorials-src/ is unexpectedly empty (wrong path / all files
      marked draft / directory accidentally emptied), valid_slugs would
      be an empty set. In that case cleanup_orphan_html() must NOT treat
      every already-published page under tutorials/ as an "orphan" and
      wipe them all out. When this abnormal situation is detected, the
      cleanup step is skipped and a loud warning is printed instead of
      silently deleting everything.

  [FIX-2] A single bad file no longer breaks the entire build:
      The old parse_front_matter() called sys.exit() on any front-matter
      error, which meant "one file has a typo in its front matter" would
      immediately terminate the whole process, preventing all subsequent
      files (including the cleanup step) from running. The new version
      raises ValueError instead, which is caught by the caller; the
      error is logged, that one file is skipped, and the build continues
      with the remaining files, with all errors summarized at the end.

  [FIX-3] Precise ordering for multiple tutorials published on the same day:
      For each article we compute an internal-only sort timestamp
      meta["_sort_dt"], with priority:
        1. Manually specified "order" in front matter (integer, higher = earlier)
        2. Manually specified "time" in front matter (e.g. "14:30" / "14:30:00")
        3. The file's most recent git commit timestamp (auto-detected)
        4. Filesystem mtime (fallback when git is unavailable)
        5. Final fallback: midnight (00:00:00) of the "date" field
      The public-facing "date": "YYYY-MM-DD" field is still exposed as
      before for page display; the precise sort timestamp is used only
      internally during the build and is never written into tutorials.js.

  [FIX-4] get_git_first_commit_time() -> get_git_latest_commit_time():
      The old version used `git log --diff-filter=A` (only the commit
      that first added the file), which caused files that were `git add`-ed
      long ago but only finished/pushed today to sort AFTER files created
      today -- because their "first commit time" predates the newer file's
      first commit time, even though their "most recent edit" is actually
      later. The new version uses `git log -1` (no --diff-filter) to get
      the file's most recent commit timestamp in git history, so the
      semantics become "whoever was edited/pushed last sorts first",
      matching the everyday "write it, then publish it" workflow intuition.

Dependencies:
  pip install pyyaml markdown
  (On macOS Homebrew Python, if you hit an
   "externally-managed-environment" error, run:
    pip3 install --break-system-packages --user pyyaml markdown)

Optional front matter fields usage example:
  ---
  title: "..."
  date: 2026-08-06
  order: 3          # optional: higher number sorts earlier (same-day only)
  # or:
  time: "14:30"     # optional: precise publish time (minute/second)
  ---
  If neither is set, the script automatically falls back to the file's
  most recent git commit time / filesystem mtime for ordering, with no
  manual maintenance required.

  # Optional bilingual card text. Tutorials are Chinese-primary; provide
  # these ONLY if you also want an English title/summary on the list
  # card when the site is switched to EN. Omit them to keep showing the
  # Chinese text. This avoids maintaining two files per tutorial.
  title_en: "..."
  summary_en: "..."
===================================================================
"""

from __future__ import annotations

import re
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import date, datetime, timezone
from email.utils import format_datetime
from typing import Any, Optional

import yaml
import markdown as md_lib


# ------------------------------------------------------------------
# 1. Path configuration
# ------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent  # parent of scripts/ = repo root

TUTORIALS_SRC_DIR   = REPO_ROOT / "tutorials-src"
TUTORIALS_OUT_DIR   = REPO_ROOT / "tutorials"
TUTORIALS_JS_PATH   = REPO_ROOT / "assets" / "js" / "data" / "tutorials.js"
TUTORIAL_TEMPLATE   = REPO_ROOT / "assets" / "templates" / "tutorial_template.html"

REQUIRED_FIELDS = ["title", "date", "summary", "type"]
DEFAULT_TYPE    = "tutorial"

# Default card cover for articles that omit the `cover:` field entirely.
# Points at the new 吴坚.png-based lockup so newly created tutorials get the
# current logo automatically; older articles keep their explicit (legacy) cover.
DEFAULT_COVER   = "https://jianwu-atlas.github.io/assets/img/logos/wu_jian_lockup.png"

# Base URL of THIS deployment, used when generating sitemap.xml and feed.xml.
# The private repo is served from Cloudflare Workers, the public repo from
# GitHub Pages, so each repo carries its own value.
SITE_BASE_URL   = "https://jianwu-atlas.github.io"

# Top-level pages emitted into sitemap.xml, with SEO hints.
# Keep this list in sync with the .html files at the repository root.
TOP_LEVEL_PAGES = [
    ("index.html",        "1.0",  "weekly"),
    ("news.html",         "0.9",  "weekly"),
    ("publications.html", "0.8",  "monthly"),
    ("experience.html",   "0.7",  "monthly"),
    ("conferences.html",  "0.6",  "monthly"),
    ("expertise.html",    "0.6",  "monthly"),
    ("tutorials.html",    "0.6",  "monthly"),
    ("gallery.html",      "0.5",  "monthly"),
    ("contact.html",      "0.4",  "yearly"),
]


# ------------------------------------------------------------------
# 2. Front matter parsing
#    [FIX-2] sys.exit() replaced with raise ValueError, caught upstream
# ------------------------------------------------------------------
FRONT_MATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?\n)---\s*\n(.*)$", re.DOTALL
)


def parse_front_matter(raw_text: str, filename: str) -> tuple[dict, str]:
    """
    Parse the YAML front matter block at the top of a Markdown file.

    Returns:
        meta  - dict, the parsed front matter metadata
        body  - str, the Markdown body text after the front matter block

    Raises:
        ValueError - raised when front matter is missing / has YAML
                     syntax errors / is missing required fields. Caught
                     by the caller (build_all_tutorials), which skips
                     that file instead of crashing the whole process.
    """
    match = FRONT_MATTER_PATTERN.match(raw_text)
    if not match:
        raise ValueError(
            "Missing YAML front matter (must start and end with '---'). Example:\n"
            "---\n"
            'title: "Ep.02 - Trajectory Analysis"\n'
            "date: 2025-11-20\n"
            'summary: "..."\n'
            "type: tutorial\n"
            'tags: ["Monocle2", "R"]\n'
            "---"
        )

    yaml_block, body = match.group(1), match.group(2)

    try:
        meta = yaml.safe_load(yaml_block) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse front matter YAML: {e}")

    missing = [f for f in REQUIRED_FIELDS if f not in meta or meta[f] in (None, "")]
    if missing:
        raise ValueError(
            f"Front matter is missing required fields: {missing} "
            f"(required fields: {REQUIRED_FIELDS})"
        )

    # Normalize date to a "YYYY-MM-DD" string
    # (YAML may auto-parse it into a datetime.date object)
    if isinstance(meta["date"], (date, datetime)):
        meta["date"] = meta["date"].strftime("%Y-%m-%d")

    # If "order" is present, coerce to int; on bad format, warn and drop
    # the field instead of erroring out
    if "order" in meta:
        try:
            meta["order"] = int(meta["order"])
        except (TypeError, ValueError):
            print(f"[warn] '{filename}' has an order field that could not be "
                  f"converted to an integer, ignoring it: {meta['order']!r}")
            meta.pop("order", None)

    # If "time" is present, coerce to string
    # (YAML may parse "14:30" into an unexpected type)
    if "time" in meta and meta["time"] is not None:
        meta["time"] = str(meta["time"])

    meta.setdefault("tags", [])
    meta.setdefault("type", DEFAULT_TYPE)
    meta.setdefault("cover", DEFAULT_COVER)
    meta.setdefault("draft", False)

    # Optional bilingual overrides for the tutorial card (EN mode shows
    # these when present, otherwise falls back to the Chinese base text)
    meta.setdefault("title_en", "")
    meta.setdefault("summary_en", "")

    return meta, body.strip()


# ------------------------------------------------------------------
# 3. Markdown -> HTML body rendering
# ------------------------------------------------------------------
def render_markdown_body(md_text: str) -> str:
    """
    Convert the Markdown body into HTML using python-markdown.
    Common extensions (fenced_code / tables / toc) are enabled for
    convenient technical-tutorial formatting.
    """
    return md_lib.markdown(
        md_text,
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            "sane_lists",
            "codehilite",
        ],
        extension_configs={
            "codehilite": {"guess_lang": False}
        },
    )


# ------------------------------------------------------------------
# 4. Render a single tutorial's static HTML page
# ------------------------------------------------------------------
IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HAS_LOADING_RE = re.compile(r"""\bloading\s*=""", re.IGNORECASE)


def add_img_lazy_loading(html: str) -> str:
    """Add loading="lazy" decoding="async" to every <img> inside the rendered
    Markdown body.

    Article-body images are always below the fold (the nav/hero template
    images are handled separately in assets/templates), so lazy-loading them
    is a pure win. Idempotent: tags that already declare a loading attribute
    are left untouched.
    """
    def repl(m):
        tag = m.group(0)
        if HAS_LOADING_RE.search(tag):
            return tag
        return tag[:-1].rstrip() + ' loading="lazy" decoding="async">'

    return IMG_TAG_RE.sub(repl, html)


def render_tutorial_page(meta: dict, html_body: str) -> str:
    """
    Load the tutorial_template.html template and perform simple
    {{placeholder}} substitution.
    """
    if not TUTORIAL_TEMPLATE.exists():
        sys.exit(f"[ERROR] Template file not found: {TUTORIAL_TEMPLATE}")

    template = TUTORIAL_TEMPLATE.read_text(encoding="utf-8")

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in meta["tags"])

    replacements = {
        "{{TITLE}}":        meta["title"],
        "{{TITLE_EN}}":     meta.get("title_en", ""),
        "{{DATE}}":         meta["date"],
        "{{SUMMARY}}":      meta["summary"],
        "{{SUMMARY_EN}}":   meta.get("summary_en", ""),
        "{{TYPE}}":         meta["type"],
        "{{TAGS_HTML}}":    tags_html,
        "{{CONTENT}}":      add_img_lazy_loading(html_body),
        "{{COVER}}":        meta.get("cover", ""),
    }

    page_html = template
    for placeholder, value in replacements.items():
        page_html = page_html.replace(placeholder, value)

    return page_html


# ------------------------------------------------------------------
# 4.5 Compute the precise sort timestamp
# ------------------------------------------------------------------
def get_git_latest_commit_time(md_path: Path) -> Optional[datetime]:
    """
    [FIX-4] Get the timestamp of the most recent git commit touching
    this file.

    Core difference from the old get_git_first_commit_time():
      - The old version used --diff-filter=A, which only cares about the
        very first time the file was added to the repo, i.e. "when was
        this article created".
      - The new version drops the diff-filter and uses `git log -1` to
        get the timestamp of the most recent commit touching this file,
        i.e. "when was this article last edited/pushed".

    This change fixes the case where a draft was `git add`-ed long ago
    but only finished and pushed today: because its "first commit time"
    is very old, it used to sort AFTER files created today, even though
    it was actually edited more recently. Sorting by "most recent commit
    time" puts whatever was edited last at the front, matching the
    intuition that "publish order = actual action order".

    Returns None when: not inside a git repo / git is not installed /
    the file has no commit history yet (e.g. just created, not yet
    `git add`-ed + committed -- in that case the caller falls back to
    filesystem mtime).
    """
    if not shutil.which("git"):
        return None

    try:
        result = subprocess.run(
            [
                "git", "log",
                "-1",                # only the most recent commit record
                "--follow",           # follow the file across renames
                "--format=%aI",       # author date, ISO 8601 with timezone
                "--",
                str(md_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None

    iso_str = result.stdout.strip()
    if not iso_str:
        return None

    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return None

    # Convert to a naive local datetime so it can be safely compared
    # against the other naive-datetime fallback paths below.
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt


def compute_sort_datetime(meta: dict, md_path: Path) -> datetime:
    """
    Compute the precise sort timestamp, in order of priority
    (highest first):
      1. Manually specified "order" (integer) in front matter --
         mapped onto a virtual time-of-day within the same date;
         higher values sort earlier (more "recent").
      2. Manually specified "time" string ("HH:MM" or "HH:MM:SS").
      3. [FIX-4] The file's most recent git commit timestamp
         (automatic, no manual upkeep needed; means "last edited/pushed").
      4. Filesystem mtime (fallback when git is unavailable).
      5. Final fallback: midnight (00:00:00) of the "date" field.
    """
    date_str = meta["date"]
    base_date = datetime.strptime(date_str, "%Y-%m-%d")

    # 1) Manual order: map 0-86399 onto "seconds within the day";
    #    higher value = later in the day = sorts earlier (newer)
    order = meta.get("order")
    if isinstance(order, int):
        seconds = max(0, min(order, 86399))
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return base_date.replace(hour=h, minute=m, second=s)

    # 2) Manual time string
    time_str = meta.get("time")
    if time_str:
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                t = datetime.strptime(time_str, fmt)
                return base_date.replace(hour=t.hour, minute=t.minute, second=t.second)
            except ValueError:
                continue
        print(f"[warn] Could not parse time field, ignoring it: {time_str!r} "
              f"(expected 'HH:MM' or 'HH:MM:SS')")

    # 3) [FIX-4] Automatically fetch the most recent git commit time
    #    (no longer the first-commit time)
    git_dt = get_git_latest_commit_time(md_path)
    if git_dt is not None:
        return git_dt

    # 4) Filesystem mtime fallback
    try:
        return datetime.fromtimestamp(md_path.stat().st_mtime)
    except OSError:
        pass

    # 5) Final fallback: midnight of the date field
    return base_date


# ------------------------------------------------------------------
# 5. Scan all Markdown source files, build metadata list + output HTML pages
#    [FIX-2] A single-file parse failure is logged and skipped, no longer
#            terminates the whole build
#    [FIX-3] Additionally computes meta["_sort_dt"] for precise ordering
# ------------------------------------------------------------------
def build_all_tutorials() -> tuple[list[dict], list[str]]:
    """
    Iterate over tutorials-src/*.md:
      - Parse front matter (on failure, log the error, skip the file,
        continue with the rest)
      - Skip files starting with an underscore "_" (convention for
        templates/drafts that should never be published)
      - Skip files with draft: true
      - Render the body to HTML and write it to tutorials/{slug}.html
      - Compute the precise sort timestamp meta["_sort_dt"]
      - Collect each article's metadata (with slug, url) for rebuilding
        tutorials.js afterwards

    Returns:
      (all_meta, errors)
        all_meta - metadata list sorted by _sort_dt descending
                   (most recent first)
        errors   - all error messages encountered during this build
                   (filename: reason)
    """
    if not TUTORIALS_SRC_DIR.exists():
        sys.exit(f"[ERROR] Source directory does not exist: {TUTORIALS_SRC_DIR}")

    TUTORIALS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(TUTORIALS_SRC_DIR.glob("*.md"))

    # Skip files starting with an underscore
    # (convention: templates/drafts, not for publishing)
    skipped_template_files = [f for f in md_files if f.stem.startswith("_")]
    md_files = [f for f in md_files if not f.stem.startswith("_")]
    for f in skipped_template_files:
        print(f"[skip] '{f.name}' starts with an underscore, "
              f"treated as a template file, skipping publication.")

    if not md_files:
        print(f"[warn] No .md files found under '{TUTORIALS_SRC_DIR}', "
              f"skipping build.")
        return [], []

    all_meta: list[dict] = []
    seen_slugs: set[str] = set()
    errors: list[str] = []  # [FIX-2] collect errors instead of exiting immediately

    for md_path in md_files:
        slug = md_path.stem

        raw_text = md_path.read_text(encoding="utf-8")

        # [FIX-2] Catch per-file parsing exceptions and continue with
        # the remaining files
        try:
            meta, body = parse_front_matter(raw_text, md_path.name)
        except ValueError as e:
            errors.append(f"{md_path.name}: {e}")
            print(f"[ERROR] '{md_path.name}' failed to parse, skipping: {e}")
            continue

        if meta.get("draft"):
            print(f"[skip] '{md_path.name}' is marked as draft, "
                  f"skipping publication.")
            continue

        if slug in seen_slugs:
            errors.append(f"{md_path.name}: duplicate slug '{slug}'")
            print(f"[ERROR] '{md_path.name}' has a duplicate slug: "
                  f"'{slug}', skipping.")
            continue
        seen_slugs.add(slug)

        try:
            html_body = render_markdown_body(body)
            page_html = render_tutorial_page(meta, html_body)
        except Exception as e:
            errors.append(f"{md_path.name}: rendering failed - {e}")
            print(f"[ERROR] '{md_path.name}' failed to render, skipping: {e}")
            continue

        out_path = TUTORIALS_OUT_DIR / f"{slug}.html"
        out_path.write_text(page_html, encoding="utf-8")
        print(f"[ok]  Generated page: {out_path.relative_to(REPO_ROOT)}")

        # Compute the precise sort timestamp (not written into
        # tutorials.js, used internally for sorting only)
        meta["_sort_dt"] = compute_sort_datetime(meta, md_path)

        meta["slug"] = slug
        meta["url"] = f"tutorials/{slug}.html"
        all_meta.append(meta)

    # Sort key: meta["_sort_dt"] (second-level precision); within the
    # same day, order follows "most recent commit time"
    all_meta.sort(key=lambda m: m["_sort_dt"], reverse=True)
    return all_meta, errors


# ------------------------------------------------------------------
# 5.5 Clean up orphan HTML files
# ------------------------------------------------------------------
def cleanup_orphan_html(valid_slugs: set[str]) -> None:
    """
    Remove "orphan" HTML files from the tutorials/ output directory --
    i.e. .html files whose stem is not in this build's valid_slugs set.

    Safety measures:
      - Only scans the top level of TUTORIALS_OUT_DIR
        (does not recurse into subdirectories)
      - Only removes files whose stem is NOT in valid_slugs
      - Every deletion is logged, nothing is removed silently

    The caller (main) is responsible for checking, via the [FIX-1]
    safety valve, whether valid_slugs is unexpectedly empty before
    calling this function, to avoid an accidental mass deletion.
    """
    if not TUTORIALS_OUT_DIR.exists():
        return

    existing_html = sorted(TUTORIALS_OUT_DIR.glob("*.html"))
    removed = []

    for html_path in existing_html:
        if html_path.stem not in valid_slugs:
            html_path.unlink()
            removed.append(html_path.name)

    if removed:
        print(f"[clean] Removed {len(removed)} orphan HTML file(s) "
              f"(source .md was renamed/deleted/marked draft):")
        for name in removed:
            print(f"   - {name}")
    else:
        print("[clean] No orphan HTML files found, output directory is up to date.")


# ------------------------------------------------------------------
# 6. Fully rebuild tutorials.js
# ------------------------------------------------------------------
def format_js_entry(meta: dict) -> str:
    """
    Format a single metadata dict into one JS object literal for
    tutorials.js. Uses json.dumps for string escaping, avoiding
    hand-rolled string concatenation escaping bugs.

    Note: meta may still carry internal fields such as
    _sort_dt / order / time / slug -- only the fields actually needed
    on the frontend are explicitly picked here, so internal fields
    never leak into the public JS file.
    """
    tags_js = json.dumps(meta["tags"], ensure_ascii=False)

    # Optional English overrides for the list card. When present, the
    # frontend (render.js: pickEn) shows them in EN mode and falls back
    # to the Chinese base text otherwise -- keeping tutorials a
    # single-source (Chinese-primary) without duplicate files.
    title_en = meta.get("title_en")
    summary_en = meta.get("summary_en")

    en_lines = ""
    if title_en:
        en_lines += f'    title_en: {json.dumps(title_en, ensure_ascii=False)},\n'
    if summary_en:
        en_lines += f'    summary_en: {json.dumps(summary_en, ensure_ascii=False)},\n'

    return (
        "  {\n"
        f'    date: {json.dumps(meta["date"])},\n'
        f'    title: {json.dumps(meta["title"], ensure_ascii=False)},\n'
        f'    summary: {json.dumps(meta["summary"], ensure_ascii=False)},\n'
        f'    url: {json.dumps(meta["url"])},\n'
        f'    cover: {json.dumps(meta.get("cover", ""))},\n'
        f'    type: {json.dumps(meta["type"])},\n'
        f"    tags: {tags_js}\n"
        f"{en_lines}"
        "  }"
    )


def build_tutorials_js(all_meta: list[dict]) -> None:
    """
    Fully regenerate the tutorials.js file content from all metadata
    and overwrite it. Commas are handled uniformly via Python's
    ",\\n".join(...), eliminating the historical "manually inserted
    text missing a comma" bug class entirely.

    The array order follows all_meta, which has already been precisely
    sorted by _sort_dt -- if the frontend render.js only compares by
    "date" (day-level precision), since JS's Array.prototype.sort() is
    a stable sort (guaranteed by ES2019+), same-day entries will retain
    the order written here, so render.js does not need to change.
    """
    entries_text = ",\n".join(format_js_entry(m) for m in all_meta)

    js_content = (
        "// This file is auto-generated by scripts/build_tutorials.py. Do not edit by hand!\n"
        "// To add/remove tutorials, edit the Markdown source files under "
        "tutorials-src/ and re-run the build script.\n"
        "\n"
        "const tutorialsData = [\n"
        f"{entries_text}\n"
        "];\n"
    )

    TUTORIALS_JS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TUTORIALS_JS_PATH.write_text(js_content, encoding="utf-8")
    print(f"[ok]  Fully rebuilt: {TUTORIALS_JS_PATH.relative_to(REPO_ROOT)} "
          f"({len(all_meta)} entries)")


# ------------------------------------------------------------------
# 7. sitemap.xml / feed.xml generation
#    Tutorial detail pages are pre-rendered HTML, so they are perfectly
#    crawlable -- but they used to be missing from sitemap.xml entirely.
#    Both files are now regenerated on every build, which keeps them in
#    sync without any manual step.
# ------------------------------------------------------------------
def _xml_escape(text: Any) -> str:
    """Minimal XML entity escaping for element text content."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _rfc822(date_str: Any) -> Optional[str]:
    """Convert 'YYYY-MM-DD' to an RFC-822 timestamp for RSS <pubDate>.
    Returns None for unparseable values (e.g. the '2026-04-XX' placeholders
    used in some tutorial titles) so the caller can omit the element."""
    try:
        dt = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
        return format_datetime(dt.replace(tzinfo=timezone.utc))
    except (ValueError, TypeError):
        return None


def write_sitemap(all_meta: list[dict]) -> None:
    """Regenerate sitemap.xml: top-level pages + every published tutorial page.
    Idempotent - running it twice produces byte-identical output."""
    urls: list[tuple[str, str, str]] = []

    for rel, priority, changefreq in TOP_LEVEL_PAGES:
        if (REPO_ROOT / rel).exists():
            urls.append((_xml_escape(f"{SITE_BASE_URL}/{rel}"), changefreq, priority))

    for m in all_meta:
        urls.append((_xml_escape(f"{SITE_BASE_URL}/{m['url']}"), "monthly", "0.5"))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        "",
    ]
    for loc, changefreq, priority in urls:
        lines += [
            "  <url>",
            f"    <loc>{loc}</loc>",
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
            "",
        ]
    lines.append("</urlset>")

    out_path = REPO_ROOT / "sitemap.xml"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok]  Regenerated sitemap.xml ({len(urls)} URLs) into "
          f"{out_path.relative_to(REPO_ROOT)}")


def write_feed(all_meta: list[dict], limit: int = 20) -> None:
    """Regenerate feed.xml (RSS 2.0) from the most recent published tutorials,
    so new episodes can be subscribed to."""
    items = all_meta[:limit]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        "  <channel>",
        "    <title>Jian Wu - Tutorials &amp; Podcast</title>",
        f"    <link>{SITE_BASE_URL}/tutorials.html</link>",
        "    <description>Latest tutorials and podcast episodes by Jian Wu "
        "(lung cell atlas, TE/ERV, aging).</description>",
        "    <language>zh-cn</language>",
        "",
    ]

    for m in items:
        link = _xml_escape(f"{SITE_BASE_URL}/{m['url']}")
        pub = _rfc822(m.get("date"))
        lines += [
            "    <item>",
            f"      <title>{_xml_escape(m['title'])}</title>",
            f"      <link>{link}</link>",
            f"      <guid isPermaLink=\"true\">{link}</guid>",
        ]
        if pub:
            lines.append(f"      <pubDate>{pub}</pubDate>")
        lines += [
            f"      <description>{_xml_escape(m.get('summary', ''))}</description>",
            "    </item>",
            "",
        ]

    lines += ["  </channel>", "</rss>"]

    out_path = REPO_ROOT / "feed.xml"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok]  Regenerated feed.xml ({len(items)} items) into "
          f"{out_path.relative_to(REPO_ROOT)}")


# ------------------------------------------------------------------
# 8. tutorials.js syntax sanity check
# ------------------------------------------------------------------
def sanity_check_js(js_path: Path) -> None:
    """
    Run a lightweight syntax sanity check right after writing the file,
    to catch problems early instead of waiting for a browser error.
    Prefers a real syntax check via `node --check`; falls back to a
    basic bracket-balance check if Node.js is not installed.
    """
    if shutil.which("node"):
        result = subprocess.run(
            ["node", "--check", str(js_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            sys.exit(
                f"[ERROR] Syntax check failed for the generated tutorials.js!\n"
                f"{result.stderr}\n"
                f"Build aborted. Check build_tutorials.py's logic or special "
                f"characters in the source Markdown content."
            )
        print("[ok]  tutorials.js passed node --check syntax validation")
    else:
        text = js_path.read_text(encoding="utf-8")
        if text.count("{") != text.count("}") or text.count("[") != text.count("]"):
            sys.exit("[ERROR] tutorials.js has mismatched brackets, "
                      "likely a syntax error. Build aborted.")
        print("[ok]  tutorials.js passed a basic bracket-balance check "
              "(install Node.js for a full syntax check)")


# ------------------------------------------------------------------
# 8. Main entry point
#    [FIX-1] Added a "cascading-delete" safety valve
#    [FIX-2] Collects per-file errors, reports them all at the end
#            (non-zero exit code as a CI warning signal, without
#            blocking successfully-built files)
#    [FIX-3][FIX-4] Prints the precise sort timestamp for each article,
#            to make it easy to verify same-day ordering matches
#            expectations
# ------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("Building Tutorials & Podcast pages...")
    print("=" * 60)

    all_meta, errors = build_all_tutorials()
    valid_slugs = {m["slug"] for m in all_meta}

    # [FIX-1] Safety valve: prevent cleanup_orphan_html() from wiping
    # out every already-published page under tutorials/ in case
    # tutorials-src/ is unexpectedly empty (wrong path / all files
    # marked draft / directory emptied / every file failed to parse
    # this run)
    existing_html_count = (
        len(list(TUTORIALS_OUT_DIR.glob("*.html"))) if TUTORIALS_OUT_DIR.exists() else 0
    )
    if not valid_slugs and existing_html_count > 0:
        print(
            f"\nSafety valve triggered: no valid tutorials were parsed this run "
            f"(valid_slugs is empty), but '{TUTORIALS_OUT_DIR}' already contains "
            f"{existing_html_count} html file(s).\n"
            f"Skipping cleanup_orphan_html() this run to avoid accidentally "
            f"deleting already-published content.\n"
            f"Please check whether the tutorials-src/ path is correct, whether "
            f"it was accidentally emptied, or whether every .md file failed to "
            f"parse / was marked draft.\n"
        )
    else:
        cleanup_orphan_html(valid_slugs)

    if not all_meta:
        print("[warn] No publishable tutorial entries found, tutorials.js was not updated.")
    else:
        build_tutorials_js(all_meta)
        sanity_check_js(TUTORIALS_JS_PATH)
        write_sitemap(all_meta)
        write_feed(all_meta)

    print("=" * 60)
    print(f"Build complete, {len(all_meta)} tutorial(s)/podcast(s) published")
    for m in all_meta:
        # Also print the precise sort timestamp (now "most recent
        # commit time") to make it easy to verify the actual same-day
        # ordering matches expectations
        sort_dt_str = m["_sort_dt"].strftime("%Y-%m-%d %H:%M:%S")
        print(f"   - [{m['date']}  sort_time:{sort_dt_str}] {m['title']}  ->  {m['url']}")
    print("=" * 60)

    # [FIX-2] Summarize all files skipped during this build as a
    # non-zero exit code (useful as a CI signal), without affecting
    # the files that were already successfully published
    if errors:
        print("\nThe following file(s) had issues and were not published "
              "this run (other files were built normally):")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
