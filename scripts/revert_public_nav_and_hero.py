#!/usr/bin/env python3
"""Revert regressions that the private->public sync introduced into the PUBLIC
repo only:

  1. index.html hero logo was switched from the legacy lungs lockup
     `assets/img/logos/Jian_Wu_logo.png` to the new calligraphy lockup
     `wu_jian_lockup.png`. The public site intentionally keeps the lungs
     lockup as its hero (documented difference vs. the private site).
  2. The "Deutschheft" / "Englishheft" links were added to the top navigation
     bar of the root pages. The public site carries NO links to the personal
     language sites at all (2026-10-25 Jian: removed from the footer too), so
     both the nav rows and the homepage footer rows must be absent here.

Also realigns og:image / twitter:image back to the lungs lockup so the social
share card matches the hero again.

IDEMPOTENT: every replacement asserts an exact number of hits, so re-running
is safe. The private repo is deliberately NOT touched -- there the nav links,
the footer links and the calligraphy hero are the intended design.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path("/Users/Jack/Documents/GitHub/jianwu-atlas.github.io")

ROOT_PAGES = [
    "index.html",
    "tutorials.html",
    "news.html",
    "gallery.html",
    "contact.html",
    "publications.html",
    "experience.html",
    "conferences.html",
    "expertise.html",
    "404.html",
]

# The two nav rows the sync added (identical across all 9 root pages).
NAV_DE = '      <a href="https://jianwu-atlas.github.io/deutschheft/" target="_blank" rel="noopener">Deutschheft</a>\n'
NAV_EN = '      <a href="https://jianwu-atlas.github.io/englishheft/" target="_blank" rel="noopener">Englishheft</a>\n'

# Hero logo block as it was before the sync (verbatim from git history).
HERO_OLD = (
    '    <img src="assets/img/logos/wu_jian_lockup.png"\n'
    '         alt="Jian Wu - Lung Cell Atlas Research | Computational Biology & Multi-omics"\n'
    '         class="hero-logo-img">'
)
HERO_NEW = (
    '    <img src="assets/img/logos/Jian_Wu_logo.png"\n'
    '         alt="Jian Wu Research Group - Lung Cell Atlas Research | Computational Biology & Multi-omics"\n'
    '         class="hero-logo-img">'
)

# The same sync also put the language-site links into the homepage footer.
# 2026-10-25 Jian asked for them to be gone from the public site entirely, so
# this step now REMOVES them (it used to restore them).
FOOTER_WITH_LINKS = (
    '    <a href="https://orcid.org/0000-0003-4720-2374" target="_blank">ORCID</a> ·\n'
    '    <a href="https://jianwu-atlas.github.io/deutschheft/" target="_blank" rel="noopener">Deutschheft（个人 · 德语学习）</a> ·\n'
    '    <a href="https://jianwu-atlas.github.io/englishheft/" target="_blank" rel="noopener">Englishheft（个人 · 英语单词）</a>\n'
    '  </div>'
)
FOOTER_CLEAN = (
    '    <a href="https://orcid.org/0000-0003-4720-2374" target="_blank">ORCID</a>\n'
    '  </div>'
)


def replace_exact(text: str, old: str, new: str, expected: int, label: str) -> str:
    n = text.count(old)
    if n == expected:
        return text.replace(old, new)
    if n == 0:
        # Already applied on a previous run (either the row is gone, or the
        # restored value is already in place) -> idempotent no-op.
        if new == "" or (new and new in text):
            return text
    sys.exit(f"[ERROR] {label}: expected {expected} occurrence(s), found {n}. Aborting.")


nav_fixes = 0
for page in ROOT_PAGES:
    p = REPO / page
    if not p.exists():
        sys.exit(f"[ERROR] missing page: {p}")
    t = p.read_text(encoding="utf-8")
    before = t
    t = replace_exact(t, NAV_DE, "", 1, f"{page} nav Deutschheft")
    t = replace_exact(t, NAV_EN, "", 1, f"{page} nav Englishheft")
    if t != before:
        p.write_text(t, encoding="utf-8")
        nav_fixes += 1
        print(f"[ok] {page}: removed 2 nav links")

# Hero logo + social card, index.html only
idx = REPO / "index.html"
t = idx.read_text(encoding="utf-8")
t = replace_exact(t, HERO_OLD, HERO_NEW, 1, "index.html hero logo")
t = replace_exact(
    t,
    '<meta property="og:image" content="https://jianwu-atlas.github.io/assets/img/logos/wu_jian_lockup.png">',
    '<meta property="og:image" content="https://jianwu-atlas.github.io/assets/img/logos/Jian_Wu_logo.png">',
    1, "index.html og:image",
)
t = replace_exact(
    t,
    '<meta name="twitter:image" content="https://jianwu-atlas.github.io/assets/img/logos/wu_jian_lockup.png">',
    '<meta name="twitter:image" content="https://jianwu-atlas.github.io/assets/img/logos/Jian_Wu_logo.png">',
    1, "index.html twitter:image",
)
t = replace_exact(t, FOOTER_WITH_LINKS, FOOTER_CLEAN, 1, "index.html footer language links")
idx.write_text(t, encoding="utf-8")
print("[ok] index.html: hero logo + og:image + twitter:image -> Jian_Wu_logo.png")
print("[ok] index.html: footer language-site links absent")

print(f"\nDone. nav links removed from {nav_fixes} page(s); hero/social realigned.")
