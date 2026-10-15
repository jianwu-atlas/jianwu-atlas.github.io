"""
批量更新导航栏品牌区（nav-brand）为紧凑双行版本
适用页面：experience / publications / conferences / expertise / tutorials / gallery / contact
使用前请先备份，或在 git 仓库中运行（可通过 git diff 检查改动）
"""

import re
import pathlib

# ── 需要处理的页面列表，按需增减 ──
TARGET_FILES = [
    "experience.html",
    "publications.html",
    "conferences.html",
    "expertise.html",
    "tutorials.html",
    "gallery.html",
    "contact.html",
]

# ── 匹配旧的 nav-brand 结构（允许任意空白/换行差异） ──
OLD_PATTERN = re.compile(
    r'<a href="index\.html" class="nav-brand">\s*'
    r'<img src="assets/img/logos/wu_jian_icon\.png" alt="Jian Wu" class="brand-icon-img">\s*'
    r'Jian Wu\s*'
    r'</a>',
    re.MULTILINE,
)

# ── 替换为紧凑双行版本 ──
NEW_BLOCK = (
    '<a href="index.html" class="nav-brand">\n'
    '      <img src="assets/img/logos/wu_jian_icon.png" alt="Jian Wu" class="brand-icon-img">\n'
    '      <span class="nav-brand-text">\n'
    '        <span class="nav-brand-title">JIAN WU</span>\n'
    '        <span class="nav-brand-sub">Lung Cell Atlas Research</span>\n'
    '      </span>\n'
    '    </a>'
)

def main():
    for fname in TARGET_FILES:
        path = pathlib.Path(fname)
        if not path.exists():
            print(f"⚠️  跳过：{fname} 不存在（请检查文件路径）")
            continue

        text = path.read_text(encoding="utf-8")
        new_text, n_subs = OLD_PATTERN.subn(NEW_BLOCK, text)

        if n_subs == 0:
            print(f"❌ {fname}: 未匹配到旧的 nav-brand 结构，请手动核查该文件的 <nav> 部分")
            continue

        path.write_text(new_text, encoding="utf-8")
        print(f"✅ {fname}: 成功替换 {n_subs} 处")

if __name__ == "__main__":
    main()
