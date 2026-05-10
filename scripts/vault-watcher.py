#!/usr/bin/env python3
"""
vault-watcher.py — MindSea 知识库健康监控

扫描知识库中所有 Markdown 文件，检查 frontmatter 完整性、
跟踪文件变化状态、自动修复缺失的元数据。

用法示例:
    python3 vault-watcher.py /path/to/vault --scan
    python3 vault-watcher.py /path/to/vault --watch --interval 30
    python3 vault-watcher.py /path/to/vault --scan --fix
    python3 vault-watcher.py /path/to/vault --scan --ignore raw,work-log
"""

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────

# 知识库目录结构
VAULT_DIRS = ["personal", "learning", "business", "media", "creative", "raw", "log-work", "_weekly"]

# 合法的笔记类型和域
VALID_TYPES = {"Concept", "Tool", "Project", "Content", "Account", "View", "Thought", "Memo", "Research", "Theme", "Ecommerce", "Strategy", "Case", "DailyLog", "LiveNote"}
VALID_DOMAINS = {"learning", "business", "media", "creative", "personal", "log-work"}

# 状态文件名
STATE_FILE = ".vault-state.json"

# frontmatter 必需字段
REQUIRED_FM_FIELDS = ["title", "type", "domain", "status", "created"]

# frontmatter 默认值（用于 --fix）
DEFAULT_FM = {
    "title": "",
    "type": "Thought",
    "domain": "personal",
    "status": "draft",
    "created": "",
    "tags": "[]",
}

# 目录到域的映射（反向）
DIR_DOMAIN_MAP = {
    "personal": "personal",
    "wiki-learning": "learning",
    "wiki-ideas": "creative",
    "wiki-work": "work",
    "wiki-chronicles": "chronicles",
}


def compute_file_hash(file_path: Path) -> str:
    """
    计算文件的 SHA-256 哈希值，用于跟踪文件变化。

    参数:
        file_path: 文件路径

    返回:
        十六进制哈希字符串
    """
    h = hashlib.sha256()
    try:
        content = file_path.read_bytes()
        h.update(content)
    except OSError:
        return ""
    return h.hexdigest()


def load_state(vault_path: Path) -> dict:
    """
    加载知识库的状态文件（.vault-state.json）。

    状态文件记录了每个文件的哈希值和上次扫描时间。

    返回:
        状态字典
    """
    state_file = vault_path / STATE_FILE
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"files": {}, "last_scan": None}


def save_state(vault_path: Path, state: dict) -> None:
    """保存状态文件。"""
    state_file = vault_path / STATE_FILE
    state["last_scan"] = datetime.now().isoformat()
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_frontmatter(content: str) -> Optional[dict]:
    """
    从 Markdown 内容中解析 YAML frontmatter。

    简单解析器，不依赖 PyYAML。只处理 key: value 格式。

    返回:
        frontmatter 字典，如果没有 frontmatter 则返回 None
    """
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    fm_text = match.group(1)
    result = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        colon_pos = line.find(":")
        if colon_pos == -1:
            continue
        key = line[:colon_pos].strip()
        value = line[colon_pos + 1:].strip()
        result[key] = value
    return result


def get_frontmatter_body(content: str) -> str:
    """提取 frontmatter 之后的正文部分。"""
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


def check_frontmatter(fm: dict, file_path: Path) -> list[str]:
    """
    检查 frontmatter 的完整性。

    返回:
        问题列表（每个问题是一条描述字符串）
    """
    issues = []

    # 检查必需字段
    for field in REQUIRED_FM_FIELDS:
        if field not in fm:
            issues.append(f"缺少必需字段: {field}")
        elif not fm[field]:
            issues.append(f"字段为空: {field}")

    # 检查 type 合法性
    if "type" in fm and fm["type"] not in VALID_TYPES:
        issues.append(f"type 值不合法: {fm['type']}（应为 {', '.join(VALID_TYPES)}）")

    # 检查 domain 合法性
    if "domain" in fm and fm["domain"] not in VALID_DOMAINS:
        issues.append(f"domain 值不合法: {fm['domain']}（应为 {', '.join(VALID_DOMAINS)}）")

    # 检查日期格式
    if "created" in fm and fm["created"]:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", fm["created"]):
            issues.append(f"created 日期格式不正确: {fm['created']}（应为 YYYY-MM-DD）")

    # 检查 tags 格式
    if "tags" in fm:
        tags_str = fm["tags"]
        if not (tags_str.startswith("[") and tags_str.endswith("]")):
            issues.append(f"tags 格式不正确: {tags_str}（应为 JSON 数组）")

    return issues


def fix_frontmatter(fm: Optional[dict], content: str, file_path: Path) -> str:
    """
    自动修复缺失的 frontmatter。

    根据文件所在目录推断域，使用默认值填充缺失字段。

    返回:
        修复后的完整 Markdown 内容
    """
    # 根据文件路径推断域
    inferred_domain = "personal"
    for dir_name, domain in DIR_DOMAIN_MAP.items():
        if dir_name in str(file_path):
            inferred_domain = domain
            break

    today = date.today().strftime("%Y-%m-%d")

    if fm is None:
        # 完全没有 frontmatter，创建一个
        title = file_path.stem.replace("-", " ").replace("_", " ").title()
        fm = {
            "title": title,
            "type": "Thought",
            "domain": inferred_domain,
            "status": "draft",
            "created": today,
            "tags": "[]",
        }
        new_fm_text = (
            f"---\n"
            f"title: {fm['title']}\n"
            f"type: {fm['type']}\n"
            f"domain: {fm['domain']}\n"
            f"status: {fm['status']}\n"
            f"created: {fm['created']}\n"
            f"tags: {fm['tags']}\n"
            f"---\n\n"
        )
        return new_fm_text + content
    else:
        # 有 frontmatter 但缺字段，补全
        updated = False
        for field, default in DEFAULT_FM.items():
            if field not in fm or not fm[field]:
                if field == "title":
                    value = file_path.stem.replace("-", " ").replace("_", " ").title()
                elif field == "domain":
                    value = inferred_domain
                elif field == "created":
                    # 尝试从文件名中提取日期
                    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
                    value = date_match.group(1) if date_match else today
                else:
                    value = default
                fm[field] = value
                updated = True

        if not updated:
            return content  # 不需要修复

        # 重建 frontmatter
        new_fm_text = "---\n"
        for field in REQUIRED_FM_FIELDS + ["tags"]:
            if field in fm:
                new_fm_text += f"{field}: {fm[field]}\n"
        new_fm_text += "---\n"

        # 加上正文
        body = get_frontmatter_body(content)
        return new_fm_text + "\n" + body


def scan_vault(vault_path: Path, fix: bool = False, ignore_dirs: list[str] = None) -> dict:
    """
    扫描知识库中所有 Markdown 文件。

    参数:
        vault_path: 知识库根目录
        fix: 是否自动修复
        ignore_dirs: 要忽略的目录列表

    返回:
        扫描结果摘要
    """
    ignore_set = set(ignore_dirs or [])
    state = load_state(vault_path)
    results = {
        "total_files": 0,
        "files_with_issues": 0,
        "files_fixed": 0,
        "new_files": 0,
        "changed_files": 0,
        "removed_files": 0,
        "issues_detail": [],
    }

    # 当前扫描到的文件
    current_files: dict[str, str] = {}

    for md_file in vault_path.rglob("*.md"):
        # 检查是否在忽略目录中
        rel_path = md_file.relative_to(vault_path)
        parts = rel_path.parts
        if any(part in ignore_set for part in parts):
            continue

        results["total_files"] += 1
        rel_str = str(rel_path)
        file_hash = compute_file_hash(md_file)
        current_files[rel_str] = file_hash

        # 检查文件是否是新增或变更
        if rel_str not in state.get("files", {}):
            results["new_files"] += 1
        elif state["files"][rel_str].get("hash") != file_hash:
            results["changed_files"] += 1

        # 读取并检查 frontmatter
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            results["issues_detail"].append((rel_str, ["无法读取文件"]))
            results["files_with_issues"] += 1
            continue

        fm = parse_frontmatter(content)
        issues = check_frontmatter(fm, md_file) if fm else ["完全没有 frontmatter"]

        if issues:
            results["files_with_issues"] += 1
            results["issues_detail"].append((rel_str, issues))

            if fix:
                # 自动修复
                fixed_content = fix_frontmatter(fm, content, md_file)
                try:
                    md_file.write_text(fixed_content, encoding="utf-8")
                    results["files_fixed"] += 1
                    # 重新计算哈希
                    current_files[rel_str] = compute_file_hash(md_file)
                except OSError as e:
                    results["issues_detail"].append((rel_str, [f"修复失败: {e}"]))

    # 检测已删除的文件
    old_files = set(state.get("files", {}).keys())
    removed = old_files - set(current_files.keys())
    results["removed_files"] = len(removed)

    # 更新状态
    new_state = {"files": {}}
    for rel_str, file_hash in current_files.items():
        new_state["files"][rel_str] = {
            "hash": file_hash,
            "last_seen": datetime.now().isoformat(),
        }
    save_state(vault_path, new_state)

    return results


def watch_vault(vault_path: Path, interval: int, ignore_dirs: list[str] = None):
    """
    持续监控知识库变化（守护进程模式）。

    每隔 interval 秒扫描一次，检测并报告变化。

    参数:
        vault_path: 知识库根目录
        interval: 扫描间隔（秒）
        ignore_dirs: 要忽略的目录列表
    """
    print(f"🔍 开始监控知识库：{vault_path}")
    print(f"   扫描间隔：{interval} 秒")
    print(f"   按 Ctrl+C 停止\n")

    try:
        while True:
            results = scan_vault(vault_path, fix=False, ignore_dirs=ignore_dirs)
            now = datetime.now().strftime("%H:%M:%S")

            changes = []
            if results["new_files"] > 0:
                changes.append(f"新增 {results['new_files']} 个文件")
            if results["changed_files"] > 0:
                changes.append(f"变更 {results['changed_files']} 个文件")
            if results["removed_files"] > 0:
                changes.append(f"删除 {results['removed_files']} 个文件")

            if changes:
                print(f"[{now}] 📢 {' | '.join(changes)}")
                if results["files_with_issues"] > 0:
                    print(f"         ⚠️  {results['files_with_issues']} 个文件有问题")
            else:
                print(f"[{now}] ✅ 无变化（共 {results['total_files']} 个文件）")

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n监控已停止。")


def print_scan_report(results: dict):
    """打印扫描报告。"""
    print("=" * 60)
    print("📊 知识库扫描报告")
    print("=" * 60)
    print(f"  总文件数：      {results['total_files']}")
    print(f"  新增文件：      {results['new_files']}")
    print(f"  变更文件：      {results['changed_files']}")
    print(f"  已删除文件：    {results['removed_files']}")
    print(f"  有问题的文件：  {results['files_with_issues']}")
    if results["files_fixed"] > 0:
        print(f"  已修复文件：    {results['files_fixed']}")
    print()

    if results["issues_detail"]:
        print("⚠️  问题详情：")
        print("-" * 60)
        for file_path, issues in results["issues_detail"]:
            print(f"  📄 {file_path}")
            for issue in issues:
                print(f"     - {issue}")
        print()

    if results["files_with_issues"] == 0:
        print("✅ 所有文件检查通过！")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="MindSea 知识库健康监控：扫描、跟踪变化、自动修复",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 vault-watcher.py /path/to/vault --scan
  python3 vault-watcher.py /path/to/vault --scan --fix
  python3 vault-watcher.py /path/to/vault --watch --interval 30
  python3 vault-watcher.py /path/to/vault --scan --ignore raw,work-log
        """,
    )
    parser.add_argument("vault", help="知识库根目录路径")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true", help="单次扫描（适合 cron 定时任务）")
    mode.add_argument("--watch", action="store_true", help="持续监控（守护进程模式）")

    parser.add_argument("--fix", action="store_true", help="自动修复缺失的 frontmatter（仅配合 --scan）")
    parser.add_argument("--interval", type=int, default=30, help="监控扫描间隔，单位秒（默认 30，仅配合 --watch）")
    parser.add_argument("--ignore", help="要忽略的目录，逗号分隔（如 raw,work-log）")

    args = parser.parse_args()

    vault_path = Path(args.vault).resolve()
    if not vault_path.is_dir():
        print(f"错误：知识库目录不存在：{vault_path}", file=sys.stderr)
        sys.exit(1)

    ignore_dirs = []
    if args.ignore:
        ignore_dirs = [d.strip() for d in args.ignore.split(",") if d.strip()]

    if args.scan:
        results = scan_vault(vault_path, fix=args.fix, ignore_dirs=ignore_dirs)
        print_scan_report(results)
    elif args.watch:
        watch_vault(vault_path, args.interval, ignore_dirs=ignore_dirs)


if __name__ == "__main__":
    main()