---
title: "template — 这里写标题"
date: 2026-07-16
summary: "这里写一句话摘要，会显示在列表卡片和搜索引擎摘要里，建议 1-2 句话，不超过 150 字符左右。"
type: tutorial
tags: ["Jian Wu", "jwtools", "R", "Seurat", "标签3"]
cover: "https://jianwu-atlas.github.io/assets/img/logos/wu_jian_lockup.png"
#cover: "https://jianwu-atlas.github.io/assets/img/logos/jwtools_logo_social_preview.png"
#cover: "https://github.com/jianwu-atlas/jwtools/raw/main/man/figures/logo.png"
---

## 小节标题

这里开始写正文内容，支持标准 Markdown 语法。

### 代码块示例

```r
library(Seurat)
obj <- CreateSeuratObject(counts = mat)
obj <- NormalizeData(obj)
```

### 图片示例

如果需要插入图片，先把图片放到 `assets/img/tutorials/` 目录下，然后这样引用：

![描述文字](../assets/img/tutorials/your-image.png)

### 表格示例

| 参数 | 说明 |
|---|---|
| `min.cutoff` | 设置颜色映射下限 |
| `max.cutoff` | 设置颜色映射上限 |

### 列表示例

- 第一点
- 第二点
  - 子要点

正文可以随意写多个二级/三级标题、代码块、图片、表格、加粗 **重点内容**、行内代码 `like_this()`，Markdown 语法都会被正确渲染成 HTML。

