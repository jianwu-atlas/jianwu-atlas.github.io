/* ============================================================
   i18n.js — 中英文切换（职责单一：只负责语言包 + 切换逻辑）
   ------------------------------------------------------------
   用法约定：
   1) 静态文本：在 HTML 元素上加 data-i18n="字典key"，
      本文件会把元素 textContent 替换为当前语言的值。
   2) 表单占位符：data-i18n-ph="key"（替换 placeholder）
   3) 原生 title 提示：data-i18n-title="key"（替换 title）
   4) 动态内容（data/*.js 驱动、render.js 渲染的区块）：
      页面内联脚本里注册一个刷新回调，切换语言时会自动重渲染：
        window.__langCallbacks.push(() => renderNews('newsTimeline', newsData));
   5) 语言选择存 localStorage('lang')，默认 'en'。
   ============================================================ */

var I18N = {
  en: {
    /* ── 通用（导航 / 页脚） ── */
    "brand.sub":        "Lung Cell Atlas Research",
    "nav.home":         "Home",
    "nav.research":     "Research ▾",
    "nav.experience":   "Experience",
    "nav.publications": "Publications",
    "nav.conferences":  "Conferences",
    "nav.expertise":    "Expertise",
    "nav.tutorials":    "Tutorials",
    "nav.news":         "News",
    "nav.gallery":      "Gallery",
    "nav.contact":      "Contact",
    "lang.switch":      "中文",
    "lang.switch.title":"Switch to Chinese",
    "footer.affil":     "Affiliated Institutions & Collaborators",

    /* ── 首页 ── */
    "title.index":      "Jian Wu | Bioinformatician · Lung Aging · LncRNA Biology",
    "hero.pubs":        "View Publications",
    "hero.news":        "Latest News",
    "hero.tagline":     "Single-cell genomics for lung aging & chronic disease",
    "hero.sub":         "Bioinformatician at CPI / MPI-BN / JLU — lung cell atlas construction, spatial transcriptomics, and reproducible multi-dataset integration.",
    "profile.title":    "Bioinformatician",
    "sb.interests":     "Research Interests",
    "int.1":            "Lung Aging & Chronic Disease (COPD / IPF)",
    "int.2":            "Lung Cell Atlas Construction",
    "int.3":            "Spatial Lung Cancer Profiling",
    "int.4":            "TE Biology",
    "int.5":            "Single-Cell & Spatial Transcriptomics",
    "sb.education":     "Education",
    "edu.phd":          "Ph.D. Candidate (Dr. rer. nat.)",
    "edu.phd.when":     "2023 – Present",
    "edu.msc":          "M.Sc. Natural Science",
    "edu.bsc":          "B.Sc. Life Sciences",
    "soc.email":        "✉️ Email",
    "soc.scholar":      "🎓 Scholar",
    "soc.lab":          "🌐 Pullamsetti Lab",
    "sec.bio":          "Biography",
    "sec.highlights":   "Recent Highlights",
    "sec.featured":     "Featured Publications",
    "sec.tutorials":    "Latest Tutorials",
    "link.allnews":     "View all news →",
    "link.allpubs":     "View all 9 publications →",
    "link.alltuts":     "View all tutorials →",
    "link.timeline":    "→ Full experience timeline",
    "bio.p1": "I am a bioinformatician working at the intersection of single-cell genomics, lung aging, and respiratory disease. Based at the Cardio-Pulmonary Institute (CPI) and the Max Planck Institute for Heart and Lung Research (MPI-BN) in Germany, I focus on decoding the cellular and molecular mechanisms underlying lung aging, COPD, and IPF.",
    "bio.p2": "My work spans single-cell and spatial transcriptomics, with ongoing projects in lung cell atlas construction and spatial lung cancer profiling. I am also involved in the DZL DataLung School, contributing to data science education in the pulmonary research community.",
    "bio.p3": "Technically, I work primarily in Linux, R and Python, with expertise in Seurat, Monocle, Slingshot, and Harmony — building reproducible pipelines for large-scale multi-dataset integration, trajectory inference, and differential expression analysis.",
    "bio.p4": "I am passionate about translating high-dimensional omics data into biological insight — and ultimately, into a better understanding of how lungs age and fail.",
    "bio.p5": "I hold concurrent Research Scientist appointments at CPI, MPI-BN, Justus-Liebig-Universität Gießen (JLU), the German Center for Lung Research (DZL), and the Institute for Lung Health (ILH), and am enrolled in the IMPRS-MOB structured PhD program, working under the supervision of Prof. Soni Savai Pullamsetti.",

    /* ── Experience ── */
    "title.exp":        "Experience | Jian Wu",
    "exp.header":       "Research & Work Experience",
    "exp.sub":          "2015 – Present · GIBH / CAS → The University of Hong Kong → CPI / CIGL, JLU Gießen",
    "sec.timeline":     "Timeline",

    /* ── Publications ── */
    "title.pubs":       "Publications | Jian Wu",
    "pubs.header":      "Publications",
    "pubs.sub":         "9 peer-reviewed papers, preprints & manuscripts in preparation",
    "sec.allpubs":      "All Publications",

    /* ── Conferences ── */
    "title.conf":       "Conferences | Jian Wu",
    "conf.header":      "Conferences & Academic Activities",
    "conf.sub":         "9 conference presentations · 2016 – 2019",
    "sec.present":      "Presentations",

    /* ── Expertise ── */
    "title.expertise":  "Expertise | Jian Wu",
    "expertise.header": "Expertise",
    "expertise.sub":    "Technical skills across programming, single-cell genomics and epigenomics",
    "sec.skills":       "Skills",
    "expertise.note":   "General expertise: Statistical analysis of large omics datasets · Strong molecular biology background · Familiarity with genomic data and approaches for high-dimensional data analysis, including scRNA-seq (spatial), bulk RNA-seq, ATAC-seq, HiC, and ChIP-seq.",

    /* ── Tutorials ── */
    "title.tut":        "Tutorials & Podcast | Jian Wu",
    "tut.header":       "Tutorials & Podcast",
    "tut.sub":          "Research tutorials and podcast episodes — ongoing series",
    "tut.back":         "← Back to all tutorials",

    /* ── News ── */
    "title.news":       "News | Jian Wu — Lung Cell Atlas Research",
    "news.header":      "News",
    "news.sub":         "Updates on publications, grants, invited talks, and lab milestones",
    "news.empty":       "No news items in this category yet.",
    "news.cat.all":     "All",
    "news.cat.publication": "Publication",
    "news.cat.grant":   "Grant",
    "news.cat.award":   "Award",
    "news.cat.talk":    "Talk",
    "news.cat.media":   "Media",
    "news.cat.team":    "Team",
    "news.cat.tool":    "Tool / Release",
    "news.readmore":    "Read more →",

    /* ── Gallery ── */
    "title.gallery":    "Gallery | Jian Wu",
    "gallery.header":   "Gallery",
    "gallery.sub":      "Photos & videos — life, fieldwork, and conferences",
    "gal.type":         "Type",
    "gal.source":       "Source",
    "gal.all":          "All",
    "gal.photos":       "📷 Photos",
    "gal.videos":       "🎬 Videos",
    "gal.allsrc":       "All Sources",
    "gal.local":        "💾 Local",
    "gal.drive":        "☁️ Google Drive",
    "gal.youtube":      "▶️ YouTube",
    "gallery.empty":    "No items match this filter",
    "gal.badge.local":  "💾 Local",
    "gal.badge.drive":  "☁️ Drive",
    "gal.badge.youtube":"▶️ YouTube",
    "gal.badge.bilibili":"📺 Bilibili",

    /* ── Contact ── */
    "title.contact":    "Contact | Jian Wu",
    "contact.header":   "Contact",
    "contact.sub":      "Get in touch — email, address, and social profiles",
    "sec.contactinfo":  "Contact Information",
    "ct.email":         "MPI-BN Email",
    "ct.address":       "Address (CPI/CIGL)",
    "ct.scholar":       "Google Scholar",
    "ct.lab":           "PI Lab",
    "sec.message":      "Send a Message",
    "contact.note":     "Feel free to reach out via email above, or send a message directly through the form below — I'll get back to you as soon as possible.",
    "ph.name":          "Your name",
    "ph.email":         "Your email",
    "ph.message":       "Message",
    "btn.send":         "Send Message",

    /* ── 404 page ── */
    "title.404":        "Page not found | Jian Wu",
    "404.code":         "404",
    "404.header":       "This page could not be found",
    "404.body":         "The link may be broken, or the page may have been moved or renamed.",
    "404.home":         "Back to homepage",
    "404.tutorials":    "Browse tutorials",
    "404.publications": "View publications"
  },

  zh: {
    /* ── 通用 ── */
    "brand.sub":        "肺细胞图谱研究",
    "nav.home":         "首页",
    "nav.research":     "研究 ▾",
    "nav.experience":   "经历",
    "nav.publications": "论文",
    "nav.conferences":  "会议",
    "nav.expertise":    "技能",
    "nav.tutorials":    "教程",
    "nav.news":         "动态",
    "nav.gallery":      "相册",
    "nav.contact":      "联系",
    "lang.switch":      "EN",
    "lang.switch.title":"Switch to English",
    "footer.affil":     "合作机构",

    /* ── 首页 ── */
    "title.index":      "吴坚 | 生物信息学家 · 肺衰老 · LncRNA 生物学",
    "hero.pubs":        "查看论文",
    "hero.news":        "最新动态",
    "hero.tagline":     "用单细胞组学解码肺衰老与慢性疾病",
    "hero.sub":         "现就职于 CPI / MPI-BN / JLU，研究方向包括肺细胞图谱构建、空间转录组学与可复现的多数据集整合。",
    "profile.title":    "生物信息学家",
    "sb.interests":     "研究方向",
    "int.1":            "肺衰老与慢性疾病（COPD / IPF）",
    "int.2":            "肺细胞图谱构建",
    "int.3":            "肺癌空间图谱分析",
    "int.4":            "转座子（TE）生物学",
    "int.5":            "单细胞与空间转录组学",
    "sb.education":     "教育背景",
    "edu.phd":          "博士研究生（Dr. rer. nat.）",
    "edu.phd.when":     "2023 – 至今",
    "edu.msc":          "理学硕士",
    "edu.bsc":          "理学学士（生命科学）",
    "soc.email":        "✉️ 邮箱",
    "soc.scholar":      "🎓 学术",
    "soc.lab":          "🌐 课题组",
    "sec.bio":          "个人简介",
    "sec.highlights":   "近期动态",
    "sec.featured":     "代表论文",
    "sec.tutorials":    "最新教程",
    "link.allnews":     "查看全部动态 →",
    "link.allpubs":     "查看全部 9 篇论文 →",
    "link.alltuts":     "查看全部教程 →",
    "link.timeline":    "→ 完整经历时间线",
    "bio.p1": "我是一名生物信息学家，研究方向聚焦单细胞基因组学、肺衰老与呼吸系统疾病的交叉领域。现就职于德国 Cardio-Pulmonary Institute（CPI）与马克斯·普朗克心肺研究所（MPI-BN），致力于解析肺衰老、COPD 与 IPF 背后的细胞与分子机制。",
    "bio.p2": "我的工作涵盖单细胞与空间转录组学，正在进行的项目包括肺细胞图谱构建与肺癌空间图谱分析。我也参与 DZL DataLung School，为肺部研究社区的数据科学教育贡献力量。",
    "bio.p3": "技术栈上，我主要使用 Linux、R 与 Python，精通 Seurat、Monocle、Slingshot 与 Harmony——构建大规模多数据集整合、轨迹推断与差异表达分析的可复现流程。",
    "bio.p4": "我热衷于把高维组学数据转化为生物学洞见，并最终服务于对肺如何衰老与衰竭的理解。",
    "bio.p5": "我同时在 CPI、MPI-BN、吉森尤斯图斯-李比希大学（JLU）、德国肺研究中心（DZL）与肺健康研究所（ILH）担任研究科学家，并参与 IMPRS-MOB 结构化博士项目，导师为 Soni Savai Pullamsetti 教授。",

    /* ── Experience ── */
    "title.exp":        "经历 | 吴坚",
    "exp.header":       "科研与工作经历",
    "exp.sub":          "2015 – 至今 · 中科院广州生物医药与健康研究院 → 香港大学 → CPI / CIGL · 吉森大学",
    "sec.timeline":     "时间线",

    /* ── Publications ── */
    "title.pubs":       "论文 | 吴坚",
    "pubs.header":      "论文发表",
    "pubs.sub":         "9 篇同行评议论文、预印本及撰写中的手稿",
    "sec.allpubs":      "全部论文",

    /* ── Conferences ── */
    "title.conf":       "会议 | 吴坚",
    "conf.header":      "会议与学术活动",
    "conf.sub":         "9 场会议报告 · 2016 – 2019",
    "sec.present":      "报告列表",

    /* ── Expertise ── */
    "title.expertise":  "专业技能 | 吴坚",
    "expertise.header": "专业技能",
    "expertise.sub":    "编程、单细胞基因组学与表观基因组学技术能力",
    "sec.skills":       "技能",
    "expertise.note":   "综合能力：大型组学数据集的统计分析 · 扎实的分子生物学背景 · 熟悉基因组数据与高维数据分析方法，包括 scRNA-seq（空间）、Bulk RNA-seq、ATAC-seq、Hi-C 与 ChIP-seq。",

    /* ── Tutorials ── */
    "title.tut":        "教程与播客 | 吴坚",
    "tut.header":       "教程与播客",
    "tut.sub":          "科研教程、播客更新，持续连载中",
    "tut.back":         "← 返回全部教程",

    /* ── News ── */
    "title.news":       "动态 | 吴坚 — 肺细胞图谱研究",
    "news.header":      "新闻动态",
    "news.sub":         "论文、基金、邀请报告与实验室动态",
    "news.empty":       "该分类下暂无动态。",
    "news.cat.all":     "全部",
    "news.cat.publication": "论文",
    "news.cat.grant":   "基金",
    "news.cat.award":   "奖项",
    "news.cat.talk":    "报告",
    "news.cat.media":   "媒体",
    "news.cat.team":    "团队",
    "news.cat.tool":    "工具 / 发布",
    "news.readmore":    "阅读更多 →",

    /* ── Gallery ── */
    "title.gallery":    "相册 | 吴坚",
    "gallery.header":   "相册",
    "gallery.sub":      "照片与视频 — 生活、学术与会议",
    "gal.type":         "类型",
    "gal.source":       "来源",
    "gal.all":          "全部",
    "gal.photos":       "📷 照片",
    "gal.videos":       "🎬 视频",
    "gal.allsrc":       "全部来源",
    "gal.local":        "💾 本地",
    "gal.drive":        "☁️ 谷歌云盘",
    "gal.youtube":      "▶️ YouTube",
    "gallery.empty":    "没有符合条件的内容",
    "gal.badge.local":  "💾 本地",
    "gal.badge.drive":  "☁️ 云盘",
    "gal.badge.youtube":"▶️ YouTube",
    "gal.badge.bilibili":"📺 B 站",

    /* ── Contact ── */
    "title.contact":    "联系方式 | 吴坚",
    "contact.header":   "联系方式",
    "contact.sub":      "邮件、地址与社交主页",
    "sec.contactinfo":  "联系信息",
    "ct.email":         "MPI-BN 邮箱",
    "ct.address":       "地址（CPI/CIGL）",
    "ct.scholar":       "谷歌学术",
    "ct.lab":           "导师实验室",
    "sec.message":      "发送留言",
    "contact.note":     "欢迎通过上方邮件联系，或直接使用下方表单留言——我会尽快回复。",
    "ph.name":          "您的姓名",
    "ph.email":         "您的邮箱",
    "ph.message":       "留言内容",
    "btn.send":         "发送留言",

    /* ── 404 页面 ── */
    "title.404":        "页面未找到 | 吴坚",
    "404.code":         "404",
    "404.header":       "页面未找到",
    "404.body":         "链接可能已失效，或者该页面已被移动 / 改名。",
    "404.home":         "返回首页",
    "404.tutorials":    "浏览教程",
    "404.publications": "查看论文"
  }
};

/* 当前语言：localStorage 记忆，默认英文 */
function getLang(){
  try{
    return (localStorage.getItem('lang') === 'zh') ? 'zh' : 'en';
  }catch(e){
    return 'en';
  }
}

/* 取字典文案：当前语言缺失时回退英文，再回退 key 本身 */
function t(key){
  var dict = I18N[getLang()] || I18N.en;
  if(dict[key] !== undefined) return dict[key];
  if(I18N.en[key] !== undefined) return I18N.en[key];
  return key;
}

/* 应用语言：DOM 静态文本 + 原生属性 + 动态内容刷新回调 */
function applyI18n(){
  var lang = getLang();
  document.documentElement.lang = (lang === 'zh') ? 'zh-CN' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(function(el){
    el.placeholder = t(el.getAttribute('data-i18n-ph'));
  });
  document.querySelectorAll('[data-i18n-title]').forEach(function(el){
    el.title = t(el.getAttribute('data-i18n-title'));
  });
  /* 动态区块（render.js 渲染的内容）由各页面注册回调后重渲染 */
  (window.__langCallbacks || []).forEach(function(fn){
    try{ fn(); }catch(e){ /* 单页异常不影响其他区块 */ }
  });
}

/* 切换语言（导航栏按钮） */
function toggleLang(){
  var next = (getLang() === 'zh') ? 'en' : 'zh';
  try{ localStorage.setItem('lang', next); }catch(e){}
  applyI18n();
}

document.addEventListener('DOMContentLoaded', applyI18n);
