import sqlite3
from collections import defaultdict

from repfuzz.config import LIBRARY_DATA_DIR, tgts


def clean_duplicated(lib_name: str, table: str) -> None:
    db_path = LIBRARY_DATA_DIR.joinpath(f"{lib_name}.db")
    if not db_path.exists():
        print(f"Database file not found: {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"SELECT rowid, full_name FROM {table}")
    data = cur.fetchall()
    counter: dict[str, int] = defaultdict(int)
    m = defaultdict(list)
    for row in data:
        counter[row[1]] += 1
        m[row[1]].append(row[0])
    for key, value in counter.items():
        if value > 1:
            print(f"{key} has {value} records")
        for rowid in m[key][1:]:
            cur.execute(f"DELETE FROM {table} WHERE rowid = {rowid}")
            print(f"Deleted rowid: {rowid}")
    conn.commit()
    conn.close()


def main():
    for lib_name in tgts:
        clean_duplicated(lib_name, "public_api")
        clean_duplicated(lib_name, "api")
        clean_duplicated(lib_name, "api_call")
        clean_duplicated(lib_name, "fuzzed_api")


if __name__ == "__main__":
    main()
