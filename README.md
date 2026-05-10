<p align="center">
  <br>
  <strong style="font-size:2em">🧠 MindSea</strong>
  <br>
  <em>AI-Native Knowledge Management Framework</em>
  <br><br>
  <strong>Your Every Thought, Growing.</strong>
  <br><br>
  <img src="https://img.shields.io/github/license/aokest/mindsea?color=7c3aed" alt="License">
  <img src="https://img.shields.io/badge/Platform-Obsidian-blue?logo=obsidian&logoColor=white" alt="Obsidian">
  <img src="https://img.shields.io/badge/AI-Powered-10b981?logo=openai&logoColor=white" alt="AI">
  <img src="https://img.shields.io/badge/Privacy-Local--First-f59e0b" alt="Privacy">
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white" alt="Python">
</p>

---

## 🧠 What is MindSea?

MindSea is an **AI-native knowledge management framework** that turns fragmented thoughts into a living, growing knowledge network.

Inspired by [Karpathy's LLM Wiki](https://x.com/karpathy) methodology — AI acts as the "read/write head" of your knowledge graph, handling structure and links, while you provide information and judgment.

> **每天的思考、阅读、对话都在"生产"知识资产。MindSea 让这些资产不再流失。**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🏗️ **Five-Domain Architecture** | Learning · Business · Media · Creative · Personal |
| 🤖 **Three-Layer AI** | Touch (Agent) + Deep (Analysis) + Storage (Obsidian) |
| 🔗 **15 Relationship Types** | Structural + semantic (supports, contradicts, evolved_to...) |
| 📊 **Cognitive Progression** | Thought → View → Strategy → Project → Content |
| 🔒 **Privacy-Embedded** | Three-level classification (🟢🟡🔴) in schema |
| 🔍 **TF-IDF Search** | Zero-dependency Chinese tokenization |
| 🏥 **Audit Toolchain** | 6 Python scripts for health/privacy/stats |
| 📝 **6 Templates** | Concept, Thought, View, Memo, Project, Investment |
| ⏰ **Expiration Tracking** | Knowledge has a shelf life |
| 🔤 **Trilingual** | English / 简体中文 / 繁體中文 |

---

## 🏛️ Architecture

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

### Knowledge Flow

```
raw/ → learning/ → creative/ → business/ → media/
         ↑                                       ↓
    personal/ ← ← ← ← (all domains feed back)
```

---

## 📁 Structure

```
mindsea/
├── _system/              # Core framework
│   ├── SCHEMA.md         # Knowledge constitution
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
├── scripts/              # 🛠️ Audit toolchain
│   ├── wiki-audit.py     #   Full audit
│   ├── wiki-health.py    #   Health check
│   ├── wiki-stats.py     #   Statistics
│   ├── privacy-scan.py   #   Privacy scan
│   ├── vectorize.py      #   TF-IDF search
│   └── vault-watcher.py  #   File monitor
│
├── index.md              # Global navigation
└── LICENSE               # MIT
```

---

## 🚀 Quick Start

### 1. Clone & Open

```bash
git clone https://github.com/aokest/mindsea.git
```

Open in [Obsidian](https://obsidian.md).

### 2. Read the Constitution

```
_system/SCHEMA.md → Iron rules, entity types, relationships
_system/LLM-WIKI-GUIDE.md → Full architecture docs
```

### 3. Build Search Index

```bash
python3 scripts/vectorize.py . build
python3 scripts/vectorize.py . search "your query" --top-k 5
```

### 4. Run Health Audit

```bash
python3 scripts/wiki-audit.py .
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

- [Andrej Karpathy](https://x.com/karpathy) — LLM Wiki methodology
- [Obsidian](https://obsidian.md) — Local-first knowledge base
- [WonderKnowledge](https://github.com/aokest/wonderknowledge) — Original framework

---

## 📄 License

MIT — Use it however you want.

---

<p align="center">
  <strong>🧠 让知识自己生长，让AI替你记忆</strong>
</p>
