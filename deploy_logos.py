#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Jian Wu Website — Batch Logo/Header/Footer Deployment Script
--------------------------------------------------------------------------
Purpose:
  1. Normalize all legacy .jpg/.jpeg logo references to .png
  2. Inject favicon links into <head>
  3. Upgrade nav-brand from text-only to icon + text lockup
  4. Insert full Hero Logo section (index.html only)
  5. Replace <footer> across all 8 pages with unified institutional footer
  6. Append corresponding CSS block to assets/css/style.css (guarded by marker)

Idempotent: safe to re-run multiple times without duplicating insertions.
================================================================================
"""

import re
import glob
import shutil
import os
from datetime import datetime

# ------------------------------------------------------------------
# 0. Backup all HTML files + style.css before modification
# ------------------------------------------------------------------
BACKUP_DIR = f"../backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(BACKUP_DIR, exist_ok=True)

files_to_backup = glob.glob("*.html") + ["assets/css/style.css"]
for f in files_to_backup:
    if os.path.exists(f):
        shutil.copy2(f, os.path.join(BACKUP_DIR, os.path.basename(f)))
print(f"✅ Backup created at: {BACKUP_DIR}\n")

# ------------------------------------------------------------------
# 1. Reusable HTML fragments
# ------------------------------------------------------------------

FAVICON_BLOCK = (
    '<link rel="icon" type="image/png" href="assets/img/logos/wu_jian_icon.png">\n'
    '<link rel="apple-touch-icon" href="assets/img/logos/wu_jian_icon.png">'
)

NAV_BRAND_NEW = (
    '<a href="index.html" class="nav-brand">\n'
    '      <img src="assets/img/logos/wu_jian_icon.png" alt="Jian Wu" class="brand-icon-img">\n'
    '      Jian Wu\n'
    '    </a>'
)

HERO_LOGO_SECTION = '''
<!-- ============ Hero Logo Section (index.html only) ============ -->
<section class="hero-logo-section">
  <img src="assets/img/logos/wu_jian_lockup.png"
       alt="Jian Wu - Lung Cell Atlas Research | Computational Biology & Multi-omics"
       class="hero-logo-img">
</section>
'''

FOOTER_NEW = '''<footer class="site-footer">

  <div class="footer-logos-wrap">
    <p class="footer-logos-label">Affiliated Institutions &amp; Collaborators</p>
    <div class="footer-logos-row">

      <a href="index.html" class="footer-logo-item footer-logo-self" title="Jian Wu">
        <img src="assets/img/logos/wu_jian_icon.png" alt="Jian Wu - Lung Cell Atlas Research">
      </a>

      <div class="footer-logo-divider"></div>

      <a href="https://www.uni-giessen.de/en" target="_blank" rel="noopener" class="footer-logo-item" title="Justus-Liebig-Universität Gießen">
        <img src="assets/img/logos/jlu-giessen.png" alt="Justus-Liebig-Universität Gießen">
      </a>

      <a href="https://www.mpi-hlr.de/en" target="_blank" rel="noopener" class="footer-logo-item" title="Max Planck Institute for Heart and Lung Research">
        <img src="assets/img/logos/mpi-kerckhoff.png" alt="Max Planck Institute for Heart and Lung Research">
      </a>

      <a href="https://cpi-online.de/" target="_blank" rel="noopener" class="footer-logo-item" title="Cardio-Pulmonary Institute">
        <img src="assets/img/logos/cpi.png" alt="Cardio-Pulmonary Institute (CPI)">
      </a>

      <a href="https://dzl.de/en/" target="_blank" rel="noopener" class="footer-logo-item" title="DZL DataLung School">
        <img src="assets/img/logos/dzl-datalung.png" alt="Deutsches Zentrum für Lungenforschung - DataLung School">
      </a>

      <a href="https://www.imprs-mob.de/" target="_blank" rel="noopener" class="footer-logo-item" title="IMPRS for Molecular Organ Biology">
        <img src="assets/img/logos/imprs-mob.png" alt="IMPRS for Molecular Organ Biology">
      </a>

      <a href="https://ilh-giessen.de/en/" target="_blank" rel="noopener" class="footer-logo-item" title="Institute for Lung Health">
        <img src="assets/img/logos/ilh.png" alt="Institute for Lung Health (ILH)">
      </a>

      <a href="https://www.spullamsettilab.com/index.php" target="_blank" rel="noopener" class="footer-logo-item" title="Pullamsetti Lab">
        <img src="assets/img/logos/pullamsetti-lab.png" alt="Pullamsetti Lab - Lung Vascular Epigenetics">
      </a>

    </div>
  </div>

  <div class="footer-copyright">
    © 2025 Jian Wu · CPI / MPI-BN / JLU Gießen / DZL / ILH ·
    <a href="https://github.com/jianwu-atlas" target="_blank">GitHub</a> ·
    <a href="https://orcid.org/0000-0003-4720-2374" target="_blank">ORCID</a>
  </div>

</footer>'''

# ------------------------------------------------------------------
# 2. Process each HTML file
# ------------------------------------------------------------------
html_files = sorted(glob.glob("*.html"))
print(f"Found {len(html_files)} HTML files: {html_files}\n")

for fname in html_files:
    with open(fname, "r", encoding="utf-8") as f:
        content = f.read()
    original = content

    # --- 2a. Safety-net: normalize any stray .jpg/.jpeg logo refs to .png ---
    content = re.sub(
        r'(assets/img/logos/[A-Za-z0-9_\-]+)\.(jpe?g)',
        r'\1.png',
        content,
        flags=re.IGNORECASE
    )

    # --- 2b. Insert favicon links (idempotent) ---
    if 'rel="icon"' not in content:
        content = content.replace(
            '<link rel="stylesheet" href="assets/css/style.css">',
            FAVICON_BLOCK + '\n<link rel="stylesheet" href="assets/css/style.css">'
        )

    # --- 2c. Upgrade nav-brand: text-only → icon + text ---
    if 'brand-icon-img' not in content:
        content = re.sub(
            r'<a href="index\.html" class="nav-brand">\s*Jian Wu\s*</a>',
            NAV_BRAND_NEW,
            content
        )

    # --- 2d. Insert Hero Logo Section (index.html only, right after </nav>) ---
    if fname == "index.html" and "hero-logo-section" not in content:
        content = content.replace("</nav>", "</nav>\n" + HERO_LOGO_SECTION, 1)

    # --- 2e. Replace <footer>...</footer> (pristine, no class attribute) ---
    content = re.sub(
        r"<footer>.*?</footer>",
        FOOTER_NEW,
        content,
        flags=re.DOTALL
    )
    # --- 2f. Re-run safety: if already updated (has site-footer class), refresh in place ---
    content = re.sub(
        r'<footer class="site-footer">.*?</footer>',
        FOOTER_NEW,
        content,
        flags=re.DOTALL
    )

    if content != original:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Updated: {fname}")
    else:
        print(f"⚠️  No changes applied: {fname} (patterns may not have matched — check manually)")

# ------------------------------------------------------------------
# 3. Append CSS block to style.css (guarded by marker comment)
# ------------------------------------------------------------------
CSS_MARKER = "/* === JIANWU-HEADER-FOOTER-LOGOS v1 === */"

CSS_BLOCK = f"""
{CSS_MARKER}

/* ---- Nav Brand Icon ---- */
.nav-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.brand-icon-img {{
    height: 34px;
    width: auto;
}}

/* ---- Hero Logo Section (index.html) ---- */
.hero-logo-section {{
    width: 100%;
    background-color: #fdfdfb;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 45px 20px 35px;
}}
.hero-logo-img {{
    max-width: 480px;
    width: 100%;
    height: auto;
}}

/* ---- Institutional Footer ---- */
.site-footer {{
    background-color: #f4f3ef;
    border-top: 1px solid rgba(27,58,45,.12);
    padding: 2.4rem 1.5rem 1.3rem;
    text-align: center;
}}
.footer-logos-wrap {{
    max-width: 1100px;
    margin: 0 auto 1.7rem;
}}
.footer-logos-label {{
    font-size: .68rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #8a8a8a;
    margin-bottom: 1.2rem;
    font-weight: 500;
}}
.footer-logos-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 1.3rem;
}}
.footer-logo-item {{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 58px;
    padding: 6px 14px;
    border-radius: 8px;
    opacity: 0.82;
    transition: opacity 0.3s ease, background-color 0.3s ease, transform 0.3s ease;
}}
.footer-logo-item img {{
    height: 100%;
    width: auto;
    max-width: 115px;
    object-fit: contain;
}}
.footer-logo-item:hover {{
    opacity: 1;
    background-color: #ffffff;
    box-shadow: 0 3px 10px rgba(0,0,0,.08);
    transform: translateY(-2px);
}}
.footer-logo-self {{
    height: 66px;
    padding: 6px 12px;
    border: 1.5px solid #c9a86a;
    background-color: #fdfdfb;
    opacity: 1;
}}
.footer-logo-self img {{
    max-width: 58px;
}}
.footer-logo-divider {{
    width: 1px;
    height: 42px;
    background-color: rgba(0,0,0,.12);
    margin: 0 0.5rem;
}}
.footer-copyright {{
    font-size: .78rem;
    color: #666;
    padding-top: 1.1rem;
    border-top: 1px solid rgba(0,0,0,.06);
    max-width: 1000px;
    margin: 0 auto;
}}
.footer-copyright a {{
    color: #1b3a2d;
    text-decoration: none;
    font-weight: 500;
}}
.footer-copyright a:hover {{
    text-decoration: underline;
}}

@media (max-width: 900px) {{
    .footer-logos-row {{ gap: 0.9rem; }}
    .footer-logo-item {{ height: 48px; padding: 5px 10px; }}
    .footer-logo-item img {{ max-width: 85px; }}
    .footer-logo-divider {{ display: none; }}
    .hero-logo-img {{ max-width: 320px; }}
    .brand-icon-img {{ height: 28px; }}
}}
@media (max-width: 480px) {{
    .footer-logos-row {{ gap: 0.6rem; }}
    .footer-logo-item {{ height: 40px; }}
    .footer-logo-self {{ height: 46px; }}
}}
"""

CSS_PATH = "assets/css/style.css"
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css_content = f.read()

if CSS_MARKER not in css_content:
    with open(CSS_PATH, "a", encoding="utf-8") as f:
        f.write(CSS_BLOCK)
    print(f"\n✅ CSS block appended to {CSS_PATH}")
else:
    print(f"\n⚠️  CSS block already present in {CSS_PATH}, skipped (idempotent).")

print("\n🎉 Batch deployment complete. Please review changes with `git diff` before pushing.")
