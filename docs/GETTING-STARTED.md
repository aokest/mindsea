# 快速上手指南

> 从零开始使用 识海，5 分钟理解核心概念，3 步完成安装。

---

## 目录

- [安装 3 步](#安装-3-步)
- [核心概念 5 分钟](#核心概念-5-分钟)
- [第一个页面教程](#第一个页面教程)
- [日常使用模式](#日常使用模式)
- [AI Agent 使用](#ai-agent-使用)
- [常见问题 FAQ](#常见问题-faq)

---

## 安装 3 步

### 第 1 步：克隆仓库

```bash
git clone https://github.com/your-org/识海.git
cd 识海
```

目录结构如下：

```
识海/
├── README.md                    # 项目说明
├── CLAUDE.md                    # Claude Code 项目约定
├── templates/                   # 页面模板
│   ├── fragment.md              # 碎片模板
│   ├── concept.md               # 概念模板
│   └── permanent.md             # 永久笔记模板
├── learning/                    # 学习域
│   ├── index.md                 # 域索引
│   ├── fragments/               # 碎片层
│   ├── concepts/                # 概念层
│   └── permanent/               # 永久层
├── creative/                    # 创意域
├── work/                        # 工作域
├── personal/                    # 个人域
├── chronicles/                  # 编年域
├── inbox/                       # 待归档收件箱
├── docs/                        # 项目文档
└── .obsidian/                   # Obsidian 配置
```

### 第 2 步：用 Obsidian 打开

1. 打开 Obsidian
2. 选择 **打开本地仓库（Open folder as vault）**
3. 选择刚才克隆的 `识海` 文件夹
4. 首次打开时，Obsidian 会提示信任该仓库 → 点击 **信任作者并开启插件**

首次打开后建议检查：

- **设置 → 编辑器** → 确认 `严格换行` 关闭
- **设置 → 文件与链接** → 新建笔记位置设为 `inbox`
- **设置 → 核心插件** → 确认 `图谱视图` 已开启

### 第 3 步：配置 AI Agent（可选）

根据你使用的 AI 工具，选择对应配置：

**Hermes Agent 用户：**

```bash
# 编辑配置文件
vim ~/.hermes-agent/config.yaml
```

```yaml
wiki:
  path: "/你的/路径/识海"
  index_update: true
capture:
  default_domain: "learning"
  default_privacy: "L2"
```

**Claude Code 用户：**

```bash
cd /你的/路径/识海
# CLAUDE.md 已随仓库提供，直接可用
claude "检查项目结构是否正确"
```

**Ollama 用户（本地 AI）：**

```bash
ollama pull qwen3:8b
ollama pull bge-m3
```

---

## 核心概念 5 分钟

### 五域（Five Domains）

识海 将所有知识划分为五个域：

| 域 | 英文 | 内容 | 示例 |
|----|------|------|------|
| 🎓 学习 | `learning` | 技术知识、理论、学习笔记 | Transformer 架构、RAG 原理 |
| 🎨 创意 | `creative` | 创作素材、灵感、设计思考 | 故事构思、UI 设计理念 |
| 💼 工作 | `work` | 项目文档、会议记录、决策 | 项目方案、技术选型记录 |
| 🧠 个人 | `personal` | 个人思考、价值观、反思 | 职业规划、读书感悟 |
| 📅 编年 | `chronicles` | 时间线记录、事件流水 | 每周回顾、里程碑记录 |

**选择域的原则**：一个知识页面只属于一个域。如果跨域，选最主要的域，然后通过双向链接关联其他域。

### 认知递进（Cognitive Progression）

每个域内的知识都经历三个阶段的递进：

```
fragments（碎片）→ concepts（概念）→ permanent（永久）
```

| 阶段 | 特征 | 生命周期 | 示例 |
|------|------|----------|------|
| **fragments** | 原始记录，未加工 | 数天~数周 | "今天学到 MoE 是稀疏激活的" |
| **concepts** | 结构化，有分析 | 数周~数月 | 完整的 MoE 架构解析，含优缺点分析 |
| **permanent** | 精炼，可复用 | 持久 | "模型扩展的核心权衡：密度 vs 效率" |

**晋升条件**：
- `fragments` → `concepts`：内容已补充完整，有明确结构，至少 2 个双向链接
- `concepts` → `permanent`：经过验证，精炼为可跨场景复用的知识

### 双向链接（Bidirectional Links）

Obsidian 的核心特性。用 `[[]]` 语法创建链接：

```markdown
MoE 架构通过稀疏激活实现高效扩展，
与 [[transformer-architecture]] 中的密集计算形成对比。
这种设计在 [[scaling-laws]] 约束下找到了新的平衡点。
```

链接不仅让 A 指向 B，B 的页面也会自动显示"被 A 引用"。

### 隐私分级（Privacy Levels）

| 级别 | 含义 | AI 处理规则 | 示例 |
|------|------|------------|------|
| **L1** | 公开内容 | 可发送云端 AI，可发布 | 公开技术笔记、博客草稿 |
| **L2** | 内部内容 | 可用受信云端 AI，不发布 | 项目内部文档、团队笔记 |
| **L3** | 隐私内容 | 仅本地 AI（Ollama） | 个人日记、密码、敏感决策 |

---

## 第一个页面教程

让我们创建一个完整的学习笔记。

### 步骤 1：选择域

这是一个关于 RAG 的学习笔记 → 属于 `learning` 域。

### 步骤 2：复制模板

在 Obsidian 中：
1. 按 `Ctrl/Cmd + P` 打开命令面板
2. 输入 `Templater`，选择 `Templater: Insert Template`
3. 选择 `templates/concept.md`（我们直接创建概念级笔记）

或者手动创建文件 `learning/concepts/rag-fundamentals.md`。

### 步骤 3：填写 Frontmatter

```yaml
---
domain: learning
privacy: L1
stage: concepts
created: 2025-06-15
updated: 2025-06-15
tags: [rag, retrieval, llm, architecture]
---
```

**字段说明**：
- `domain`：所属域（learning/creative/work/personal/chronicles）
- `privacy`：隐私级别（L1/L2/L3）
- `stage`：认知阶段（fragments/concepts/permanent）
- `created`：创建日期
- `updated`：最后更新日期
- `tags`：标签数组

### 步骤 4：撰写内容

```markdown
# RAG 基础：检索增强生成

## 核心定义

RAG（Retrieval-Augmented Generation）是一种将外部知识检索与大语言模型
生成能力结合的架构模式。核心思想：先检索，再生成。

## 工作流程

1. **索引阶段**：将文档切块 → 向量化 → 存入向量数据库
2. **查询阶段**：用户问题 → 向量检索 → 获取相关片段
3. **生成阶段**：将检索结果 + 问题 → 输入 LLM → 生成回答

## 关键组件

- **Chunking**：文档切块策略直接影响检索质量
- **Embedding Model**：将文本转为向量，推荐 [[bge-m3]]
- **Vector Store**：向量数据库，如 Milvus、Chroma、Qdrant
- **Retriever**：检索器，核心是相似度匹配
- **Generator**：LLM，整合检索结果生成最终回答

## 与其他模式的关系

- [[prompt-engineering]]：RAG 是高级 prompt 技术的基础
- [[fine-tuning]]：RAG 和微调是互补的两种知识注入方式
- [[ai-agent]]：Agentic RAG 是 RAG 的进化方向

## 局限性

- 检索质量决定回答质量（garbage in, garbage out）
- 上下文窗口限制了能检索到的内容量
- 无法处理需要推理才能得出的隐含信息

## 参考资料

- Lewis et al., 2020 — 原始 RAG 论文
- [LangChain RAG 文档](https://python.langchain.com/docs/tutorials/rag/)

## 思考

> RAG 的本质是在推理时注入知识，与训练时注入知识（微调）形成互补。
> 未来方向是 Agentic RAG——Agent 自主决定何时检索、检索什么、如何整合。
```

### 步骤 5：建立双向链接

检查笔记中的 `[[]]` 链接，确保它们指向存在的页面或你计划创建的页面：

- `[[bge-m3]]` → 如果不存在，记下来稍后创建
- `[[prompt-engineering]]` → 同上
- `[[fine-tuning]]` → 同上
- `[[ai-agent]]` → 同上

对于不存在的链接，Obsidian 图谱视图中会显示为"未创建的节点"，你可以随时点击创建。

### 步骤 6：更新索引

打开 `learning/index.md`，在相应区域添加新笔记的链接：

```markdown
## 最近更新

- [[learning/concepts/rag-fundamentals| RAG 基础：检索增强生成]] — 2025-06-15
```

**或者使用 Dataview 自动更新**（如果你的 index.md 已配置 Dataview 查询）：

```dataview
TABLE tags, updated, privacy
FROM "learning"
SORT updated DESC
LIMIT 10
```

---

## 日常使用模式

### 每天 5 分钟（碎片捕获）

适合：忙碌的日常，保持知识输入的连续性。

```
早上通勤：
  → Hermes，帮我记录一下：[今天想研究的主题/学到的东西]

午休碎片时间：
  → 打开 Obsidian，快速浏览 inbox/ 中的新碎片

睡前：
  → 确认今天 inbox 的碎片是否需要补充链接
  （如果配置了 Hermes cron，这步自动完成）
```

### 每周 30 分钟（知识整理）

适合：保持知识库的有序性，不积累太多待处理项。

```
周末安排 30 分钟：

1. 碎片回顾（10 分钟）
   - 浏览本周积累的 fragments
   - 标记值得深挖的碎片（添加 TODO 或 star 标记）

2. 链接整理（10 分钟）
   - 检查新建笔记的双向链接是否合理
   - 在图谱视图中发现新的关联

3. Stage 评估（10 分钟）
   - 已成熟的碎片 → 晋升为 concepts
   - 过时的碎片 → 归档或删除
```

### 每月 2 小时（深度维护）

适合：保持知识库的长期健康度。

```
每月第一个周末安排 2 小时：

1. Claude Code 知识审计（30 分钟）
   - 运行月度审计脚本
   - 审查孤立页面和断链报告
   - 决定处理方案

2. 隐私审查（30 分钟）
   - L3 内容是否仍需保持 L3？
   - 是否有内容可以降级为 L1/L2？

3. 结构优化（30 分钟）
   - 域结构是否需要调整？
   - 标签体系是否需要统一？

4. 内容产出（30 分钟）
   - 从 concepts 中选择成熟的内容
   - 通过 OpenClaw 生成博客/文档/Newsletter
```

---

## AI Agent 使用

根据你的工具组合，选择适合的工作方式。

### 无 Agent · 纯手动

完全使用 Obsidian 原生能力，零 AI 依赖。

**优点**：完全控制，零隐私风险
**适合**：AI 工具不可用，或 L3 隐私内容

**手动工作流**：
1. 手动创建笔记（使用模板）
2. 手动填写 frontmatter
3. 手动建立双向链接
4. 手动更新 index.md
5. 手动管理 stage 晋升

**效率提示**：
- 善用 Templater 模板减少重复操作
- 利用 Dataview 自动生成索引和统计
- 设置 Obsidian 快捷键加速常用操作

### 有 Hermes · 轻量使用

Hermes 处理日常碎片捕获和知识查询。

**日常对话中**：
```
你：帮我记一下，今天我们讨论了微服务的优缺点，
   核心观点是微服务适合大团队但增加运维复杂度。

Hermes：已创建笔记 → work/fragments/2025-06-15-microservice-pros-cons.md
       已自动链接到：[[work/concepts/microservice-architecture]]
       还有其他要补充的吗？
```

**知识查询**：
```
你：我之前记录过哪些关于数据库优化的笔记？

Hermes：找到了 3 条相关内容：
       1. work/concepts/query-optimization.md — SQL 查询优化策略
       2. learning/fragments/2025-05-index-design.md — 索引设计笔记
       3. learning/concepts/b-tree-index.md — B-Tree 索引原理
```

**自动维护**（通过 cron）：
- 每日：碎片归档、链接检查
- 每周：索引更新
- 每月：审计提醒

### 有 Claude Code · 深度使用

Claude Code 处理需要深度推理的维护任务。

**知识审计**：
```bash
cd /path/to/识海
claude "执行本月知识审计，重点关注：
1. fragments 中超过 30 天未更新的页面
2. 孤立页面清单
3. 标签使用建议"
```

**批量格式化**：
```bash
claude "检查所有 .md 文件的 frontmatter 完整性，
缺少字段的自动补充默认值"
```

**内容重构**：
```bash
claude "把 learning/fragments/ 下关于 Rust 的 5 个碎片
整合为一篇完整的 concepts 级笔记"
```

### 组合使用（推荐）

```
Hermes（日常）+ Claude Code（月度）+ Ollama（L3 隐私）
```

这是最高效的工作方式：
- **Hermes** 负责日常碎片捕获、知识查询、自动维护
- **Claude Code** 负责月度审计、批量处理、深度重构
- **Ollama** 负责 L3 隐私内容的本地处理

---

## 常见问题 FAQ

### Q: 一个笔记属于多个域怎么办？

**A**: 选择一个主域存放文件，通过双向链接关联其他域。例如一篇"AI 在项目管理中的应用"，主域是 `work`，但可以链接到 `learning/concepts/ai-agent`。

### Q: fragments 存了很久都没晋升，要删除吗？

**A**: 不建议删除。有三种处理方式：
1. **补充后晋升**：花 10 分钟补充内容，升级为 concepts
2. **合并**：多个相关碎片合并为一篇 concepts
3. **归档**：移动到 `archive/` 目录，保留但不影响活跃视图

### Q: 隐私级别标记错了怎么办？

**A**: 
- 如果 L1/L2 标错了：直接修改 frontmatter 中的 `privacy` 字段
- 如果 L3 内容被错误发送到云端：立即修改该内容的敏感信息，并检查是否有其他 L3 内容被泄露

### Q: Dataview 查询不生效？

**A**: 检查以下几点：
1. Dataview 插件是否已安装并启用
2. 查询语法是否正确（注意反引号数量）
3. frontmatter 中的字段名是否拼写正确
4. 退出阅读模式查看原始代码块

### Q: 没有 AI Agent 也能用吗？

**A**: 完全可以。识海 的核心是结构化知识管理，AI 工具是增强而非必要。手动模式下，善用 Obsidian 模板和 Dataview 就能高效运作。

### Q: Ollama 太慢了怎么办？

**A**: 
- 使用更小的模型：`qwen3:4b` 代替 `qwen3:8b`
- 只对 L3 内容使用 Ollama，L1/L2 用云端 AI
- 使用 GPU 加速：`OLLAMA_GPU=1 ollama serve`

### Q: 如何备份知识库？

**A**: 识海 基于纯 Markdown 文件，备份方式灵活：
```bash
# Git 备份（推荐）
git add -A && git commit -m "backup: $(date +%Y-%m-%d)" && git push

# 本地备份
tar -czf mindsea-backup-$(date +%Y%m%d).tar.gz /path/to/识海
```

### Q: 多人协作可以吗？

**A**: 可以。通过 Git 同步，但建议：
- 每人负责自己的域，减少冲突
- `inbox/` 作为公共区域
- L3 内容放在 `.gitignore` 中，不提交到共享仓库

### Q: 如何从其他笔记工具迁移？

**A**: 
- **从 Notion**：导出为 Markdown，按域重新组织
- **从 Roam/Obsidian**：直接复制文件，补充 frontmatter
- **从 Evernote**：使用 enex-to-markdown 工具转换
- **通用方法**：将现有笔记放入 `inbox/`，逐步分类到各域

### Q: 标签太多太乱怎么办？

**A**: 定期整理标签体系：
```bash
# Claude Code 可以帮你分析标签使用情况
claude "统计所有标签的使用频率，找出拼写变体和低频标签"
```

建议标签规范：
- 使用小写英文：`rag` 而非 `RAG` 或 `Rag`
- 用连字符连接：`machine-learning` 而非 `machinelearning`
- 控制总数：核心标签 20-30 个，避免过度细分

---

> **下一步**: 阅读 [工具集成指南](TOOL-INTEGRATION.md) 了解如何配置 AI 工具实现自动化维护。
