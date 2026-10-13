// ============================================================
// News data — single source of truth: `sortDate` (YYYY-MM-DD)
// `date` is only for display formatting; `year` is auto-derived
// from sortDate by render.js — no need to maintain it manually.
// category: 'publication' | 'grant' | 'award' | 'talk' | 'media' | 'team' | 'tool'
// ============================================================
const newsData = [
    {
    sortDate: "2026-10-13",
    date: "Oct 13, 2026",
    category: "tool",
    title: "Jian's German Language Website (deutschheft)",
    summary: "Launched a personal German learning website covering the A1–A1.2 curriculum — lessons, vocabulary, grammar (incl. Das Perfekt), word forms, reading texts, exercises, and Notion-synced notes. Bilingual Chinese–German interface.",
    link: "https://deutschheft.edgeone.cool/",
    linkText: "Visit the German site →"
  },
  {
    sortDate: "2026-07-17",
    date: "Jul 17, 2026",
    category: "tool",
    title: "jwtools v0.2.0: New Cell-Type Proportion Analysis Toolkit",
    summary: "Released jwtools v0.2.0, adding ct_proportion_analysis() for donor-level cell-type proportion statistics with pairwisse significance testing and dataset/batch overlay diagnostics, plus rename_dataset_origin() and save_dual() helper functions.",
    link: "https://github.com/jianwu-atlas/jwtools/releases/tag/v0.2.0",
    linkText: "View Release Notes →",
    logo: "assets/img/logos/jwtools-hex.png"
  },
  {
    sortDate: "2026-07-16",
    date: "July 16, 2026",
    category: "tool",
    title: "Introducing jwtools: An R Package for Single-Cell & Omics Utility Functions",
    summary: "Released jwtools, a personal R package formalizing reusable utility functions from daily single-cell and omics analysis work — starting with qs_save_workspace() and qs_load_workspace() for fast, memory-efficient workspace snapshots via the qs format. A living package, with future additions covering single-cell QC helpers, TE/ERV quantification utilities, and large-matrix data wrangling tools. Licensed under MIT.",
    link: "https://github.com/jianwu-atlas/jwtools",
    linkText: "View on GitHub →"
  },
  {
    sortDate: "2026-03-05",
    date: "Mar 5, 2026",
    category: "award",
    title: "Invited to Join the DZL DataLung Training Program (BioTrack)",
    summary: "Selected among the top candidates following expert committee review of all applications; invited by the DZL DataLung School to join the upcoming BioTrack training program, in recognition of prior qualifications and computational research experience.",
    link: "https://dzl.de/en/academy-training/dzl-datalung-school-academy/",
    linkText: "DZL DataLung School →"
  },
  {
    sortDate: "2025-07-01",
    date: "Jul 1, 2025",
    category: "team",
    title: "Launched New Academic Website",
    summary: "Established a new academic personal website to present ongoing research on lung aging, and single-cell atlas integration projects.",
    link: "index.html",
    linkText: "Visit homepage →"
  },
  /*
  {
    sortDate: "2025-10-01",
    date: "Oct 2025",
    category: "publication",
    title: "LungERVmap: A Single-Cell Atlas of Endogenous Retrovirus Expression in the Human Lung",
    summary: "Our flagship atlas mapping ERV/TE expression across major lung cell types is now available as a preprint, integrating multi-cohort single-cell RNA-seq data.",
    link: "publications.html",
    linkText: "View publication →"
  },
  */
  /*
  {
    sortDate: "2025-08-01",
    date: "Aug 2025",
    category: "talk",
    title: "Invited Talk — ERS International Congress",
    summary: "Presented 'Age-Dependent Derepression of Endogenous Retroviruses in Alveolar Macrophages' at the European Respiratory Society International Congress.",
    link: "conferences.html",
    linkText: "Conference details →"
  },
  */
  /*
  {
    sortDate: "2025-02-01",
    date: "Feb 2025",
    category: "grant",
    title: "IMPRS-MOB Structured PhD Program — Confirmed Continuation",
    summary: "Successful annual thesis committee review; continued funding confirmed for the LungAgingERV and HERV-eQTL-Lung-soloTE projects.",
    link: "experience.html",
    linkText: "Full experience timeline →"
  },
  */
  /*
  {
    sortDate: "2024-11-01",
    date: "Nov 2024",
    category: "publication",
    title: "SoloTE-Based Structural Profiling of HERV Loci in Lung eQTL Data",
    summary: "Manuscript submitted describing integration of soloTE with lung eQTL datasets to resolve locus-specific HERV expression regulation.",
    link: "publications.html",
    linkText: "View publication →"
  },
  */
  /*
  {
    sortDate: "2024-09-01",
    date: "Sep 2024",
    category: "award",
    title: "Travel Award — IMPRS-MOB Annual Retreat",
    summary: "Awarded a travel fellowship to present early findings on macrophage-specific ERV subtypes (Mac-MER11D, Mac-MER41D, Mac-SVA) at the IMPRS-MOB annual retreat.",
    link: "gallery.html",
    linkText: "Retreat photos →"
  },
  */
  /*
  {
    sortDate: "2024-06-01",
    date: "Jun 2024",
    category: "media",
    title: "Featured in CPI Research Highlights",
    summary: "Our work on aging-related M1/M2 macrophage polarization shifts and ERV reactivation was featured in the Cardio-Pulmonary Institute's quarterly research highlights.",
    link: "https://cpi-online.de/",
    linkText: "Read on CPI website →"
  },
  */
  /*
  {
    sortDate: "2024-03-01",
    date: "Mar 2024",
    category: "team",
    title: "Launched LungERVmap Project Website",
    summary: "Established the public-facing project page for LungERVmap, the core flagship atlas integrating ERV/TE expression across lung aging, IPF, and COPD datasets.",
    link: "index.html",
    linkText: "Visit homepage →"
  }
  */
];