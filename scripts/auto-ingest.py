#!/usr/bin/env python3
"""
auto-ingest.py — WonderKnowledge 自动入库脚本

将对话、想法、笔记等内容自动分类并写入知识库。
支持从 stdin、命令行参数或文件输入。

用法示例:
    echo "学习一下递归算法的原理" | python3 auto-ingest.py /path/to/vault
    python3 auto-ingest.py /path/to/vault --text "我觉得这个方案可行"
    python3 auto-ingest.py /path/to/vault --file notes.txt
    python3 auto-ingest.py /path/to/vault --text "..." --type view --domain personal
    python3 auto-ingest.py /path/to/vault --text "..." --dry-run

分类规则（基于关键词匹配，无需 LLM）:
    - 包含"我认为/我觉得/我的判断/我相信" → View（观点）, personal
    - 包含"记一下/想法/灵感/突然想到" → Thought（想法）, personal
    - 包含"提醒/备忘/不要忘记" → Memo（备忘）, personal
    - 包含"学习/概念/原理/算法" → Concept（概念）, learning
    - 包含"项目/产品/开发/设计" → Project（项目）, creative
    - 默认 → Thought, personal
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────
# 常量定义
# ──────────────────────────────────────────────

# 知识库域（domain）到目录的映射
DOMAIN_DIR_MAP = {
    "learning": "wiki-learning",
    "creative": "wiki-ideas",
    "work": "wiki-work",
    "personal": "personal",
    "chronicles": "wiki-chronicles",
}

# 合法的笔记类型
VALID_TYPES = {"Concept", "View", "Thought", "Memo", "Project"}

# 合法的域
VALID_DOMAINS = set(DOMAIN_DIR_MAP.keys())

# 分类规则：(关键词列表, 类型, 域)
CLASSIFICATION_RULES: list[tuple[list[str], str, str]] = [
    (["我认为", "我觉得", "我的判断", "我相信"], "View", "personal"),
    (["记一下", "想法", "灵感", "突然想到"], "Thought", "personal"),
    (["提醒", "备忘", "不要忘记"], "Memo", "personal"),
    (["学习", "概念", "原理", "算法", "公式", "定义"], "Concept", "learning"),
    (["项目", "产品", "开发", "设计", "架构", "方案"], "Project", "creative"),
]


def classify_text(text: str) -> tuple[str, str]:
    """
    根据关键词规则对文本进行分类。

    参数:
        text: 输入文本

    返回:
        (笔记类型, 域名) 的元组
    """
    for keywords, note_type, domain in CLASSIFICATION_RULES:
        for kw in keywords:
            if kw in text:
                return note_type, domain
    # 默认分类：想法 + personal
    return "Thought", "personal"


def generate_title(text: str, max_len: int = 50) -> str:
    """
    从文本中提取标题。

    取第一行或前 max_len 个字符作为标题，
    去掉 Markdown 标记和多余空白。
    """
    # 取第一行
    first_line = text.strip().split("\n")[0].strip()
    # 去掉 Markdown 标题符号
    first_line = re.sub(r"^#+\s*", "", first_line)
    # 截断
    if len(first_line) > max_len:
        first_line = first_line[:max_len].rstrip()
    return first_line if first_line else "未命名笔记"


def generate_filename(title: str) -> str:
    """
    根据标题生成文件名。

    去掉特殊字符，用短横线连接，加上日期前缀。
    """
    today = date.today().strftime("%Y-%m-%d")
    # 清洗标题：只保留中英文、数字和空格
    clean = re.sub(r"[^\w\s\u4e00-\u9fff]", "", title)
    clean = re.sub(r"\s+", "-", clean.strip())
    if not clean:
        clean = "note"
    # 限制长度
    if len(clean) > 60:
        clean = clean[:60]
    return f"{today}-{clean}.md"


def build_frontmatter(title: str, note_type: str, domain: str, tags: list[str]) -> str:
    """
    生成 YAML frontmatter（笔记头部元数据）。

    参数:
        title: 笔记标题
        note_type: 笔记类型（Concept/View/Thought/Memo/Project）
        domain: 所属域
        tags: 标签列表

    返回:
        格式化的 frontmatter 字符串
    """
    today = date.today().strftime("%Y-%m-%d")
    tags_str = json.dumps(tags, ensure_ascii=False)
    return (
        f"---\n"
        f"title: {title}\n"
        f"type: {note_type}\n"
        f"domain: {domain}\n"
        f"status: draft\n"
        f"created: {today}\n"
        f"tags: {tags_str}\n"
        f"---\n"
    )


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """
    从文本中提取关键词（简单的基于频率的方法）。

    对中文按字符二元组分词，对英文按单词分词，
    去掉停用词后返回频率最高的关键词。
    """
    # 英文停用词
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "can", "shall",
        "and", "or", "but", "if", "then", "else", "when", "at", "from",
        "by", "for", "with", "about", "against", "between", "through",
        "during", "before", "after", "above", "below", "to", "of", "in",
        "on", "off", "over", "under", "again", "further", "than", "this",
        "that", "these", "those", "it", "its", "i", "me", "my", "we",
        "our", "you", "your", "he", "him", "his", "she", "her", "they",
        "them", "their", "what", "which", "who", "whom", "not", "no",
        "nor", "so", "very", "just", "also", "too", "only", "already",
    }
    # 中文停用词
    cn_stop = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一",
               "个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有",
               "看", "好", "自己", "这", "他", "她", "它", "们", "吗", "吧", "啊", "呢"}

    freq: dict[str, int] = {}

    # 提取英文单词
    eng_words = re.findall(r"[a-zA-Z]{2,}", text)
    for w in eng_words:
        wl = w.lower()
        if wl not in stop_words and len(wl) > 2:
            freq[wl] = freq.get(wl, 0) + 1

    # 提取中文字符（连续中文片段）
    cn_segments = re.findall(r"[\u4e00-\u9fff]+", text)
    for seg in cn_segments:
        for i in range(len(seg) - 1):
            bigram = seg[i:i + 2]
            if bigram not in cn_stop:
                freq[bigram] = freq.get(bigram, 0) + 1

    # 按频率排序，取前 N 个
    sorted_kw = sorted(freq.items(), key=lambda x: -x[1])
    return [kw for kw, _ in sorted_kw[:max_keywords]]


def search_existing_pages(vault_path: Path, keywords: list[str]) -> list[str]:
    """
    在知识库中搜索与关键词匹配的已有页面。

    参数:
        vault_path: 知识库根目录
        keywords: 关键词列表

    返回:
        匹配的页面标题列表（用于建议链接）
    """
    matched: list[str] = []
    for md_file in vault_path.rglob("*.md"):
        # 跳过索引文件和日志文件
        if md_file.name in ("index.md", "log.md"):
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # 从 frontmatter 提取标题
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        fm = fm_match.group(1)
        title_match = re.search(r"title:\s*(.+)", fm)
        if not title_match:
            continue
        page_title = title_match.group(1).strip()
        # 检查关键词是否出现在页面内容中
        for kw in keywords:
            if kw in content and page_title not in matched:
                matched.append(page_title)
                break
    return matched


def classify_with_ollama(text: str, ollama_url: str) -> Optional[tuple[str, str]]:
    """
    尝试使用本地 Ollama LLM 进行分类（可选功能）。

    如果 Ollama 服务不可用，返回 None，回退到规则分类。

    参数:
        text: 输入文本
        ollama_url: Ollama API 地址

    返回:
        (类型, 域) 或 None
    """
    prompt = (
        "请将以下文本分类。只回复 JSON 格式：{\"type\": \"类型\", \"domain\": \"域\"}\n"
        "类型只能是：Concept, View, Thought, Memo, Project\n"
        "域只能是：learning, creative, work, personal, chronicles\n\n"
        f"文本：{text[:500]}"
    )
    payload = json.dumps({
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{ollama_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            response_text = data.get("response", "")
            # 尝试解析 JSON
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
                note_type = result.get("type", "")
                domain = result.get("domain", "")
                if note_type in VALID_TYPES and domain in VALID_DOMAINS:
                    return note_type, domain
    except (urllib.error.URLError, OSError, json.JSONDecodeError, KeyError):
        pass
    return None


def update_domain_index(vault_path: Path, domain: str, title: str, filename: str) -> None:
    """
    更新域目录下的 index.md 文件，添加新笔记的链接。

    参数:
        vault_path: 知识库根目录
        domain: 域名
        title: 笔记标题
        filename: 笔记文件名
    """
    domain_dir = vault_path / DOMAIN_DIR_MAP[domain]
    index_file = domain_dir / "index.md"

    if not index_file.exists():
        # 创建初始索引文件
        content = f"# {DOMAIN_DIR_MAP[domain]}\n\n## 最新笔记\n\n- [{title}]({filename})\n"
        index_file.write_text(content, encoding="utf-8")
        return

    existing = index_file.read_text(encoding="utf-8", errors="replace")
    link = f"- [{title}]({filename})"
    if link not in existing:
        # 在"最新笔记"标题后插入，或追加到末尾
        if "## 最新笔记" in existing:
            existing = existing.replace("## 最新笔记\n", f"## 最新笔记\n\n{link}\n", 1)
        else:
            existing += f"\n{link}\n"
        index_file.write_text(existing, encoding="utf-8")


def append_domain_log(vault_path: Path, domain: str, title: str, filename: str) -> None:
    """
    在域目录下的 log.md 中追加一条入库记录。

    参数:
        vault_path: 知识库根目录
        domain: 域名
        title: 笔记标题
        filename: 笔记文件名
    """
    domain_dir = vault_path / DOMAIN_DIR_MAP[domain]
    log_file = domain_dir / "log.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{now}] 新增 [{title}]({filename})\n"

    if not log_file.exists():
        content = f"# {DOMAIN_DIR_MAP[domain]} 操作日志\n\n{entry}"
        log_file.write_text(content, encoding="utf-8")
    else:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)


def main():
    parser = argparse.ArgumentParser(
        description="WonderKnowledge 自动入库：将文本分类并写入知识库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  echo "学习递归算法" | python3 auto-ingest.py /path/to/vault
  python3 auto-ingest.py /path/to/vault --text "我觉得方案A更好"
  python3 auto-ingest.py /path/to/vault --file notes.txt --dry-run
  python3 auto-ingest.py /path/to/vault --text "..." --type view --domain personal
        """,
    )
    parser.add_argument("vault", help="知识库根目录路径")
    parser.add_argument("--text", "-t", help="直接传入文本内容")
    parser.add_argument("--file", "-f", help="从文件读取内容")
    parser.add_argument("--type", choices=list(VALID_TYPES), help="手动指定笔记类型")
    parser.add_argument("--domain", choices=list(VALID_DOMAINS), help="手动指定所属域")
    parser.add_argument("--tags", nargs="*", default=[], help="添加标签")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际写入")
    parser.add_argument("--ollama-url", help="Ollama API 地址（如 http://localhost:11434），启用 LLM 分类")
    parser.add_argument("--max-title-len", type=int, default=50, help="标题最大长度（默认 50）")

    args = parser.parse_args()

    vault_path = Path(args.vault).resolve()
    if not vault_path.is_dir():
        print(f"错误：知识库目录不存在：{vault_path}", file=sys.stderr)
        sys.exit(1)

    # ── 读取输入文本 ──
    if args.file:
        file_path = Path(args.file)
        if not file_path.is_file():
            print(f"错误：文件不存在：{file_path}", file=sys.stderr)
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8", errors="replace").strip()
    elif args.text:
        text = args.text.strip()
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("错误：未提供输入。请通过 --text、--file 或管道传入文本。", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("错误：输入文本为空。", file=sys.stderr)
        sys.exit(1)

    # ── 分类 ──
    if args.type and args.domain:
        # 用户手动指定了类型和域
        note_type = args.type
        domain = args.domain
        source = "手动指定"
    elif args.ollama_url:
        # 尝试 LLM 分类
        llm_result = classify_with_ollama(text, args.ollama_url)
        if llm_result:
            note_type, domain = llm_result
            source = "LLM 分类"
        else:
            note_type, domain = classify_text(text)
            source = "关键词分类（LLM 不可用，已回退）"
    else:
        note_type, domain = classify_text(text)
        source = "关键词分类"

    # ── 生成笔记 ──
    title = generate_title(text, args.max_title_len)
    filename = generate_filename(title)
    frontmatter = build_frontmatter(title, note_type, domain, args.tags)

    # ── 搜索已有页面，建议可能的链接 ──
    keywords = extract_keywords(text)
    related_pages = search_existing_pages(vault_path, keywords)

    # ── 组装完整内容 ──
    content_parts = [frontmatter, "\n", text, "\n"]
    if related_pages:
        content_parts.append("\n---\n## 相关笔记\n\n")
        for page in related_pages[:10]:
            content_parts.append(f"- [[{page}]]\n")

    full_content = "".join(content_parts)

    # ── 确定目标目录 ──
    target_dir = vault_path / DOMAIN_DIR_MAP[domain]
    target_file = target_dir / filename

    # ── 输出预览或写入 ──
    if args.dry_run:
        print("=" * 60)
        print("[预览模式] 以下内容将被写入：")
        print("=" * 60)
        print(f"  文件路径：{target_file}")
        print(f"  分类来源：{source}")
        print(f"  笔记类型：{note_type}")
        print(f"  所属域：  {domain}")
        print(f"  标题：    {title}")
        if related_pages:
            print(f"  相关笔记：{', '.join(related_pages[:5])}")
        print("-" * 60)
        print(full_content)
        print("=" * 60)
        return

    # 确保目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    # 如果文件已存在，加序号避免覆盖
    if target_file.exists():
        stem = target_file.stem
        for i in range(1, 100):
            candidate = target_dir / f"{stem}-{i}.md"
            if not candidate.exists():
                target_file = candidate
                break

    # 写入文件
    target_file.write_text(full_content, encoding="utf-8")

    # 更新索引和日志
    update_domain_index(vault_path, domain, title, target_file.name)
    append_domain_log(vault_path, domain, title, target_file.name)

    # 打印摘要
    print("✅ 笔记已入库！")
    print(f"   文件：{target_file}")
    print(f"   类型：{note_type} | 域：{domain} | 来源：{source}")
    print(f"   标题：{title}")
    if related_pages:
        print(f"   相关笔记：{', '.join(related_pages[:5])}")


if __name__ == "__main__":
    main()
