import os
import sqlite3
from pathlib import Path

from repfuzz.config import DATA_DIR


def main():
    library_name = "fuzz_record"
    column_name = "py_cov"
    for f1 in os.listdir(DATA_DIR):
        f2 = DATA_DIR.joinpath(f1)
        if f2.is_dir():
            for f3 in os.listdir(DATA_DIR.joinpath(f1)):
                f4 = f2.joinpath(f3)
                if f4.suffix == ".db":
                    conn = sqlite3.connect(f4)
                    cur = conn.cursor()
                    cur.execute(
                        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{library_name}'"
                    )
                    if cur.fetchone() is None:
                        continue
                    cur.execute(
                        f"SELECT name FROM pragma_table_info('{library_name}') WHERE name='{column_name}'"
                    )
                    if cur.fetchone() is None:
                        cur.execute(
                            f"ALTER TABLE {library_name} ADD COLUMN {column_name} INTEGER DEFAULT 0"
                        )
                    conn.commit()
                    conn.close()


if __name__ == "__main__":
    main()
