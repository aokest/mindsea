#!/usr/bin/env python3
"""
vectorize.py — MindSea TF-IDF 语义搜索引擎

零依赖实现 TF-IDF 向量化 + 余弦相似度搜索。
支持中英文混合文本，中文用字符二元组分词，英文用正则分词。

用法示例:
    python3 vectorize.py /path/to/vault build     # 构建完整索引
    python3 vectorize.py /path/to/vault update    # 增量更新
    python3 vectorize.py /path/to/vault search "递归算法" --top-k 5
    python3 vectorize.py /path/to/vault clear     # 清除索引

索引存储在知识库的 .vault-index/ 目录下：
    - vectors.json: 每个文件的 TF-IDF 向量
    - idf.json: IDF 值
    - metadata.json: 文件元数据和哈希值
"""

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────

INDEX_DIR = ".vault-index"
VECTORS_FILE = "vectors.json"
IDF_FILE = "idf.json"
METADATA_FILE = "metadata.json"

# 英文停用词
EN_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "and", "or", "but", "if",
    "then", "else", "when", "at", "from", "by", "for", "with", "about",
    "against", "between", "through", "during", "before", "after", "above",
    "below", "to", "of", "in", "on", "off", "over", "under", "again",
    "further", "than", "this", "that", "these", "those", "it", "its",
    "i", "me", "my", "we", "our", "you", "your", "he", "him", "his",
    "she", "her", "they", "them", "their", "what", "which", "who", "whom",
    "not", "no", "nor", "so", "very", "just", "also", "too", "only",
    "already", "some", "any", "each", "every", "all", "both", "few",
    "more", "most", "other", "such", "into", "out", "up", "down",
}

# 中文停用词（单字符高频虚词）
CN_STOP_WORDS = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都",
    "一", "个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
    "着", "没有", "看", "好", "自己", "这", "他", "她", "它", "们",
    "吗", "吧", "啊", "呢", "把", "被", "让", "给", "从", "向",
}


def compute_hash(file_path: Path) -> str:
    """计算文件 SHA-256 哈希。"""
    h = hashlib.sha256()
    try:
        h.update(file_path.read_bytes())
    except OSError:
        return ""
    return h.hexdigest()


def tokenize(text: str) -> list[str]:
    """
    对文本进行分词。

    英文：正则提取单词（小写化）
    中文：字符二元组（bigram）

    参数:
        text: 输入文本

    返回:
        token 列表
    """
    tokens: list[str] = []

    # 提取英文单词
    en_words = re.findall(r"[a-zA-Z]{2,}", text)
    for w in en_words:
        wl = w.lower()
        if wl not in EN_STOP_WORDS and len(wl) > 2:
            tokens.append(wl)

    # 提取中文字符，生成二元组
    cn_segments = re.findall(r"[\u4e00-\u9fff]+", text)
    for seg in cn_segments:
        for i in range(len(seg) - 1):
            bigram = seg[i:i + 2]
            if bigram not in CN_STOP_WORDS:
                tokens.append(bigram)

    return tokens


def strip_frontmatter(content: str) -> str:
    """去掉 YAML frontmatter，只返回正文。"""
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


def compute_tf(tokens: list[str]) -> dict[str, float]:
    """
    计算词频（Term Frequency）。

    使用归一化 TF：每个词的出现次数 / 总词数。
    """
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = len(tokens)
    return {term: count / total for term, count in counts.items()}


def compute_idf(doc_tokens: list[list[str]]) -> dict[str, float]:
    """
    计算逆文档频率（IDF）。

    IDF = log(N / df)，其中 N 是文档总数，df 是包含该词的文档数。
    """
    n_docs = len(doc_tokens)
    if n_docs == 0:
        return {}

    # 统计每个词出现在多少个文档中
    doc_freq: Counter = Counter()
    for tokens in doc_tokens:
        unique_tokens = set(tokens)
        for t in unique_tokens:
            doc_freq[t] += 1

    # 计算 IDF
    idf = {}
    for term, df in doc_freq.items():
        idf[term] = math.log((n_docs + 1) / (df + 1)) + 1  # 平滑处理
    return idf


def tfidf_vector(tf: dict[str, float], idf: dict[str, float]) -> dict[str, float]:
    """
    计算 TF-IDF 向量。

    TF-IDF = TF * IDF
    """
    return {term: tf_val * idf.get(term, 0) for term, tf_val in tf.items()}


def cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    """
    计算两个稀疏向量的余弦相似度。

    参数:
        vec1, vec2: {term: weight} 字典

    返回:
        相似度分数，范围 [0, 1]
    """
    # 找到共同的维度
    common_terms = set(vec1.keys()) & set(vec2.keys())
    if not common_terms:
        return 0.0

    # 点积
    dot_product = sum(vec1[t] * vec2[t] for t in common_terms)

    # 各自的范数
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def load_index(vault_path: Path) -> Optional[dict]:
    """
    加载已有的索引文件。

    返回:
        {"vectors": {...}, "idf": {...}, "metadata": {...}} 或 None
    """
    idx_dir = vault_path / INDEX_DIR
    if not idx_dir.is_dir():
        return None

    try:
        vectors = json.loads((idx_dir / VECTORS_FILE).read_text(encoding="utf-8", errors="replace"))
        idf = json.loads((idx_dir / IDF_FILE).read_text(encoding="utf-8", errors="replace"))
        metadata = json.loads((idx_dir / METADATA_FILE).read_text(encoding="utf-8", errors="replace"))
        return {"vectors": vectors, "idf": idf, "metadata": metadata}
    except (OSError, json.JSONDecodeError):
        return None


def save_index(vault_path: Path, vectors: dict, idf: dict, metadata: dict):
    """保存索引文件。"""
    idx_dir = vault_path / INDEX_DIR
    idx_dir.mkdir(parents=True, exist_ok=True)

    (idx_dir / VECTORS_FILE).write_text(
        json.dumps(vectors, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (idx_dir / IDF_FILE).write_text(
        json.dumps(idf, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (idx_dir / METADATA_FILE).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def collect_documents(vault_path: Path) -> list[tuple[Path, str]]:
    """
    收集知识库中所有 Markdown 文件。

    返回:
        [(文件路径, 内容), ...] 列表
    """
    docs = []
    for md_file in vault_path.rglob("*.md"):
        # 跳过索引目录
        if INDEX_DIR in md_file.parts:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
            docs.append((md_file, content))
        except OSError:
            continue
    return docs


def build_full_index(vault_path: Path) -> None:
    """
    构建完整的 TF-IDF 索引。

    步骤：
    1. 收集所有 .md 文件
    2. 分词
    3. 计算全局 IDF
    4. 计算每个文件的 TF-IDF 向量
    5. 保存索引
    """
    print("🔧 正在构建索引...")
    docs = collect_documents(vault_path)

    if not docs:
        print("⚠️  未找到任何 Markdown 文件。")
        return

    # 分词
    file_tokens: list[tuple[str, list[str]]] = []
    for file_path, content in docs:
        body = strip_frontmatter(content)
        tokens = tokenize(body)
        if tokens:
            rel = str(file_path.relative_to(vault_path))
            file_tokens.append((rel, tokens))

    if not file_tokens:
        print("⚠️  所有文件分词后为空。")
        return

    # 计算 IDF
    all_doc_tokens = [tokens for _, tokens in file_tokens]
    idf = compute_idf(all_doc_tokens)

    # 计算每个文件的 TF-IDF 向量
    vectors: dict[str, dict[str, float]] = {}
    metadata: dict[str, dict] = {}

    for rel_path, tokens in file_tokens:
        full_path = vault_path / rel_path
        tf = compute_tf(tokens)
        vec = tfidf_vector(tf, idf)
        vectors[rel_path] = vec
        metadata[rel_path] = {
            "hash": compute_hash(full_path),
            "token_count": len(tokens),
            "built_at": __import__("datetime").datetime.now().isoformat(),
        }

    save_index(vault_path, vectors, idf, metadata)
    print(f"✅ 索引构建完成！共 {len(vectors)} 个文件，{len(idf)} 个词条。")
    print(f"   索引目录：{vault_path / INDEX_DIR}")


def update_index(vault_path: Path) -> None:
    """
    增量更新索引。

    只处理新增或变更的文件，删除已移除文件的索引。
    """
    print("🔄 正在增量更新索引...")

    existing = load_index(vault_path)
    if not existing:
        print("⚠️  未找到已有索引，将执行完整构建。")
        build_full_index(vault_path)
        return

    vectors = existing["vectors"]
    old_idf = existing["idf"]
    metadata = existing["metadata"]

    # 收集当前所有文件
    docs = collect_documents(vault_path)
    current_files: dict[str, list[str]] = {}
    for file_path, content in docs:
        if INDEX_DIR in str(file_path):
            continue
        rel = str(file_path.relative_to(vault_path))
        body = strip_frontmatter(content)
        tokens = tokenize(body)
        if tokens:
            current_files[rel] = tokens

    # 检测变更
    updated = 0
    added = 0
    removed = 0

    # 新增和变更的文件
    all_doc_tokens = []
    for rel_path, tokens in current_files.items():
        full_path = vault_path / rel_path
        current_hash = compute_hash(full_path)

        if rel_path not in metadata or metadata[rel_path].get("hash") != current_hash:
            # 需要更新
            all_doc_tokens.append(tokens)
        else:
            # 未变更，保留旧的 token（用于重新计算 IDF）
            old_tokens = []
            for term, weight in vectors.get(rel_path, {}).items():
                # 反推近似 token 列表（用于 IDF 计算）
                count = max(1, round(weight * 100))
                old_tokens.extend([term] * count)
            all_doc_tokens.append(old_tokens)

    # 重新计算全局 IDF
    new_idf = compute_idf(all_doc_tokens)

    # 更新向量
    for rel_path, tokens in current_files.items():
        full_path = vault_path / rel_path
        current_hash = compute_hash(full_path)

        if rel_path not in metadata:
            added += 1
        elif metadata[rel_path].get("hash") != current_hash:
            updated += 1
        else:
            # 未变更，只需重新计算 TF-IDF（因为 IDF 可能变了）
            tf = compute_tf(tokens)
            vectors[rel_path] = tfidf_vector(tf, new_idf)
            continue

        tf = compute_tf(tokens)
        vectors[rel_path] = tfidf_vector(tf, new_idf)
        metadata[rel_path] = {
            "hash": current_hash,
            "token_count": len(tokens),
            "built_at": __import__("datetime").datetime.now().isoformat(),
        }

    # 删除已不存在的文件
    to_remove = [r for r in vectors if r not in current_files]
    for r in to_remove:
        del vectors[r]
        if r in metadata:
            del metadata[r]
        removed += 1

    save_index(vault_path, vectors, new_idf, metadata)
    print(f"✅ 增量更新完成！新增 {added}，变更 {updated}，删除 {removed}，共 {len(vectors)} 个文件。")


def search_index(vault_path: Path, query: str, top_k: int = 5) -> list[tuple[str, float, str]]:
    """
    搜索知识库。

    参数:
        vault_path: 知识库根目录
        query: 查询文本
        top_k: 返回前 K 个结果

    返回:
        [(文件路径, 相似度分数, 标题), ...] 列表
    """
    index = load_index(vault_path)
    if not index:
        print("错误：索引不存在。请先运行 build 命令。", file=sys.stderr)
        sys.exit(1)

    vectors = index["vectors"]
    idf = index["idf"]
    metadata = index["metadata"]

    # 对查询文本分词并计算 TF-IDF
    query_tokens = tokenize(query)
    if not query_tokens:
        print("⚠️  查询文本分词后为空，无法搜索。")
        return []

    query_tf = compute_tf(query_tokens)
    query_vec = tfidf_vector(query_tf, idf)

    # 计算与每个文档的余弦相似度
    scores: list[tuple[str, float]] = []
    for rel_path, doc_vec in vectors.items():
        sim = cosine_similarity(query_vec, doc_vec)
        if sim > 0:
            scores.append((rel_path, sim))

    # 按相似度降序排序
    scores.sort(key=lambda x: -x[1])
    top_results = scores[:top_k]

    # 提取标题
    results = []
    for rel_path, score in top_results:
        full_path = vault_path / rel_path
        title = extract_title(full_path)
        results.append((rel_path, score, title))

    return results


def extract_title(file_path: Path) -> str:
    """从 Markdown 文件中提取标题。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        # 先从 frontmatter 提取
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            title_match = re.search(r"title:\s*(.+)", fm_match.group(1))
            if title_match:
                return title_match.group(1).strip()
        # 再从第一个标题行提取
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                return re.sub(r"^#+\s*", "", line)
    except OSError:
        pass
    return file_path.stem


def clear_index(vault_path: Path) -> None:
    """清除索引目录。"""
    idx_dir = vault_path / INDEX_DIR
    if not idx_dir.is_dir():
        print("索引目录不存在，无需清除。")
        return

    for f in idx_dir.iterdir():
        if f.is_file():
            f.unlink()
    idx_dir.rmdir()
    print("✅ 索引已清除。")


def main():
    parser = argparse.ArgumentParser(
        description="MindSea TF-IDF 语义搜索引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 vectorize.py /path/to/vault build
  python3 vectorize.py /path/to/vault update
  python3 vectorize.py /path/to/vault search "递归算法" --top-k 5
  python3 vectorize.py /path/to/vault clear
        """,
    )
    parser.add_argument("vault", help="知识库根目录路径")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # build 子命令
    subparsers.add_parser("build", help="构建完整索引（全量扫描）")

    # update 子命令
    subparsers.add_parser("update", help="增量更新索引（仅处理变更文件）")

    # search 子命令
    search_parser = subparsers.add_parser("search", help="搜索知识库")
    search_parser.add_argument("query", help="搜索查询文本")
    search_parser.add_argument("--top-k", type=int, default=5, help="返回前 K 个结果（默认 5）")

    # clear 子命令
    subparsers.add_parser("clear", help="清除索引")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    vault_path = Path(args.vault).resolve()
    if not vault_path.is_dir():
        print(f"错误：知识库目录不存在：{vault_path}", file=sys.stderr)
        sys.exit(1)

    if args.command == "build":
        build_full_index(vault_path)

    elif args.command == "update":
        update_index(vault_path)

    elif args.command == "search":
        results = search_index(vault_path, args.query, args.top_k)
        if not results:
            print("未找到匹配结果。")
            return

        print(f"🔍 搜索「{args.query}」的结果：\n")
        print(f"{'排名':<4} {'相似度':<8} {'文件':<50} {'标题'}")
        print("-" * 90)
        for i, (rel_path, score, title) in enumerate(results, 1):
            print(f"{i:<4} {score:<8.4f} {rel_path:<50} {title}")

    elif args.command == "clear":
        clear_index(vault_path)


if __name__ == "__main__":
    main()