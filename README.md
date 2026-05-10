<p align="center">
  <br>
  <strong style="font-size:2.5em">🧠 识海 MindSea</strong>
  <br><br>
  <strong style="font-size:1.3em">你的每一次思考，都在生长</strong>
  <br>
  <em>Your Every Thought, Growing.</em>
  <br><br>
  <em>AI-Native Knowledge Management Framework</em>
  <br><br>
  <img src="https://img.shields.io/github/license/aokest/mindsea?color=7c3aed" alt="License">
  <img src="https://img.shields.io/badge/Platform-Obsidian-blue?logo=obsidian&logoColor=white" alt="Obsidian">
  <img src="https://img.shields.io/badge/AI-Powered-10b981?logo=openai&logoColor=white" alt="AI">
  <img src="https://img.shields.io/badge/Privacy-Local--First-f59e0b" alt="Privacy">
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white" alt="Python">
</p>

---

[English](#english) · [简体中文](#简体中文) · [繁體中文](#繁體中文)

---

## About the Author / 关于作者

**傲客（AK）** — 化学专业出身的网络安全从业者。信奉「大胆假设，小心求证」，用 AI 重建了从投资研究到内容生产的整套工作流。

> 「思考了半年，用一周打造出来。识海，就是把 AI 变成外脑这条路走通后留下的地图。」

## Project Vision / 项目愿景

**识海**的诞生源于一个简单的观察：**我们每天产生大量有价值的思考，但它们大部分都消散了。**

和 AI 的对话里有洞察，读文章时有灵感，开会时有判断——这些碎片想法如果只停留在聊天记录里，就永远只是碎片。

**识海**要解决的是：**如何让碎片想法自动生长为系统智慧？**

- 💬 **让知识和对话成为资产** — 不是记笔记，是构建认知基础设施
- 🧩 **碎片想法，系统智慧** — 从一个念头到一个决策，有完整的生长链路
- 🌱 **你的每一次思考，都在生长** — AI 负责结构和链接，你只管输入和判断

这不是又一个笔记模板。这是一个**让 AI 帮你管理终身知识资产的框架**。

---

<a id="english"></a>

## English

### What is MindSea?

MindSea is an **AI-native knowledge management framework** that turns fragmented thoughts into a living, growing knowledge network.

Inspired by [Karpathy's LLM Wiki](https://x.com/karpathy) methodology — AI acts as the "read/write head" of your knowledge graph, handling structure and links, while you provide information and judgment.

> **Every day's thinking, reading, and conversations are producing knowledge assets. MindSea ensures these assets are no longer lost.**

### Features

| Feature | Description |
|---------|-------------|
| 🏗️ **Five-Domain Architecture** | Learning · Business · Media · Creative · Personal |
| 🤖 **Three-Layer AI** | Touch (Agent) + Deep (Analysis) + Storage (Obsidian) |
| 🔗 **15 Relationship Types** | Structural + semantic (supports, contradicts, evolved_to...) |
| 📊 **Cognitive Progression** | Thought → View → Strategy → Project → Content |
| 🔒 **Privacy-Embedded** | Three-level classification (🟢🟡🔴) in schema |
| 🔍 **TF-IDF Search** | Zero-dependency Chinese bigram tokenization |
| 🏥 **Audit Toolchain** | 7 Python scripts: health/privacy/stats/ingest/watcher/vectorize/audit |
| 📝 **6 Templates** | Concept, Thought, View, Memo, Project, Investment |
| ⏰ **Expiration Tracking** | Knowledge has a shelf life (staleness field) |
| 🤖 **Auto-Ingest** | Conversation → structured wiki page, automatically |
| 📖 **7 Docs** | Getting started, use cases, comparison, automation, configuration |
| 🔤 **Trilingual** | English / 简体中文 / 繁體中文 |

### Architecture

```
┌─────────────────────────────────────────────┐
│           Touch Layer (AI Agent)            │
│    Always-on · Fragment Capture · Query     │
├─────────────────────────────────────────────┤
│           Deep Layer (Deep Agent)           │
│    Batch Processing · Cross-Audit · LLM     │
├─────────────────────────────────────────────┤
│          Storage Layer (Obsidian)           │
│    Graph Visualization · Manual Edit        │
└─────────────────────────────────────────────┘
```

### Quick Start

```bash
git clone https://github.com/aokest/mindsea.git
# Open in Obsidian, then:
python3 scripts/wiki-audit.py .        # Full audit
python3 scripts/vectorize.py . build   # Build search index
python3 scripts/auto-ingest.py . --text "your thought"  # Auto-ingest
```

---

<a id="简体中文"></a>

## 简体中文

### 什么是识海？

**识海（MindSea）** 是一个开源的 AI 原生知识管理框架，将碎片想法转化为活的、生长的知识网络。

灵感来自 [Andrej Karpathy 的 LLM Wiki 方法论](https://x.com/karpathy)——AI 作为知识图谱的"读写头"，负责结构和链接，你负责信息和判断。

> **每天的思考、阅读、对话都在"生产"知识资产。识海让这些资产不再流失。**

### 核心特性

| 特性 | 说明 |
|------|------|
| 🏗️ **五域架构** | 学习·商业·自媒体·创意·个人 |
| 🤖 **三层 AI 协作** | 触达层（Agent）+ 深度层（分析）+ 存储层（Obsidian） |
| 🔗 **15 种关系类型** | 结构关系 + 语义关系（支持/矛盾/演化/启发/实例） |
| 📊 **认知递进模型** | 想法→观点→策略→项目→内容 |
| 🔒 **隐私嵌入架构** | 三级分类（🟢🟡🔴）写进 Schema |
| 🔍 **TF-IDF 语义搜索** | 零依赖中文 bigram 分词 |
| 🏥 **审计工具链** | 7 个 Python 脚本：健康/隐私/统计/录入/监控/检索/全审 |
| 📝 **6 种模板** | 概念/想法/观点/备忘/项目/投资 |
| ⏰ **知识过期追踪** | staleness 字段：知识有保质期 |
| 🤖 **自动录入** | 对话碎片→结构化知识页面，全自动 |
| 📖 **7 份文档** | 快速上手/场景演示/竞品对比/自动化/配置/工具集成/数据分级 |

### 快速开始

```bash
git clone https://github.com/aokest/mindsea.git
# 用 Obsidian 打开，然后：
python3 scripts/wiki-audit.py .                      # 全面审计
python3 scripts/vectorize.py . build                 # 构建搜索索引
python3 scripts/auto-ingest.py . --text "你的想法"    # 自动录入
```

### 文档索引

| 文档 | 说明 |
|------|------|
| `_system/SCHEMA.md` | 知识宪法（五条铁律） |
| `_system/LLM-WIKI-GUIDE.md` | 完整架构指南 |
| `docs/GETTING-STARTED.md` | 快速上手指南 |
| `docs/USE-CASES.md` | 5 大场景演示 |
| `docs/COMPARISON.md` | 竞品对比 |
| `docs/TOOL-INTEGRATION.md` | AI 工具集成指南 |
| `docs/CONFIGURATION.md` | AI Agent 配置 |
| `docs/DATA-CLASSIFICATION.md` | 数据分类分级 |
| `docs/AUTOMATION.md` | 自动化架构 |

### 联系方式

- 🐦 **微博**: [weibo.com/aokest](https://weibo.com/aokest)
- 💬 **微信**: aokest
- 📱 **微信公众号**: 付能量 / 皇帝没穿衣服
- ✈️ **Telegram**: [@w0n6erfu](https://t.me/w0n6erfu)
- 🐙 **GitHub**: [github.com/aokest](https://github.com/aokest)

---

<a id="繁體中文"></a>

## 繁體中文

### 什麼是識海？

**識海（MindSea）** 是一個開源的 AI 原生知識管理框架，將碎片想法轉化為活的、生長的知識網路。

靈感來自 [Andrej Karpathy 的 LLM Wiki 方法論](https://x.com/karpathy)——AI 作為知識圖譜的「讀寫頭」，負責結構和連結，你負責資訊和判斷。

> **每天的思考、閱讀、對話都在「生產」知識資產。識海讓這些資產不再流失。**

### 快速開始

```bash
git clone https://github.com/aokest/mindsea.git
# 用 Obsidian 開啟，然後：
python3 scripts/wiki-audit.py .                      # 全面審計
python3 scripts/vectorize.py . build                 # 建構搜尋索引
python3 scripts/auto-ingest.py . --text "你的想法"    # 自動錄入
```

---

## 📁 Structure

```
mindsea/
├── _system/              # Core framework
│   ├── SCHEMA.md         # Knowledge constitution (15 relationship types)
│   ├── WORKFLOW.md       # AI collaboration workflow
│   ├── LLM-WIKI-GUIDE.md # Complete architecture guide
│   └── templates/        # 6 page templates
│
├── learning/             # 📚 Concepts & tools
├── business/             # 💼 Investment & strategy
├── media/                # 📱 Content & platforms
├── creative/             # 💡 Projects & ideas
├── personal/             # 🔒 Private thoughts & views
├── raw/                  # 📦 Original materials
│
├── scripts/              # 🛠️ Automation toolchain
│   ├── wiki-audit.py     #   Full audit (health+stats+privacy)
│   ├── wiki-health.py    #   Health check
│   ├── wiki-stats.py     #   Statistics
│   ├── privacy-scan.py   #   Privacy scan
│   ├── vectorize.py      #   TF-IDF semantic search
│   ├── vault-watcher.py  #   File change monitor
│   └── auto-ingest.py    #   Conversation → knowledge page
│
├── docs/                 # 📖 Documentation
│   ├── GETTING-STARTED.md
│   ├── USE-CASES.md
│   ├── COMPARISON.md
│   ├── TOOL-INTEGRATION.md
│   ├── CONFIGURATION.md
│   ├── DATA-CLASSIFICATION.md
│   └── AUTOMATION.md
│
├── index.md              # Global navigation
├── ACKNOWLEDGMENTS.md    # Open source credits
└── LICENSE               # MIT
```

---

## 📜 Five Iron Rules

1. **One Note, One Concept** — Atomic knowledge units
2. **Name is Taxonomy** — Self-explanatory filenames
3. **Links Must Be Bidirectional** — A→B requires B→A
4. **Source Attribution Required** — Every fact has a source
5. **Expiration Must Be Marked** — Time-sensitive knowledge has a shelf life

---

## 🔗 15 Relationship Types

### Structural
`prerequisite_of` · `part_of` · `related_to` · `uses` · `derived_from` · `created_by` · `depends_on` · `targets` · `produces` · `influences`

### Semantic
`supports` (✓) · `contradicts` (⚔) · `evolved_to` (→) · `inspired_by` (💡) · `instance_of` (∈)

---

## 🔒 Privacy

| Level | Icon | Storage | AI Processing |
|-------|------|---------|---------------|
| Public | 🟢 | Local + backup | Any model |
| Internal | 🟡 | Local + encrypted | Trusted models |
| Secret | 🔴 | Local only | Local models only |

---

## 🙏 Acknowledgments

See [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for full credits.

- [Andrej Karpathy](https://x.com/karpathy) — LLM Wiki methodology
- [Obsidian](https://obsidian.md) — Local-first knowledge base
- [Hermes Agent](https://github.com/nousresearch/hermes-agent) — AI touch layer
- [Anthropic Claude](https://claude.ai) — Deep analysis agent
- [Ollama](https://ollama.ai) — Local LLM inference
- [bge-m3](https://huggingface.co/BAAI/bge-m3) — Multilingual embeddings
- [Zettelkasten](https://zettelkasten.de/) — Linking philosophy
- [PARA Method](https://fortelabs.com/) — Organization framework

---

## 📄 License

[MIT](LICENSE) — Use it however you want.

---

<p align="center">
  <strong>🧠 你的每一次思考，都在生长</strong>
  <br>
  <em>Your Every Thought, Growing.</em>
</p>
