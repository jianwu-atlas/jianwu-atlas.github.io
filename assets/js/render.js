/* ============================================================
   render.js — 通用渲染引擎
   以后新增内容只需修改 assets/js/data/*.js，本文件无需改动
   ------------------------------------------------------------
   i18n 约定（与 assets/js/i18n.js 配合）：
   - 数据对象里的 "xxx_zh" 字段是中文备选；
     pick(obj,'xxx') 在中文模式下优先取 xxx_zh，缺失则回退 xxx。
   - 换语言后由页面注册 window.__langCallbacks 回调重渲染，
     渲染函数天然支持重复调用（innerHTML 全量重绘）。
============================================================ */

/* 当前语言（i18n.js 未加载时安全回退 en） */
function curLang(){
  return (typeof getLang === 'function') ? getLang() : 'en';
}

/* 语言回退取值：中文模式优先 field+'_zh'，否则用原 field */
function pick(obj, field){
  if(!obj) return obj;
  if(curLang() === 'zh'){
    var zh = obj[field + '_zh'];
    if(zh !== undefined && zh !== null && zh !== '') return zh;
  }
  return obj[field];
}

/* 语言回退取值（英文覆盖方向）：英文模式优先 field+'_en'，否则用原 field
   用于 tutorials 这类「中文为主、可选英文」的数据，方向与 pick 的 _zh 相反 */
function pickEn(obj, field){
  if(!obj) return obj;
  if(curLang() === 'en'){
    var en = obj[field + '_en'];
    if(en !== undefined && en !== null && en !== '') return en;
  }
  return obj[field];
}

/* 1. Experience */
function renderExperience(containerId, data){
  const el = document.getElementById(containerId);
  if(!el) return;
  el.innerHTML = data.map(e => {
    const points = (curLang() === 'zh' && e.points_zh) ? e.points_zh : e.points;
    return `
    <div class="exp-block">
      <div class="exp-logo">${e.icon}</div>
      <div>
        <p class="exp-role">${pick(e, 'role')}</p>
        <p class="exp-org">${pick(e, 'org')}</p>
        <p class="exp-date">${pick(e, 'date')}</p>
        <div class="exp-body">
          ${e.advisor ? `<p><strong>${pick(e, 'advisor')}</strong></p>` : ''}
          <ul>${points.map(p => `<li>${p}</li>`).join('')}</ul>
          <div class="tags">
            ${e.tags.map(tg => `<span class="tag tag-${tg.type}">${pick(tg, 'label')}</span>`).join('')}
          </div>
        </div>
      </div>
    </div>`;
  }).join('');
}

/* 2. Publications */
function renderPublications(containerId, data, featuredOnly = false){
  const el = document.getElementById(containerId);
  if(!el) return;
  const list = featuredOnly ? data.filter(p => p.featured) : data;
  el.innerHTML = list.map((p, i) => `
    <div class="pub-row">
      <span class="pub-num">${i + 1}</span>
      <div>
        <span class="pub-badge badge-${p.badgeType}">${p.badge}</span>
        <p class="pub-title">${pick(p, 'title')}</p>
        <p class="pub-authors">${p.authors}</p>
        <p class="pub-journal">${p.journal || ''}</p>
        <div class="pub-links">
          ${p.links.map(l => `<a href="${l.url}" class="pub-link ${l.primary ? 'primary' : ''}" target="_blank">${pick(l, 'label')}</a>`).join('')}
        </div>
      </div>
    </div>
  `).join('');
}

/* 3. Conferences */
function renderConferences(containerId, data){
  const el = document.getElementById(containerId);
  if(!el) return;
  el.innerHTML = data.map((c, i) => `
    <div class="conf-row">
      <span class="conf-num">${i + 1}</span>
      <p class="conf-text"><strong>${c.year}</strong> — ${pick(c, 'text')}</p>
    </div>
  `).join('');
}

/* 4. Expertise */
function renderExpertise(containerId, data){
  const el = document.getElementById(containerId);
  if(!el) return;
  el.innerHTML = data.map(group => `
    <div class="exp-card">
      <p class="exp-card-label">${pick(group, 'label')}</p>
      <div class="skill-tags tags">
        ${group.skills.map(s => `<span class="tag tag-${s.type}">${pick(s, 'name')}</span>`).join('')}
      </div>
    </div>
  `).join('');
}

/* ============================================================
   5. Tutorials / Podcast
   ------------------------------------------------------------
   设计说明：
   - renderTutorials() 内部永远自己做一次"按 date 降序排序"，
     不信任调用方传入数组的原始顺序。
     （历史 bug：之前调用方各自用 .reverse() / .slice(-2).reverse()
      去"猜"数据顺序，猜错了导致首页和列表页顺序相反、且首页展示的
      是最旧的两篇。现在把排序责任收归到渲染函数内部，调用方只需要
      声明"要不要分组"和"要不要限制数量"这两个展示层意图。）
   - options.groupByYear: 是否按年份插入分组标题（用于 tutorials.html
     的完整列表页，类似 News 页面的年份分组，但不引入分类筛选）。
   - options.limit: 只取最新 N 条（用于首页 "Latest Tutorials" 预览）。
     limit 在排序 *之后* 应用，保证拿到的一定是"最新的 N 条"，
     而不是数组物理位置上的最后 N 条。
============================================================ */

/* 从 'YYYY-MM-DD' 形式的日期字符串中提取年份；
   容错处理空值/异常格式，避免生成 "Undefined" 分组标题 */
function getYearFromDate(dateStr){
  if(!dateStr || typeof dateStr !== 'string' || dateStr.length < 4){
    return "Undated";
  }
  return dateStr.slice(0, 4);
}

/* 生成单个教程卡片的 HTML，抽成独立小函数，
   避免 groupByYear 分支和非分组分支各写一遍卡片模板导致重复维护 */
function tutorialCardHTML(t){
  // tutorials 以中文为主：英文模式优先取 title_en / summary_en，否则回退中文
  const title = pickEn(t, 'title');
  const summary = pickEn(t, 'summary');
  return `
    <a class="tut-card" href="${t.url}">
      <div class="tut-cover">
        ${t.cover ? `<img src="${t.cover}" alt="${title}" loading="lazy" decoding="async">` : (t.type === 'podcast' ? '🎙️' : '📝')}
      </div>
      <div class="tut-body">
        <p class="tut-date">${t.date}</p>
        <p class="tut-title">${title}</p>
        <p class="tut-summary">${summary}</p>
        <div class="tags tut-tags">
          ${t.tags.map(x => `<span class="tag tag-g">${x}</span>`).join('')}
        </div>
      </div>
    </a>
  `;
}

function renderTutorials(containerId, data, options = {}){
  const el = document.getElementById(containerId);
  if(!el) return;

  const { groupByYear = false, limit = null } = options;

  // 关键修复点：排序永远在函数内部完成，调用方不需要也不应该自己 reverse/slice
  let sorted = sortByDateDesc(data, 'date');

  // limit 在排序之后应用 —— 保证 "最新 N 条" 是按真实日期算出来的，
  // 而不是数组物理顺序的头 N 条或尾 N 条
  if (limit !== null){
    sorted = sorted.slice(0, limit);
  }

  if (!groupByYear){
    // 首页 "Latest Tutorials" 走这个分支：扁平网格，不需要年份标题
    el.innerHTML = sorted.map(t => tutorialCardHTML(t)).join('');
    return;
  }

  // tutorials.html 完整列表页走这个分支：按年份插入分组标题
  // 注意：.tut-year-label 需要在 CSS 里设置 grid-column: 1 / -1，
  // 否则它会被当成 grid 里的一个普通格子，而不是跨行标题
  const years = [...new Set(sorted.map(t => getYearFromDate(t.date)))];

  let html = "";
  years.forEach(year => {
    html += `<div class="tut-year-label">${year}</div>`;
    sorted
      .filter(t => getYearFromDate(t.date) === year)
      .forEach(t => { html += tutorialCardHTML(t); });
  });

  el.innerHTML = html;
}

/* ============================================================
   6. Gallery — 支持 type（photo/video）+ source（local/drive/youtube/bilibili）
      多重筛选，并提供数量统计辅助函数
   ------------------------------------------------------------
   修复说明（相对旧版）：
   ① getGalleryCounts()：不再硬编码 local/drive 两个 key，
      改为动态扫描 data 里出现过的所有 source 值自动统计。
      以后新增任何 source（如 "vimeo"/"x"），这里都不需要再改。
   ② renderGallery() 徽章逻辑：从"二选一三元表达式"改为
      GALLERY_SOURCE_BADGE_MAP 查表，支持任意数量的 source 分类。
   ③ openLightbox()：核心修复点。原逻辑只对 source==='drive'
      的视频使用 <iframe>，其余视频一律走 <video src=...> 标签，
      导致 YouTube 这类"embed 网页型"视频源无法播放（<video>
      标签只能解析真实的媒体文件如 .mp4，不能解析网页 embed 链接）。
      现在改为：只要是"iframe 类视频源"（drive / youtube / bilibili 等），
      统一用 <iframe>；只有真正的本地媒体文件（source === 'local'
      且是 .mp4 等直链）才用 <video> 标签。
   ④ 图片懒加载 + 缩略图约定：
      - 所有由本文件渲染的 <img> 都带 loading="lazy" decoding="async"；
        首屏图（导航 logo / hero / 头像）在静态 HTML 里单独排除，不使用此属性。
      - 相册照片：thumb 字段指向缩略图（assets/img/gallery/thumbs/*.webp，
        由 scripts/optimize_gallery.py 生成），src 仍保留原图路径。
        渲染时用 g.thumb || g.src 回退，因此没有缩略图的新照片会自动
        退回显示原图，不会出现裂图。
      - openLightbox() 继续使用 item.src（原图），因为灯箱是用户主动
        点击后打开的，理应给全分辨率。
============================================================ */

/* 归一化来源：单来源条目用 source/src，多平台条目用 sources 数组
   （同一部影片可同时有 youtube + bilibili，合并为一张卡） */
function gallerySources(item){
  if (Array.isArray(item.sources) && item.sources.length) return item.sources;
  return [{ source: item.source, src: item.src }];
}

/* 统计各分类的数量，供 Tab 徽章显示
   —— 动态版本：自动适配 galleryData 里出现过的任意 source 值 */
function getGalleryCounts(data){
  const counts = {
    all:   data.length,
    photo: data.filter(g => g.type === 'photo').length,
    video: data.filter(g => g.type === 'video').length
  };

  // 动态扫描所有出现过的 source（多平台条目按每个平台各计一次）
  data.forEach(g => gallerySources(g).forEach(s => {
    counts[s.source] = (counts[s.source] || 0) + 1;
  }));

  // 类别（category）统计：counts.category[<名称>]
  counts.category = { all: data.length };
  data.forEach(g => {
    if (g.category) counts.category[g.category] = (counts.category[g.category] || 0) + 1;
  });

  return counts;
}

/* Source 徽章的展示映射表：中英文案
   新增 source 类型时，只需要在这里加一行，
   renderGallery() 和 openLightbox() 都不需要再改 */
const GALLERY_SOURCE_BADGE_MAP = {
  local:    { en: '💾 Local',    zh: '💾 本地' },
  drive:    { en: '☁️ Drive',    zh: '☁️ 云盘' },
  youtube:  { en: '▶️ YouTube',  zh: '▶️ YouTube' },
  bilibili: { en: '📺 Bilibili', zh: '📺 B 站' }
};

/* 徽章文案：按当前语言取 en/zh（未配置语言时回退 en，再回退 source 名） */
function galleryBadgeText(key){
  var m = GALLERY_SOURCE_BADGE_MAP[key] || { en: key };
  return (curLang() === 'zh') ? (m.zh || m.en) : m.en;
}

/* 判断某个视频 item 是否需要用 <iframe> 播放
   （凡是"embed 网页型"视频源都属于此类，与 source 类型解耦，
    以后加 vimeo 等，只需要把对应 source 加进这个数组） */
const IFRAME_VIDEO_SOURCES = ['drive', 'youtube', 'bilibili'];

/* 来源徽章文案：单来源显示一个，多平台用 " · " 连接 */
function galleryBadgeLabel(item){
  return gallerySources(item)
    .map(s => galleryBadgeText(s.source))
    .join(' · ');
}

/* 渲染 Gallery 列表；filters = {type, category, source}，各自可取 'all' */
function renderGallery(containerId, data, filters = {type:'all', category:'all', source:'all'}){
  const el = document.getElementById(containerId);
  if(!el) return;

  let list = data;
  if(filters.type && filters.type !== 'all'){
    list = list.filter(g => g.type === filters.type);
  }
  if(filters.category && filters.category !== 'all'){
    list = list.filter(g => g.category === filters.category);
  }
  if(filters.source && filters.source !== 'all'){
    list = list.filter(g => gallerySources(g).some(s => s.source === filters.source));
  }

  // 按日期降序 —— 最新在前（sortByDateDesc 见文件末尾，函数声明会提升）
  list = sortByDateDesc(list, 'date');

  if(list.length === 0){
    el.innerHTML = `<p style="grid-column:1/-1;text-align:center;color:var(--text-3);padding:2rem 0">${t('gallery.empty')}</p>`;
    window.__currentGalleryList = [];
    return;
  }

  // 按年份分组：list 已按日期降序，年份标题自然降序。
  // 只插入标题、不重排数组，因此 openLightboxByIndex(i) 的索引仍与 list 一一对应。
  let html = '';
  let currentYear = null;
  list.forEach((g, i) => {
    const year = (g.date || '').slice(0, 4) || 'Undated';
    if (year !== currentYear) {
      currentYear = year;
      html += `<div class="gal-year-label">${year}</div>`;
    }

    // 徽章查表，找不到则给一个兜底文案（避免未来漏配置时页面报错/空白）
    const badge = galleryBadgeLabel(g);
    const caption = pick(g, 'caption') || '';

    html += `
    <div class="gal-item" onclick="openLightboxByIndex(${i})">
      ${g.type === 'video'
        ? `<img src="${g.thumb}" alt="${caption}" loading="lazy" decoding="async"><div class="gal-play">▶</div>`
        : `<img src="${g.thumb || g.src}" alt="${caption}" loading="lazy" decoding="async">`}
      <span class="gal-source-badge">${badge}</span>
      <div class="gal-caption">${caption}</div>
    </div>
  `;
  });

  el.innerHTML = html;

  window.__currentGalleryList = list;
}

function openLightboxByIndex(idx){
  const item = window.__currentGalleryList[idx];
  if(item) openLightbox(item);
}

/* 核心修复：判断视频用 <iframe> 还是 <video> 标签
   - IFRAME_VIDEO_SOURCES 里的 source（drive / youtube / bilibili）→ <iframe>
   - 其余（例如 source==='local' 且直接存的是 .mp4 文件）→ <video> 标签 */
function iframeFor(src){
  return `<iframe src="${src}" width="800" height="480" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen frameborder="0"></iframe>`;
}

function openLightbox(item){
  const lb = document.getElementById('lightbox');
  const body = document.getElementById('lightboxBody');
  if(!lb || !body) return;

  const srcs = gallerySources(item);

  if(item.type === 'video' && srcs.some(s => IFRAME_VIDEO_SOURCES.includes(s.source))){
    let html = '';
    // 多平台（如 YouTube + Bilibili）→ 顶部给一排切换按钮
    if(srcs.length > 1){
      html += '<div class="lb-src-tabs">';
      srcs.forEach((s, i) => {
        html += `<button class="lb-src-btn${i === 0 ? ' active' : ''}" data-i="${i}" onclick="lbSwitchSource(${i})">${galleryBadgeText(s.source)}</button>`;
      });
      html += '</div>';
    }
    html += `<div id="lbFrameWrap">${iframeFor(srcs[0].src)}</div>`;
    body.innerHTML = html;
    window.__lbSrcs = srcs;
  } else if(item.type === 'video'){
    body.innerHTML = `<video src="${item.src}" controls autoplay></video>`;
  } else {
    body.innerHTML = `<img src="${item.src}" alt="${item.caption || ''}">`;
  }
  lb.classList.add('open');
}

/* 切换多平台视频的播放源（灯箱内） */
function lbSwitchSource(i){
  const srcs = window.__lbSrcs || [];
  if(!srcs[i]) return;
  const wrap = document.getElementById('lbFrameWrap');
  if(wrap) wrap.innerHTML = iframeFor(srcs[i].src);
  document.querySelectorAll('.lb-src-btn').forEach(b => {
    b.classList.toggle('active', Number(b.dataset.i) === i);
  });
}

function closeLightbox(){
  const lb = document.getElementById('lightbox');
  const body = document.getElementById('lightboxBody');
  if(lb) lb.classList.remove('open');
  if(body) body.innerHTML = '';
}

document.addEventListener('DOMContentLoaded', () => {
  const lb = document.getElementById('lightbox');
  if(lb){
    lb.addEventListener('click', (e) => { if(e.target === lb) closeLightbox(); });
  }
  document.addEventListener('keydown', (e) => { if(e.key === 'Escape') closeLightbox(); });
});

// ============================================================
// News helpers — single source of truth: item.sortDate (YYYY-MM-DD)
// Year labels and chronological order are ALWAYS derived from
// sortDate automatically. Never rely on a manually-typed `year`
// field — this avoids "year label vs. displayed date" mismatches.
// ============================================================

/* 通用日期降序排序：优先使用调用方指定的 field，
   其次回退 sortDate，再回退 date（兼容 News 和 Tutorials 两套数据结构）*/
function sortByDateDesc(data, field){
  return [...data].sort((a, b) => {
    const da = (field && a[field]) || a.sortDate || a.date;
    const db = (field && b[field]) || b.sortDate || b.date;
    if (!da) return 1;
    if (!db) return -1;
    return String(db).localeCompare(String(da));
  });
}

/* 从 sortDate（YYYY-MM-DD）中提取年份，用于 News 分组标题
   （Tutorials 用的是上面新增的 getYearFromDate，字段名不同，故分开写，
    避免为了共用一个函数而引入 "field 名称到底是 date 还是 sortDate" 的隐藏耦合）*/
function getYearFromItem(item){
  if (item.sortDate) return item.sortDate.slice(0, 4);
  if (item.year) return String(item.year);
  return "Undated";
}

const NEWS_BADGE_MAP = {
  publication: { label: "Publication", cls: "news-badge-pub" },
  grant:       { label: "Grant",       cls: "news-badge-grant" },
  award:       { label: "Award",       cls: "news-badge-award" },
  talk:        { label: "Talk",        cls: "news-badge-talk" },
  media:       { label: "Media",       cls: "news-badge-media" },
  team:        { label: "Team",        cls: "news-badge-team" },
  tool:        { label: "Tool / Release", cls: "news-badge-tool" }
};

/* News 徽章中文案（与 i18n.js 的 news.cat.* 同源，缺失时回退英文 label） */
const NEWS_BADGE_LABEL_ZH = {
  publication: "论文", grant: "基金", award: "奖项", talk: "报告",
  media: "媒体", team: "团队", tool: "工具 / 发布"
};
function newsBadgeLabel(cat){
  var m = NEWS_BADGE_MAP[cat] || { label: cat, cls: "news-badge-team" };
  if(curLang() === 'zh') return NEWS_BADGE_LABEL_ZH[cat] || m.label;
  return m.label;
}

/* News 默认「阅读更多」文案（数据未提供 linkText 时） */
function newsReadMoreText(){
  return (typeof t === 'function') ? t('news.readmore') : 'Read more →';
}

// ============================================================
// Render News Timeline (auto-sorted by sortDate, grouped by
// year derived from sortDate — reverse chronological)
// ============================================================
function renderNews(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!data || data.length === 0) {
    container.innerHTML = `<p class="news-empty">${t('news.empty')}</p>`;
    return;
  }

  const sorted = sortByDateDesc(data);
  const years = [...new Set(sorted.map(item => getYearFromItem(item)))];

  let html = "";
  years.forEach(year => {
    html += `<div class="news-year-label">${year}</div>`;
    sorted.filter(item => getYearFromItem(item) === year).forEach(item => {
      const badge = NEWS_BADGE_MAP[item.category] || { label: item.category, cls: "news-badge-team" };
      html += `
        <div class="news-item">
          <div class="news-date">${pick(item, 'date')}</div>
          <div class="news-content">
            <span class="news-badge ${badge.cls}">${newsBadgeLabel(item.category)}</span>
            <p class="news-title">${pick(item, 'title')}</p>
            <p class="news-summary">${pick(item, 'summary')}</p>
            ${item.link ? `<a class="news-link" href="${item.link}" target="${item.link.startsWith('http') ? '_blank' : '_self'}" rel="noopener">${pick(item, 'linkText') || newsReadMoreText()}</a>` : ''}
          </div>
        </div>`;
    });
  });

  container.innerHTML = html;
}

// ============================================================
// Render News Category Filter Tabs (All / Publication / Grant / ...)
// ============================================================
function renderNewsTabs(tabsContainerId, timelineContainerId, data) {
  const tabsContainer = document.getElementById(tabsContainerId);
  if (!tabsContainer) return;

  const categoryOrder = ["all", "publication", "grant", "award", "talk", "media", "team", "tool"];
  const categoryLabels = {
    all:          { en: "All",           zh: "全部" },
    publication:  { en: "Publication",   zh: "论文" },
    grant:        { en: "Grant",         zh: "基金" },
    award:        { en: "Award",         zh: "奖项" },
    talk:         { en: "Talk",          zh: "报告" },
    media:        { en: "Media",         zh: "媒体" },
    team:         { en: "Team",          zh: "团队" },
    tool:         { en: "Tool / Release", zh: "工具 / 发布" }
  };
  const catLabel = (cat) => (curLang() === 'zh') ? (categoryLabels[cat].zh) : (categoryLabels[cat].en);

  const counts = { all: data.length };
  categoryOrder.slice(1).forEach(cat => {
    counts[cat] = data.filter(item => item.category === cat).length;
  });

  let html = "";
  categoryOrder.forEach(cat => {
    const activeClass = cat === "all" ? " active" : "";
    html += `
      <button class="news-tab${activeClass}" data-category="${cat}">
        ${catLabel(cat)}
        <span class="news-tab-count">${counts[cat]}</span>
      </button>`;
  });
  tabsContainer.innerHTML = html;

  const tabs = tabsContainer.querySelectorAll(".news-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      const selected = tab.dataset.category;
      const filtered = selected === "all" ? data : data.filter(item => item.category === selected);
      renderNews(timelineContainerId, filtered);
    });
  });
}

// ============================================================
// Render Compact News Highlights (for homepage preview module)
// ============================================================
function renderNewsHighlights(containerId, data, count = 3) {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!data || data.length === 0) {
    el.innerHTML = `<p class="news-empty">${t('news.empty')}</p>`;
    return;
  }

  const sorted = sortByDateDesc(data);
  const list = sorted.slice(0, count);

  el.innerHTML = list.map(item => {
    const badge = NEWS_BADGE_MAP[item.category] || { label: item.category, cls: "news-badge-team" };
    return `
      <div class="highlight-item">
        <div class="highlight-date">${pick(item, 'date')}</div>
        <div class="highlight-content">
          <span class="news-badge ${badge.cls}">${newsBadgeLabel(item.category)}</span>
          <p class="highlight-title">${pick(item, 'title')}</p>
          <p class="highlight-summary">${pick(item, 'summary')}</p>
          ${item.link ? `<a class="news-link" href="${item.link}" target="${item.link.startsWith('http') ? '_blank' : '_self'}" rel="noopener">${pick(item, 'linkText') || newsReadMoreText()}</a>` : ''}
        </div>
      </div>`;
  }).join('');
}