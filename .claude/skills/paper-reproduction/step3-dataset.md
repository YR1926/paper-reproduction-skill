# 第三步：数据集放置

## 目标
将用户数据集按源码要求放置到正确位置。

## 执行流程

### 1. 确定数据集源目录
- 默认：`./datasets`（或用户指定名称如 `Dataset`、`data`）
- 目录不存在 → 报错等待用户提供

### 2. 分析源码对数据集的期望
**这是最关键的一步——源码期望什么样的目录结构和命名？**

- 阅读 `README.md` 的数据准备章节
- Grep 搜索关键文件（`train.py`、`test.py`、`config.py`、`*.yaml`）中的路径变量：
  `data_root`、`train_dir`、`val_dir`、`test_dir`、`dataset_path`、`dataroot`
- **必须阅读数据加载代码**（`dataset.py`、`dataloader.py`、`data/` 目录下的文件），理解：
  - 期望的**目录结构**（几层？子目录叫什么？）
  - 期望的**子目录命名**（输入图目录叫什么？标签目录叫什么？）
  - 是 paired 还是 unpaired？
  - 文件名是否需要匹配？
- 记录源码期望的准确目录名，例如：源码期望 `images/` + `labels/`，或 `input/` + `gt/` 等

### 3. 分析用户数据集结构
- 用 `ls` / `tree` 列出 `datasets` 文件夹的完整结构
- 识别：训练集/验证集/测试集、各子数据集、文件格式
- **用源码期望去匹配用户结构**：
  - 找到用户数据中对应"输入图"的目录（可能叫 `input`/`images`/`hazy`/`distorted`/`A` 等）
  - 找到用户数据中对应"标签图"的目录（可能叫 `target`/`labels`/`gt`/`groundtruth`/`clear`/`B` 等）
  - 自动检测 paired（有标签目录）和 unpaired（仅有输入目录）
- **自动检测异常并标记**：
  - 同名文件数量不一致
  - 空目录
  - 多余子目录（如 test-LSUI 有 input1/target1 可能是预处理过的副本）

### 4. 制定映射方案
- 对比：源码期望的目录名 vs 用户实际的目录名 → 得出映射关系
- **映射的是目录名，不是固定规则**：每次根据实际分析结果决定
- 多个数据集需要合并到一个 val/test 目录时，先检测文件名冲突
- **优先使用软链接**（Linux/Mac: `ln -s`，Windows: `mklink /J` for 目录, `ln -s` for 文件），不可用时复制
- 用户指定了命名要求（如"data改成datasets"），使用用户指定的名称

### 5. 询问用户（仅在以下情况）
- 源码的目录期望无法从代码中确定（太模糊）
- 用户数据结构与源码期望差异太大，有多种可能的映射方式
- input 和 target 文件数量不一致需要用户决策
- 用户明确要求"需要确认后再执行"
- 其他情况直接执行，不询问

### 6. 执行并报告
- 按方案创建目录结构 + 软链接/复制
- 完成后列出最终结构：
  ```
  datasets/train/images/ → 5600 files (linked)
  datasets/train/labels/ → 5600 files (linked)
  datasets/val/images/   → 490 files (linked)
  datasets/val/labels/   → 489 files (linked, 1 missing)
  ```
