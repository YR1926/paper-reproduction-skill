# 论文复现全流程 Skill (Paper Reproduction Skill)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | 中文

---

## 中文

### 简介

一个 Claude Code 的 skill，用于自动化论文复现全流程。支持从论文搜索、源码克隆、环境配置、数据集放置到代码修改与测试的完整流水线。

### 功能

1. **论文获取**：根据论文名称搜索/下载 PDF，查找并克隆官方源码
2. **环境配置**：自动分析依赖，支持生成 `Claude-require.txt`（适合远程服务器）或直接安装 conda/pip 环境
3. **数据集放置**：分析源码对数据结构的期望，自动匹配用户数据集并建立映射（软链接优先）
4. **代码修改**：修改路径与超参数、补全缺失的评估指标（LPIPS/PSNR/SSIM/UCIQE 等）、生成批量测试脚本、打包源码

### 特性

- **状态持久化**：通过 `.paper-repro-state.json` 记录进度，支持中断后从断点恢复
- **智能判断**：能自主分析的问题不打扰用户，仅在关键决策点询问
- **兼容性检查**：内置 protobuf/tensorboard、numpy/numba 等已知冲突的自动修复
- **灵活起点**：支持从任意步骤开始（"从第二步"、"只需要改代码"）
- **快速模式**：同时提供 Git 地址 + 数据集路径时，最大化自动化处理

### 安装

将本仓库的 `.claude/skills/` 目录复制到你的项目根目录：

```bash
git clone https://github.com/<your-username>/paper-reproduction.git
cp -r paper-reproduction/.claude/skills/ <your-project>/.claude/
```

或者直接作为你的项目模板使用。

### 使用

在 Claude Code 对话中直接描述你的需求即可触发：

```
帮我复现这篇论文：UIR-Net
```

**常用触发词**：论文复现、复现论文、reproduce paper、paper reproduction、从零开始复现

**快捷指令**：

| 表述 | 行为 |
|------|------|
| "从零开始"、"第一步" | 从论文获取开始 |
| "装好环境了"、"从第二步" | 跳过论文获取 |
| "从第三步" | 跳过论文获取和环境配置 |
| "从第四步"、"只需要改代码" | 只修改代码和测试 |
| "继续" | 从上次中断处继续 |
| "服务器/远程/autodl" | 环境配置自动选"生成 require 文件" |
| "本地/本机" | 环境配置自动选"直接安装" |

### 目录结构

```
.claude/skills/
├── paper-reproduction.md              # 主 skill 文件
└── paper-reproduction/
    ├── step1-acquire.md               # 第一步：获取论文与源码
    ├── step2-environment.md           # 第二步：环境依赖分析
    ├── step3-dataset.md               # 第三步：数据集结构分析与放置
    └── step4-code.md                  # 第四步：代码修改 + 测试 + 打包
```

### 许可证

MIT

---

## English

### Overview

A Claude Code skill that automates the full paper reproduction pipeline. It covers paper search, source code cloning, environment setup, dataset placement, code modification, and testing—all within a single guided workflow.

### Features

1. **Paper Acquisition**: Search/download paper PDFs by title, locate and clone official source code
2. **Environment Setup**: Auto-analyze dependencies; choose between generating a `Claude-require.txt` (ideal for remote servers) or installing a conda/pip environment directly
3. **Dataset Placement**: Analyze source code's expected data structure, auto-match user datasets, and map them (prefers symlinks)
4. **Code Modification**: Adjust paths and hyperparameters, add missing evaluation metrics (LPIPS/PSNR/SSIM/UCIQE, etc.), generate batch test scripts, and package source code

### Highlights

- **State Persistence**: Progress is tracked in `.paper-repro-state.json`, allowing recovery from interruptions
- **Minimal Prompts**: Makes autonomous decisions where possible, only asking the user at key decision points
- **Compatibility Checks**: Built-in auto-fixes for known conflicts (protobuf/tensorboard, numpy/numba, etc.)
- **Flexible Entry**: Start from any step ("skip to step 3", "just fix the code")
- **Fast Mode**: When both Git URL and dataset path are provided, maximizes automation

### Installation

Copy the `.claude/skills/` directory to your project root:

```bash
git clone https://github.com/<your-username>/paper-reproduction.git
cp -r paper-reproduction/.claude/skills/ <your-project>/.claude/
```

Or use this repository directly as your project template.

### Usage

Simply describe your need in a Claude Code conversation:

```
Help me reproduce this paper: UIR-Net
```

**Trigger phrases**: 论文复现, 复现论文, reproduce paper, paper reproduction, 从零开始复现

**Quick commands**:

| Phrase | Behavior |
|--------|----------|
| "from scratch" / "step 1" | Start from paper acquisition |
| "environment is ready" / "step 2" | Skip paper acquisition |
| "step 3" | Skip acquisition and environment setup |
| "step 4" / "just modify the code" | Only modify code and test |
| "continue" | Resume from last checkpoint |
| "server/remote/autodl" | Auto-select "generate requirements file" |
| "local" | Auto-select "install directly" |

### Directory Structure

```
.claude/skills/
├── paper-reproduction.md              # Main skill file
└── paper-reproduction/
    ├── step1-acquire.md               # Step 1: Paper & source acquisition
    ├── step2-environment.md           # Step 2: Dependency analysis
    ├── step3-dataset.md               # Step 3: Dataset structure & placement
    └── step4-code.md                  # Step 4: Code modification + testing + packaging
```

### License

MIT
