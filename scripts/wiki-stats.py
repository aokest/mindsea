#!/usr/bin/env python3
"""
MindSea 知识图谱统计工具

生成知识图谱统计报告：
- 域/类型分布
- 链接密度分析
- 活跃度（创建/更新时间）
- 健康评分
- 标签云

支持 --json 输出。

纯 Python 3.10+ 标准库，只读操作。
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

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
def cyan(t: str) -> str:    return _c(36, t)
def bold(t: str) -> str:    return _c(1, t)
def dim(t: str) -> str:     return _c(2, t)

# ── 常量 ──────────────────────────────────────────────────
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
KV_RE = re.compile(r"^(\w+)\s*:\s*(.+)$", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

DATE_FORMATS = ["%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"]

# ── 解析工具 ──────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    body = m.group(1)
    return {k.lower().strip(): v.strip() for k, v in KV_RE.findall(body)}


def extract_wikilinks(text: str) -> list[str]:
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(text)]


def parse_date(s: str) -> datetime | None:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None


def get_domain(filepath: Path, vault_root: Path) -> str:
    rel = filepath.relative_to(vault_root)
    return rel.parts[0] if len(rel.parts) > 1 else "_root"


SKIP_DIRS = {"_system", "_weekly", "_publish", "scripts", ".obsidian", ".vault-index", "_archive"}

def load_vault(vault_root: Path) -> list[dict]:
    pages = []
    for md in vault_root.rglob("*.md"):
        rel_parts = md.relative_to(vault_root).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = parse_frontmatter(text)
        links = extract_wikilinks(text)
        pages.append({
            "path": md,
            "domain": get_domain(md, vault_root),
            "frontmatter": fm,
            "links": links,
            "link_count": len(links),
            "text": text,
            "size": md.stat().st_size if md.exists() else 0,
        })
    return pages

# ── 统计计算 ──────────────────────────────────────────────

def domain_breakdown(pages: list[dict]) -> dict[str, int]:
    return dict(Counter(p["domain"] for p in pages).most_common())


def type_breakdown(pages: list[dict]) -> dict[str, int]:
    return dict(Counter(
        p["frontmatter"].get("type", "未分类") for p in pages
    ).most_common())


def link_density_stats(pages: list[dict]) -> dict:
    counts = [p["link_count"] for p in pages]
    if not counts:
        return {"min": 0, "max": 0, "avg": 0, "total_links": 0, "sparse": 0}
    return {
        "min": min(counts),
        "max": max(counts),
        "avg": round(sum(counts) / len(counts), 2),
        "total_links": sum(counts),
        "sparse": sum(1 for c in counts if c < 2),
    }


def activity_stats(pages: list[dict]) -> dict:
    """分析创建/更新时间"""
    created_dates = []
    updated_dates = []
    for p in pages:
        fm = p["frontmatter"]
        if c := fm.get("created"):
            if d := parse_date(c):
                created_dates.append(d)
        if u := fm.get("updated"):
            if d := parse_date(u):
                updated_dates.append(d)

    def _range(dates: list[datetime]) -> dict:
        if not dates:
            return {"earliest": None, "latest": None, "count": 0}
        return {
            "earliest": min(dates).strftime("%Y-%m-%d"),
            "latest": max(dates).strftime("%Y-%m-%d"),
            "count": len(dates),
        }

    return {
        "created": _range(created_dates),
        "updated": _range(updated_dates),
    }


def tag_cloud(pages: list[dict]) -> dict[str, int]:
    counter: Counter = Counter()
    for p in pages:
        tags_raw = p["frontmatter"].get("tags", "")
        if tags_raw:
            tags_raw = tags_raw.strip().strip("[]")
            for tag in tags_raw.split(","):
                tag = tag.strip().strip('"').strip("'").lower()
                if tag and tag not in ("", "[", "]"):
                    counter[tag] += 1
    return dict(counter.most_common(30))


def health_score(pages: list[dict]) -> dict:
    """计算综合健康评分 (0-100)"""
    if not pages:
        return {"score": 0, "details": {}}

    total = len(pages)
    details = {}

    # 1. Frontmatter 完整度 (30 分)
    with_fm = sum(1 for p in pages if p["frontmatter"])
    fm_score = round(30 * with_fm / total)
    details["frontmatter_completeness"] = fm_score

    # 2. 链接密度 (30 分)
    sparse = sum(1 for p in pages if p["link_count"] < 2)
    link_score = round(30 * (1 - sparse / total))
    details["link_density"] = link_score

    # 3. 有标签的页面比例 (20 分)
    with_tags = sum(1 for p in pages if p["frontmatter"].get("tags"))
    tag_score = round(20 * with_tags / total)
    details["tag_coverage"] = tag_score

    # 4. 活跃度 (20 分) — 有 updated 字段的比例
    with_updated = sum(1 for p in pages if p["frontmatter"].get("updated"))
    active_score = round(20 * with_updated / total)
    details["activity"] = active_score

    return {
        "score": fm_score + link_score + tag_score + active_score,
        "details": details,
    }


def bar(value: int, max_val: int, width: int = 20) -> str:
    """生成文本进度条"""
    filled = round(width * value / max_val) if max_val > 0 else 0
    return "█" * filled + "░" * (width - filled)

# ── 主逻辑 ──────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="MindSea 知识图谱统计工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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

    pages = load_vault(vault_root)
    if not pages:
        print(yellow("警告: 未找到任何 .md 文件"))
        return 1

    # 计算各项统计
    domains = domain_breakdown(pages)
    types = type_breakdown(pages)
    link_stats = link_density_stats(pages)
    act_stats = activity_stats(pages)
    tags = tag_cloud(pages)
    health = health_score(pages)

    if args.json:
        result = {
            "total_pages": len(pages),
            "domains": domains,
            "types": types,
            "link_density": link_stats,
            "activity": act_stats,
            "tag_cloud": tags,
            "health": health,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        total = len(pages)
        print(bold(f"\n═══ ═══ MindSea 统计报告 ═══ ═══\n"))

        # 总览
        print(bold("📊 总览"))
        print(f"  页面总数: {bold(str(total))}")
        print(f"  链接总数: {link_stats['total_links']}")
        print(f"  平均链接: {link_stats['avg']}/页")
        print()

        # 域分布
        print(bold("📁 域分布"))
        max_d = max(domains.values()) if domains else 1
        for d, c in domains.items():
            pct = round(100 * c / total, 1)
            print(f"  {d:20s} {bar(c, max_d, 15)} {c:>4} ({pct}%)")
        print()

        # 类型分布
        print(bold("🏷️  类型分布"))
        max_t = max(types.values()) if types else 1
        for t, c in types.items():
            pct = round(100 * c / total, 1)
            print(f"  {t:20s} {bar(c, max_t, 15)} {c:>4} ({pct}%)")
        print()

        # 链接密度
        print(bold("🔗 链接密度"))
        print(f"  最小: {link_stats['min']}  最大: {link_stats['max']}  平均: {link_stats['avg']}")
        if link_stats["sparse"] > 0:
            sparse_count = link_stats["sparse"]
            print(f"  {yellow(f'⚠ {sparse_count} 个页面链接不足 2 条')}")
        print()

        # 活跃度
        print(bold("📅 活跃度"))
        c = act_stats["created"]
        u = act_stats["updated"]
        if c["count"]:
            print(f"  创建记录: {c['count']} 条  {c['earliest']} ~ {c['latest']}")
        if u["count"]:
            print(f"  更新记录: {u['count']} 条  {u['earliest']} ~ {u['latest']}")
        print()

        # 健康评分
        print(bold("💚 健康评分"))
        score = health["score"]
        color_fn = green if score >= 80 else (yellow if score >= 60 else red)
        print(f"  综合得分: {color_fn(str(score))}/100")
        for k, v in health["details"].items():
            label = {
                "frontmatter_completeness": "Frontmatter 完整度",
                "link_density": "链接密度",
                "tag_coverage": "标签覆盖率",
                "activity": "活跃度",
            }.get(k, k)
            print(f"    {label}: {v}")
        print()

        # 标签云
        if tags:
            print(bold("☁️  标签云 (Top 20)"))
            top20 = list(tags.items())[:20]
            max_tc = top20[0][1] if top20 else 1
            for tag, count in top20:
                print(f"  {cyan(tag):25s} {bar(count, max_tc, 10)} {count}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())