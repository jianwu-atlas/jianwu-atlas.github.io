# jianwu-atlas.github.io — Jian Wu 学术主页（多页版 + 相册/播客）

个人学术主页，风格延续深森绿 (`#1b3a2d`) + 铜色 (`#c17f5a`) 配色。
采用"数据驱动"架构：新增论文/会议/教程/照片，只需编辑 `assets/js/data/` 里的
一个 JS 数组，无需改动任何 HTML/CSS。

**在线访问：** https://jianwu-atlas.github.io/

---

## 📁 目录结构

```
jianwu-atlas.github.io/
├─ index.html                首页 —— 头像/简介 + Featured Publications + 最新教程
├─ experience.html           科研与工作经历（时间线）
├─ publications.html         全部论文列表
├─ conferences.html          会议与学术活动
├─ expertise.html            技能标签（R/Python/Seurat/ATAC-seq 等）
├─ tutorials.html            教程/播客列表
├─ gallery.html               相册与视频（本地 + Google Drive 双来源，双重 Tab 筛选）
├─ contact.html               联系方式 + Google Map + 留言表单
│
├─ tutorials/                 ← 每一集教程/播客的详情页
│  ├─ ep00-intro.html
│  ├─ ep01-scrna-pipeline.html
│  └─ template.html          ← 复制此文件 = 新建一集
│
└─ assets/
   ├─ css/
   │  └─ style.css            全站唯一样式表（改配色只改这一个文件）
   ├─ js/
   │  ├─ main.js              导航高亮 / 暗色模式 / 移动端菜单
   │  ├─ render.js            渲染引擎（读 data → 生成卡片，通常不用改）
   │  └─ data/                 ★ 你以后主要编辑的地方
   │     ├─ experience.js
   │     ├─ publications.js
   │     ├─ conferences.js
   │     ├─ expertise.js
   │     ├─ tutorials.js
   │     └─ gallery.js         相册数据（本地图片路径 + Google Drive 文件ID）
   └─ img/
      ├─ avatar.jpg            头像（固定文件名，换头像直接替换同名文件）
      └─ gallery/               本地照片存放位置
```

---

## 🧩 为什么这样设计（方便你以后维护）

| 特点 | 说明 |
|---|---|
| **导航条统一** | 每个页面顶部的 `<nav id="navbar">` 结构完全一致，以后新增页面（比如 Blog），只要在所有页面顶部同步加一个 `<a>` 标签即可 |
| **内容与展示分离** | Experience / Publications / Conferences / Expertise / Tutorials / Gallery 全部由 `assets/js/data/*.js` 里的数组驱动，改内容不用碰 HTML |
| **样式集中管理** | 只有一份 `style.css`，换整站配色只需改文件顶部 `:root` 里的几个 CSS 变量 |
| **暗色模式内置** | 右上角🌙按钮切换，状态存在浏览器本地，刷新页面不会丢失 |
| **Gallery 双重分类统计** | 按「类型（照片/视频）」和「来源（本地/Google Drive）」两排独立 Tab 筛选，每个 Tab 上都带实时数量徽章，两排可以同时组合筛选 |
| **Contact 页嵌入地图** | Google Maps 免费嵌入（无需 API Key/无需绑卡），默认卫星混合视图 |
| **用户主页部署** | 仓库名精确匹配 `jianwu-atlas.github.io`，GitHub 自动识别为用户主页，无需手动配置 Pages 分支，网址简洁无二级路径 |

---

## ✏️ 日常更新速查表

| 想做什么 | 编辑哪个文件 |
|---|---|
| 加一篇新论文 | `assets/js/data/publications.js` → 复制一条对象，改内容，放数组最前面 |
| 加一次新会议 | `assets/js/data/conferences.js` → 加一行 `{year, text}` |
| 加一段新工作经历 | `assets/js/data/experience.js` → 加一个对象 |
| 加一项新技能 | `assets/js/data/expertise.js` → 找到对应分组的 `skills` 数组加一条 |
| 写一集新播客/教程 | ① 复制 `tutorials/template.html` 改名改内容 ② 在 `assets/js/data/tutorials.js` 加一条记录指向它 |
| 加照片/视频 | 见下方「相册与视频」章节 |
| 换头像 | 直接用新图片覆盖 `assets/img/avatar.jpg`（保持同名） |
| 改全站配色 | 只改 `assets/css/style.css` 顶部 `:root{ }` 里的颜色变量 |
| 加/改社交链接 | `index.html` 的 `.social-grid` 区块 + `contact.html` 的 `.contact-grid` 区块，两处需同步修改 |
| 换办公地址/地图位置 | `contact.html` 里的地址文字 + Google Map `iframe` 的 `src` 里的地址参数，两处需同步修改 |

---

## 🖼️ 相册与视频（Gallery）—— 本地 + Google Drive 双来源

`gallery.html` 支持两种照片/视频来源混用，页面顶部有**两排独立的 Tab**：

- **第一排（Type）**：All / 📷 Photos / 🎬 Videos
- **第二排（Source）**：All Sources / 💾 Local / ☁️ Google Drive

每个 Tab 上都会显示该分类下的实际数量（例如 `Photos (5)`、`Google Drive (2)`），
两排 Tab 可以**同时组合筛选**（比如只看"来自 Drive 的视频"）。

### 方式 A — 本地图片（推荐用于头像、封面等重要固定图片）

1. 把图片放进 `assets/img/gallery/` 文件夹
2. 在 `assets/js/data/gallery.js` 里加一条：
```js
{ type: "photo", source: "local", src: "assets/img/gallery/你的文件名.jpg", caption: "描述文字" }
```
> ⚠️ 注意：GitHub Pages 区分大小写，文件名务必和代码里写的完全一致（含大小写）。

### 方式 B — Google Drive 直链（推荐用于日常照片/播客录音视频，省仓库空间）

**第一步** — 在 Google Drive 里找到文件 → 右键 →「共享」→ 常规访问权限改为
**「知道链接的任何人」+「查看者」**

**第二步** — 复制分享链接，形如：
```
https://drive.google.com/file/d/1AbCDefGhIJKLmnop/view?usp=sharing
```
中间这段 `1AbCDefGhIJKLmnop` 就是文件 ID。

**第三步** — 填进 `assets/js/data/gallery.js`：

照片：
```js
{
  type: "photo",
  source: "drive",
  src: "https://drive.google.com/thumbnail?id=你的文件ID&sz=w1000",
  caption: "描述文字"
}
```

视频：
```js
{
  type: "video",
  source: "drive",
  src: "https://drive.google.com/file/d/你的文件ID/preview",
  thumb: "https://drive.google.com/thumbnail?id=你的文件ID&sz=w500",
  caption: "描述文字"
}
```

**验证权限是否生效：** 在浏览器无痕窗口（不登录账号）打开缩略图链接，
能看到图片才算成功；显示"无权限"说明第一步共享设置没做对。

> ⚠️ Google Drive 直链有隐性流量限制，访客量大时可能偶尔加载失败。
> 重要的固定图片（头像、代表作封面）建议用方式 A，日常生活照/播客片段用方式 B 更省事。

---

## 📍 Contact 页面地图（Google Maps，免费版）

`contact.html` 里嵌入了 Google Maps，显示 CPI/CIGL 办公地址，采用**免费嵌入方式**：

```html
<iframe src="https://www.google.com/maps?q=地址&t=h&output=embed"></iframe>
```

- **无需申请 API Key，无需绑定信用卡**
- `t=h` 参数指定默认显示**卫星 + 街道名混合视图**（去掉此参数则是普通地图模式，`t=k` 是纯卫星图无标注）
- 用户可以在嵌入的地图里自由缩放、拖动、切换图层模式
- 局限：没有侧边地点信息卡和"获取路线"导航按钮（如果需要这些高级功能，可以改用 Google Maps Embed API + API Key 的完整版，需要在 [Google Cloud Console](https://console.cloud.google.com/) 申请，详见 Google 官方文档）

---

## 🎙️ Tutorials / 播客 —— 新建一集的方法

1. 复制 `tutorials/template.html`，改名为例如 `ep02-xxx.html`
2. 打开新文件，改标题、日期和正文内容
3. 打开 `assets/js/data/tutorials.js`，在数组里加一条：
```js
{
  title: "Ep.02 — 标题",
  date: "2025-02-01",
  summary: "一句话简介",
  url: "tutorials/ep02-xxx.html",
  type: "podcast",
  tags: ["标签1", "标签2"]
}
```
保存后 `tutorials.html` 和首页的「Latest Tutorials」会自动显示新条目。

---

## 🚀 部署到 GitHub Pages（用户主页方式）

本仓库使用 GitHub 的「用户主页」（User Site）规则部署：

- 仓库名**必须**精确等于 `你的GitHub用户名.github.io`（本仓库对应 `jianwu-atlas.github.io`）
- 一个 GitHub 账号**只能有一个**这种用户主页仓库
- **不需要**手动去 Settings → Pages 设置分支，只要仓库名匹配规则，GitHub 会自动识别并部署
- 网址是最简洁的根路径形式：`https://jianwu-atlas.github.io/`（没有额外的项目名路径）

### 日常更新已上线的网站

**方式 A —— GitHub Desktop（推荐，图形界面无需命令行）**
1. 本地修改好文件
2. 打开 GitHub Desktop，确认 Current Repository 是 `jianwu-atlas.github.io`
3. 左侧 Changes 会自动列出改动的文件
4. 填写 Commit 说明 → 点击 **Commit to main**
5. 点击 **Push origin**
6. 约 1-3 分钟后线上自动更新

**方式 B —— 网页手动编辑（适合改动单个文件）**
1. 打开仓库 → 点击要改的文件 → 右上角铅笔图标 ✏️
2. 编辑内容 → 拉到底部 **Commit changes**

**方式 C —— 批量重新上传（适合改动多个文件）**
1. 仓库首页 → **Add file → Upload files**
2. 把改动过的文件重新拖进去（文件名相同会自动覆盖旧版本）
3. **Commit changes**

---

## 💻 本地预览

直接双击打开 `index.html` 即可在浏览器里预览（`file://` 协议下功能完全正常）。
如果遇到某些浏览器安全策略限制，可以用 Python 起一个本地服务器：
```bash
python3 -m http.server 8000
```
然后访问 `http://localhost:8000`。

---

## 🐞 常见问题排查

| 现象 | 常见原因 | 解决方法 |
|---|---|---|
| 页面空白 / 数据不显示 | JS 文件里有语法错误（比如误用 `#` 做注释，JS 不支持） | 打开浏览器控制台（`Cmd+Option+I`）查看 Console 报错信息；JS 注释请用 `//` 而不是 `#` |
| 某张图片显示黑色方块 | 图片文件不存在或路径/文件名大小写不匹配 | 检查 `assets/img/gallery/` 文件夹里文件是否真实存在，文件名大小写是否完全一致 |
| Google Drive 图片/视频显示"无权限" | 共享权限没设置为"知道链接的任何人" | 回到 Drive 重新设置共享权限为 Viewer + Anyone with the link |
| Tab 数量统计显示 `—` 不是数字 | render.js 没有加载成功或版本过旧 | 确认 `assets/js/render.js` 是最新完整版本，且在 HTML 里的引入顺序是 `data → render.js → main.js` |
| 页面顶部内容被导航栏遮挡 | CSS `calc()` 函数里加号/减号前后缺少空格 | `calc()` 里必须写成 `calc(var(--nav-h) + 2rem)`，无空格会导致整条声明失效 |
| 某个联系方式排版占了一整行，导致后面项目错位 | HTML 里该项带了 `ct-row-full` 这个 class | 如果不需要横跨整行显示，去掉 `ct-row-full`，改回普通的 `class="ct-row"` |
| 浏览器窗口显示网页比预期小，四周有大片空白 | 浏览器窗口本身没有最大化（不是网页问题） | 双击浏览器标题栏或点击绿色圆点按钮让窗口铺满屏幕；网页内容本身的 `max-width` 限制是刻意设计，保证宽屏下阅读体验 |
| 表单提交后跳转到 404 页面 | `contact.html` 里 `_next` 隐藏字段的链接路径不对 | 确认是 `https://jianwu-atlas.github.io/index.html`（根路径，不带任何仓库名） |
| Footer/头部 GitHub 图标链接打不开 | 链接还指向旧的项目页面仓库名 | 全局搜索检查是否还有残留的旧仓库名，统一替换为 `jianwu-atlas.github.io` |
| 保存的 .html 文件打不开 | 记事本/TextEdit 保存时格式或编码不对 | Windows 记事本另存为要选"所有文件(*.*)"；Mac TextEdit 要先切换"制作纯文本" |

---

© 2025 Jian Wu · CPI / MPI-HLR · JLU Gießen · DZL / ILH