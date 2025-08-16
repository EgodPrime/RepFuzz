import asyncio
import importlib
import io
import os
import signal
import sys
import time
from multiprocessing import Pipe, Process, Queue
import tqdm
from colorama import Fore

from repfuzz.config import CHAT_LLM, LIBRARY_DATA_DIR, skip, tgts
from repfuzz.database.sqlite_proxy import (
    _create_table,
    add_fuzz_record,
    get_all_api_cals,
    get_all_apis,
    get_or_create_db,
    insert_into_api_call,
    query_api_call_by_full_name,
)
from repfuzz.gen_api_call import clean_api_call, handle_sigint
from repfuzz.prompts.gen_prompts import get_gen_prompt


def time_limit_exec(code, seconds: int = 1):
    def raise_timeout_error(signum, frame):
        raise TimeoutError

    try:
        signal.signal(signal.SIGALRM, raise_timeout_error)
        signal.alarm(seconds)
        exec(code)
    except Exception as e:
        raise e
    finally:
        signal.alarm(0)


def eval_func(library: str, data: Queue, conn):
    print(f"eval_func for {library} start", file=sys.__stdout__, flush=True)
    while not data.empty():
        full_name, api_call = data.get()
        try:
            time_limit_exec(api_call)
        except Exception:
            pass
        conn.send(0)
    conn.send(1)


def main():
    batch_size = 100

    for lib in tgts:
        if lib in skip:
            continue
        conn = get_or_create_db(lib)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM api_call")
        total = cur.fetchone()[0]
        print(f"{lib} has {total} generated api calls", file=sys.__stdout__)
        pbar = tqdm.tqdm(
            total=total,
            bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
            file=sys.__stderr__,
            desc=lib,
            leave=True,
        )
        t0 = time.time()
        cnt = 0
        for offset in range(0, total, batch_size):
            cur.execute(
                "SELECT full_name, api_call FROM api_call ORDER BY full_name LIMIT ? OFFSET ?",
                (
                    batch_size,
                    offset,
                ),
            )
            data = cur.fetchall()
            data_queue = Queue()
            for x in data:
                data_queue.put(x)
            r_size = data_queue.qsize()
            cnt += data_queue.qsize()
            # print(f"handle {data_queue.qsize()}")
            fail = False
            while not data_queue.empty():
                p_conn, c_conn = Pipe()
                p = Process(
                    target=eval_func,
                    args=(
                        lib,
                        data_queue,
                        c_conn,
                    ),
                )
                p.start()
                while True:
                    if p_conn.poll(1):
                        r = p_conn.recv()
                        if r:
                            break
                    else:
                        print("Child timeout, killing", file=sys.__stdout__)
                        os.kill(p.pid, 9)
                        fail = True  # Abort the current batch_size api calls
                        break
                p.join()
                p.close()
                if fail:
                    break
            pbar.update(r_size)
        dt = time.time() - t0
        add_fuzz_record(conn, int(time.time()), cnt, dt, 0)
        pbar.close()


if __name__ == "__main__":
    fake_stdout = io.StringIO()
    fake_stderr = io.StringIO()
    sys.stdout = fake_stdout
    sys.stderr = fake_stderr
    main()
