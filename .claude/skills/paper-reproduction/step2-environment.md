# 第二步：环境配置

## 目标
分析依赖，提供两种选择：生成 `Claude-require.txt` 或直接安装环境。

## 1. 扫描依赖

按优先级查找：`README.md` → `requirements.txt` → `environment.yml` → `setup.py` → `pyproject.toml` → `Pipfile` → Dockerfile

**同时扫描测试脚本的额外依赖**：分析 `test.py`、`eval.py`、用户提供的参考脚本的 import 语句，找出 `requirements.txt` 中未包含的包（如 `lpips`、`torchmetrics`、`scikit-image`），加入最终依赖列表。

## 2. 分析版本

- 从 README 提取环境要求（Python/CUDA/PyTorch 版本）
- 从 requirements.txt 提取所有依赖
- **API 最低版本检查**：扫描源码 import 的关键 API（如 `AugMix`、`F.interpolate`），确认推断的版本包含这些 API。不确定时用 `WebSearch` 查 "torchvision AugMix added version" 确认
- 未指定版本的包：基于已明确版本包的发布时间推断兼容版本
- Python 版本：优先 README > requirements.txt > 默认 3.8

## 3. 兼容性检查（生成 require 文件前必须执行）

检查以下已知冲突链，自动补充约束包：

| 冲突模式 | 触发条件 | 自动添加/操作 |
|---------|---------|--------------|
| protobuf ⊗ tensorboard | `pytorch-lightning<2.0` 或 `tensorboard` 在依赖中 | `protobuf<=3.20` |
| API 在推断版本中不存在 | 任何 import 报 `cannot import name 'X'` | ①先查代码是否真正调用该API（死代码就删掉）；②若确实需要，再查该 API 最低版本
| numpy ⊗ numba | `numba` 且 numpy 未锁定 | `numpy<1.24` |
| setuptools ⊗ tensorboard | `tensorboard` 且 Python≥3.12 | 降 Python 到 3.10 |

此表持续更新。遇到新的兼容冲突时，修复后回写到本表。

## 4. 呈现并询问 A/B

```
📋 环境依赖分析结果：
核心依赖：
- Python: 3.8
- PyTorch: 1.10.2 (CUDA 11.3)
- torchvision: 0.11.3
...共 N 个包

请选择：
A. 生成 Claude-require.txt（手动安装，适合远程服务器）
B. 直接帮我安装环境（环境名：<模型简称>）
```

**自动判断**：用户说了"服务器/远程/autodl"→ 选A，"本地/本机"→ 选B，否则询问。

## 选项A：生成 Claude-require.txt

- 每个包必须明确版本号（`package==version`）
- 文件头部注释：Python版本 + CUDA版本 + 服务器部署步骤
- 更新状态文件，提示用户准备好后回复"继续"

## 选项B：直接安装环境

- 优先 conda → 不可用则 pip+venv
- 环境名：从模型名称提取简称（如 "UIR-Net" → "uir-net"）
- 步骤：`conda create` → `conda install pytorch` → `pip install -r`
- 验证：`python -c "import torch; print(torch.__version__)"`

## 中断处理
安装失败时记录 `last_error`，保留已创建环境，提示修复方案。
