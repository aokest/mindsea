---
title: Transformer 架构
type: Concept
domain: learning
status: mature
created: 2026-01-15
updated: 2026-05-01
tags: [ai, transformer, deep-learning, nlp]
sources: ["Attention Is All You Need (Vaswani et al., 2017)"]
confidence: high
privacy: 🟢
staleness: yearly
---

# Transformer 架构

## 定义

Transformer 是一种基于自注意力机制（Self-Attention）的深度学习架构，摒弃了传统的 RNN/CNN 结构，完全依赖注意力机制来捕捉序列中的依赖关系。

## 核心要点

- **自注意力机制**: 通过 Query-Key-Value 矩阵计算序列内部的关联权重
- **多头注意力**: 并行多个注意力头，捕捉不同维度的特征
- **位置编码**: 由于没有循环结构，需要额外注入位置信息
- **编码器-解码器**: 原始架构由编码器和解码器两部分组成

## 意义

Transformer 是当前几乎所有大语言模型（GPT、Claude、LLaMA）的基础架构。

## 关联

- [[attention-mechanism|注意力机制]] — Transformer 的核心组件
- [[large-language-models|大语言模型]] — 基于 Transformer 构建
- [[bert|BERT]] — Transformer 编码器的代表应用
