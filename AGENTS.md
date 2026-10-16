# AGENTS.md · jianwu-atlas.github.io（公网学术首页）

> Jian 的**职业学术主页**（Bioinformatician / Lung Aging / LncRNA）。静态 HTML，push main 即发布到 https://jianwu-atlas.github.io/。私人版镜像在 `jianwu-atlas-private`。

## 定位
- **纯职业导向**：导航/正文围绕研究、发表、会议、专长、教程、新闻。
- 个人兴趣（如德语学习）只以**低调 footer 链接**呈现，不进主导航，避免稀释专业印象。

## 主要页面
`index.html` / `experience.html` / `publications.html` / `conferences.html` / `expertise.html` / `tutorials.html` / `news.html` / `gallery.html` / `contact.html`；数据在 `assets/js/data/*.js`，渲染 `assets/js/render.js`。

## 部署
- GitHub Pages：`git push` main 即发布（`*.github.io` 国内常不可达）。

## 中英文切换 (i18n)
- 语言包 + 切换逻辑在 `assets/js/i18n.js`：`I18N.{en,zh}` 字典，`t(key)` / `applyI18n()` / `toggleLang()`，存 `localStorage('lang')`，默认英文。
- **静态 UI 文本**：元素加 `data-i18n="key"`（textContent）、`data-i18n-ph`（placeholder）、`data-i18n-title`（title）。
- **数据驱动区块**（`assets/js/data/*.js` → `render.js`）：数据对象写 `field_zh` 中文备选，`render.js` 用 `pick(obj,'field')`（中文模式优先 `_zh`，缺失回退原字段）取值；切换语言时各页注册 `window.__langCallbacks.push(() => renderXxx(...))` 重渲染。
- **教程（中文为主、可选英文）**：`tutorials-src/*.md` 单文件，Front Matter 可加 `title_en` / `summary_en`，`build_tutorials.py` 有值才写入 `tutorials.js`，`render.js` 用 `pickEn()` 在英文模式优先取 `_en`；不填则回退中文，**正文不翻译、无需两份文件**。
- 一次性迁移脚本 `scripts/add_i18n_marks.py`（`--apply` 才写入；默认 dry-run），每处替换断言恰好命中一次，避免误伤。
- 新增英文文案先补 `i18n.js` 的 en/zh 两键，再在 HTML 挂 `data-i18n`；勿在页面硬编码双语。

## 构建与性能脚本
```bash
python3 scripts/build_tutorials.py    # 教程页 + tutorials.js + sitemap.xml + feed.xml + 正文 img 懒加载
python3 scripts/optimize_gallery.py   # 相册 WebP 缩略图(长边1200/q80) 并写 gallery.js 的 thumb 字段
python3 scripts/add_lazy_loading.py   # 静态页 <img> 加 loading="lazy"(排除首屏图)
python3 scripts/audit_images.py       # 图片引用审计:被引用 vs 孤儿
```
- `SITE_BASE_URL`（`build_tutorials.py`）= `https://jianwu-atlas.github.io`，与私有库的 workers.dev 版区分，**勿混用**。
- 相册图片约定：`gallery.js` 的 `thumb:` 指缩略图、`src:` 留原图；`render.js` 网格用 `g.thumb || g.src`，灯箱用 `item.src`（按需全分辨率）。
- 新增 `404.html`（GitHub Pages 自动用于未知路径，`noindex, follow`），i18n 键 `404.*`。
- 上传新相册照片后**必须重跑** `optimize_gallery.py`，否则该图仍以原图体积进首屏。

## 最近更新
- 2026-10-17：性能与 SEO 收口——`build_tutorials.py` 自动生成 `sitemap.xml`（9 顶层页 + 全部教程详情页）与 `feed.xml`（RSS 最新 20 条）；新增 `scripts/optimize_gallery.py` / `add_lazy_loading.py` / `audit_images.py`；相册照片改 WebP 缩略图（`assets/img/gallery/thumbs/`，本库 46.98MB → 1.76MB，其中 `DZL 2025合照.jpg` 单张 27.92MB → 129KB）；全站 `<img>` 懒加载（129 张中 112 lazy / 17 首屏保持 eager）；新增 `404.html`。
- 2026-10-15：`index.html` 的 `footer-copyright` 行新增个人链接 **Englishheft（个人 · 英语单词）** → https://jianwu-atlas.github.io/englishheft/（英语单词站同域子路径，与 Deutschheft 并列的姊妹站；内容为《15000 英语单词口袋书》蒸馏）。
- 2026-10-15：全站接入中英文切换（i18n）——新增 `assets/js/i18n.js` + 导航右上角即时切换；9 个主页面与教程文章模板挂 `data-i18n`；`render.js` 加 `pick`/`pickEn`，数据文件补 `_zh` 字段；`build_tutorials.py` 支持可选 `title_en`/`summary_en`；图库英文 caption 补 `caption_zh`。
- 2026-10-13：`index.html` 的 `footer-copyright` 行末尾新增个人链接 **Deutschheft（个人 · 德语学习）** → https://jianwu-atlas.github.io/deutschheft/（德语学习站同域子路径；国内访问用独立域名 deutschheft.edgeone.cool，不经本首页）。
