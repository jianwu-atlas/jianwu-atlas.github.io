---
title: "如何查看jwtools包里有哪些可用函数"
date: 2026-07-16
summary: "介绍 6 种在 R 中查找已安装包导出函数的方法，从 ls() 到 NAMESPACE 源码核查，并以自建包 jwtools 为例演示。"
type: tutorial
tags: ["Jian Wu", "R", "jwtools", 'R包开发']
cover: "https://jianwu-atlas.github.io/assets/img/logos/jwtools_logo_social_preview.png"
---

在 R 中查找 `jwtools` 包里有哪些可用函数，有几种常用方法，按推荐程度列出：

## 1. `ls()` 查看已加载包的所有导出对象（最常用）

```r
library(jwtools)
ls("package:jwtools")
```

## 2. 不加载包，直接列出所有导出函数

```r
ls(getNamespace("jwtools"), all.names = FALSE)
# 或
ls("package:jwtools")  # 需先 library(jwtools)
```

## 3. 查看包的帮助文档索引（会打开一个 HTML 页面，列出所有带文档的函数）

```r
help(package = "jwtools")
```

## 4. 用 `lsf.str()` 同时看函数和参数签名（更直观）

```r
library(jwtools)
lsf.str("package:jwtools")
```

## 5. 如果你想连**未导出（internal）的函数**也一起看

```r
ls(getNamespace("jwtools"), all.names = TRUE)
```

## 6. 查看包的 NAMESPACE 文件（源码层面，最准确）

如果你本地有源码（比如 `~/Documents/GitHub/jwtools`），可以直接看：

```bash
cat NAMESPACE
```

或者在 R 里：

```r
# 如果包是通过 devtools::load_all() 加载的
devtools::load_all("~/path/to/jwtools")
ls("package:jwtools")
```

---

### 💡 针对你目前 jwtools 的情况

根据之前记忆，你的包里目前至少包含：
- `qs_save_workspace()`
- `qs_load_workspace()`

如果你想快速确认这两个（以及可能后续新增的函数）是否都已正确导出并可用，最直接的方式是：

```r
library(jwtools)
ls("package:jwtools")
```

如果输出为空或缺函数，很可能是 `NAMESPACE` 没有正确 `export()`，或者包还没有重新 `devtools::document()` + 重装。


