import os
import sqlite3
import subprocess
import sys

import fire
import tqdm
from colorama import Fore

from repfuzz.config import DATA_DIR


def clean_fake_api_call(library_name: str):
    library_dir = DATA_DIR.joinpath(library_name)
    for file in os.listdir(library_dir):
        filepath = library_dir.joinpath(file)
        conn = sqlite3.connect(str(filepath))
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, full_name, api_call FROM api_call")
        rows = cursor.fetchall()
        pbar = tqdm.tqdm(
            total=len(rows),
            bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
            file=sys.stdout,
            desc=f"Checking {filepath}",
        )
        del_cnt = 0
        for rowid, full_name, api_call in rows:
            with open("/tmp/gen.code", "w") as f:
                f.write(api_call)
            try:
                subprocess.run(
                    ["python", "/tmp/gen.code"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                    check=True,
                )
            except subprocess.TimeoutExpired:
                cursor.execute("DELETE FROM api_call WHERE rowid = ?", (rowid,))
                conn.commit()
                del_cnt += 1
            except subprocess.CalledProcessError as e:
                cursor.execute("DELETE FROM api_call WHERE rowid = ?", (rowid,))
                conn.commit()
                del_cnt += 1
            pbar.set_description(f"Checking {filepath} (Deleted {del_cnt} calls)")
            pbar.update(1)
        conn.close()


if __name__ == "__main__":
    fire.Fire(clean_fake_api_call)
