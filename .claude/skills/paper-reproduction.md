---
name: paper-reproduction
description: >
  论文复现全流程自动化工具。支持：
  1. 根据论文名称搜索/下载PDF + 克隆源码
  2. 分析环境依赖并生成 Claude-require.txt 或直接安装conda/pip环境
  3. 数据集自动放置（分析源码预期 → 匹配用户数据结构 → 映射）
  4. 修改训练/推理代码路径和超参数
  5. 对比参考脚本补全缺失指标（LPIPS/PSNR/SSIM/UCIQE）
  6. 自动生成批量测试脚本 + 服务器配置建议 + 源码打包
  支持从任意步骤开始，支持中断后恢复（状态持久化）。
  触发词：论文复现、复现论文、reproduce paper、paper reproduction、从零开始复现
---

# 论文复现全流程 Skill

## 核心原则

1. **状态持久化优先**：每个步骤开始前先读 `.paper-repro-state.json`，完成后立即更新。
2. **默认值优先**：用户未指定的参数一律使用源码默认值。
3. **最小询问原则**：能自主判断的就直接执行。仅在信息不足/结构不匹配/用户明确要求时才询问。
4. **中断安全**：中断时在状态文件记录进度和错误，下次从断点继续。
5. **禁止虚构**：搜索论文必须用真实URL，找不到如实告知。

## 状态文件 `.paper-repro-state.json`

```json
{
  "current_step": 1,
  "paper_name": "...",
  "source_dir": "./xxx-src",
  "git_url": "https://github.com/...",
  "datasets_folder": "Dataset",
  "env_name": "xxx",
  "env_type": "conda",
  "requirements_file": "Claude-require.txt",
  "step_history": [
    {"step": 1, "status": "completed", "note": "已克隆源码"}
  ],
  "last_error": null
}
```

- 每次启动时先检查此文件
- 存在 → 告知用户进度，询问是否继续
- 不存在 → 从头开始或从用户指定步骤开始

## 快速启动模式

用户同时提供 Git地址 + 数据集路径 + 训练/测试要求时，最大化自动化：
- 直接克隆源码、分析数据集结构、修改路径、补全指标、生成测试脚本
- **环境判断**：用户说"服务器/远程/autodl/租显卡"→ 自动选A（生成require文件），"本地/本机"→ 自动选B（直接安装），未说明 → 照常询问A/B
- 完成后自动输出服务器配置建议，选A时自动打包源码

## 四步流程

执行每一步时，**必须同时读取对应子skill文件**获取详细指令：

| 步骤 | 子skill | 核心 |
|------|--------|------|
| 第一步 | `paper-reproduction/step1-acquire.md` | 获取论文与源码 |
| 第二步 | `paper-reproduction/step2-environment.md` | 环境依赖分析 + A/B选择 |
| 第三步 | `paper-reproduction/step3-dataset.md` | 数据集结构分析 + 放置 |
| 第四步 | `paper-reproduction/step4-code.md` | 代码修改 + 测试 + 打包 |

## 用户指令

| 用户表述 | 行为 |
|---------|------|
| "从零开始"、"第一步" | 从第一步开始 |
| "装好环境了"、"从第二步" | 跳过第一步 |
| "从第三步" | 跳过第一、二步 |
| "从第四步"、"只需要改代码" | 只执行第四步 |
| "继续" | 从断点继续 |
| "数据集文件夹叫 XXX" | 设置 datasets_folder |
| "环境名叫 XXX" | 使用指定环境名 |
| "用 pip 不用 conda" | 跳过 conda |
| "跳过环境安装" | 跳过第二步 |
| "服务器/远程/autodl" | 第二步自动选 A |
| "本地/本机" | 第二步自动选 B |
