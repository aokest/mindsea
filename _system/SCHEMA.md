# MindSea 知识宪法 (Knowledge Constitution)

> 版本: 2.0 | 本文档定义了整个知识图谱的结构规范、实体类型、关联规则和操作铁律。
> 所有 AI Agent 和用户操作均须遵守本宪法。

---

## 一、域结构 (Domain Architecture)

MindSea 采用五域架构，每个域对应知识生命周期的不同阶段：

| 域 | 目录 | 隐私 | 说明 |
|---|---|---|---|
| **学习** | `learning/` | 🟡 中等 | 概念、工具、技术原理 |
| **商业** | `business/` | 🟡 中等 | 投资、电商、商业策略 |
| **自媒体** | `media/` | 🟡 中等 | 内容创作、平台运营 |
| **创意** | `creative/` | 🟢 低 | 项目创意、产品设计 |
| **个人** | `personal/` | 🔴 高 | 私密想法、个人观点、备忘 |

### 域间流动

```
raw/ → learning/ → creative/ → business/ → media/
         ↑                                       ↓
    personal/ ← ← ← ← (所有域的思想沉淀)
```

---

## 二、实体类型 (Entity Types)

### 学习域
- **Concept** — 技术概念（如 Transformer、LoRA、RAG）
- **Tool** — 工具/框架（如 Obsidian、Claude Code）

### 商业域
- **Investment** — 投资理财
- **Strategy** — 商业策略
- **Case** — 商业案例
- **Ecommerce** — 电商运营

### 自媒体域
- **Content** — 内容（文章、视频、帖子）
- **Platform** — 平台（微博、知乎、小红书等）

### 创意域
- **Project** — 项目
- **Idea** — 产品创意

### 个人域
- **Thought** — 日常想法/灵感
- **View** — 观点/判断（状态: draft→held→validated/refuted）
- **Memo** — 备忘录（instant/short/mid 三级时效）

---

## 三、关系类型 (Relationship Types)

### 结构关系 (10种)
| 关系 | 方向 | 说明 |
|---|---|---|
| `prerequisite_of` | A → B | A 是 B 的前置知识 |
| `part_of` | A → B | A 属于 B 的一部分 |
| `related_to` | A ↔ B | 通用相关（双向）|
| `uses` | A → B | A 使用工具/技术 B |
| `derived_from` | A → B | A 来源于 B |
| `created_by` | A → B | A 由 B 创建/负责 |
| `depends_on` | A → B | A 依赖 B |
| `targets` | A → B | A 的目标受众/平台是 B |
| `produces` | A → B | A 产出内容 B |
| `influences` | A → B | A 影响/启发 B |

### 语义关系 (5种)
| 关系 | 语法 | 说明 |
|---|---|---|
| `supports` | `✓ [[note]]` | 论据支持 |
| `contradicts` | `⚔ [[note]]` | 观点对立 |
| `evolved_to` | `→ [[note]]` | 演化为 |
| `inspired_by` | `💡 [[note]]` | 受启发于 |
| `instance_of` | `∈ [[note]]` | 实例化 |

### 关联强度
```yaml
related:
  - "[[note-a]]"              # 默认 normal
  - "[[note-b]]"  # strong    # 强关联
  - "[[note-c]]"  # weak      # 弱关联
```

---

## 四、Frontmatter 规范

```yaml
---
title: 页面标题
type: Concept | Tool | Project | Content | View | ...
domain: learning | business | media | creative | personal
status: draft | active | mature | archived
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [source1]
confidence: high | medium | low
privacy: 🟢 | 🟡 | 🔴

# 过期管理（有时间敏感性的知识必填）
expires: YYYY-MM-DD
review_by: YYYY-MM-DD
staleness: daily | weekly | monthly | quarterly | yearly
---
```

---

## 五、状态生命周期

```
创建 ──→ seed ──→ growing ──→ mature ──→ archived
            │         │          │
            ▼         ▼          ▼
         rejected   paused     done
```

| 域 | 初始状态 | 正常流转 | 终态 |
|---|---|---|---|
| 学习域 | `mature` | `mature` → `archived` | `archived` |
| 创意域 | `seed` | `seed` → `growing` → `mature` | `mature` 或 `archived` |
| 商业域 | `active` | `active` → `paused` → `done` | `done` → `archived` |
| 个人域 | `draft` | `draft` → `held` → `validated` / `refuted` | `archived` |

---

## 六、五条铁律

1. **一笔记一概念** — 每个文件只承载一个知识原子
2. **命名即分类** — 文件名自解释: `<type>-<domain>-<topic>.md`
3. **关联必双向** — A→B 必须有 B→A
4. **来源必标注** — 每个知识实体必须标注来源
5. **过期必标记** — 有时间敏感性的知识必须标注 `expires` 和 `review_by`

---

## 七、命名规范

- 文件名：小写英文+连字符，如 `transformer-architecture.md`
- 页面标题：中文，如 `# Transformer 架构`
- 目录：英文小写，如 `learning/`, `business/`
- 标签：全小写，多词用连字符，层级用 `/`，如 `#ai/transformer`

---

## 八、知识图谱健康指标

| 指标 | 健康值 | 警告值 | 说明 |
|---|---|---|---|
| 孤儿笔记比例 | < 5% | > 15% | 无任何关联的笔记 |
| 平均关联数 | 3-8 | < 1 或 > 20 | 每个笔记的平均关联数 |
| 双向链接完整率 | > 95% | < 80% | 关联是否双向 |
| 过期内容比例 | < 10% | > 30% | 已过复审日期的内容 |
| 标签碎片率 | < 5% | > 20% | 低频标签（< 2次）的比例 |
| Frontmatter 完整率 | > 90% | < 70% | 必填字段覆盖率 |

运行 `python3 scripts/wiki-audit.py /path/to/vault` 获取完整健康报告。

---

## 九、标签分类法

| 标签域 | 示例标签 |
|---|---|
| AI/ML | `ai`, `ml`, `llm`, `deep-learning`, `nlp` |
| 编程 | `python`, `javascript`, `rust`, `api`, `devops` |
| 商业 | `ecommerce`, `investment`, `business-model`, `monetization` |
| 自媒体 | `weibo`, `zhihu`, `xiaohongshu`, `douyin`, `content-creation` |
| 元 | `tutorial`, `case-study`, `trend`, `comparison` |
