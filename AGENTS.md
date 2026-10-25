# AGENTS.md · jianwu-atlas.github.io（公网学术首页）

> Jian 的**职业学术主页**（Bioinformatician / Lung Cell Atlas Research）。静态 HTML，push main 即发布到 https://jianwu-atlas.github.io/。私人版镜像在 `jianwu-atlas-private`。

## 定位
- **纯职业导向**：导航/正文围绕研究、发表、会议、专长、教程、新闻。
- 个人兴趣（如德语学习）**在公开站完全不出现**（2026-10-25 Jian 决定：连 footer 链接也删掉；此前是「低调 footer 链接」）。语言站只在私有站主导航保留。

## ⚠️ 与私有站 jianwu-atlas-private 的刻意差异（同步时勿覆盖）
两站共用同一套 CSS/JS/构建脚本，但以下三点**故意不同**，从私有库 `cp` 文件过来时必须保留本站版本：
| 项 | 公开站（本站） | 私有站 |
| -- | -- | -- |
| hero 大 logo | `assets/img/logos/Jian_Wu_logo.png`（lungs lockup 1378×585） | `wu_jian_lockup.png`（吴坚书法版） |
| 全站标识（导航/favicon/apple-touch/footer自标/教程页） | `assets/img/logos/jianwu_atlas_emblem.png`（公开学术徽章：肺 + JIAN WU RESEARCH GROUP 圆徽，深森林绿+铜） | `wu_jian_icon.png`（吴坚书法+鹿，**私人印记**） |
| 主导航语言站链接 | **一个都没有**（导航与 footer 均无） | 有 Deutschheft / Englishheft |
| `SITE_BASE_URL` | `https://jianwu-atlas.github.io` | `https://jianwu-atlas-private.jian-wu.workers.dev` |

- 回归修复脚本（幂等、带命中次数断言）：`scripts/revert_public_nav_and_hero.py`
  —— 恢复 hero lungs lockup、删主导航两个语言站链接、删首页 footer 语言站链接、把 og:image / twitter:image 对齐回 lungs lockup。
- 历史教训（2026-10-17）：一次从私有库整文件 `cp`（含 `index.html` 与 9 个根页面）把上面三点全部覆盖，导致 hero 变书法版、语言站链接跑进主导航、首页 footer 链接被删。**同步只应 cp 明确需要同步的文件，且改完必须 `git diff <同步前commit> -- <file>` 复核**。

## 主要页面
`index.html` / `experience.html` / `publications.html` / `conferences.html` / `expertise.html` / `tutorials.html` / `news.html` / `gallery.html` / `contact.html`；数据在 `assets/js/data/*.js`，渲染 `assets/js/render.js`。

## 部署
- GitHub Pages：`git push` main 即发布（`*.github.io` 国内常不可达）。
- 私有站 `jianwu-atlas-private`：Cloudflare Workers + **GitHub 自动部署**，push main 即部署（**勿手动 `wrangler deploy`**，纯冗余；实测 push 后约 16 秒自动部署完成）；全站在 Cloudflare Access 认证门后，curl/外网验证不了线上内容（返回 302）。

## 中英文切换 (i18n)
- 语言包 + 切换逻辑在 `assets/js/i18n.js`：`I18N.{en,zh}` 字典，`t(key)` / `applyI18n()` / `toggleLang()`，存 `localStorage('lang')`，默认英文。
- **静态 UI 文本**：元素加 `data-i18n="key"`（textContent）、`data-i18n-ph`（placeholder）、`data-i18n-title`（title）。
- **数据驱动区块**（`assets/js/data/*.js` → `render.js`）：数据对象写 `field_zh` 中文备选，`render.js` 用 `pick(obj,'field')`（中文模式优先 `_zh`，缺失回退原字段）取值；切换语言时各页注册 `window.__langCallbacks.push(() => renderXxx(...))` 重渲染。
- **教程（中文为主、可选英文）**：`tutorials-src/*.md` 单文件，Front Matter 可加 `title_en` / `summary_en`，`build_tutorials.py` 有值才写入 `tutorials.js`，`render.js` 用 `pickEn()` 在英文模式优先取 `_en`；不填则回退中文，**正文不翻译、无需两份文件**。
- **正文整条切换**（与字段回退互补）：当两种语言是**整句不同**的独立文案（如语录、slogan），不做逐字段 `_zh`/`_en` 回退，而是让数据对象**同时**携带 `zh` 与 `en` 两个整串字段，`render.js` 按当前语言**整条**切换（`lang==='zh'?q.zh:q.en`）。**选型**：只有部分字段随语言变 → 用 `pick`/`pickEn` 回退；两种语言是不同完整句子 → 用整条切换。
- **⚠️ `data-i18n` 的 textContent 陷阱**：`applyI18n()` 对带 `data-i18n` 的元素是**整段替换 `textContent`**，会**抹掉**其内的 `<a>`/子节点。「一行既有静态文案又要嵌链接」时，`<p>` 与 `<a>` 都**不要**挂 `data-i18n`，只把 `data-i18n` 挂在**内层 `<span>`** 上，链接结构切语言时天然存活。
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
- 2026-10-25（晚）：**页脚合作机构 logo 重新排序**（Jian 定，两站同序）——自家徽章仍居最左且不参与排序；其后依次 Pullamsetti Lab → CPI → MPI HLR → DZL DataLung → JLU Gießen → IMPRS-MOB → ILH（原序是 JLU → MPI → CPI → DZL → IMPRS → ILH → Pullamsetti）。
- 2026-10-25（晚）：**公开站彻底移除个人语言站链接**（Jian 决定）——`index.html` 页脚 `footer-copyright` 去掉 Deutschheft / Englishheft 两行，`404.html` 的移动导航里同款两行也一并删（那两行本就是同步事故遗留、与「公开站主导航不放语言站」的约定相悖）。回归脚本 `scripts/revert_public_nav_and_hero.py` 同步改造：footer 那段从「恢复」改为「删除」，`ROOT_PAGES` 补入 `404.html`，仍保持幂等（命中数断言）。私有站不动，语言站链接继续留在其主导航。
- 2026-10-25（晚）：首页 SEO 文案统一到 Atlas 品牌——`meta description` / `og:description` / `twitter:description` / Schema.org Person `description` 与 `news.html` 描述改为以 "building single-cell lung cell atlases" 起句，保留 lung aging / COPD/IPF / LncRNA / ERV/TE 关键词。
- 2026-10-25（深夜）：**学术徽章收紧版**（commit `2f3e6f8`）——Jian 反馈"公开网站 logo 空白太多"。实测三因：① 白底四角在深绿导航上成白块 → 环外改透明；② 内容仅占内环 93% → 按中心 ×1.05（401→421，不越内环 428）；③ 细外环在 42px 下亚像素不可见 → 加粗至 30px/1000px（≈1.3px@42px）。 artwork/配色/双环设计不变；apple-touch-icon.png 换白底 180px 渲染；`jianwu_avatar_1000.png` 同款更新（GitHub 头像需手动重传）。线上已验证（corner alpha=0）。
- 2026-10-25（晚）：**公开站品牌标识重构——学术徽章上位，私人鹿盘退出公开站**（commit `da07a26`）。Jian 明确鹿盘（吴坚书法+鹿）是**私人 logo**，公开学术站须用公开徽章。① 新增 `assets/img/logos/jianwu_atlas_emblem.png`（512px，肺 + JIAN WU RESEARCH GROUP 圆徽，深森林绿 H150 S55 + 铜 H26 S62）作为全站标识：导航图标 / favicon / apple-touch / footer 自标 / 教程与新闻页品牌标，15 个页面 59 处引用整体切换，HTML 仅换文件名；② `jianwu_avatar_1000.png`（外部品牌资产）同款加深——**改仓库文件不会自动更新 GitHub 头像，需手动重传**；③ `wu_jian_icon.png` 恢复原版灰绿、公开站零引用（当日早先的深紫改色 `5d00524` 随之撤回）；④ root `apple-touch-icon.png` 换为徽章渲染图。另核实：鹿盘图标版底部签名被裁（完整 lockup 底部为「Wu Jian」花体+长横线，图标只剩「Wu」）——属私有站资产问题，本站未改。
- 2026-10-25（早）：深紫方案改色 `wu_jian_icon.png` + hero 加深（commit `5d00524`）——**当日晚上已被 `da07a26` 取代**：该图标实为私人 logo，公开站改持学术徽章；hero 的深森林绿+铜加深版保留有效。
- 2026-10-21：AGENTS.md「中英文切换 (i18n)」节补两条约定——①「正文整条切换」模型（数据对象同时带 `zh`+`en` 双整串字段，与 `pick`/`pickEn` 字段回退互补）；② `data-i18n` 的 `textContent` 陷阱（会抹掉内嵌 `<a>`，需内嵌链接时把 `data-i18n` 挂内层 `<span>`）。**纯文档改动，不影响公开网站任何可见内容。**
- 2026-10-17（晚）：**回滚同步回归**（详见上方「刻意差异」节）——hero 恢复 `Jian_Wu_logo.png`；9 个根页面主导航移除 Deutschheft / Englishheft；首页 footer 语言站链接恢复；og:image / twitter:image 对齐回 lungs lockup。新增幂等修复脚本 `scripts/revert_public_nav_and_hero.py`。
- 2026-10-17：性能与 SEO 收口——`build_tutorials.py` 自动生成 `sitemap.xml`（9 顶层页 + 全部教程详情页）与 `feed.xml`（RSS 最新 20 条）；新增 `scripts/optimize_gallery.py` / `add_lazy_loading.py` / `audit_images.py`；相册照片改 WebP 缩略图（`assets/img/gallery/thumbs/`，本库 46.98MB → 1.76MB，其中 `DZL 2025合照.jpg` 单张 27.92MB → 129KB）；全站 `<img>` 懒加载（129 张中 112 lazy / 17 首屏保持 eager）；新增 `404.html`。
- 2026-10-15：`index.html` 的 `footer-copyright` 行新增个人链接 **Englishheft（个人 · 英语单词）** → https://jianwu-atlas.github.io/englishheft/（英语单词站同域子路径，与 Deutschheft 并列的姊妹站；内容为《15000 英语单词口袋书》蒸馏）。
- 2026-10-15：全站接入中英文切换（i18n）——新增 `assets/js/i18n.js` + 导航右上角即时切换；9 个主页面与教程文章模板挂 `data-i18n`；`render.js` 加 `pick`/`pickEn`，数据文件补 `_zh` 字段；`build_tutorials.py` 支持可选 `title_en`/`summary_en`；图库英文 caption 补 `caption_zh`。
- 2026-10-13：`index.html` 的 `footer-copyright` 行末尾新增个人链接 **Deutschheft（个人 · 德语学习）** → https://jianwu-atlas.github.io/deutschheft/（德语学习站同域子路径；国内访问用独立域名 deutschheft.edgeone.cool，不经本首页）。
