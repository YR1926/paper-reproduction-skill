# 第四步：代码修改 + 测试 + 打包

## 目标
修改训练/测试代码（路径、参数），补全测试指标，生成批量脚本，打包源码。

## 1. 确定用户目标
- "训练" → 聚焦 train 相关文件
- "测试/推理" → 聚焦 test/eval 文件
- 优先检查是否存在 config 文件（`config.py`、`config.yaml`、`options.py` 等）

## 2. 定位关键位置
阅读训练入口 + config 文件，定位：
- 数据路径（`data_root`、`train_dir`、`val_dir`）
- 预训练/输出路径
- 超参数（`batch_size`、`lr`、`epochs`）
- 设备选择（`gpu`、`device`）

## 3. 收集修改项
- 用户已指定的 → 按要求修改
- "按默认值" → 只改路径，不改超参数
- 未提到的超参数 = 使用源码默认值

## 4. 执行路径修改
优先修改 config 文件，减少对训练主文件的侵入。

## 5. 增强测试脚本
如果用户提供了参考测试脚本（如 `test_final.py`），对比源码 `test.py`：
- 提取参考脚本的所有指标（PSNR、SSIM、LPIPS、UCIQE 等）
- 找出源码缺失的指标，自动补全
- 整合参考脚本的合理功能（resize、ref/noref 模式等）
- 同步更新 `Claude-require.txt` 添加新依赖（如 `lpips`）

## 6. 生成批量测试脚本
多测试集时自动生成 `run_tests.sh`：
```bash
# 每个测试集独立运行，结果输出到独立目录
python test.py --val_dir <path> --mode ref --resize 256 --result_dir results/<name>
```

## 7. 服务器配置建议
全部修改完成后输出：
```
📋 服务器配置建议：
- Python: 3.8
- PyTorch: 1.10.2
- CUDA: 11.3
- 显卡: 建议 RTX 3090 或以上（≥8GB 显存）
- 推荐 AutoDL 镜像：PyTorch 1.10 + CUDA 11.3
```

## 8. 打包（选A时执行，询问用户选择方式）

向用户说明两种打包方式：

**A. 仅源码**（适合服务器已有数据集的人）：
- 排除 `datasets/` 目录，只打包修改好的源码
- `tar -czhf <project>-src.tar.gz --exclude="datasets" <source_dir>/`
- 打包后用相对路径告知数据集映射：
  ```
  上传后按以下相对结构放置（从 <source_dir>/../ 视角）：
  <source_dir>/datasets/train/images/     ← 原始 Dataset/train/input/
  <source_dir>/datasets/train/labels/     ← 原始 Dataset/train/target/
  <source_dir>/datasets/val/images/       ← 原始 testset(ref)/{EUVP,LSUI,UIEB}/input/ (合并)
  <source_dir>/datasets/val/labels/       ← 原始 testset(ref)/{EUVP,LSUI,UIEB}/target/ (合并)
  <source_dir>/../Dataset/testset(ref)/   ← 原始 Dataset/testset(ref)/ (测试用，保持原结构)
  <source_dir>/../Dataset/testset(non-ref)/ ← 原始 Dataset/testset(non-ref)/

  所有路径均为相对路径，本地和服务器通用。
  ```

**B. 源码+数据集**（适合从零开始部署）：
- `tar -czhf <project>-src.tar.gz <source_dir>/ ../Dataset/`
- 将源码和 Dataset 一起打包，上传解压后直接可用

## 9. 验证
检查关键引用的路径是否实际存在。

## 10. 输出运行命令
全部完成后，必须清晰列出终端运行命令：
```
# 训练
conda activate <env_name>
cd <source_dir>
python train_supervision.py

# 测试（4个集独立运行）
bash run_tests.sh <checkpoint_path>
# 或逐个运行：
python test.py --val_dir <path> --mode ref --resize 256 --weight <ckpt> --result_dir results/<name>
```

## 错误处理
- 路径不存在 → 检查是否有遗漏的硬编码路径
- 语法错误 → 检查 Python 导入
