#!/usr/bin/env python3
"""
MindSea 知识图谱健康检查器

检查知识图谱健康状况：
- 孤立页面（无入链无出链）
- 断链（指向不存在的页面）
- 双向链接合规性
- Frontmatter 必填字段验证
- 链接密度（每页 <2 条 wikilink 为警告）

Exit codes: 0=健康, 1=有警告, 2=有错误
纯 Python 3.10+ 标准库，只读操作。
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ── 颜色支持 ──────────────────────────────────────────────
def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_COLOR = _supports_color()

def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text

def red(t: str) -> str:    return _c(31, t)
def yellow(t: str) -> str:  return _c(33, t)
def green(t: str) -> str:   return _c(32, t)
def bold(t: str) -> str:    return _c(1, t)

# ── 常量 ──────────────────────────────────────────────────
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
KV_RE = re.compile(r"^(\w+)\s*:\s*(.+)$", re.MULTILINE)
REQUIRED_FIELDS = {"title", "type", "domain", "status", "created"}

VAULT_DIRS = [
    "personal", "learning", "business", "media", "creative",
    "raw", "log-work", "_system", "_weekly", "scripts",
]

# ── 解析工具 ──────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict[str, str]:
    """从 markdown 文本提取 frontmatter 键值对"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    body = m.group(1)
    return {k.lower().strip(): v.strip() for k, v in KV_RE.findall(body)}


def extract_wikilinks(text: str) -> list[str]:
    """提取所有 wikilink 目标（不含 alias 部分）"""
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(text)]


def slugify(path: Path) -> str:
    """将文件路径转为知识库中的 slug（不含 .md）"""
def slugify(path: Path) -> str:
    """将文件路径转为知识库中的 slug（不含 .md）"""
    return path.stem


def load_vault(vault_root: Path) -> dict:
    """
    加载整个知识库，返回:
      pages: {slug: {path, frontmatter, links, text}}
      all_slugs: set[str]
      slug_aliases: {full_rel_path_stem: slug}  — for resolving path-style wikilinks
    """
    pages: dict[str, dict] = {}
    slug_aliases: dict[str, str] = {}
    for md in vault_root.rglob("*.md"):
        rel_parts = md.relative_to(vault_root).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        slug = slugify(md)
        pages[slug] = {
            "path": md,
            "frontmatter": parse_frontmatter(text),
            "links": extract_wikilinks(text),
            "text": text,
        }
        # Register path-based alias: e.g. "learning/concepts/agentic-ai-workflow" -> "agentic-ai-workflow"
        rel_stem = str(md.relative_to(vault_root).with_suffix(""))
        slug_aliases[rel_stem] = slug
        slug_aliases[slug] = slug  # self-alias
    return pages, set(pages.keys()), slug_aliases


def resolve_link(link_target: str, slug_aliases: dict) -> str | None:
    """Resolve a wikilink target to its canonical slug."""
    # Direct match
    if link_target in slug_aliases:
        return slug_aliases[link_target]
    # Try stripping path prefix
    stem = Path(link_target).stem
    if stem in slug_aliases:
        return slug_aliases[stem]
    return None

# ── 检查项 ──────────────────────────────────────────────

SYSTEM_STEMS = {"index", "log", "README", "CLAUDE", "AGENTS", "WORKFLOW", "SCHEMA"}

def check_frontmatter(pages: dict) -> list[tuple[str, str]]:
    """检查 frontmatter 缺失必填字段（跳过系统文件）"""
    errors = []
    for slug, info in pages.items():
        if slug in SYSTEM_STEMS or slug.startswith("2026-W"):
            continue
        fm = info["frontmatter"]
        missing = REQUIRED_FIELDS - fm.keys()
        if missing:
            errors.append((slug, f"缺少必填字段: {', '.join(sorted(missing))}"))
    return errors


def check_orphans(pages: dict, all_slugs: set) -> list[str]:
    """孤立页面：既无入链也无出链"""
    # 收集所有被链接到的 slug
    linked_by: dict[str, set] = defaultdict(set)
    for slug, info in pages.items():
        for target in info["links"]:
            linked_by[target].add(slug)

    orphans = []
    for slug in all_slugs:
        has_out = bool(pages[slug]["links"])
        has_in = slug in linked_by and bool(linked_by[slug])
        if not has_out and not has_in:
            orphans.append(slug)
    return sorted(orphans)


def check_broken_links_v2(pages: dict, slug_aliases: dict) -> list[tuple[str, str]]:
    """断链：指向不存在的页面（支持路径格式解析）"""
    broken = []
    for slug, info in pages.items():
        for target in info["links"]:
            resolved = resolve_link(target, slug_aliases)
            if resolved is None:
                broken.append((slug, target))
    return broken


def check_bidirectional_v2(pages: dict, slug_aliases: dict) -> list[tuple[str, str]]:
    """双向链接检查：A→B 但 B↛A（支持路径格式解析）"""
    missing = []
    for slug, info in pages.items():
        for target in info["links"]:
            resolved = resolve_link(target, slug_aliases)
            if resolved and resolved in pages and slug not in pages[resolved]["links"]:
                missing.append((slug, target))
    return missing


def check_link_density(pages: dict) -> list[tuple[str, int]]:
    """链接密度：wikilink 数 < 2 的页面"""
    sparse = []
    for slug, info in pages.items():
        n = len(info["links"])
        if n < 2:
            sparse.append((slug, n))
    return sparse

# ── 主逻辑 ──────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="MindSea 知识图谱健康检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes: 0=健康, 1=有警告, 2=有错误",
    )
    parser.add_argument("vault", nargs="?", default=".",
                        help="知识库根目录路径 (默认当前目录)")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出结果")
    args = parser.parse_args()

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(red(f"错误: 目录不存在 {vault_root}"), file=sys.stderr)
        return 2

    pages, all_slugs, slug_aliases = load_vault(vault_root)
    if not pages:
        print(yellow("警告: 未找到任何 .md 文件"))
        return 1

    # 执行所有检查
    fm_errors = check_frontmatter(pages)
    orphans = check_orphans(pages, all_slugs)
    broken = check_broken_links_v2(pages, slug_aliases)
    bidir_missing = check_bidirectional_v2(pages, slug_aliases)
    sparse = check_link_density(pages)

    has_error = bool(fm_errors or broken)
    has_warn = bool(orphans or bidir_missing or sparse)

    if args.json:
        result = {
            "total_pages": len(pages),
            "frontmatter_errors": [{"page": s, "msg": m} for s, m in fm_errors],
            "orphan_pages": orphans,
            "broken_links": [{"from": s, "to": t} for s, t in broken],
            "bidirectional_missing": [{"from": s, "to": t} for s, t in bidir_missing],
            "sparse_pages": [{"page": s, "links": n} for s, n in sparse],
            "status": "error" if has_error else ("warn" if has_warn else "ok"),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(bold(f"\n═══ ═══ MindSea 健康报告 ═══ ═══  共 {len(pages)} 页\n"))

        # Frontmatter 错误
        if fm_errors:
            print(red(f"✘ Frontmatter 错误 ({len(fm_errors)})"))
            for s, m in fm_errors:
                print(f"  • {bold(s)}: {m}")
            print()

        # 断链
        if broken:
            print(red(f"✘ 断链 ({len(broken)})"))
            for s, t in broken:
                print(f"  • {bold(s)} → [[{red(t)}]]")
            print()

        # 孤立页面
        if orphans:
            print(yellow(f"⚠ 孤立页面 ({len(orphans)})"))
            for s in orphans:
                print(f"  • {s}")
            print()

        # 双向链接缺失
        if bidir_missing:
            print(yellow(f"⚠ 双向链接缺失 ({len(bidir_missing)})"))
            for s, t in bidir_missing[:20]:  # 截断避免刷屏
                print(f"  • {bold(s)} → [[{t}]]  (t 未反链)")
            if len(bidir_missing) > 20:
                print(f"  ... 共 {len(bidir_missing)} 条")
            print()

        # 链接密度
        if sparse:
            print(yellow(f"⚠ 链接密度不足 ({len(sparse)})"))
            for s, n in sparse:
                print(f"  • {bold(s)}: {n} 条链接 (建议 ≥2)")
            print()

        # 总结
        if not has_error and not has_warn:
            print(green("✔ 所有检查通过，知识图谱状态健康！"))
        elif has_error:
            print(red(f"✘ 发现 {len(fm_errors) + len(broken)} 个错误"))
        else:
            print(yellow(f"⚠ 有警告但无错误"))

    return 2 if has_error else (1 if has_warn else 0)


if __name__ == "__main__":
    sys.exit(main())