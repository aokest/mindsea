#!/usr/bin/env python3
"""
wiki-audit.py — MindSea 一键知识图谱全面审计

整合健康检查 + 统计报告 + 隐私扫描，一次运行全部。
借鉴自 WonderKnowledge 项目。

用法:
    python3 wiki-audit.py /path/to/vault          # 全量审计
    python3 wiki-audit.py /path/to/vault --json    # JSON 输出
    python3 wiki-audit.py /path/to/vault --health  # 仅健康检查
    python3 wiki-audit.py /path/to/vault --stats   # 仅统计报告
    python3 wiki-audit.py /path/to/vault --privacy # 仅隐私扫描
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# ── 颜色 ──────────────────────────────────────────
def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"): return False
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

# ── 常量 ──────────────────────────────────────────
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
KV_RE = re.compile(r"^(\w+)\s*:\s*(.+)$", re.MULTILINE)
DATE_FORMATS = ["%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y/%m/%d"]
REQUIRED_FIELDS = {"title", "type", "domain", "status", "created"}

# 隐私相关
DEFAULT_SENSITIVE_KEYWORDS = [
    "密码", "password", "token", "secret", "API-KEY", "api_key",
    "private-key", "私钥", "ssh", "信用卡", "credit-card",
    "SSN", "身份证", "手机号", "邮箱地址",
]
L3_DOMAINS = {"personal", "log-work"}

# ── 解析工具 ──────────────────────────────────────
def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m: return {}
    return {k.lower().strip(): v.strip() for k, v in KV_RE.findall(m.group(1))}

def extract_wikilinks(text):
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(text)]

def get_domain(filepath, vault_root):
    rel = filepath.relative_to(vault_root)
    return rel.parts[0] if len(rel.parts) > 1 else "_root"

def parse_date(s):
    for fmt in DATE_FORMATS:
        try: return datetime.strptime(s.strip(), fmt)
        except ValueError: continue
    return None

SKIP_DIRS = {"_system", "_weekly", "_publish", "scripts", ".obsidian", ".vault-index", "_archive"}

def load_vault(vault_root):
    pages = []
    slug_aliases = {}  # full_rel_path_stem -> stem, for path-style wikilinks
    for md in vault_root.rglob("*.md"):
        # Skip system directories
        rel_parts = md.relative_to(vault_root).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue
        try: text = md.read_text(encoding="utf-8", errors="replace")
        except OSError: continue
        fm = parse_frontmatter(text)
        links = extract_wikilinks(text)
        stem = md.stem
        rel_stem = str(md.relative_to(vault_root).with_suffix(""))
        slug_aliases[rel_stem] = stem
        slug_aliases[stem] = stem
        pages.append({
            "path": md, "domain": get_domain(md, vault_root), "stem": stem,
            "frontmatter": fm, "links": links, "link_count": len(links),
            "text": text, "size": md.stat().st_size if md.exists() else 0,
        })
    return pages, slug_aliases


def resolve_link(link_target, slug_aliases):
    if link_target in slug_aliases:
        return slug_aliases[link_target]
    from pathlib import Path
    stem = Path(link_target).stem
    if stem in slug_aliases:
        return slug_aliases[stem]
    return None

# ── 健康检查 ──────────────────────────────────────
def run_health(pages, slug_aliases):
    all_stems = {p["stem"] for p in pages}
    stem_map = {p["stem"]: p for p in pages}

    # Frontmatter errors (skip system-like files: index, log, README, CLAUDE)
    SYSTEM_STEMS = {"index", "log", "README", "CLAUDE", "AGENTS", "WORKFLOW", "SCHEMA"}
    fm_errors = []
    for p in pages:
        stem = p["stem"]
        if stem in SYSTEM_STEMS or stem.startswith("2026-W"):
            continue
        missing = REQUIRED_FIELDS - p["frontmatter"].keys()
        if missing:
            fm_errors.append((stem, f"缺少: {', '.join(sorted(missing))}"))

    # Orphans (no incoming or outgoing resolved links)
    linked_by = defaultdict(set)
    for p in pages:
        for t in p["links"]:
            resolved = resolve_link(t, slug_aliases)
            if resolved:
                linked_by[resolved].add(p["stem"])
    orphans = sorted([s for s in all_stems if not stem_map[s]["links"] and s not in linked_by])

    # Broken links (unresolvable targets)
    broken = [(p["stem"], t) for p in pages for t in p["links"] if resolve_link(t, slug_aliases) is None]

    # Bidirectional missing
    bidir = []
    for p in pages:
        for t in p["links"]:
            resolved = resolve_link(t, slug_aliases)
            if resolved and resolved in stem_map and p["stem"] not in [resolve_link(l, slug_aliases) for l in stem_map[resolved]["links"]]:
                bidir.append((p["stem"], t))

    # Sparse
    sparse = [(p["stem"], p["link_count"]) for p in pages if p["link_count"] < 2]

    has_error = bool(fm_errors or broken)
    has_warn = bool(orphans or bidir or sparse)

    return {
        "fm_errors": fm_errors, "orphans": orphans, "broken": broken,
        "bidir_missing": bidir, "sparse": sparse,
        "status": "error" if has_error else ("warn" if has_warn else "ok"),
    }

# ── 统计报告 ──────────────────────────────────────
def run_stats(pages):
    total = len(pages)
    if not total: return {}

    domains = dict(Counter(p["domain"] for p in pages).most_common())
    types = dict(Counter(p["frontmatter"].get("type", "未分类") for p in pages).most_common())
    link_counts = [p["link_count"] for p in pages]
    link_stats = {
        "min": min(link_counts), "max": max(link_counts),
        "avg": round(sum(link_counts) / total, 2), "total": sum(link_counts),
        "sparse": sum(1 for c in link_counts if c < 2),
    }

    # Health score
    with_fm = sum(1 for p in pages if p["frontmatter"])
    with_tags = sum(1 for p in pages if p["frontmatter"].get("tags"))
    with_updated = sum(1 for p in pages if p["frontmatter"].get("updated"))
    sparse_count = sum(1 for c in link_counts if c < 2)

    fm_score = round(30 * with_fm / total)
    link_score = round(30 * (1 - sparse_count / total))
    tag_score = round(20 * with_tags / total)
    active_score = round(20 * with_updated / total)
    health_score = fm_score + link_score + tag_score + active_score

    # Tag cloud (supports both YAML array [t1, t2] and comma-separated)
    tags = Counter()
    for p in pages:
        t = p["frontmatter"].get("tags", "")
        if t:
            # Strip YAML array brackets if present
            t = t.strip().strip("[]")
            for tag in t.split(","):
                tag = tag.strip().strip('"').strip("'").lower()
                if tag and tag not in ("", "[", "]"): tags[tag] += 1

    # Activity
    created = [parse_date(p["frontmatter"].get("created", "")) for p in pages]
    created = [d for d in created if d]
    updated = [parse_date(p["frontmatter"].get("updated", "")) for p in pages]
    updated = [d for d in updated if d]

    return {
        "total": total, "domains": domains, "types": types,
        "link_stats": link_stats, "health_score": health_score,
        "health_details": {
            "frontmatter": fm_score, "links": link_score,
            "tags": tag_score, "activity": active_score,
        },
        "tag_cloud": dict(tags.most_common(20)),
        "activity": {
            "created_range": f"{min(created).strftime('%Y-%m-%d')} ~ {max(created).strftime('%Y-%m-%d')}" if created else "N/A",
            "updated_range": f"{min(updated).strftime('%Y-%m-%d')} ~ {max(updated).strftime('%Y-%m-%d')}" if updated else "N/A",
        },
    }

# ── 隐私扫描 ──────────────────────────────────────
def run_privacy(pages, keywords=None):
    if keywords is None:
        keywords = DEFAULT_SENSITIVE_KEYWORDS
    findings = []

    # Pages that discuss security concepts (not actual leaks)
    SECURITY_CONCEPT_STEMS = {"agentic-ai-workflow", "llm-wiki-methodology", "tc260-gov-llm-security-standard",
                              "WORKFLOW", "SCHEMA",
                              "log", "README",
                              }
    for p in pages:
        stem = p["path"].stem
        # Skip files that legitimately discuss security concepts
        if stem in SECURITY_CONCEPT_STEMS:
            continue
        # Keyword leaks in non-L3 domains
        if p["domain"] not in L3_DOMAINS:
            for kw in keywords:
                if kw.lower() in p["text"].lower():
                    findings.append({
                        "severity": "high",
                        "page": stem,
                        "domain": p["domain"],
                        "msg": f"敏感词 '{kw}' 出现在非私密域",
                    })

    # Missing privacy field
    for p in pages:
        if "privacy" not in p["frontmatter"]:
            findings.append({
                "severity": "low",
                "page": p["path"].stem,
                "domain": p["domain"],
                "msg": "缺少 privacy 字段",
            })

    return findings

# ── 输出 ──────────────────────────────────────────
def bar(value, max_val, width=15):
    filled = round(width * value / max_val) if max_val > 0 else 0
    return "█" * filled + "░" * (width - filled)

def print_health(h):
    print(bold("\n═══ 健康检查 ═══\n"))
    if h["fm_errors"]:
        print(red(f"✘ Frontmatter 错误 ({len(h['fm_errors'])})"))
        for s, m in h["fm_errors"][:10]:
            print(f"  • {bold(s)}: {m}")
    if h["broken"]:
        print(red(f"✘ 断链 ({len(h['broken'])})"))
        for s, t in h["broken"][:10]:
            print(f"  • {bold(s)} → [[{red(t)}]]")
    if h["orphans"]:
        print(yellow(f"⚠ 孤立页面 ({len(h['orphans'])})"))
        for s in h["orphans"][:10]:
            print(f"  • {s}")
    if h["bidir_missing"]:
        print(yellow(f"⚠ 双向链接缺失 ({len(h['bidir_missing'])})"))
        for s, t in h["bidir_missing"][:10]:
            print(f"  • {bold(s)} → [[{t}]] (未反链)")
    if h["sparse"]:
        print(yellow(f"⚠ 链接密度不足 ({len(h['sparse'])})"))
        for s, n in h["sparse"][:10]:
            print(f"  • {bold(s)}: {n} 条链接")
    if h["status"] == "ok":
        print(green("✔ 所有检查通过！"))
    print()

def print_stats(s):
    print(bold("\n═══ 统计报告 ═══\n"))
    print(f"📊 总计: {bold(str(s['total']))} 页 | 链接: {s['link_stats']['total']} | 平均: {s['link_stats']['avg']}/页")
    print()
    print(bold("📁 域分布"))
    max_d = max(s["domains"].values()) if s["domains"] else 1
    for d, c in s["domains"].items():
        pct = round(100 * c / s["total"], 1)
        print(f"  {d:15s} {bar(c, max_d, 12)} {c:>4} ({pct}%)")
    print()
    print(bold("🏷️  类型分布"))
    max_t = max(s["types"].values()) if s["types"] else 1
    for t, c in s["types"].items():
        pct = round(100 * c / s["total"], 1)
        print(f"  {t:15s} {bar(c, max_t, 12)} {c:>4} ({pct}%)")
    print()
    score = s["health_score"]
    color_fn = green if score >= 80 else (yellow if score >= 60 else red)
    print(f"💚 健康评分: {color_fn(str(score))}/100")
    for k, v in s["health_details"].items():
        label = {"frontmatter": "Frontmatter完整度", "links": "链接密度", "tags": "标签覆盖", "activity": "活跃度"}.get(k, k)
        print(f"    {label}: {v}/{'30' if k in ('frontmatter','links') else '20'}")
    print()
    if s["tag_cloud"]:
        print(bold("☁️  标签云 Top 15"))
        for tag, count in list(s["tag_cloud"].items())[:15]:
            print(f"  {cyan(tag):20s} {count}")
    print()
    print(f"📅 活跃度: 创建 {s['activity']['created_range']} | 更新 {s['activity']['updated_range']}")

def print_privacy(findings):
    print(bold("\n═══ 隐私扫描 ═══\n"))
    if not findings:
        print(green("✔ 未发现隐私风险"))
    else:
        high = sum(1 for f in findings if f["severity"] == "high")
        med = sum(1 for f in findings if f["severity"] == "medium")
        low = sum(1 for f in findings if f["severity"] == "low")
        sev_color = {"high": red, "medium": yellow, "low": lambda t: t}
        for f in findings[:15]:
            color_fn = sev_color[f["severity"]]
            sev = f["severity"].upper()
            print(f"  {color_fn('[' + sev + ']')} {bold(f['page'])} — {f['msg']}")
        print(f"\n  统计: {red(f'高危 {high}')} {yellow(f'中危 {med}')} 低危 {low}")

# ── 主逻辑 ──────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="MindSea 知识图谱全面审计")
    parser.add_argument("vault", nargs="?", default=".", help="知识库根目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--health", action="store_true", help="仅健康检查")
    parser.add_argument("--stats", action="store_true", help="仅统计报告")
    parser.add_argument("--privacy", action="store_true", help="仅隐私扫描")
    parser.add_argument("--keywords", nargs="*", help="自定义敏感词")
    args = parser.parse_args()

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(red(f"错误: 目录不存在 {vault_root}"), file=sys.stderr)
        return 2

    pages, slug_aliases = load_vault(vault_root)
    if not pages:
        print(yellow("警告: 未找到任何 .md 文件"))
        return 1

    run_all = not (args.health or args.stats or args.privacy)

    results = {}
    if run_all or args.health:
        results["health"] = run_health(pages, slug_aliases)
    if run_all or args.stats:
        results["stats"] = run_stats(pages)
    if run_all or args.privacy:
        results["privacy"] = run_privacy(pages, args.keywords)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(bold(f"\n═══ MindSea 全面审计 ═══  共 {len(pages)} 页"))
        if "health" in results: print_health(results["health"])
        if "stats" in results: print_stats(results["stats"])
        if "privacy" in results: print_privacy(results["privacy"])

    return 0

if __name__ == "__main__":
    sys.exit(main())
