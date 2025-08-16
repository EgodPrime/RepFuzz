import os
import subprocess

from repfuzz.config import FUZZ


def clean_fake_crash():
    crash_dir = FUZZ.crash_dir
    for file in os.listdir(crash_dir):
        if not file[0].isdigit():
            continue
        if not file.endswith(".py"):
            continue
        filepath = crash_dir.joinpath(file)
        print(f"Testing {filepath}...", end="", flush=True)
        cmd = ["python", str(filepath)]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
        except subprocess.TimeoutExpired:
            print("timeout", flush=True)
            # 将文件重命名为timeout_n.py
            filepath.rename(crash_dir.joinpath(f"timeout_{file}"))
            continue
        if res.returncode == 0:
            filepath.unlink()
            print("removed", flush=True)
            continue
        else:
            stderr = res.stderr.decode()
            if "Error: " in stderr:
                filepath.unlink()
                print("removed", flush=True)
                continue
            print("true", flush=True)
            filepath.rename(crash_dir.joinpath(f"crash_{file}"))


if __name__ == "__main__":
    clean_fake_crash()
