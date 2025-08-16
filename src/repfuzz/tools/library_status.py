import os
import sqlite3

import fire
import pandas

from repfuzz.config import DATA_DIR


def count_database(db_name: str):
    df = pandas.DataFrame(
        columns=[
            "library_name",
            "#Public",
            "#Parsed",
            "#Gen",
            "#Fuzzed",
            "#Exec",
            "#TimeCost",
            "Exec.Speed",
        ]
    )
    db_path = DATA_DIR.joinpath(db_name)
    for file in os.listdir(db_path):
        if file.endswith(".db"):
            conn = sqlite3.connect(db_path.joinpath(file))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM public_api")
            public_api_cnt = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM api")
            api_cnt = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM api_call")
            api_call_cnt = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM fuzzed_api")
            fuzzed_api_cnt = cursor.fetchone()[0]
            try:
                cursor.execute(
                    "SELECT exec_num, time_cost FROM fuzz_record WHERE exec_num != 0 AND time_cost != 0 ORDER BY date DESC LIMIT 1"
                )
                result = cursor.fetchone()
            except Exception as e:
                result = None
            if result:
                exec_num, time_cost = result
                exec_speed = exec_num / time_cost
            else:
                exec_num, time_cost = 0, 0
                exec_speed = 0

            # add to df
            df.loc[len(df)] = [
                file.replace(".db", ""),
                public_api_cnt,
                api_cnt,
                api_call_cnt,
                fuzzed_api_cnt,
                exec_num,
                time_cost,
                exec_speed,
            ]
            conn.close()
    # sort df by public_api
    df.sort_values(by="#Public", ascending=True, inplace=True)
    # print df
    print(df)


def main():
    fire.Fire(count_database)


if __name__ == "__main__":
    main()
