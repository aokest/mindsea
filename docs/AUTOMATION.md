# 识海 自动化架构

## 概述

识海 自动化系统通过三组 Python 脚本实现知识图谱的**健康检查**、**隐私扫描**和**统计分析**。所有脚本均为只读操作，不会修改知识库内容。

## 脚本一览

| 脚本 | 功能 | 退出码 |
|------|------|--------|
| `wiki-health.py` | 知识图谱健康检查 | 0=健康, 1=警告, 2=错误 |
| `privacy-scan.py` | 隐私泄露扫描 | 0=安全, 1=中危, 2=高危 |
| `wiki-stats.py` | 统计与可视化报告 | 0=正常 |

## 知识库结构

```
mindsea/
├── personal/          # 个人域 (L3 机密)
├── wiki-learning/     # 学习域 (L2 内部)
├── wiki-ideas/        # 创意域 (L2 内部)
├── wiki-work/         # 工作域 (L2 内部)
├── wiki-chronicles/   # 记录域 (L1 公开)
├── raw/               # 原始素材 (L1 公开)
├── work-log/          # 工作日志 (L3 机密)
├── _system/           # 系统配置
├── scripts/           # 自动化脚本
└── docs/              # 文档
```

## Frontmatter 规范

每个 `.md` 文件必须包含 YAML frontmatter：

```yaml
---
title: 页面标题
type: note|concept|log|project
domain: personal|wiki-learning|...
status: draft|active|archived
created: 2025-01-15
updated: 2025-03-20
tags: machine-learning, python
---
```

**必填字段**: `title`, `type`, `domain`

## 链接规则

- 每个页面应包含 **≥ 2 条 wikilink** (`[[目标页面]]`)
- 相关页面应建立**双向链接**
- L3 域内容不应被 L1/L2 域页面链接

## 隐私分级

| 级别 | 含义 | 域 |
|------|------|----|
| L1 | 公开 | wiki-chronicles, raw |
| L2 | 内部 | wiki-learning, wiki-ideas, wiki-work |
| L3 | 机密 | personal, work-log |

## 使用示例

```bash
# 健康检查
python scripts/wiki-health.py .

# 隐私扫描（自定义关键词）
python scripts/privacy-scan.py . --keywords "公司名" "项目代号"

# 统计报告（JSON 输出）
python scripts/wiki-stats.py . --json > report.json
```

## CI/CD 集成

建议将健康检查和隐私扫描集成到 pre-commit hook 或 CI 流水线中，确保提交前知识图谱符合规范。

## 设计原则

1. **只读**: 所有脚本仅读取文件，不做任何修改
2. **零依赖**: 仅使用 Python 标准库
3. **渐进式**: 先警告后错误，给用户修复时间
4. **可扩展**: 关键词、域映射等均可配置
