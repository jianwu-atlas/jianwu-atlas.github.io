// ============================================================
// News data — single source of truth: `sortDate` (YYYY-MM-DD)
// `date` is only for display formatting; `year` is auto-derived
// from sortDate by render.js — no need to maintain it manually.
// category: 'publication' | 'grant' | 'award' | 'talk' | 'media' | 'team' | 'tool'
// ============================================================
const newsData = [
    {
    sortDate: "2026-10-19",
    date: "Oct 19, 2026",
    date_zh: "2026年10月19日",
    category: "team",
    title: "Lung Science Week 2026 — Helmholtz Munich (DataLung)",
    title_zh: "2026 肺科学周（Lung Science Week）· 赫尔墨茨慕尼黑（DataLung）",
    summary: "Invitation and full program for the DZL DataLung 'Introduction to Translational Lung Research' course, 19–23 October 2026 at the Helmholtz Munich campus — venue, transport, day-by-day schedule, and social events.",
    summary_zh: "DZL DataLung「转化肺研究导论——肺生物学与生理学基础」课程（2026 年 10 月 19–23 日，赫尔墨茨慕尼黑校区 Neuherberg）的邀请函与完整日程：场地、交通、逐日议程与社交活动。",
    link: "news/lung-science-week-2026.html",
    linkText: "Read the full program →",
    linkText_zh: "查看完整日程 →"
  },
    {
    sortDate: "2026-10-13",
    date: "Oct 13, 2026",
    date_zh: "2026年10月13日",
    category: "tool",
    title: "Jian's German Language Website (deutschheft)",
    title_zh: "德语学习网站（deutschheft）上线",
    summary: "Launched a personal German learning website covering the A1–A1.2 curriculum — lessons, vocabulary, grammar (incl. Das Perfekt), word forms, reading texts, exercises, and Notion-synced notes. Bilingual Chinese–German interface.",
    summary_zh: "上线了个人德语学习网站，覆盖 A1–A1.2 课程体系——课程、词汇、语法（含 Das Perfekt）、词形、阅读文本、练习以及与 Notion 同步的笔记。中德双语界面。",
    link: "https://jianwu-atlas.github.io/deutschheft/",
    linkText: "Visit the German site →",
    linkText_zh: "访问德语网站 →"
  },
  {
    sortDate: "2026-07-17",
    date: "Jul 17, 2026",
    date_zh: "2026年7月17日",
    category: "tool",
    title: "jwtools v0.2.0: New Cell-Type Proportion Analysis Toolkit",
    title_zh: "jwtools v0.2.0：全新细胞类型比例分析工具",
    summary: "Released jwtools v0.2.0, adding ct_proportion_analysis() for donor-level cell-type proportion statistics with pairwisse significance testing and dataset/batch overlay diagnostics, plus rename_dataset_origin() and save_dual() helper functions.",
    summary_zh: "发布 jwtools v0.2.0，新增 ct_proportion_analysis()：支持供体水平细胞类型比例统计、两两显著性检验与 dataset/batch 覆盖诊断，并新增 rename_dataset_origin() 与 save_dual() 辅助函数。",
    link: "https://github.com/jianwu-atlas/jwtools/releases/tag/v0.2.0",
    linkText: "View Release Notes →",
    linkText_zh: "查看 Release Notes →",
    logo: "assets/img/logos/jwtools-hex.png"
  },
  {
    sortDate: "2026-07-16",
    date: "July 16, 2026",
    date_zh: "2026年7月16日",
    category: "tool",
    title: "Introducing jwtools: An R Package for Single-Cell & Omics Utility Functions",
    title_zh: "jwtools 发布：单细胞与组学分析的 R 工具包",
    summary: "Released jwtools, a personal R package formalizing reusable utility functions from daily single-cell and omics analysis work — starting with qs_save_workspace() and qs_load_workspace() for fast, memory-efficient workspace snapshots via the qs format. A living package, with future additions covering single-cell QC helpers, TE/ERV quantification utilities, and large-matrix data wrangling tools. Licensed under MIT.",
    summary_zh: "发布 jwtools——把日常单细胞与组学分析中可复用的工具函数整理成的个人 R 包。首批功能为 qs_save_workspace() 与 qs_load_workspace()，基于 qs 格式实现快速、省内存的工作区快照。这是一个持续演进的包，后续将加入单细胞 QC 辅助、TE/ERV 定量以及大矩阵数据处理工具。MIT 许可证。",
    link: "https://github.com/jianwu-atlas/jwtools",
    linkText: "View on GitHub →",
    linkText_zh: "在 GitHub 上查看 →"
  },
  {
    sortDate: "2026-06-03",
    date: "Jun 3, 2026",
    date_zh: "2026年6月3日",
    category: "team",
    title: "JPMorganChase Corporate Challenge Frankfurt 2026",
    title_zh: "摩根大通企业挑战赛 · 法兰克福 2026",
    summary: "Took part in the JPMorganChase Corporate Challenge in Frankfurt — a company running event at Opernplatz on Wednesday, 3 June 2026, starting at 7:00 p.m.",
    summary_zh: "参加法兰克福 JPMorganChase Corporate Challenge 企业跑步活动——2026 年 6 月 3 日（周三）晚 7:00 于 Opernplatz 起跑。",
    link: "https://www.jpmorganchasecc.com/en/home/our-locations/frankfurt",
    linkText: "Event details →",
    linkText_zh: "活动详情 →"
  },
  {
    sortDate: "2026-03-05",
    date: "Mar 5, 2026",
    date_zh: "2026年3月5日",
    category: "award",
    title: "Invited to Join the DZL DataLung Training Program (BioTrack)",
    title_zh: "入选 DZL DataLung 培训项目（BioTrack）",
    summary: "Selected among the top candidates following expert committee review of all applications; invited by the DZL DataLung School to join the upcoming BioTrack training program, in recognition of prior qualifications and computational research experience.",
    summary_zh: "经专家委员会对全部申请的评审，从优秀候选人中脱颖而出，获 DZL DataLung School 邀请加入即将启动的 BioTrack 培训项目，以肯定此前的资质与计算研究经验。",
    link: "https://dzl.de/en/academy-training/dzl-datalung-school-academy/",
    linkText: "DZL DataLung School →",
    linkText_zh: "DZL DataLung School →"
  },
  {
    sortDate: "2025-07-01",
    date: "Jul 1, 2025",
    date_zh: "2025年7月1日",
    category: "team",
    title: "Launched New Academic Website",
    title_zh: "新版学术网站上线",
    summary: "Established a new academic personal website to present ongoing research on lung aging, and single-cell atlas integration projects.",
    summary_zh: "搭建新版个人学术网站，展示正在进行的肺衰老与单细胞图谱整合研究。",
    link: "index.html",
    linkText: "Visit homepage →",
    linkText_zh: "访问主页 →"
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