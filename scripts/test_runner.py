#!/usr/bin/env python3
"""
统一测试运行脚本 —— 遍历测试集列表，逐个调用 test.py 并输出到独立结果目录。

特性:
  - 默认遇错即停：中途任何一个测试失败，立即终止后续测试
  - 默认失败回滚：终止后自动删除本次批量测试产生的所有结果目录，恢复到测试前状态
  - 使用 --continue-on-failure 可恢复旧行为（失败后继续运行）
  - 使用 --no-rollback 可保留已完成的结果目录

用法:
  python scripts/test_runner.py --config test_config.json

配置格式 (test_config.json):
{
  "test_script": "test.py",
  "path_arg": "--val_dir",
  "result_arg": "--result_dir",
  "result_base": "results",
  "common": {
    "mode": "ref",
    "resize": 256,
    "weight": "checkpoints/best.pth"
  },
  "datasets": [
    {"name": "EUVP",   "path": "datasets/test/EUVP/input"},
    {"name": "LSUI",   "path": "datasets/test/LSUI/input", "override": {"mode": "noref"}},
    {"name": "UIEB",   "path": "datasets/test/UIEB/input"}
  ]
}

运行效果:
  python test.py --mode ref --resize 256 --weight checkpoints/best.pth \
      --val_dir datasets/test/EUVP/input --result_dir results/EUVP
  python test.py --mode ref --resize 256 --weight checkpoints/best.pth \
      --val_dir datasets/test/LSUI/input --result_dir results/LSUI --mode noref
  python test.py --mode ref --resize 256 --weight checkpoints/best.pth \
      --val_dir datasets/test/UIEB/input --result_dir results/UIEB
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    required = ["test_script", "path_arg", "result_arg", "result_base", "datasets"]
    for key in required:
        if key not in config:
            raise ValueError(f"配置文件缺少必填字段: {key}")
    if not config["datasets"]:
        raise ValueError("datasets 列表为空")
    config.setdefault("common", {})
    return config


def build_args(config: dict, dataset: dict) -> list[str]:
    """为单个数据集构建命令行参数列表。"""
    merged = dict(config["common"])
    merged.update(dataset.get("override", {}))

    args = []
    for key, value in merged.items():
        flag = f"--{key}"
        if isinstance(value, bool):
            if value:
                args.append(flag)
        else:
            args.extend([flag, str(value)])

    args.extend([config["path_arg"], dataset["path"]])
    args.extend([config["result_arg"], f"{config['result_base']}/{dataset['name']}"])
    return args


def run_one(test_script: str, args: list[str]) -> dict:
    """运行一次测试，返回结果字典。"""
    cmd = [sys.executable, test_script] + args
    cmd_str = " ".join(cmd)
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        elapsed = time.time() - start
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed": elapsed,
            "cmd": cmd_str,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": "测试超时（>2小时）",
            "elapsed": elapsed,
            "cmd": cmd_str,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"找不到文件: {test_script}",
            "elapsed": 0,
            "cmd": cmd_str,
        }


def rollback_results(result_dirs: dict[str, Path], pre_existing: dict[str, bool]) -> None:
    """回滚：删除本次批量测试产生的所有结果目录。"""
    print(f"\n[回滚] 删除本次测试产生的所有结果目录...")
    for name, result_dir in result_dirs.items():
        if not result_dir.exists():
            continue
        if pre_existing.get(name, False):
            print(f"  跳过（测试前已存在）: {result_dir}")
            continue
        try:
            shutil.rmtree(result_dir)
            print(f"  已删除: {result_dir}")
        except Exception as e:
            print(f"  删除失败: {result_dir} ({e})")
    print("[回滚] 完成。")


def main():
    parser = argparse.ArgumentParser(description="统一测试运行脚本")
    parser.add_argument("--config", required=True, help="测试配置 JSON 文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅打印命令，不实际执行")
    parser.add_argument("--continue-on-failure", action="store_true",
                        help="即使某个测试失败也继续运行后续测试（默认：遇错即停并回滚）")
    parser.add_argument("--no-rollback", action="store_true",
                        help="失败时不删除已完成的测试结果（默认：回滚已完成的测试结果）")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[ERROR] 配置文件不存在: {args.config}")
        sys.exit(1)

    config = load_config(args.config)
    test_script = config["test_script"]

    if args.dry_run:
        print(f"[DRY-RUN] 将执行 {len(config['datasets'])} 个测试集：")
        for ds in config["datasets"]:
            cmd_args = build_args(config, ds)
            print(f"  python {test_script} " + " ".join(cmd_args))
        sys.exit(0)

    # 构建每个数据集对应的结果目录路径
    base = Path(config["result_base"])
    result_dirs: dict[str, Path] = {}
    for ds in config["datasets"]:
        result_dirs[ds["name"]] = base / ds["name"]

    # 记录测试前哪些结果目录已经存在
    pre_existing = {name: result_dir.exists() for name, result_dir in result_dirs.items()}

    stop_on_failure = not args.continue_on_failure
    do_rollback = not args.no_rollback

    print(f"测试脚本: {test_script}")
    print(f"测试集数: {len(config['datasets'])}")
    print(f"结果目录: {config['result_base']}/<name>")
    if stop_on_failure:
        print(f"模式: 遇错即停 + 失败回滚")
    print()

    results = []
    failed = False
    for i, ds in enumerate(config["datasets"], 1):
        name = ds["name"]
        print(f"[{i}/{len(config['datasets'])}] {name} ... ", end="", flush=True)
        cmd_args = build_args(config, ds)
        r = run_one(test_script, cmd_args)
        results.append({"name": name, **r})

        if r["success"]:
            print(f"OK ({r['elapsed']:.0f}s)")
        else:
            print(f"FAIL (rc={r['returncode']})")
            if r["stderr"]:
                lines = r["stderr"].strip().split("\n")
                for line in lines[-8:]:
                    print(f"  {line}")
            failed = True
            if stop_on_failure:
                print(f"\n[中断] {name} 测试失败，停止后续测试。")
                break

    # 失败时回滚
    if failed and do_rollback:
        rollback_results(result_dirs, pre_existing)

    # 汇总
    ok = sum(1 for r in results if r["success"])
    fail = len(results) - ok
    total_elapsed = sum(r["elapsed"] for r in results)
    print(f"\n{'='*50}")
    print(f"测试完成: {ok}/{len(results)} 成功", end="")
    if fail:
        print(f", {fail} 失败")
    else:
        print()
    print(f"总耗时: {total_elapsed:.0f}s")
    print(f"结果目录: {config['result_base']}/")

    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
