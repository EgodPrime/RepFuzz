import os
import sqlite3

from repfuzz.config import LIBRARY_DATA_DIR


def remove_all_api_call():
    for file in os.listdir(LIBRARY_DATA_DIR):
        if not file.endswith(".db"):
            continue
        filepath = LIBRARY_DATA_DIR.joinpath(file)
        conn = sqlite3.connect(str(filepath))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM api_call")
        conn.commit()
        conn.close()


if __name__ == "__main__":
    remove_all_api_call()
