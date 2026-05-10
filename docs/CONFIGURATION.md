# AI Agent 配置指南

> 识海 AI Agent 完整配置手册  
> 版本: 1.0 | 最后更新: 2026-05-10

## 目录

1. [Obsidian 设置](#1-obsidian-设置)
2. [Hermes Agent 配置](#2-hermes-agent-配置)
3. [Claude Code 配置](#3-claude-code-配置)
4. [Ollama 本地模型](#4-ollama-本地模型)
5. [隐私-模型映射](#5-隐私-模型映射)
6. [自动化工作流](#6-自动化工作流)

---

## 1. Obsidian 设置

### 必装插件

| 插件 | 用途 | 配置要点 |
|-----|------|---------|
| Dataview | 动态查询与索引 | 开启 JavaScript 查询 |
| Graph Analysis | 知识图谱分析 | 设置最小连结阈值 |

### 推荐插件

- **Templater**: 模板引擎，用于自动生成带有 frontmatter 的笔记模板
- **Tag Wrangler**: 标签管理
- **Calendar**: 日历视图，便于时间线领域管理
- **Excalidraw**: 可视化绘图

### Dataview 配置

```dataview
// 按分类级别查看所有笔记
TABLE classification AS "级别", domain AS "领域"
FROM ""
WHERE classification
SORT classification ASC
```

```dataview
// 查看所有 L3 私密笔记
TABLE domain AS "领域", created AS "创建时间"
FROM ""
WHERE classification = "L3"
```

### Vault 结构

```
识海/
├── 00-Inbox/          # 收件箱
├── 01-Learning/       # 📚 学习领域
├── 02-Creative/       # 🎨 创意领域
├── 03-Work/           # 💼 工作领域
├── 04-Personal/       # 🏠 个人领域 (L3)
├── 05-Chronicles/     # 📅 时间线
├── Templates/         # 笔记模板
├── Attachments/       # 附件
├── SCHEMA.md          # 知识库架构定义
└── .obsidian/         # Obsidian 配置
```

---

## 2. Hermes Agent 配置

### config.yaml 示例

```yaml
# Hermes Agent 配置 - 识海
# 文档: https://hermes-agent.nousresearch.com/docs

# ========== 模型提供商 ==========
providers:
  # 顶级云端 (仅 L1 数据)
  anthropic:
    type: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    models:
      - claude-sonnet-4-20250514
    max_tokens: 8192
    
  # 本地模型 (L1/L2/L3 数据)
  ollama:
    type: ollama
    base_url: http://localhost:11434
    models:
      - qwen3:8b
      - gemma3:12b
    embedding_model: bge-m3

# ========== 工具配置 ==========
tools:
  file_read:
    enabled: true
    allowed_paths:
      - /path/to/识海/**
    blocked_paths:
      - "**/.git/**"
      - "**/node_modules/**"
      
  file_write:
    enabled: true
    allowed_paths:
      - /path/to/识海/**
    classification_check: true  # 写入前检查数据分类
    
  terminal:
    enabled: true
    allowed_commands:
      - "git *"
      - "ollama *"
      - "dataview *"

  search_files:
    enabled: true

# ========== 定时任务 ==========
cron_jobs:
  # 每日知识索引更新
  - name: "daily-index-update"
    schedule: "0 2 * * *"  # 每天凌晨 2 点
    command: |
      cd /path/to/识海
      # 更新 Dataview 索引
      # 生成每日知识图谱报告
    model: ollama/qwen3:8b
    
  # 每周知识整理
  - name: "weekly-cleanup"
    schedule: "0 3 * * 0"  # 每周日凌晨 3 点
    command: |
      # 清理未分类笔记
      # 生成周报摘要
    model: ollama/qwen3:8b
    
  # 每月隐私审计
  - name: "monthly-privacy-audit"
    schedule: "0 4 1 * *"  # 每月 1 日凌晨 4 点
    command: |
      # 检查 L3 数据是否泄露到云端
      # 生成合规报告
    model: ollama/qwen3:8b

# ========== 记忆系统 ==========
memory:
  enabled: true
  provider: ollama
  embedding_model: bge-m3
  storage_path: /path/to/识海/.memory/
  
# ========== 安全设置 ==========
security:
  data_classification_enforcement: true
  log_all_api_calls: true
  redact_sensitive_in_logs: true
```

### 环境变量 (.env)

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-xxx

# 路径
WONDERKNOWLEDGE_PATH=/path/to/识海

# 安全
ENABLE_CLASSIFICATION_CHECK=true
```

---

## 3. Claude Code 配置

### CLAUDE.md 模板

将以下内容放在项目根目录：

```markdown
# 识海 - Claude Code 配置

## 项目概述
识海 是基于 Karpathy LLM Wiki 方法论的 AI 原生知识管理框架。

## 核心规则

### 数据分类
- L1 (公开): 学习、创意(早期)、时间线 → 可使用云端模型
- L2 (内部): 工作、创意(成熟) → 仅可信云端或本地
- L3 (私密): 个人领域 → 仅限本地模型

### 写入规范
所有笔记 frontmatter 必须包含:
```yaml
---
title: "标题"
classification: L1/L2/L3
domain: learning/creative/work/personal/chronicles
created: YYYY-MM-DD
---
```

### 禁止事项
- 禁止将 L3 数据发送到任何外部 API
- 禁止在提交信息中包含敏感内容
- 禁止修改 .obsidian/ 核心配置

## 领域目录
- 01-Learning/ → 📚 学习 (L1)
- 02-Creative/ → 🎨 创意 (L1/L2)
- 03-Work/ → 💼 工作 (L2)
- 04-Personal/ → 🏠 个人 (L3)
- 05-Chronicles/ → 📅 时间线 (L1)
```

### 常用审计命令

```bash
# 检查所有笔记是否包含 classification 字段
find . -name "*.md" -not -path "./.git/*" | xargs grep -L "classification:"

# 检查 L3 笔记是否有意外的外部链接
grep -r "classification: L3" --include="*.md" -l | xargs grep -l "http"

# 验证 frontmatter 格式
find . -name "*.md" -exec head -5 {} \; | grep -c "^---$"

# 检查是否有敏感信息泄露到 L1/L2 笔记
grep -rn "身份证\|银行卡\|密码\|社保" --include="*.md" | grep -v "classification: L3"

# 统计各领域笔记数量
for d in Learning Creative Work Personal Chronicles; do
  echo "$d: $(find 0*-$d -name '*.md' 2>/dev/null | wc -l)"
done
```

---

## 4. Ollama 本地模型

### 安装 Ollama

```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama
```

### 拉取推荐模型

```bash
# 文本生成模型
ollama pull qwen3:8b       # 通用推理，适合 L2/L3 数据
ollama pull gemma3:12b     # 更强推理能力

# 嵌入模型
ollama pull bge-m3         # 多语言嵌入，知识检索核心
```

### 模型选择指南

| 场景 | 推荐模型 | 原因 |
|-----|---------|------|
| 日常笔记整理 | qwen3:8b | 速度快，中文优秀 |
| 深度知识分析 | gemma3:12b | 推理能力更强 |
| 知识检索 | bge-m3 | 多语言嵌入效果最佳 |
| 隐私数据处理 | qwen3:8b | 本地运行，安全可控 |

### Ollama API 使用

```bash
# 文本生成
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:8b",
  "prompt": "总结以下学习笔记的要点...",
  "stream": false
}'

# 文本嵌入
curl http://localhost:11434/api/embed -d '{
  "model": "bge-m3",
  "input": "知识图谱分析"
}'
```

---

## 5. 隐私-模型映射配置

```yaml
# privacy_model_mapping.yaml
# 根据数据分类自动选择 AI 模型

mapping:
  L1:
    description: "公开数据 - 可使用任意模型"
    preferred_provider: anthropic
    preferred_model: claude-sonnet-4-20250514
    fallback_provider: ollama
    fallback_model: qwen3:8b
    allowed_providers: [anthropic, openai, ollama]
    
  L2:
    description: "内部数据 - 仅可信云端或本地"
    preferred_provider: ollama
    preferred_model: gemma3:12b
    fallback_provider: anthropic  # 仅企业版
    fallback_model: claude-sonnet-4-20250514
    allowed_providers: [anthropic, ollama]
    requires_confirmation: true
    
  L3:
    description: "私密数据 - 仅限本地"
    preferred_provider: ollama
    preferred_model: qwen3:8b
    fallback_provider: ollama
    fallback_model: gemma3:12b
    allowed_providers: [ollama]
    block_cloud: true

# 自动路由规则
routing:
  # 检测笔记分类并选择模型
  detect_classification: true
  # 如果检测失败，默认使用最高安全级别
  default_classification: L3
  # 日志记录所有路由决策
  log_routing_decisions: true
```

---

## 6. 自动化工作流

### Cron 任务配置

```yaml
# workflows.yaml
workflows:
  # ===== 每日任务 =====
  
  # 知识索引更新
  daily_index:
    schedule: "0 2 * * *"
    description: "更新知识库索引和图谱"
    steps:
      - action: "scan_new_notes"
        path: "/path/to/识海"
      - action: "update_dataview_index"
      - action: "generate_daily_summary"
        model: "ollama/qwen3:8b"
      - action: "save_to_chronicles"
        classification: L1

  # 收件箱整理
  inbox_triage:
    schedule: "0 8 * * *"  # 每天早上 8 点
    description: "整理收件箱中的待分类笔记"
    steps:
      - action: "list_unclassified_notes"
        path: "00-Inbox/"
      - action: "suggest_classification"
        model: "ollama/qwen3:8b"
      - action: "move_to_domain"
        require_confirmation: true

  # ===== 每周任务 =====
  
  # 知识连接发现
  weekly_connections:
    schedule: "0 3 * * 0"  # 每周日凌晨 3 点
    description: "发现笔记之间的潜在连接"
    steps:
      - action: "analyze_graph"
        min_connections: 2
      - action: "suggest_links"
        model: "ollama/gemma3:12b"
      - action: "create_connection_report"
        classification: L1

  # 孤立笔记清理
  orphan_cleanup:
    schedule: "0 4 * * 0"  # 每周日凌晨 4 点
    description: "识别并处理孤立笔记"
    steps:
      - action: "find_orphan_notes"
        min_age_days: 30
      - action: "suggest_actions"
        options: [link, merge, archive, delete]
      - action: "generate_report"

  # ===== 每月任务 =====
  
  # 隐私合规审计
  privacy_audit:
    schedule: "0 5 1 * *"  # 每月 1 日凌晨 5 点
    description: "全面隐私合规检查"
    steps:
      - action: "verify_classifications"
      - action: "check_cloud_leaks"
      - action: "audit_downgrade_history"
      - action: "generate_compliance_report"
        classification: L3  # 报告本身也是私密的
      
  # 知识增长报告
  growth_report:
    schedule: "0 6 1 * *"  # 每月 1 日早上 6 点
    description: "生成月度知识增长报告"
    steps:
      - action: "count_notes_by_domain"
      - action: "calculate_growth_metrics"
      - action: "identify_trending_topics"
      - action: "generate_report"
        model: "ollama/qwen3:8b"
        classification: L1
```

### 手动触发命令

```bash
# Hermes Agent
hermes run daily-index-update
hermes run privacy-audit --dry-run

# Claude Code
claude -p "运行知识索引更新"
claude -p "执行隐私审计检查"
```

---

> **提示**: 所有涉及 L3 数据的工作流必须使用本地模型执行，且日志中不得包含原始敏感内容。
