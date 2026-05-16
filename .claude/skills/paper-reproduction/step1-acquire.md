# 第一步：获取论文与源码

## 目标
获取论文PDF（可选）和可复现源代码。

## 情况A：用户提供论文名称（无源码地址）

1. **搜索论文**：`WebSearch` 搜索论文名称 + "arxiv"
2. **下载PDF**：`curl -L -o "<paper_name>.pdf" "<pdf_url>"`
3. **查找源码**：`WebSearch` 搜索 "论文名称 github" 或 "论文名称 code"
4. **克隆源码**：`git clone <repo_url> <paper_short_name>-src`
5. 更新状态文件，`current_step = 2`

## 情况B：用户提供源码Git地址（无论文名称）

1. **克隆源码**：`git clone <repo_url>`（目录名用仓库名）
2. 从 README 查找论文标题/链接（可选下载PDF）
3. 更新状态文件

## 情况C：源码已存在

1. 扫描当前目录，识别包含 `train.py`、`README.md`、`requirements.txt` 的源码目录
2. 多个候选时列出让用户选择
3. 更新状态文件

## 错误处理
- `git clone` 失败 → 尝试 `--depth=1`，仍失败则询问用户是否有本地副本
