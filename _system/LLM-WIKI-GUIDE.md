# 识海 · 完整架构指南

> 版本: 2.0
> MindSea 是一个面向 LLM 时代的知识管理框架，基于 Karpathy 的 LLM Wiki 方法论，
> 结合 Obsidian 的本地优先理念和 AI Agent 的自动化能力，构建个人/团队的结构化知识图谱。

---

## 一、设计理念

### 1.1 为什么需要 LLM Wiki？

1. **信息碎片化**: 知识分散在不同平台、不同格式中，难以形成体系
2. **关联缺失**: 线性笔记无法表达知识间的复杂关系
3. **检索低效**: 关键词搜索无法理解语义，找笔记比记笔记更费时

核心理念：**让 AI 成为知识的架构师，而不仅仅是记录的工具**。

### 1.2 三个坚持

1. **本地优先 (Local First)**: 数据永远在你的设备上
2. **结构化自由 (Structured Freedom)**: 在规范框架内保持表达灵活性
3. **人机共生 (Human-AI Symbiosis)**: 人负责创意和决策，AI 负责组织和维护

---

## 二、整体架构

### 2.1 五域一库

```
mindsea/
├── _system/              # 系统配置与模板
│   ├── SCHEMA.md         # 知识宪法
│   ├── WORKFLOW.md       # AI 协作工作流
│   ├── LLM-WIKI-GUIDE.md # 本指南
│   └── templates/        # 通用模板
│       ├── concept.md
│       ├── thought.md
│       ├── view.md
│       ├── memo.md
│       ├── project.md
│       └── investment.md
│
├── learning/             # 📚 学习域 — 知识输入
│   ├── concepts/         # 概念笔记
│   └── tools/            # 工具笔记
│
├── business/             # 💼 商业域 — 投资与策略
│   ├── investment/       # 投资理财
│   └── strategies/       # 商业策略
│
├── media/                # 📱 自媒体域 — 内容与平台
│   ├── platforms/        # 平台运营
│   └── content/          # 内容策略
│
├── creative/             # 💡 创意域 — 项目与想法
│   └── projects/         # 项目
│
├── personal/             # 🔒 个人域 — 私密空间
│   ├── thoughts/         # 个人思想
│   ├── views/            # 个人观点（5组: business/tech/philosophy/creative/trends）
│   └── memos/            # 个人备忘
│
├── raw/                  # 📦 素材库 — 原始材料（不可变）
│   └── articles/         # 文章原文
│
├── index.md              # 全局导航
└── log.md                # 全局操作日志
```

---

## 三、域详解

### 3.1 学习域 (learning/)
**使命**: 将外部知识转化为内部结构化概念。

实体类型：Concept（概念）、Tool（工具）

质量标准：
- 每个概念必须有明确的定义
- 必须标注知识来源
- 必须与至少 1 个其他概念建立关联

### 3.2 商业域 (business/)
**使命**: 沉淀投资判断和商业策略。

实体类型：Investment、Strategy、Case、Ecommerce

### 3.3 自媒体域 (media/)
**使命**: 记录内容创作和平台运营经验。

实体类型：Content、Platform

### 3.4 创意域 (creative/)
**使命**: 孵化思想，形成独立见解。

实体类型：Project、Idea

生命周期：🌱 seed → 🌿 growing → 🌳 mature

### 3.5 个人域 (personal/)
**使命**: 私密的思想空间，最高隐私保护。

实体类型：Thought、View、Memo

隐私规则：🔴 绝密等级，所有内容仅本地存储。

---

## 四、关联图谱

### 4.1 关联类型（15种）

详见 `SCHEMA.md` 第三节。

### 4.2 图谱健康度指标

详见 `SCHEMA.md` 第八节。

---

## 五、AI 协作模式

### 5.1 触达层：日常交互

```
用户: "帮我记一个笔记，关于注意力机制的"
AI:   → 创建 learning/concepts/attention-mechanism.md
      → 填写 Frontmatter (type, created, tags)
      → 建立与相关概念的关联（双向）
```

### 5.2 深度层：周期性分析

**每日**: 扫描变更、生成日报、检查关联完整性
**每周**: 知识图谱健康度审计、关联建议、过期提醒
**每月**: 趋势分析报告、标签体系优化建议

---

## 六、隐私与安全

| 等级 | 标识 | 存储 | AI 处理 |
|---|---|---|---|
| 🟢 公开 | `public` | 本地 + 云端备份 | 无限制 |
| 🟡 内部 | `internal` | 本地 + 加密同步 | 仅可信模型 |
| 🔴 绝密 | `secret` | 仅本地 | 仅本地模型 |

---

## 七、快速开始

1. 克隆或下载 MindSea 模板
2. 在 Obsidian 中打开项目文件夹
3. 阅读 `_system/SCHEMA.md` 了解规范
4. 运行 `python3 scripts/wiki-audit.py .` 检查初始状态
5. 开始记录你的第一个知识页面！

---

## 八、最佳实践

- 保持原子化：一笔记一概念
- 强制双向链接：每个页面至少 2 条出链
- 定期审计：每周运行 `wiki-audit.py`
- 标签一致：优先使用已有标签，避免碎片化
- 隐私前置：创建页面时就设定隐私等级，不要事后补
