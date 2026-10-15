#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tutorials.py
===================================================================
教程/播客发布流水线（Tutorials & Podcast Build Pipeline）

功能：
  1. 扫描 tutorials-src/ 目录下所有 Markdown 源文件（含 YAML front matter）
  2. 将每篇 Markdown 渲染为独立的静态 HTML 页面 → tutorials/{slug}.html
  3. **全量重建**（而非追加）assets/js/data/tutorials.js
     —— 这是本次重构的核心：彻底避免"追加文本导致漏加逗号"的历史 bug

设计原则（对应你之前遇到的问题）：
  - 旧版脚本用字符串 rfind("];") 定位插入点，属于"脆弱的文本手术"，
    一旦前一个元素末尾没有逗号，插入后就会产生非法 JS 语法。
  - 新版脚本不再"插入"，而是每次都：
        读取全部 md 源文件的 metadata → 排序 → 用 Python 生成完整的
        JS 数组文本 → 整体覆盖写入 tutorials.js
    这样"逗号"永远是由代码统一生成的，不存在人为遗漏的可能。

依赖：
  pip install pyyaml markdown
===================================================================
"""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path
from datetime import date, datetime
from typing import Any

import yaml
import markdown as md_lib


# ────────────────────────────────────────────────────────────────
# 1. 路径配置（按你的仓库结构调整，如有出入请告诉我实际路径）
# ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ 的上一级 = 仓库根目录

TUTORIALS_SRC_DIR   = REPO_ROOT / "tutorials-src"                 # Markdown 源文件目录
TUTORIALS_OUT_DIR   = REPO_ROOT / "tutorials"                      # 生成的静态 HTML 输出目录
TUTORIALS_JS_PATH   = REPO_ROOT / "assets" / "js" / "data" / "tutorials.js"
TUTORIAL_TEMPLATE   = REPO_ROOT / "tutorials" / "tutorial_template.html"

REQUIRED_FIELDS = ["title", "date", "summary", "type"]  # front matter 必填字段
DEFAULT_TYPE    = "tutorial"                             # tutorial / podcast


# ────────────────────────────────────────────────────────────────
# 2. Front Matter 解析（不依赖额外第三方 frontmatter 包，手写即可）
# ────────────────────────────────────────────────────────────────
FRONT_MATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?\n)---\s*\n(.*)$", re.DOTALL
)


def parse_front_matter(raw_text: str, filename: str) -> tuple[dict, str]:
    """
    解析 Markdown 文件头部的 YAML front matter。

    返回:
        meta  - dict，front matter 解析出的元数据
        body  - str，front matter 之后的正文 Markdown 文本
    """
    match = FRONT_MATTER_PATTERN.match(raw_text)
    if not match:
        sys.exit(
            f"[ERROR] '{filename}' 缺少 YAML front matter（必须以 '---' 开头和结尾）。\n"
            f"请检查文件头部格式，例如：\n"
            f"---\n"
            f'title: "Ep.02 — Trajectory Analysis"\n'
            f"date: 2025-11-20\n"
            f'summary: "..."\n'
            f"type: tutorial\n"
            f'tags: ["Monocle2", "R"]\n'
            f"---\n"
        )

    yaml_block, body = match.group(1), match.group(2)

    try:
        meta = yaml.safe_load(yaml_block) or {}
    except yaml.YAMLError as e:
        sys.exit(f"[ERROR] '{filename}' front matter YAML 解析失败：{e}")

    # 校验必填字段，缺失就立刻报错，而不是生成半残缺的条目
    missing = [f for f in REQUIRED_FIELDS if f not in meta or meta[f] in (None, "")]
    if missing:
        sys.exit(
            f"[ERROR] '{filename}' front matter 缺少必填字段: {missing}\n"
            f"必填字段列表: {REQUIRED_FIELDS}"
        )

    # date 字段统一转成字符串 "YYYY-MM-DD"（YAML 可能自动解析成 datetime.date 对象）
    if isinstance(meta["date"], (date, datetime)):
        meta["date"] = meta["date"].strftime("%Y-%m-%d")

    meta.setdefault("tags", [])
    meta.setdefault("type", DEFAULT_TYPE)
    meta.setdefault("cover", "")
    meta.setdefault("draft", False)
    # 可选英文覆盖字段（教程以中文为主）：存在即写入 tutorials.js 的 title_en/summary_en，
    # 由 render.js 的 pickEn() 在英文模式下优先取用；缺失则回退中文 title/summary 正文。
    meta.setdefault("title_en", "")
    meta.setdefault("summary_en", "")

    return meta, body.strip()


# ────────────────────────────────────────────────────────────────
# 3. Markdown → HTML 正文渲染
# ────────────────────────────────────────────────────────────────
def render_markdown_body(md_text: str) -> str:
    """
    使用 python-markdown 将正文转换为 HTML。
    开启 fenced_code / tables / toc 等常用扩展，便于代码教程排版。
    """
    return md_lib.markdown(
        md_text,
        extensions=[
            "fenced_code",      # ```python 代码块
            "tables",           # Markdown 表格
            "toc",              # 自动生成锚点，便于教程内跳转
            "sane_lists",
            "codehilite",       # 代码高亮（需配合 pygments CSS）
        ],
        extension_configs={
            "codehilite": {"guess_lang": False}
        },
    )


# ────────────────────────────────────────────────────────────────
# 4. 生成单篇教程的静态 HTML 页面
# ────────────────────────────────────────────────────────────────
def render_tutorial_page(meta: dict, html_body: str) -> str:
    """
    读取模板文件 tutorial_template.html，用简单的 {{placeholder}} 占位符替换。
    如果你的模板引擎不是这种写法，请告诉我实际的模板占位符格式，我再对应调整。
    """
    if not TUTORIAL_TEMPLATE.exists():
        sys.exit(f"[ERROR] 找不到模板文件: {TUTORIAL_TEMPLATE}")

    template = TUTORIAL_TEMPLATE.read_text(encoding="utf-8")

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in meta["tags"])

    replacements = {
        "{{TITLE}}":        meta["title"],
        "{{TITLE_EN}}":     meta.get("title_en", ""),
        "{{DATE}}":         meta["date"],
        "{{SUMMARY}}":      meta["summary"],
        "{{SUMMARY_EN}}":   meta.get("summary_en", ""),
        "{{TYPE}}":         meta["type"],
        "{{TAGS_HTML}}":    tags_html,
        "{{CONTENT}}":      html_body,
        "{{COVER}}":        meta.get("cover", ""),
    }

    page_html = template
    for placeholder, value in replacements.items():
        page_html = page_html.replace(placeholder, value)

    return page_html


# ────────────────────────────────────────────────────────────────
# 5. 扫描全部 Markdown 源文件，生成 metadata 列表 + 输出 HTML 页面
# ────────────────────────────────────────────────────────────────
def build_all_tutorials() -> list[dict]:
    """
    遍历 tutorials-src/*.md：
      - 解析 front matter
      - 跳过以下划线 "_" 开头的文件（约定作为模板/草稿，不参与发布）
      - 跳过 draft: true 的草稿
      - 渲染正文 HTML 并写入 tutorials/{slug}.html
      - 收集每篇的 metadata（附带 slug、url）用于后续重建 tutorials.js

    返回：
      按 date 降序排列的 metadata 列表（最新的在前面）
    """
    if not TUTORIALS_SRC_DIR.exists():
        sys.exit(f"[ERROR] 源目录不存在: {TUTORIALS_SRC_DIR}")

    TUTORIALS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(TUTORIALS_SRC_DIR.glob("*.md"))

    # >>> 新增：跳过以下划线开头的文件（约定作为模板/草稿，不参与发布）
    # 例如 tutorials-src/_template.md 会被永久保留在源码目录里当模板，
    # 但既不会生成 tutorials/_template.html，也不会被写入 tutorials.js
    skipped_template_files = [f for f in md_files if f.stem.startswith("_")]
    md_files = [f for f in md_files if not f.stem.startswith("_")]
    for f in skipped_template_files:
        print(f"[skip] '{f.name}' 以下划线开头，视为模板文件，跳过发布。")
    # <<< 新增结束

    if not md_files:
        print(f"[warn] '{TUTORIALS_SRC_DIR}' 下没有找到任何 .md 文件，跳过构建。")
        return []

    all_meta: list[dict] = []
    seen_slugs: set[str] = set()

    for md_path in md_files:
        slug = md_path.stem  # 文件名（不含扩展名）作为 slug，例如 ep02-trajectory-analysis

        raw_text = md_path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw_text, md_path.name)

        if meta.get("draft"):
            print(f"[skip] '{md_path.name}' 标记为 draft，跳过发布。")
            continue

        if slug in seen_slugs:
            sys.exit(f"[ERROR] slug 重复: '{slug}'，请检查文件名是否冲突。")
        seen_slugs.add(slug)

        html_body = render_markdown_body(body)
        page_html = render_tutorial_page(meta, html_body)

        out_path = TUTORIALS_OUT_DIR / f"{slug}.html"
        out_path.write_text(page_html, encoding="utf-8")
        print(f"[ok]  生成页面: {out_path.relative_to(REPO_ROOT)}")

        meta["slug"] = slug
        meta["url"] = f"tutorials/{slug}.html"
        all_meta.append(meta)

    # 按日期降序排序，最新的教程排在数组最前面（首页/列表页展示顺序）
    all_meta.sort(key=lambda m: m["date"], reverse=True)
    return all_meta


# ────────────────────────────────────────────────────────────────
# 6. 全量重建 tutorials.js（核心修复：不再"追加"，而是"整体重写"）
# ────────────────────────────────────────────────────────────────
def format_js_entry(meta: dict) -> str:
    """
    把单条 metadata 格式化成 tutorials.js 里的一个 JS 对象字面量文本。
    使用 json.dumps 处理字符串转义（引号、特殊字符），避免手写拼接引发的转义错误。
    """
    tags_js = json.dumps(meta["tags"], ensure_ascii=False)

    # 可选英文覆盖字段：有值才输出，保持中文源文件简洁（无 _en 即回退中文）
    extra_lines = ""
    if meta.get("title_en"):
        extra_lines += f'    title_en: {json.dumps(meta["title_en"], ensure_ascii=False)},\n'
    if meta.get("summary_en"):
        extra_lines += f'    summary_en: {json.dumps(meta["summary_en"], ensure_ascii=False)},\n'

    return (
        "  {\n"
        f'    date: {json.dumps(meta["date"])},\n'
        f'    title: {json.dumps(meta["title"], ensure_ascii=False)},\n'
        f'    summary: {json.dumps(meta["summary"], ensure_ascii=False)},\n'
        f'    url: {json.dumps(meta["url"])},\n'
        f'    cover: {json.dumps(meta.get("cover", ""))},\n'
        f'    type: {json.dumps(meta["type"])},\n'
        f"{extra_lines}"
        f"    tags: {tags_js}\n"
        "  }"
    )


def build_tutorials_js(all_meta: list[dict]) -> None:
    """
    用全部 metadata **整体重新生成** tutorials.js 文件内容并覆盖写入。

    关键点：
      - 逗号由 Python 的 ",\n".join(...) 统一处理，
        每个元素之间必然有且只有一个逗号，最后一个元素之后没有多余逗号。
      - 这就是为什么这种写法从架构上杜绝了"手动插入漏加逗号"的 bug。
    """
    entries_text = ",\n".join(format_js_entry(m) for m in all_meta)

    js_content = (
        "// ⚠️ 本文件由 scripts/build_tutorials.py 自动生成，请勿手动编辑！\n"
        "// 如需增删教程，请修改 tutorials-src/ 下的 Markdown 源文件后重新运行构建脚本。\n"
        "\n"
        "const tutorialsData = [\n"
        f"{entries_text}\n"
        "];\n"
    )

    TUTORIALS_JS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TUTORIALS_JS_PATH.write_text(js_content, encoding="utf-8")
    print(f"[ok]  已全量重建: {TUTORIALS_JS_PATH.relative_to(REPO_ROOT)} "
          f"（共 {len(all_meta)} 条）")


# ────────────────────────────────────────────────────────────────
# 7. 简单的语法自检：写完之后立刻用 Node（如果有）或正则做基本校验
# ────────────────────────────────────────────────────────────────
def sanity_check_js(js_path: Path) -> None:
    """
    写入后做一次轻量语法自检，尽早发现问题而不是等浏览器报错。
    优先尝试调用系统的 node 做真正的语法检查；没有 node 就退化为括号配对检查。
    """
    import subprocess
    import shutil

    if shutil.which("node"):
        result = subprocess.run(
            ["node", "--check", str(js_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            sys.exit(
                f"[ERROR] 生成的 tutorials.js 语法检查未通过！\n{result.stderr}\n"
                f"构建已中止，请检查 build_tutorials.py 逻辑或源 Markdown 内容中的特殊字符。"
            )
        print("[ok]  tutorials.js 通过 node --check 语法自检")
    else:
        # 退化方案：简单检查大括号 / 中括号是否配对
        text = js_path.read_text(encoding="utf-8")
        if text.count("{") != text.count("}") or text.count("[") != text.count("]"):
            sys.exit("[ERROR] tutorials.js 括号数量不匹配，疑似语法错误，构建已中止。")
        print("[ok]  tutorials.js 通过基础括号配对自检（建议安装 Node.js 以获得完整语法检查）")


# ────────────────────────────────────────────────────────────────
# 8. 主入口
# ────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("开始构建 Tutorials & Podcast 页面...")
    print("=" * 60)

    all_meta = build_all_tutorials()

    if not all_meta:
        print("[warn] 没有可发布的教程条目，tutorials.js 未更新。")
        return

    build_tutorials_js(all_meta)
    sanity_check_js(TUTORIALS_JS_PATH)

    print("=" * 60)
    print(f"构建完成 ✅  共发布 {len(all_meta)} 篇教程/播客")
    for m in all_meta:
        print(f"   - [{m['date']}] {m['title']}  →  {m['url']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
