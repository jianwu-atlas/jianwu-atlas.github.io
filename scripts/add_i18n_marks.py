#!/usr/bin/env python3
"""
add_i18n_marks.py — One-shot migration to add Chinese/English i18n markers.

This script edits the 9 main HTML pages to:
  1) Include <script src="assets/js/i18n.js"></script> before main.js
  2) Add a language switch button in the navbar (before the dark-mode button)
  3) Mark static UI text with data-i18n="key" (Chinese fallback in dict)
  4) Mark form placeholders with data-i18n-ph, native tooltips with data-i18n-title
  5) Register window.__langCallbacks so dynamic content re-renders on language toggle
  6) Update the <title> element to use data-i18n

Usage:
  python3 scripts/add_i18n_marks.py            # dry-run (prints plan, no writes)
  python3 scripts/add_i18n_marks.py --apply    # actually modify files

Each replacement is asserted to match exactly once per file, so the script
either fully succeeds or aborts with a clear error pointing at the drift.
Idempotent: running twice on an already-migrated file is a no-op (asserts fail
because markers are already present — re-run git checkout to recover).
"""

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# COMMON replacements — applied to all 9 pages.
# Every tuple is (old_substring, new_substring) and must match exactly once.
# ---------------------------------------------------------------------------
COMMON = [
    # 1) Brand sub-tag in navbar
    (
        '<span class="nav-brand-sub">Lung Cell Atlas Research</span>',
        '<span class="nav-brand-sub" data-i18n="brand.sub">Lung Cell Atlas Research</span>'
    ),
    # 2) Research dropdown button
    (
        '<button>Research ▾</button>',
        '<button data-i18n="nav.research">Research ▾</button>'
    ),
    # 3) Plain nav links (not the index/news active ones — handled per-file)
    (
        '<a href="experience.html">Experience</a>',
        '<a href="experience.html" data-i18n="nav.experience">Experience</a>'
    ),
    (
        '<a href="publications.html">Publications</a>',
        '<a href="publications.html" data-i18n="nav.publications">Publications</a>'
    ),
    (
        '<a href="conferences.html">Conferences</a>',
        '<a href="conferences.html" data-i18n="nav.conferences">Conferences</a>'
    ),
    (
        '<a href="expertise.html">Expertise</a>',
        '<a href="expertise.html" data-i18n="nav.expertise">Expertise</a>'
    ),
    (
        '<a href="tutorials.html">Tutorials</a>',
        '<a href="tutorials.html" data-i18n="nav.tutorials">Tutorials</a>'
    ),
    (
        '<a href="gallery.html">Gallery</a>',
        '<a href="gallery.html" data-i18n="nav.gallery">Gallery</a>'
    ),
    (
        '<a href="contact.html">Contact</a>',
        '<a href="contact.html" data-i18n="nav.contact">Contact</a>'
    ),
    # 4) Language switch button — inserted before the dark-mode button
    (
        '<button onclick="toggleDark()" title="Dark mode">🌙</button>',
        '<button class="lang-btn" onclick="toggleLang()" data-i18n="lang.switch" data-i18n-title="lang.switch.title" title="Switch to Chinese">中文</button>\n      <button onclick="toggleDark()" title="Dark mode">🌙</button>'
    ),
    # 5) Footer affiliations label
    (
        '<p class="footer-logos-label">Affiliated Institutions &amp; Collaborators</p>',
        '<p class="footer-logos-label" data-i18n="footer.affil">Affiliated Institutions &amp; Collaborators</p>'
    ),
    # 6) Inject i18n.js before main.js (i18n must be parsed before main.js so
    #    window.__langCallbacks registration works on first DOMContentLoaded)
    (
        '<script src="assets/js/main.js"></script>',
        '<script src="assets/js/i18n.js"></script>\n<script src="assets/js/main.js"></script>'
    ),
]

# ---------------------------------------------------------------------------
# PER-FILE replacements — page-specific markers + page-specific callback wiring.
# Indexed by HTML filename.
# ---------------------------------------------------------------------------
PER_FILE = {
    'index.html': [
        # Page title
        (
            '<title>Jian Wu | Bioinformatician · Lung Aging · LncRNA Biology</title>',
            '<title data-i18n="title.index">Jian Wu | Bioinformatician · Lung Aging · LncRNA Biology</title>'
        ),
        # Nav Home with active class
        (
            '<a href="index.html" class="active">Home</a>',
            '<a href="index.html" class="active" data-i18n="nav.home">Home</a>'
        ),
        # Hero CTAs
        (
            '<a href="publications.html" class="hero-cta-btn">View Publications</a>',
            '<a href="publications.html" class="hero-cta-btn" data-i18n="hero.pubs">View Publications</a>'
        ),
        (
            '<a href="news.html" class="hero-cta-btn hero-cta-outline">Latest News</a>',
            '<a href="news.html" class="hero-cta-btn hero-cta-outline" data-i18n="hero.news">Latest News</a>'
        ),
        # Sidebar profile title
        (
            '<p class="profile-title">Bioinformatician</p>',
            '<p class="profile-title" data-i18n="profile.title">Bioinformatician</p>'
        ),
        # Sidebar research interests card title
        (
            '<p class="sb-title">Research Interests</p>',
            '<p class="sb-title" data-i18n="sb.interests">Research Interests</p>'
        ),
        # Interest items 1-5 (int.6 contains <a> — leave as proper noun)
        (
            '<div class="int-item"><span class="int-dot"></span>Lung Aging &amp; Chronic Disease (COPD / IPF)</div>',
            '<div class="int-item" data-i18n="int.1"><span class="int-dot"></span>Lung Aging &amp; Chronic Disease (COPD / IPF)</div>'
        ),
        (
            '<div class="int-item"><span class="int-dot"></span>Lung Cell Atlas Construction</div>',
            '<div class="int-item" data-i18n="int.2"><span class="int-dot"></span>Lung Cell Atlas Construction</div>'
        ),
        (
            '<div class="int-item"><span class="int-dot"></span>Spatial Lung Cancer Profiling</div>',
            '<div class="int-item" data-i18n="int.3"><span class="int-dot"></span>Spatial Lung Cancer Profiling</div>'
        ),
        (
            '<div class="int-item"><span class="int-dot"></span>TE Biology</div>',
            '<div class="int-item" data-i18n="int.4"><span class="int-dot"></span>TE Biology</div>'
        ),
        (
            '<div class="int-item"><span class="int-dot"></span>Single-Cell &amp; Spatial Transcriptomics</div>',
            '<div class="int-item" data-i18n="int.5"><span class="int-dot"></span>Single-Cell &amp; Spatial Transcriptomics</div>'
        ),
        # Education card
        (
            '<p class="sb-title">Education</p>',
            '<p class="sb-title" data-i18n="sb.education">Education</p>'
        ),
        (
            '<p class="edu-deg">🎓 Ph.D. Candidate (Dr. rer. nat.)</p>',
            '<p class="edu-deg" data-i18n="edu.phd">🎓 Ph.D. Candidate (Dr. rer. nat.)</p>'
        ),
        (
            '<p class="edu-when">2023 – Present</p>',
            '<p class="edu-when" data-i18n="edu.phd.when">2023 – Present</p>'
        ),
        (
            '<p class="edu-deg">🎓 M.Sc. Natural Science</p>',
            '<p class="edu-deg" data-i18n="edu.msc">🎓 M.Sc. Natural Science</p>'
        ),
        (
            '<p class="edu-deg">🎓 B.Sc. Life Sciences</p>',
            '<p class="edu-deg" data-i18n="edu.bsc">🎓 B.Sc. Life Sciences</p>'
        ),
        # Social buttons (only the ones whose label needs translation)
        (
            '<a href="mailto:Jian.Wu@mpi-bn.mpg.de" class="soc-btn"><span>✉️ Email</span></a>',
            '<a href="mailto:Jian.Wu@mpi-bn.mpg.de" class="soc-btn"><span data-i18n="soc.email">✉️ Email</span></a>'
        ),
        (
            '<a href="https://scholar.google.com/citations?user=-pYIKQkAAAAJ&hl" class="soc-btn" target="_blank"><span>🎓 Scholar</span></a>',
            '<a href="https://scholar.google.com/citations?user=-pYIKQkAAAAJ&hl" class="soc-btn" target="_blank"><span data-i18n="soc.scholar">🎓 Scholar</span></a>'
        ),
        (
            '<a href="https://www.spullamsettilab.com/index.php" class="soc-btn" target="_blank"><span>🌐 Pullamsetti Lab</span></a>',
            '<a href="https://www.spullamsettilab.com/index.php" class="soc-btn" target="_blank"><span data-i18n="soc.lab">🌐 Pullamsetti Lab</span></a>'
        ),
        # Section titles
        (
            '<h2 class="sec-title"><span class="sec-icon">👤</span> Biography</h2>',
            '<h2 class="sec-title" data-i18n="sec.bio"><span class="sec-icon">👤</span> Biography</h2>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">📰</span> Recent Highlights</h2>',
            '<h2 class="sec-title" data-i18n="sec.highlights"><span class="sec-icon">📰</span> Recent Highlights</h2>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">⭐</span> Featured Publications</h2>',
            '<h2 class="sec-title" data-i18n="sec.featured"><span class="sec-icon">⭐</span> Featured Publications</h2>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">🎙️</span> Latest Tutorials</h2>',
            '<h2 class="sec-title" data-i18n="sec.tutorials"><span class="sec-icon">🎙️</span> Latest Tutorials</h2>'
        ),
        # Footer-of-section links
        (
            '<a href="news.html">View all news →</a>',
            '<a href="news.html" data-i18n="link.allnews">View all news →</a>'
        ),
        (
            '<a href="publications.html">View all 9 publications →</a>',
            '<a href="publications.html" data-i18n="link.allpubs">View all 9 publications →</a>'
        ),
        (
            '<a href="tutorials.html">View all tutorials →</a>',
            '<a href="tutorials.html" data-i18n="link.alltuts">View all tutorials →</a>'
        ),
        (
            '<a href="experience.html">→ Full experience timeline</a>',
            '<a href="experience.html" data-i18n="link.timeline">→ Full experience timeline</a>'
        ),
        # Bio paragraphs 1-5
        (
            '<p>I am a bioinformatician working at the intersection of single-cell genomics, lung aging, and respiratory disease. Based at the <strong>Cardio-Pulmonary Institute (CPI)</strong> and the <strong>Max Planck Institute for Heart and Lung Research (MPI-BN)</strong> in Germany, I focus on decoding the cellular and molecular mechanisms underlying lung aging, COPD, and IPF.</p>',
            '<p data-i18n="bio.p1">I am a bioinformatician working at the intersection of single-cell genomics, lung aging, and respiratory disease. Based at the <strong>Cardio-Pulmonary Institute (CPI)</strong> and the <strong>Max Planck Institute for Heart and Lung Research (MPI-BN)</strong> in Germany, I focus on decoding the cellular and molecular mechanisms underlying lung aging, COPD, and IPF.</p>'
        ),
        (
            '<p>My work spans single-cell and spatial transcriptomics, with ongoing projects in <strong>lung cell atlas construction</strong> and <strong>spatial lung cancer profiling</strong>. I am also involved in the <strong>DZL DataLung School</strong>, contributing to data science education in the pulmonary research community.</p>',
            '<p data-i18n="bio.p2">My work spans single-cell and spatial transcriptomics, with ongoing projects in <strong>lung cell atlas construction</strong> and <strong>spatial lung cancer profiling</strong>. I am also involved in the <strong>DZL DataLung School</strong>, contributing to data science education in the pulmonary research community.</p>'
        ),
        (
            '<p>Technically, I work primarily in <strong>Linux, R and Python</strong>, with expertise in <strong>Seurat, Monocle, Slingshot, and Harmony</strong> — building reproducible pipelines for large-scale multi-dataset integration, trajectory inference, and differential expression analysis.</p>',
            '<p data-i18n="bio.p3">Technically, I work primarily in <strong>Linux, R and Python</strong>, with expertise in <strong>Seurat, Monocle, Slingshot, and Harmony</strong> — building reproducible pipelines for large-scale multi-dataset integration, trajectory inference, and differential expression analysis.</p>'
        ),
        (
            '<p>I am passionate about translating high-dimensional omics data into biological insight — and ultimately, into a better understanding of how lungs age and fail.</p>',
            '<p data-i18n="bio.p4">I am passionate about translating high-dimensional omics data into biological insight — and ultimately, into a better understanding of how lungs age and fail.</p>'
        ),
        (
            '<p style="margin-top:.8rem">I hold concurrent Research Scientist appointments at CPI, MPI-BN, Justus-Liebig-Universität Gießen (JLU), the German Center for Lung Research (DZL), and the Institute for Lung Health (ILH), and am enrolled in the <strong>IMPRS-MOB</strong> structured PhD program, working under the supervision of <a href="https://www.spullamsettilab.com/index.php" target="_blank">Prof. Soni Savai Pullamsetti</a>.</p>',
            '<p data-i18n="bio.p5" style="margin-top:.8rem">I hold concurrent Research Scientist appointments at CPI, MPI-BN, Justus-Liebig-Universität Gießen (JLU), the German Center for Lung Research (DZL), and the Institute for Lung Health (ILH), and am enrolled in the <strong>IMPRS-MOB</strong> structured PhD program, working under the supervision of <a href="https://www.spullamsettilab.com/index.php" target="_blank">Prof. Soni Savai Pullamsetti</a>.</p>'
        ),
        # Render callbacks — push instead of direct call so language toggle
        # can re-render dynamic content.
        (
            '  renderNewsHighlights(\'homeHighlights\', newsData, 3);\n  renderPublications(\'featuredPubs\', publicationsData, true);\n  renderTutorials(\'latestTutorials\', tutorialsData, { limit: 2 });',
            '  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderNewsHighlights(\'homeHighlights\', newsData, 3); });\n  window.__langCallbacks.push(() => { renderPublications(\'featuredPubs\', publicationsData, true); });\n  window.__langCallbacks.push(() => { renderTutorials(\'latestTutorials\', tutorialsData, { limit: 2 }); });'
        ),
    ],

    'experience.html': [
        (
            '<title>Experience | Jian Wu</title>',
            '<title data-i18n="title.exp">Experience | Jian Wu</title>'
        ),
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>Research &amp; Work Experience</h1>',
            '<h1 data-i18n="exp.header">Research &amp; Work Experience</h1>'
        ),
        (
            '<p>2015 – Present · GIBH / CAS → The University of Hong Kong → CPI / CIGL, JLU Gießen</p>',
            '<p data-i18n="exp.sub">2015 – Present · GIBH / CAS → The University of Hong Kong → CPI / CIGL, JLU Gießen</p>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">🔬</span> Timeline</h2>',
            '<h2 class="sec-title" data-i18n="sec.timeline"><span class="sec-icon">🔬</span> Timeline</h2>'
        ),
        (
            '  renderExperience(\'expList\', experienceData);',
            '  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderExperience(\'expList\', experienceData); });'
        ),
    ],

    'publications.html': [
        (
            '<title>Publications | Jian Wu</title>',
            '<title data-i18n="title.pubs">Publications | Jian Wu</title>'
        ),
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>Publications</h1>',
            '<h1 data-i18n="pubs.header">Publications</h1>'
        ),
        (
            '<p>9 peer-reviewed papers, preprints &amp; manuscripts in preparation</p>',
            '<p data-i18n="pubs.sub">9 peer-reviewed papers, preprints &amp; manuscripts in preparation</p>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">📄</span> All Publications</h2>',
            '<h2 class="sec-title" data-i18n="sec.allpubs"><span class="sec-icon">📄</span> All Publications</h2>'
        ),
        (
            '  renderPublications(\'pubList\', publicationsData);',
            '  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderPublications(\'pubList\', publicationsData); });'
        ),
    ],

    'conferences.html': [
        (
            '<title>Conferences | Jian Wu</title>',
            '<title data-i18n="title.conf">Conferences | Jian Wu</title>'
        ),
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>Conferences &amp; Academic Activities</h1>',
            '<h1 data-i18n="conf.header">Conferences &amp; Academic Activities</h1>'
        ),
        (
            '<p>9 conference presentations · 2016 – 2019</p>',
            '<p data-i18n="conf.sub">9 conference presentations · 2016 – 2019</p>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">🎤</span> Presentations</h2>',
            '<h2 class="sec-title" data-i18n="sec.present"><span class="sec-icon">🎤</span> Presentations</h2>'
        ),
        (
            '  renderConferences(\'confList\', conferencesData);',
            '  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderConferences(\'confList\', conferencesData); });'
        ),
    ],

    'expertise.html': [
        (
            '<title>Expertise | Jian Wu</title>',
            '<title data-i18n="title.expertise">Expertise | Jian Wu</title>'
        ),
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>Expertise</h1>',
            '<h1 data-i18n="expertise.header">Expertise</h1>'
        ),
        (
            '<p>Technical skills across programming, single-cell genomics and epigenomics</p>',
            '<p data-i18n="expertise.sub">Technical skills across programming, single-cell genomics and epigenomics</p>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">🛠️</span> Skills</h2>',
            '<h2 class="sec-title" data-i18n="sec.skills"><span class="sec-icon">🛠️</span> Skills</h2>'
        ),
        # General expertise note — replace the whole block (drop the inline
        # <strong> for the label and put the full sentence under one i18n key).
        (
            '    <div style="margin-top:1.5rem;padding:1.1rem;background:rgba(27,58,45,.04);border-radius:var(--radius);border:1px solid rgba(27,58,45,.1)">\n      <p style="margin:0;font-size:.87rem;color:var(--text-2)">\n        <strong>General expertise:</strong> Statistical analysis of large omics datasets · Strong molecular biology background · Familiarity with genomic data and approaches for high-dimensional data analysis, including scRNA-seq (spatial), bulk RNA-seq, ATAC-seq, HiC, and ChIP-seq.\n      </p>\n    </div>',
            '    <div style="margin-top:1.5rem;padding:1.1rem;background:rgba(27,58,45,.04);border-radius:var(--radius);border:1px solid rgba(27,58,45,.1)">\n      <p style="margin:0;font-size:.87rem;color:var(--text-2)" data-i18n="expertise.note">\n        General expertise: Statistical analysis of large omics datasets · Strong molecular biology background · Familiarity with genomic data and approaches for high-dimensional data analysis, including scRNA-seq (spatial), bulk RNA-seq, ATAC-seq, HiC, and ChIP-seq.\n      </p>\n    </div>'
        ),
        (
            '  renderExpertise(\'expertiseGrid\', expertiseData);',
            '  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderExpertise(\'expertiseGrid\', expertiseData); });'
        ),
    ],

    'tutorials.html': [
        (
            '<title>Tutorials & Podcast | Jian Wu</title>',
            '<title data-i18n="title.tut">Tutorials & Podcast | Jian Wu</title>'
        ),
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>Tutorials &amp; Podcast</h1>',
            '<h1 data-i18n="tut.header">Tutorials &amp; Podcast</h1>'
        ),
        (
            '<p>科研教程、播客更新，持续连载中</p>',
            '<p data-i18n="tut.sub">科研教程、播客更新，持续连载中</p>'
        ),
        # Tutorials page renders Chinese content directly; re-render on toggle
        # is a no-op (pick() on tutorial entries already handles zh data), but
        # registering a callback keeps the page in the standard pattern.
        (
            '  // 不传 limit，展示 tutorials.js 里的全部条目\n  renderTutorials(\'tutGrid\', tutorialsData, { groupByYear: true });',
            '  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderTutorials(\'tutGrid\', tutorialsData, { groupByYear: true }); });'
        ),
    ],

    'news.html': [
        (
            '<title>News | Jian Wu — Lung Cell Atlas Research</title>',
            '<title data-i18n="title.news">News | Jian Wu — Lung Cell Atlas Research</title>'
        ),
        (
            '<a href="news.html" class="active">News</a>',
            '<a href="news.html" class="active" data-i18n="nav.news">News</a>'
        ),
        # Plain Home link (news.html doesn't mark Home as active)
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>News</h1>',
            '<h1 data-i18n="news.header">News</h1>'
        ),
        (
            '<p>Updates on publications, grants, invited talks, and lab milestones</p>',
            '<p data-i18n="news.sub">Updates on publications, grants, invited talks, and lab milestones</p>'
        ),
        (
            '  renderNewsTabs(\'newsTabs\', \'newsTimeline\', newsData);\n  renderNews(\'newsTimeline\', newsData);',
            '  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderNewsTabs(\'newsTabs\', \'newsTimeline\', newsData); });\n  window.__langCallbacks.push(() => { renderNews(\'newsTimeline\', newsData); });'
        ),
    ],

    'gallery.html': [
        (
            '<title>Gallery | Jian Wu</title>',
            '<title data-i18n="title.gallery">Gallery | Jian Wu</title>'
        ),
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>Gallery</h1>',
            '<h1 data-i18n="gallery.header">Gallery</h1>'
        ),
        (
            '<p>Photos &amp; videos — life, fieldwork, and conferences</p>',
            '<p data-i18n="gallery.sub">Photos &amp; videos — life, fieldwork, and conferences</p>'
        ),
        # Gallery tab labels — wrap the label text in a span so the count
        # badge (managed by JS) is preserved on language toggle.
        (
            '<span class="gal-tab-label">Type</span>',
            '<span class="gal-tab-label" data-i18n="gal.type">Type</span>'
        ),
        (
            '<span class="gal-tab-label">Source</span>',
            '<span class="gal-tab-label" data-i18n="gal.source">Source</span>'
        ),
        (
            'data-filter-val="all" onclick="setTypeFilter(\'all\', this)">\n      All <span class="gal-tab-count" id="count-type-all">',
            'data-filter-val="all" onclick="setTypeFilter(\'all\', this)">\n      <span data-i18n="gal.all">All</span> <span class="gal-tab-count" id="count-type-all">'
        ),
        (
            'data-filter-val="photo" onclick="setTypeFilter(\'photo\', this)">\n      📷 Photos <span class="gal-tab-count" id="count-type-photo">',
            'data-filter-val="photo" onclick="setTypeFilter(\'photo\', this)">\n      <span data-i18n="gal.photos">📷 Photos</span> <span class="gal-tab-count" id="count-type-photo">'
        ),
        (
            'data-filter-val="video" onclick="setTypeFilter(\'video\', this)">\n      🎬 Videos <span class="gal-tab-count" id="count-type-video">',
            'data-filter-val="video" onclick="setTypeFilter(\'video\', this)">\n      <span data-i18n="gal.videos">🎬 Videos</span> <span class="gal-tab-count" id="count-type-video">'
        ),
        (
            'data-filter-val="all" onclick="setSourceFilter(\'all\', this)">\n      All Sources <span class="gal-tab-count" id="count-source-all">',
            'data-filter-val="all" onclick="setSourceFilter(\'all\', this)">\n      <span data-i18n="gal.allsrc">All Sources</span> <span class="gal-tab-count" id="count-source-all">'
        ),
        (
            'data-filter-val="local" onclick="setSourceFilter(\'local\', this)">\n      💾 Local <span class="gal-tab-count" id="count-source-local">',
            'data-filter-val="local" onclick="setSourceFilter(\'local\', this)">\n      <span data-i18n="gal.local">💾 Local</span> <span class="gal-tab-count" id="count-source-local">'
        ),
        (
            'data-filter-val="drive" onclick="setSourceFilter(\'drive\', this)">\n      ☁️ Google Drive <span class="gal-tab-count" id="count-source-drive">',
            'data-filter-val="drive" onclick="setSourceFilter(\'drive\', this)">\n      <span data-i18n="gal.drive">☁️ Google Drive</span> <span class="gal-tab-count" id="count-source-drive">'
        ),
        (
            'data-filter-val="youtube" onclick="setSourceFilter(\'youtube\', this)">\n      ▶️ YouTube <span class="gal-tab-count" id="count-source-youtube">',
            'data-filter-val="youtube" onclick="setSourceFilter(\'youtube\', this)">\n      <span data-i18n="gal.youtube">▶️ YouTube</span> <span class="gal-tab-count" id="count-source-youtube">'
        ),
        # Gallery has no re-render on toggle for counts (numbers are
        # language-independent), but we re-render the grid so captions and
        # source badges update. Match with surrounding IIFE context so we
        # only catch the initial render call (the filter handlers
        # setTypeFilter/setSourceFilter also call renderGallery — they stay).
        (
            '  })();\n\n  renderGallery(\'galGrid\', galleryData, currentFilters);',
            '  })();\n\n  window.__langCallbacks = window.__langCallbacks || [];\n  window.__langCallbacks.push(() => { renderGallery(\'galGrid\', galleryData, currentFilters); });'
        ),
    ],

    'contact.html': [
        (
            '<title>Contact | Jian Wu</title>',
            '<title data-i18n="title.contact">Contact | Jian Wu</title>'
        ),
        (
            '<a href="index.html">Home</a>',
            '<a href="index.html" data-i18n="nav.home">Home</a>'
        ),
        (
            '<h1>Contact</h1>',
            '<h1 data-i18n="contact.header">Contact</h1>'
        ),
        (
            '<p>Get in touch — email, address, and social profiles</p>',
            '<p data-i18n="contact.sub">Get in touch — email, address, and social profiles</p>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">✉️</span> Contact Information</h2>',
            '<h2 class="sec-title" data-i18n="sec.contactinfo"><span class="sec-icon">✉️</span> Contact Information</h2>'
        ),
        (
            '<p class="ct-label">MPI-BN Email</p>',
            '<p class="ct-label" data-i18n="ct.email">MPI-BN Email</p>'
        ),
        (
            '<p class="ct-label">Address (CPI/CIGL)</p>',
            '<p class="ct-label" data-i18n="ct.address">Address (CPI/CIGL)</p>'
        ),
        (
            '<p class="ct-label">Google Scholar</p>',
            '<p class="ct-label" data-i18n="ct.scholar">Google Scholar</p>'
        ),
        (
            '<p class="ct-label">PI Lab</p>',
            '<p class="ct-label" data-i18n="ct.lab">PI Lab</p>'
        ),
        (
            '<h2 class="sec-title"><span class="sec-icon">📮</span> Send a Message</h2>',
            '<h2 class="sec-title" data-i18n="sec.message"><span class="sec-icon">📮</span> Send a Message</h2>'
        ),
        (
            '<p style="font-size:.85rem;color:var(--text-2);margin-bottom:1rem">\n      Feel free to reach out via email above, or send a message directly through the form below — I\'ll get back to you as soon as possible.\n    </p>',
            '<p style="font-size:.85rem;color:var(--text-2);margin-bottom:1rem" data-i18n="contact.note">\n      Feel free to reach out via email above, or send a message directly through the form below — I\'ll get back to you as soon as possible.\n    </p>'
        ),
        (
            '<input type="text" name="name" placeholder="Your name" required>',
            '<input type="text" name="name" placeholder="Your name" data-i18n-ph="ph.name" required>'
        ),
        (
            '<input type="email" name="email" placeholder="Your email" required>',
            '<input type="email" name="email" placeholder="Your email" data-i18n-ph="ph.email" required>'
        ),
        (
            '<textarea name="message" rows="4" placeholder="Message" required></textarea>',
            '<textarea name="message" rows="4" placeholder="Message" data-i18n-ph="ph.message" required></textarea>'
        ),
        (
            '<button type="submit">Send Message</button>',
            '<button type="submit" data-i18n="btn.send">Send Message</button>'
        ),
    ],
}

PAGES = list(PER_FILE.keys())


def apply_replacements(html: str, replacements, page_name: str, dry: bool) -> str:
    """Apply each (old, new) pair exactly once; raise on drift."""
    for idx, (old, new) in enumerate(replacements, 1):
        count = html.count(old)
        if count == 0:
            raise SystemExit(
                f"  [ERROR] {page_name}: replacement #{idx} matched 0 times.\n"
                f"    old: {old[:80]!r}{'...' if len(old) > 80 else ''}"
            )
        if count > 1:
            raise SystemExit(
                f"  [ERROR] {page_name}: replacement #{idx} matched {count} times "
                f"(expected exactly 1). Refusing to apply ambiguous replace.\n"
                f"    old: {old[:80]!r}{'...' if len(old) > 80 else ''}"
            )
        if not dry:
            html = html.replace(old, new, 1)
    return html


def main():
    dry = '--apply' not in sys.argv
    if dry:
        print("DRY RUN — no files will be modified. Pass --apply to write changes.\n")
    else:
        print("APPLYING — files will be modified in place.\n")

    for page in PAGES:
        path = ROOT / page
        if not path.exists():
            raise SystemExit(f"  [ERROR] {page}: file not found")
        html = path.read_text(encoding='utf-8')
        original_len = len(html)

        # Common + per-file replacements
        all_repls = COMMON + PER_FILE[page]
        new_html = apply_replacements(html, all_repls, page, dry)

        added = len(new_html) - original_len
        if not dry:
            path.write_text(new_html, encoding='utf-8')
        print(f"  {page:20s}  {len(all_repls):2d} replacements  +{added:5d} chars  "
              f"{'[written]' if not dry else '[ok]'}")

    print()
    if dry:
        print("Run with --apply to actually modify the files.")
    else:
        print("Done. Run `node --check` on the rendered JS to verify nothing broke,")
        print("then `python3 -m http.server` and browse a few pages to spot-check.")


if __name__ == '__main__':
    main()
