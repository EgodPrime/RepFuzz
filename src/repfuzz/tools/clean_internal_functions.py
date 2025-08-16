import os
import sqlite3

from repfuzz.config import LIBRARY_DATA_DIR


def clean_internal_apis():
    for file in os.listdir(LIBRARY_DATA_DIR):
        if not file.endswith(".db"):
            continue
        filepath = LIBRARY_DATA_DIR.joinpath(file)
        print(f"Checking {filepath}...", end="", flush=True)
        conn = sqlite3.connect(str(filepath))
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM api")
        rows = cursor.fetchall()
        for row in rows:
            if any(list(filter(lambda x: x.startswith("_"), row[0].split(".")))):
                print(f"Removing {row[0]}...", end="", flush=True)
                cursor.execute(f"DELETE FROM api WHERE full_name='{row[0]}'")
                conn.commit()
                print("removed", flush=True)
        cursor.execute("SELECT full_name FROM api_call")
        rows = cursor.fetchall()
        for row in rows:
            if any(list(filter(lambda x: x.startswith("_"), row[0].split(".")))):
                print(f"Removing {row[0]}...", end="", flush=True)
                cursor.execute(f"DELETE FROM api_call WHERE full_name='{row[0]}'")
                conn.commit()
                print("removed", flush=True)
        cursor.execute("SELECT full_name FROM fuzzed_api")
        rows = cursor.fetchall()
        for row in rows:
            if any(list(filter(lambda x: x.startswith("_"), row[0].split(".")))):
                print(f"Removing {row[0]}...", end="", flush=True)
                cursor.execute(f"DELETE FROM fuzzed_api WHERE full_name='{row[0]}'")
                conn.commit()
                print("removed", flush=True)
        conn.close()


if __name__ == "__main__":
    clean_internal_apis()
