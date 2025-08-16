#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

def run_fuzz_jobs(json_file: str):
    """读取 JSON 配置文件并执行每个任务"""
    try:
        with open(json_file, 'r') as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件 {json_file} 不存在", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: {json_file} 不是有效的 JSON 文件", file=sys.stderr)
        sys.exit(1)

    for i, job in enumerate(jobs, 1):
        try:
            # 提取任务参数
            config = job['config']
            folder = job['folder']
            batch_size = job.get('batch_size', 30)  # 提供默认值
            model_name = job['model_name']
            target = job['target']

            print(f"\n🚀 开始任务 {i}:")
            print(f"📄 配置: {config}")
            print(f"📁 输出目录: {folder}")
            print(f"🔢 批量大小: {batch_size}")
            print(f"🤖 模型: {model_name}")
            print(f"🎯 目标: {target}")

            # 创建输出目录（如果不存在）
            Path(folder).mkdir(parents=True, exist_ok=True)

            # 运行 Fuzz 任务
            cmd = [
                "python", "Fuzz4All/fuzz.py",
                "--config", config,
                "main_with_config",
                "--folder", folder,
                "--batch_size", str(batch_size),
                "--model_name", model_name,
                "--target", target
            ]

            result = subprocess.run(
                cmd,
                check=False,  # 不自动抛出异常
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ 任务失败 (退出码: {result.returncode}):")
                print(f"错误输出:\n{result.stderr}")
            else:
                print("✅ 任务完成!")
                print(f"输出:\n{result.stdout[:200]}...")  # 只打印前200字符

            print("-" * 40)

        except Exception as e:
            print(f"❌ 未知错误: {type(e).__name__}: {e}", file=sys.stderr)
            continue

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python f4a.py <config.json>", file=sys.stderr)
        sys.exit(1)
    
    run_fuzz_jobs(sys.argv[1])