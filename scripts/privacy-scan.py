#!/usr/bin/env python3
"""
MindSea 隐私扫描器

检查知识库中的隐私泄露风险：
1. L3（机密）关键词泄漏到 L1/L2 域
2. 跨域敏感信息泄漏（如 work 域内容出现在 learning 域）
3. 缺少隐私标签的页面

支持 --keywords 自定义敏感词列表。

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
KV_RE = re.compile(r"^(\w+)\s*:\s*(.+)$", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

# 默认敏感关键词（可被 --keywords 覆盖或追加）
DEFAULT_SENSITIVE_KEYWORDS = [
    "密码", "password", "token", "secret", "API-KEY", "api_key",
    "private-key", "私钥", "ssh", "信用卡", "credit-card",
    "SSN", "身份证", "手机号", "邮箱地址",
]

# L3 机密域名标识
L3_DOMAINS = {"personal", "log-work"}
# L1/L2 公开/内部域名
L1_L2_DOMAINS = {"learning", "business", "media", "creative", "raw", "_weekly"}

# 跨域禁止映射：key 域的内容不应出现在 value 域中
CROSS_DOMAIN_RULES = {
    "log-work": {"learning", "business", "media", "creative", "raw"},
    "personal": {"learning", "business", "media", "creative", "raw"},
    "business": {"learning", "media", "creative"},
}

# ── 解析工具 ──────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict[str, str]:
    """提取 frontmatter 键值对"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    body = m.group(1)
    return {k.lower().strip(): v.strip() for k, v in KV_RE.findall(body)}


def get_domain(filepath: Path, vault_root: Path) -> str:
    """根据文件相对路径推断所属域"""
    rel = filepath.relative_to(vault_root)
    parts = rel.parts
    return parts[0] if len(parts) > 1 else "_root"


SKIP_DIRS = {"_system", "_weekly", "_publish", "scripts", ".obsidian", ".vault-index", "_archive"}
SECURITY_CONCEPT_STEMS = {"agentic-ai-workflow", "llm-wiki-methodology", "tc260-gov-llm-security-standard",
                          "WORKFLOW", "SCHEMA",
                          "log", "README",
                          }

def load_vault(vault_root: Path) -> list[dict]:
    """加载所有 .md 文件"""
    pages = []
    for md in vault_root.rglob("*.md"):
        rel_parts = md.relative_to(vault_root).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        pages.append({
            "path": md,
            "domain": get_domain(md, vault_root),
            "frontmatter": parse_frontmatter(text),
            "text": text,
        })
    return pages

# ── 扫描项 ──────────────────────────────────────────────

def scan_keyword_leaks(pages: list[dict], keywords: list[str]) -> list[dict]:
    """L3 关键词出现在 L1/L2 域页面中"""
    findings = []
    for page in pages:
        if page["domain"] not in L1_L2_DOMAINS:
            continue
        for kw in keywords:
            if kw.lower() in page["text"].lower():
                findings.append({
                    "type": "keyword_leak",
                    "severity": "high",
                    "page": str(page["path"]),
                    "domain": page["domain"],
                    "keyword": kw,
                    "msg": f"L1/L2 域发现敏感关键词 '{kw}'",
                })
    return findings


def scan_cross_domain_leaks(pages: list[dict], keywords: list[str]) -> list[dict]:
    """跨域泄漏：L3 域的敏感内容被链接到 L1/L2 域"""
    findings = []

    # 建立 L3 域页面标题集
    l3_titles: dict[str, set] = defaultdict(set)
    for page in pages:
        if page["domain"] in L3_DOMAINS:
            fm = page["frontmatter"]
            title = fm.get("title", page["path"].stem)
            l3_titles[page["domain"]].add(title.lower())

    # 检查 L1/L2 域是否 wikilink 到 L3 内容
    for page in pages:
        if page["domain"] not in L1_L2_DOMAINS:
            continue
        links = WIKILINK_RE.findall(page["text"])
        for target, _alias in links:
            target_lower = target.strip().lower()
            for l3_domain, titles in l3_titles.items():
                if target_lower in titles:
                    findings.append({
                        "type": "cross_domain_leak",
                        "severity": "high",
                        "page": str(page["path"]),
                        "domain": page["domain"],
                        "linked_to": target,
                        "source_domain": l3_domain,
                        "msg": f"跨域泄漏: {page['domain']} 链接到 {l3_domain} 内容 '{target}'",
                    })

    # 检查禁止映射
    for page in pages:
        src = page["domain"]
        if src not in CROSS_DOMAIN_RULES:
            continue
        links = WIKILINK_RE.findall(page["text"])
        for target, _alias in links:
            # 检查目标页面是否在禁止域中
            for other in pages:
                other_title = other["frontmatter"].get("title", other["path"].stem).lower()
                if target.strip().lower() == other_title and other["domain"] in CROSS_DOMAIN_RULES[src]:
                    findings.append({
                        "type": "cross_domain_forbidden",
                        "severity": "medium",
                        "page": str(page["path"]),
                        "domain": src,
                        "linked_to": target,
                        "target_domain": other["domain"],
                        "msg": f"域 {src} 不应链接到 {other['domain']} 的内容",
                    })

    return findings


def scan_missing_privacy_tags(pages: list[dict]) -> list[dict]:
    """缺少隐私级别标签的页面"""
    findings = []
    for page in pages:
        fm = page["frontmatter"]
        tags_raw = fm.get("tags", "")
        tags = [t.strip().lower() for t in tags_raw.split(",")] if tags_raw else []
        has_privacy_tag = any(t in ("l1", "l2", "l3", "public", "internal", "confidential") for t in tags)
        if not has_privacy_tag:
            findings.append({
                "type": "missing_privacy_tag",
                "severity": "low",
                "page": str(page["path"]),
                "domain": page["domain"],
                "msg": "缺少隐私级别标签 (建议添加 L1/L2/L3)",
            })
    return findings

# ── 主逻辑 ──────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="MindSea 隐私扫描器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("vault", nargs="?", default=".",
                        help="知识库根目录路径 (默认当前目录)")
    parser.add_argument("--keywords", nargs="*", default=None,
                        help="自定义敏感关键词列表（追加到默认列表）")
    parser.add_argument("--replace-keywords", nargs="*", default=None,
                        help="完全替换默认关键词列表")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出结果")
    parser.add_argument("--severity", choices=["low", "medium", "high"],
                        default="low", help="最低显示级别 (默认 low)")
    args = parser.parse_args()

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(red(f"错误: 目录不存在 {vault_root}"), file=sys.stderr)
        return 2

    # 确定关键词
    if args.replace_keywords is not None:
        keywords = args.replace_keywords
    elif args.keywords is not None:
        keywords = DEFAULT_SENSITIVE_KEYWORDS + args.keywords
    else:
        keywords = DEFAULT_SENSITIVE_KEYWORDS

    severity_order = {"low": 0, "medium": 1, "high": 2}
    min_sev = severity_order[args.severity]

    pages = load_vault(vault_root)
    if not pages:
        print(yellow("警告: 未找到任何 .md 文件"))
        return 1

    # 执行扫描
    all_findings = []
    all_findings.extend(scan_keyword_leaks(pages, keywords))
    all_findings.extend(scan_cross_domain_leaks(pages, keywords))
    all_findings.extend(scan_missing_privacy_tags(pages))

    # 按严重级别过滤
    filtered = [f for f in all_findings if severity_order[f["severity"]] >= min_sev]

    high_count = sum(1 for f in filtered if f["severity"] == "high")
    med_count = sum(1 for f in filtered if f["severity"] == "medium")
    low_count = sum(1 for f in filtered if f["severity"] == "low")

    if args.json:
        result = {
            "total_pages": len(pages),
            "keywords_used": len(keywords),
            "findings": filtered,
            "summary": {"high": high_count, "medium": med_count, "low": low_count},
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(bold(f"\n═══ ═══ MindSea 隐私扫描报告 ═══ ═══  共 {len(pages)} 页\n"))

        if not filtered:
            print(green("✔ 未发现隐私风险"))
        else:
            sev_color = {"high": red, "medium": yellow, "low": lambda t: t}
            for f in filtered:
                sev = f["severity"].upper()
                color_fn = sev_color[f["severity"]]
                print(f"  {color_fn(f'[{sev}]')} {bold(f['page'])}")
                print(f"         {f['msg']}")
                print()

            print(bold("统计:"),
                  red(f"高危 {high_count}"),
                  yellow(f"中危 {med_count}"),
                  f"低危 {low_count}")

    return 2 if high_count > 0 else (1 if med_count > 0 else 0)


if __name__ == "__main__":
    sys.exit(main())