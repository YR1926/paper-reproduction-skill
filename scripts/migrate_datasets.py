#!/usr/bin/env python3
"""
数据集迁移脚本 —— 将源路径的数据集复制/链接到目标路径。

用法:
  # 命令行传入多对路径（--src 和 --dst 按顺序一一对应）
  python migrate_datasets.py \
      --src datasets/train/input --dst src/data/train/images \
      --src datasets/train/target --dst src/data/train/labels \
      --src datasets/val/input --dst src/data/val/images

  # 通过 JSON 配置文件传入
  python migrate_datasets.py --config migrate_config.json

  # 可选参数
  --method auto   # auto(默认) / link / copy
                    auto: 优先符号链接，失败则复制
                    link: 仅符号链接，失败报错
                    copy: 仅复制
  --mode  dirs    # dirs(默认) / files / mixed
  --dry-run       # 仅打印操作，不实际执行
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def read_config(config_path: str) -> list[dict]:
    """从 JSON 配置文件读取映射列表。"""
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        mappings = data.get("mappings", [])
    elif isinstance(data, list):
        mappings = data
    else:
        raise ValueError(f"配置文件格式错误，期望 list 或 dict，实际: {type(data)}")
    if not mappings:
        raise ValueError("配置文件中没有映射条目")
    for m in mappings:
        m.setdefault("method", "auto")
        m.setdefault("mode", "dirs")
    return mappings


def try_symlink(src: str, dst: str) -> bool:
    """尝试创建符号链接。目录用 junction(Windows)，文件用 symlink。"""
    src_path = Path(src).resolve()
    dst_path = Path(dst)
    try:
        if dst_path.exists() or dst_path.is_symlink():
            dst_path.unlink()
        if sys.platform == "win32" and src_path.is_dir():
            os.system(f'mklink /J "{dst_path}" "{src_path}"')
            return dst_path.exists()
        else:
            dst_path.symlink_to(src_path, target_is_directory=src_path.is_dir())
            return True
    except Exception:
        return False


def try_copy(src: str, dst: str) -> bool:
    """复制源到目标（目录递归复制，文件直接复制）。"""
    src_path = Path(src)
    dst_path = Path(dst)
    try:
        if src_path.is_dir():
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        return True
    except Exception:
        return False


def migrate_one(src: str, dst: str, method: str = "auto") -> dict:
    """迁移单对路径，返回结果字典。"""
    result = {"src": src, "dst": dst, "method": method, "success": False, "action": None, "error": None}
    src_path = Path(src)
    if not src_path.exists():
        result["error"] = f"源路径不存在: {src}"
        return result

    dst_parent = Path(dst).parent
    dst_parent.mkdir(parents=True, exist_ok=True)

    if method in ("auto", "link"):
        if try_symlink(src, dst):
            result["success"] = True
            result["action"] = "symlink"
            return result
        elif method == "link":
            result["error"] = "符号链接失败"
            return result

    if method in ("auto", "copy"):
        if try_copy(src, dst):
            result["success"] = True
            result["action"] = "copy"
            return result
        else:
            result["error"] = "复制失败"
            return result

    result["error"] = f"未知 method: {method}"
    return result


def count_items(path: str) -> int:
    """统计目录中文件/子目录数量。"""
    p = Path(path)
    if not p.exists():
        return 0
    if p.is_dir():
        return sum(1 for _ in p.iterdir())
    return 1


def main():
    parser = argparse.ArgumentParser(description="数据集迁移脚本")
    parser.add_argument("--src", action="append", default=[], help="源路径（可多次指定，与 --dst 一一对应）")
    parser.add_argument("--dst", action="append", default=[], help="目标路径（可多次指定，与 --src 一一对应）")
    parser.add_argument("--config", help="JSON 配置文件路径（含 mappings 数组）")
    parser.add_argument("--method", choices=["auto", "link", "copy"], default="auto",
                        help="迁移方式: auto=先链接后复制, link=仅链接, copy=仅复制 (默认: auto)")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不实际执行")

    args = parser.parse_args()

    mappings = []

    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"[ERROR] 配置文件不存在: {args.config}")
            sys.exit(1)
        mappings = read_config(args.config)
    elif args.src or args.dst:
        if len(args.src) != len(args.dst):
            print(f"[ERROR] --src ({len(args.src)}个) 和 --dst ({len(args.dst)}个) 数量不一致")
            sys.exit(1)
        if not args.src:
            print("[ERROR] 未提供任何映射。请使用 --src/--dst 或 --config 指定。")
            sys.exit(1)
        for s, d in zip(args.src, args.dst):
            mappings.append({"src": s, "dst": d, "method": args.method, "mode": "dirs"})
    else:
        print("[ERROR] 未提供任何映射。请使用 --src/--dst 或 --config 指定。")
        sys.exit(1)

    if args.dry_run:
        print("[DRY-RUN] 将执行以下操作：")
        for m in mappings:
            src_count = count_items(m["src"])
            print(f"  {m['src']} ({src_count} 项) → {m['dst']}  (method={m.get('method', args.method)})")
        sys.exit(0)

    # 执行迁移
    results = []
    errors = 0
    for m in mappings:
        method = m.get("method", args.method)
        r = migrate_one(m["src"], m["dst"], method)
        results.append(r)
        if r["success"]:
            count = count_items(r["dst"])
            print(f"[OK] {r['src']} → {r['dst']}  ({r['action']}, {count} 项)")
        else:
            errors += 1
            print(f"[FAIL] {r['src']} → {r['dst']}: {r['error']}")

    # 汇总
    total = len(results)
    ok = total - errors
    print(f"\n{'='*50}")
    print(f"迁移完成: {ok}/{total} 成功", end="")
    if errors:
        print(f", {errors} 失败")
    else:
        print()

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
