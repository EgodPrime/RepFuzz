import sqlite3
from sqlite3 import Connection, Cursor

from repfuzz.config import FUZZFILE_PATH, LIBRARY_DATA_DIR
from repfuzz.database.models import API, adapt_API, convert_API


def get_or_create_db(db_name: str) -> Connection:
    """
    Get or create a SQLite database.

    Args:
        db_name (str): The name of the database.

    Returns:
        Connection: The SQLite database connection.
    """
    LIBRARY_DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = LIBRARY_DATA_DIR.joinpath(db_name + ".db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    _create_table(cur, "public_api", ["full_name"])
    _create_table(
        cur,
        "api",
        [
            "full_name",
            "type",
            "source",
            "doc",
            "num_normal_arg",
            "num_kwonly_arg",
            "normal_arg_list",
            "kwonly_arg_list",
        ],
    )
    _create_table(cur, "api_call", ["full_name", "api_call"])
    _create_table(cur, "fuzzed_api", ["full_name"])
    _create_table(cur, "fuzz_record", ["date", "exec_num", "time_cost", "py_cov"])
    return conn


def _create_table(cur: Cursor, table_name: str, columns: list[str]) -> None:
    columns_str = ", ".join(columns)
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
    cur.execute(query)


def set_public_apis(conn: Connection, public_apis: list[str]) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM public_api")
    for api in public_apis:
        cur.execute("INSERT INTO public_api VALUES (?)", (api,))
    conn.commit()


def insert_into_api(conn: Connection, api: API):
    data = adapt_API(api)
    cur = conn.cursor()
    cur.execute("INSERT INTO api VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()


def insert_into_fuzzed_api(conn: Connection, full_name: str) -> None:
    cur = conn.cursor()
    cur.execute("INSERT INTO fuzzed_api VALUES (?)", (full_name,))
    conn.commit()


def get_all_apis(conn: Connection) -> list[API]:
    """
    Get all APIs from the SQLite database.

    Args:
        conn (Connection): The SQLite database connection.

    Returns:
        list[API]: A list of all APIs.
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM api")
    rows = cur.fetchall()
    apis = [convert_API(row) for row in rows]
    return apis


def query_api_by_full_name(conn: Connection, full_name: str) -> API | None:
    """
    Query an API by its full name from the SQLite database.

    Args:
        conn (Connection): The SQLite database connection.
        full_name (str): The full name of the API.

    Returns:
        API: The API object.
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM api WHERE full_name=?", (full_name,))
    row = cur.fetchone()
    if row is None:
        return None
    return convert_API(row)


def query_api_call_by_full_name(conn: Connection, full_name: str) -> list[str]:
    """
    Query an API call by its full name from the SQLite database.
    Args:
        conn (Connection): The SQLite database connection.
        full_name (str): The full name of the API.

    Returns:
        list[str]: A list of API calls.
    """
    cur = conn.cursor()
    cur.execute("SELECT api_call FROM api_call WHERE full_name=?", (full_name,))
    res = cur.fetchall()
    res = [row[0] for row in res]
    return res


def get_all_api_cals(conn: Connection) -> list[str]:
    """
    Get all API calls from the SQLite database.
    Args:
        conn (Connection): The SQLite database connection.

    Returns:
        list[str]: A list of all API calls.
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM api_call")
    rows = cur.fetchall()
    return rows


def insert_into_api_call(conn: Connection, full_name: str, api_call: str):
    cur = conn.cursor()
    cur.execute("INSERT INTO api_call VALUES (?, ?)", (full_name, api_call))
    conn.commit()


def init_fuzz():
    if not FUZZFILE_PATH.exists():
        FUZZFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(FUZZFILE_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS fuzz(status)")
    cur.execute("DELETE FROM fuzz")
    cur.execute("INSERT INTO fuzz VALUES (?)", (0,))
    conn.commit()


def start_fuzz():
    conn = sqlite3.connect(FUZZFILE_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE fuzz SET status = 1 WHERE status = 0")
    conn.commit()
    conn.close()


def can_fuzz(full_name: str) -> bool:
    conn = sqlite3.connect(FUZZFILE_PATH)
    cur = conn.cursor()
    res = cur.execute("SELECT status FROM fuzz")
    if res.fetchone()[0] == 0:
        conn.close()
        return False
    else:
        res = cur.execute("SELECT full_name FROM fuzzed WHERE full_name = ?", (full_name,))
        if res.fetchone() is None:
            conn.close()
            return True
        else:
            conn.close()
            return False


def get_fuzzed(conn: Connection):
    cur = conn.cursor()
    cur.execute("SELECT full_name FROM fuzzed_api")
    rows = cur.fetchall()
    return rows


def add_fuzz_record(conn: Connection, date: int, exec_num: int, time_cost: int, py_cov: int = 0):
    cur = conn.cursor()
    cur.execute("INSERT INTO fuzz_record VALUES (?, ?, ?, ?)", (date, exec_num, time_cost, py_cov))
    conn.commit()
