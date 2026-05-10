# 工具集成指南

> 识海 如何与 AI 工具协同工作，实现知识的持续维护与产出。

---

## 目录

- [工具矩阵](#工具矩阵)
- [Hermes Agent](#hermes-agent-触觉层)
- [Claude Code](#claude-code-深度层)
- [Codex](#codex-自动化层)
- [OpenClaw](#openclaw-内容分发层)
- [Obsidian](#obsidian-存储层)
- [Ollama](#ollama-本地推理层)
- [协同工作流](#协同工作流)
- [配置速查](#配置速查)

---

## 工具矩阵

| 工具 | 角色 | 典型场景 | 隐私级别 | 部署方式 |
|------|------|----------|----------|----------|
| **Hermes Agent** | 触觉层 · 碎片捕获 | 日常对话中捕获观点、查询知识库、定时整理 | L1-L2（可配置） | 本地/云端 |
| **Claude Code** | 深度层 · 审计重构 | L3 隐私审查、月度知识审计、批量格式化 | L2-L3（需人工确认） | 本地终端 |
| **Codex** | 自动化层 · 脚本执行 | Dataview 查询、自定义工作流、批量操作 | L1-L3（取决于脚本） | 本地终端 |
| **OpenClaw** | 分发层 · 内容生产 | 概念→博客、想法→文档、编年史→Newsletter | L1（仅公开内容） | 云端 |
| **Obsidian** | 存储层 · 知识图谱 | 可视化浏览、双向链接、插件生态 | L1-L3（本地存储） | 本地应用 |
| **Ollama** | 推理层 · 本地 AI | 嵌入生成、本地对话、离线查询 | L3（完全本地） | 本地服务 |

### 隐私级别说明

| 级别 | 含义 | 数据流向 |
|------|------|----------|
| **L1** | 公开内容 | 可发送至云端 AI、可发布 |
| **L2** | 内部内容 | 仅限可信 AI 服务，不发布 |
| **L3** | 隐私内容 | 仅本地处理，绝不外传 |

---

## Hermes Agent（触觉层）

Hermes 是你的日常知识助手，通过自然语言对话完成碎片捕获和知识查询。

### 功能概览

| 功能 | 说明 | 示例 |
|------|------|------|
| 碎片捕获 | 从对话中提取知识碎片 | "帮我记录：RAG 的核心是检索+生成的两阶段架构" |
| 观点沉淀 | 将零散想法整理为结构化观点 | "我最近在想 AI Agent 的记忆问题，帮我整理一下" |
| 知识查询 | 搜索知识库中的相关内容 | "我之前记录过哪些关于 Transformer 的笔记？" |
| 定时任务 | cron 自动执行知识整理 | 每日归档、每周索引更新、每月审计提醒 |

### config.yaml 配置示例

```yaml
# ~/.hermes-agent/config.yaml

# Wiki 知识库根目录
wiki:
  path: "/path/to/your/识海"
  index_update: true

# 定时任务配置
crons:
  # 每天 23:00 归档当天碎片到对应域
  - name: "daily-fragment-archive"
    schedule: "0 23 * * *"
    task: |
      扫描 inbox/ 目录下的新文件，
      根据 frontmatter 中的 domain 字段，
      将文件移动到对应域的 fragments/ 目录。
      更新该域的 index.md 中的最近更新列表。

  # 每周日 10:00 更新全局索引
  - name: "weekly-index-update"
    schedule: "0 10 * * 0"
    task: |
      遍历所有域的 index.md，
      统计各域页面数量和最近活动，
      更新根目录的 README.md 全局概览。

  # 每月 1 日 09:00 触发 L3 隐私审计提醒
  - name: "monthly-l3-audit-reminder"
    schedule: "0 9 1 * *"
    task: |
      扫描所有域中 privacy: L3 的页面，
      检查是否有内容已过期或可以降级为 L2/L1，
      生成审计报告并通知用户。

# 碎片捕获默认配置
capture:
  default_domain: "learning"      # 默认域
  default_privacy: "L2"           # 默认隐私级别
  default_stage: "fragments"      # 默认认知阶段
  auto_link: true                 # 自动建立双向链接
  max_links_per_fragment: 3       # 每个碎片最多自动链接数
```

### 碎片捕获流程

```
用户对话 → Hermes 提取关键信息
         → 生成 frontmatter（domain/privacy/stage/tags）
         → 写入 inbox/ 待归档
         → 每日 cron 归档到对应域
```

**实际使用示例：**

```
你：今天读了一篇关于 Mixture of Experts 的论文，核心观点是稀疏激活
   可以在不增加推理成本的情况下扩展模型容量。记到 learning 域。

Hermes：已创建笔记 → learning/fragments/2025-06-moe-sparse-activation.md
       frontmatter:
         domain: learning
         privacy: L1
         stage: fragments
         tags: [transformer, moe, architecture]
       已自动链接到：[[learning/concepts/transformer-architecture]]
```

---

## Claude Code（深度层）

Claude Code 处理需要深度推理的知识任务：审计、重构、批量处理。

### CLAUDE.md 模板

将以下内容放在 识海 仓库根目录：

```markdown
# CLAUDE.md — 识海 项目约定

## 项目结构
识海 是基于 Obsidian 的 AI 原生知识管理框架。
- 五域结构：learning / creative / work / personal / chronicles
- 认知递进：fragments → concepts → permanent
- 隐私分级：L1（公开）/ L2（内部）/ L3（隐私）

## 命名规范
- 文件名使用 kebab-case：my-concept-name.md
- 域索引文件固定为 index.md
- 模板文件位于 templates/ 目录

## Frontmatter 规范
所有 .md 文件必须包含：
```yaml
---
domain: learning|creative|work|personal|chronicles
privacy: L1|L2|L3
stage: fragments|concepts|permanent
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
---
```

## L3 隐私规则
- privacy: L3 的文件**绝不**发送至外部 API
- L3 文件处理仅限本地模型（Ollama）
- 修改 L3 文件前必须确认用户意图

## 审计任务
- L3 审计：检查隐私标记准确性，扫描敏感信息泄露
- 月度审计：检查孤立页面、断链、过期内容、stage 晋升机会
- 批量处理：frontmatter 规范化、标签统一、链接修复

## 禁止操作
- 不要自动发布任何 L2/L3 内容
- 不要删除文件，只归档
- 不要修改 templates/ 目录中的原始模板
```

### L3 隐私审计

```bash
# 在 识海 目录下运行 Claude Code
cd /path/to/识海

# 执行 L3 审计
claude "执行 L3 隐私审计：
1. 扫描所有 privacy: L3 的文件
2. 检查是否有 L3 内容被错误标记为 L1/L2
3. 检查是否有敏感信息（邮箱、手机号、密码）出现在 L1/L2 文件中
4. 生成审计报告到 docs/audit/ 目录"
```

### 月度知识审计

```bash
claude "执行月度知识审计：
1. 统计各域文件数量、stage 分布
2. 列出孤立页面（无任何双向链接）
3. 列出断链（指向不存在的页面）
4. 列出超过 30 天未更新的 fragments（建议晋升或归档）
5. 标签使用统计，找出低频标签
6. 生成报告到 docs/audit/monthly-$(date +%Y-%m).md"
```

### 批量处理

```bash
# 规范化 frontmatter
claude "扫描所有 .md 文件，确保 frontmatter 包含完整的
domain/privacy/stage/created/updated/tags 字段，
缺少的字段用合理默认值补充"

# 修复链接
claude "扫描所有双向链接 [[...]]，找出指向不存在文件的断链，
生成修复建议报告"
```

---

## Codex（自动化层）

Codex 负责脚本化任务：自动化流水线、Dataview 查询生成、自定义工作流。

### 自动化脚本示例

#### 每日快照生成

```python
#!/usr/bin/env python3
"""daily_snapshot.py — 生成每日知识库快照"""

import os
from datetime import datetime
from pathlib import Path

VAULT = Path("/path/to/识海")
DOMAINS = ["learning", "creative", "work", "personal", "chronicles"]

def generate_snapshot():
    today = datetime.now().strftime("%Y-%m-%d")
    report = [f"# 知识库快照 — {today}\n"]

    total = 0
    for domain in DOMAINS:
        domain_path = VAULT / domain
        if not domain_path.exists():
            continue

        counts = {"fragments": 0, "concepts": 0, "permanent": 0}
        for stage in counts:
            stage_path = domain_path / stage
            if stage_path.exists():
                counts[stage] = len(list(stage_path.glob("*.md")))
                total += counts[stage]

        report.append(f"## {domain}")
        report.append(f"| 阶段 | 数量 |")
        report.append(f"|------|------|")
        for stage, count in counts.items():
            report.append(f"| {stage} | {count} |")
        report.append("")

    report.insert(1, f"**总计: {total} 个知识页面**\n")

    output = VAULT / "docs" / "snapshots" / f"{today}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(report))
    print(f"快照已生成: {output}")

if __name__ == "__main__":
    generate_snapshot()
```

#### Dataview 查询生成器

```python
#!/usr/bin/env python3
"""generate_dataview.py — 生成常用 Dataview 查询块"""

QUERIES = {
    "recent_fragments": """
```dataview
TABLE domain, stage, privacy, tags, created
FROM ""
WHERE stage = "fragments"
SORT created DESC
LIMIT 20
```""",

    "orphan_pages": """
```dataview
TABLE domain, stage, file.inlinks.length AS inlinks
FROM ""
WHERE file.inlinks.length = 0 AND file.outlinks.length = 0
SORT domain ASC
```""",

    "stage_distribution": """
```dataview
TABLE length(rows.file.name) AS count
FROM ""
GROUP BY domain + " / " + stage
SORT domain ASC
```""",

    "privacy_audit": """
```dataview
TABLE domain, stage, updated
FROM ""
WHERE privacy = "L3"
SORT updated ASC
```""",
}

def generate_queries():
    for name, query in QUERIES.items():
        print(f"--- {name} ---")
        print(query)
        print()

if __name__ == "__main__":
    generate_queries()
```

### 自定义工作流

```bash
# Codex 工作流：新笔记归档
codex run archive-new-notes -- \
  --source "inbox/" \
  --target-pattern "{domain}/{stage}/{filename}" \
  --update-index true

# Codex 工作流：批量 stage 晋升
codex run promote-notes -- \
  --from-stage "fragments" \
  --to-stage "concepts" \
  --min-age-days 30 \
  --min-links 2
```

---

## OpenClaw（内容分发层）

OpenClaw 将知识库中的内容转化为可发布的输出物。

### 知识→内容 转换矩阵

| 输入 | 输出 | 说明 |
|------|------|------|
| `learning/concepts/` | 技术博客 | 概念解释→深度文章 |
| `creative/` | 创作作品集 | 草稿→润色发布 |
| `work/` | 项目文档 | 笔记→结构化文档 |
| `personal/fragments/` | 思考随笔 | 碎片→主题文章 |
| `chronicles/` | Newsletter | 编年史→月刊 |

### 使用示例

```bash
# 概念 → 博客文章
openclaw generate blog \
  --source "learning/concepts/transformer-architecture.md" \
  --style "technical-explainer" \
  --audience "intermediate" \
  --output "output/blog/"

# 编年史 → 月度 Newsletter
openclaw generate newsletter \
  --source "chronicles/2025/06/" \
  --template "monthly-digest" \
  --output "output/newsletter/june-2025.md"

# 多个碎片 → 综合文档
openclaw generate doc \
  --source "learning/fragments/" \
  --topic "AI Agent 架构" \
  --filter-tags "agent,architecture" \
  --output "output/docs/ai-agent-arch.md"
```

### 隐私安全

OpenClaw 默认只处理 `privacy: L1` 的内容：

```yaml
# openclaw.config.yaml
privacy:
  max_level: "L1"           # 只处理 L1 内容
  require_confirmation: true # 发布前需人工确认
  strip_metadata: true       # 发布时移除内部元数据
```

---

## Obsidian（存储层）

Obsidian 是 识海 的核心存储和可视化界面。

### 必装插件

| 插件 | 用途 | 必装 |
|------|------|------|
| **Dataview** | 数据查询，自动生成索引和统计 | ✅ |
| **Graph View** | 内置图谱，查看知识关联 | ✅（内置） |
| **Templater** | 高级模板引擎，自动化页面生成 | ✅ |
| **Tag Wrangler** | 标签管理与批量重命名 | 推荐 |
| **Periodic Notes** | 周期性笔记（日/周/月） | 推荐 |
| **Excalidraw** | 手绘图解，嵌入笔记 | 可选 |

### 推荐配置

```json
// .obsidian/app.json
{
  "newFileLocation": "folder",
  "newFileFolderPath": "inbox",
  "attachmentFolderPath": "assets",
  "alwaysUpdateLinks": true,
  "useMarkdownLinks": false,
  "showLineNumber": true,
  "strictLineBreaks": false
}
```

```json
// .obsidian/plugins/dataview/data.json
{
  "enableDataviewJs": true,
  "enableInlineDataview": true,
  "enableInlineDataviewJs": true,
  "prettyRenderInlineFields": true,
  "dataviewJsKeyword": "dataviewjs"
}
```

### Dataview 查询示例

#### 五域概览仪表盘

```dataview
TABLE domain, privacy, stage, updated
FROM ""
WHERE file.name != "index"
GROUP BY domain
SORT domain ASC
```

#### 最近活跃的知识页面

```dataview
TABLE domain, stage, tags, updated
FROM ""
WHERE updated >= date(today) - dur(7 days)
SORT updated DESC
LIMIT 15
```

#### 待晋升的碎片（已存在 30 天以上）

```dataview
LIST file.inlinks.length AS links, created
FROM ""
WHERE stage = "fragments" AND created <= date(today) - dur(30 days)
SORT created ASC
```

#### 标签云数据

```dataviewjs
const pages = dv.pages();
const tagCount = {};
for (const page of pages) {
  for (const tag of page.file.tags || []) {
    tagCount[tag] = (tagCount[tag] || 0) + 1;
  }
}
const sorted = Object.entries(tagCount)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 20);
dv.table(["标签", "使用次数"], sorted);
```

#### 隐私级别分布

```dataview
TABLE length(rows.file.name) AS count
FROM ""
GROUP BY privacy
SORT privacy ASC
```

### Templater 模板示例

放置在 `templates/new-note.md`：

```markdown
---
domain: <% tp.file.cursor(1, "learning") %>
privacy: L2
stage: fragments
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags: []
---

# <% tp.file.title %>

## 要点

- 

## 关联

- [[]]

## 来源

- 

## 思考

> 
```

---

## Ollama（本地推理层）

Ollama 提供完全本地的 AI 能力，处理 L3 隐私内容。

### 安装与模型配置

```bash
# 安装 Ollama（macOS/Linux）
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取推荐模型
ollama pull qwen3:8b          # 推理模型：8B 参数，适合对话和分析
ollama pull bge-m3             # 嵌入模型：多语言向量化，适合检索

# 验证安装
ollama list
ollama run qwen3:8b "你好"
```

### 模型选择指南

| 模型 | 用途 | 大小 | 推荐场景 |
|------|------|------|----------|
| `qwen3:8b` | 对话/分析/写作 | ~5GB | L3 内容分析、本地知识查询、摘要生成 |
| `bge-m3` | 文本嵌入 | ~2GB | 向量检索、语义搜索、知识图谱增强 |

### Hermes Agent 集成 Ollama

在 Hermes 配置中指定 Ollama 作为 L3 内容的后端：

```yaml
# ~/.hermes-agent/config.yaml

# Ollama 本地推理配置
ollama:
  enabled: true
  base_url: "http://localhost:11434"
  models:
    chat: "qwen3:8b"          # 对话模型
    embedding: "bge-m3"        # 嵌入模型

# L3 隐私路由：L3 内容自动使用 Ollama
privacy_routing:
  L1: "cloud"                  # L1 内容可使用云端 AI
  L2: "cloud"                  # L2 内容可使用云端 AI（受信）
  L3: "ollama"                 # L3 内容强制本地处理

# 向量检索配置
vector:
  enabled: true
  model: "bge-m3"
  collection: "mindsea"
  chunk_size: 512
  chunk_overlap: 64
```

### 本地向量检索流程

```
用户查询 → bge-m3 生成查询向量
         → 搜索本地向量数据库
         → 返回相关知识片段
         → qwen3:8b 基于片段生成回答
```

### Ollama 直接使用

```bash
# 快速查询本地知识
ollama run qwen3:8b "基于以下知识片段回答问题：
$(cat learning/concepts/transformer-architecture.md)
问题：Transformer 的注意力机制是如何工作的？"

# 批量生成嵌入
python3 -c "
import requests, json
text = 'Hello world'
resp = requests.post('http://localhost:11434/api/embeddings',
    json={'model': 'bge-m3', 'prompt': text})
print(json.dumps(resp.json(), indent=2))
"
```

---

## 协同工作流

### 核心流水线

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Hermes      │───▶│  Obsidian   │───▶│ Claude Code │───▶│  OpenClaw   │
│  捕获碎片    │    │  存储图谱   │    │  审计重构   │    │  内容产出   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       │             ┌────┴────┐            │                  │
       │             │ Ollama  │            │                  │
       │             │本地推理  │            │                  │
       │             └─────────┘            │                  │
       │                                    │                  │
       ▼                                    ▼                  ▼
   inbox/                          docs/audit/           output/
   (待归档)                        (审计报告)            (发布物)
```

### 完整工作流示例

**场景：从一个想法到一篇博客文章**

```
第1步 · Hermes 捕获（日常对话中）
  "记录一下：我认为 RAG 的未来是 Agentic RAG，Agent 自主决定
   何时检索、检索什么、如何整合。"
  → 写入 inbox/2025-06-15-agentic-rag-idea.md

第2步 · Obsidian 存储（每日 cron 自动）
  归档到 learning/fragments/2025-06-15-agentic-rag-idea.md
  自动链接到 [[learning/concepts/rag]] 和 [[learning/concepts/ai-agent]]

第3步 · Hermes 辅助深化（对话中持续积累）
  后续对话中补充更多观点和案例
  碎片 stage 从 fragments 晋升为 concepts

第4步 · Claude Code 月度审计
  检查 learning/concepts/agentic-rag.md 的完整性
  确认无 L3 隐私内容
  建议补充哪些关联页面

第5步 · OpenClaw 内容产出
  从 learning/concepts/agentic-rag.md 生成博客初稿
  人工审核润色后发布
```

### 日常维护工作流

| 频率 | 执行者 | 任务 | 说明 |
|------|--------|------|------|
| 每日 | Hermes (cron) | 碎片归档 | inbox → 对应域 |
| 每日 | Hermes (cron) | 链接检查 | 修复简单断链 |
| 每周 | Hermes (cron) | 索引更新 | 更新各域 index.md |
| 每周 | 手动 | 碎片回顾 | 浏览本周碎片，标记值得深挖的 |
| 每月 | Claude Code | L3 隐私审计 | 检查隐私标记准确性 |
| 每月 | Claude Code | 知识审计 | 孤立页面、断链、stage 晋升 |
| 每月 | OpenClaw | 内容产出 | 从知识库生成月度输出 |
| 每季 | 手动 | 全局清理 | 归档过期内容，调整域结构 |

---

## 配置速查

### 各工具最小配置清单

```
✅ Hermes Agent
   - ~/.hermes-agent/config.yaml（wiki.path + crons）
   - 确认 AI 后端可访问（云端或 Ollama）

✅ Claude Code
   - 识海/CLAUDE.md（项目约定）
   - 终端可访问

✅ Obsidian
   - 安装 Dataview + Templater 插件
   - 配置新文件默认路径为 inbox/

✅ Ollama
   - ollama pull qwen3:8b
   - ollama pull bge-m3
   - 确认 localhost:11434 可访问

✅ OpenClaw
   - openclaw.config.yaml（privacy.max_level: L1）
   - 确认输出目录存在
```

---

> **下一步**: 阅读 [快速上手指南](GETTING-STARTED.md) 开始使用 识海。
