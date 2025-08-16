import asyncio
import json
import signal
import subprocess
import sys
import time

import tqdm
from colorama import Fore

from repfuzz.config import CHAT_LLM, tgts
from repfuzz.database.models import API
from repfuzz.database.sqlite_proxy import (
    get_all_apis,
    get_or_create_db,
    insert_into_api_call,
    query_api_call_by_full_name,
)
from repfuzz.llm import async_generate
from repfuzz.prompts.gen_prompts import get_gen_prompt
from repfuzz.tools.tools import clean_api_call

cnt_try = 0
cnt_success = 0


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


async def generate_api_call(api: API) -> None:
    global cnt_try, cnt_success
    cnt_try += 1
    api_name = api.full_name
    module_tokens = api_name.split(".")
    conn = get_or_create_db(module_tokens[0])

    print(f"{Fore.BLUE}Start generating call to {api_name}{Fore.RESET}")

    success = False
    for _ in range(20):
        prompt = get_gen_prompt(api)
        api_call = await async_generate(prompt)
        api_call = clean_api_call(api_call)
        if api_call.count(module_tokens[-1] + "(") < 1:
            continue
        try:
            compile(api_call, "", "exec")
        except Exception:
            print(f"{Fore.YELLOW}Compile Error when generating call to {api_name}{Fore.RESET}")
            continue

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
        except TimeoutError:
            print(f"{Fore.YELLOW}Timeout when generating call to {api_name}{Fore.RESET}")
            return
        except Exception:
            print(f"{Fore.YELLOW}Execution Error when generating call to {api_name}{Fore.RESET}")
            continue
        success = True
        print(f"{Fore.GREEN}Finished generating call to {api_name}{Fore.RESET}")
        break

    if success:
        cnt_success += 1
        insert_into_api_call(conn, api_name, api_call)
    else:
        print(f"{Fore.RED}Failed to generate call to {api_name}{Fore.RESET}")


async def generate_one_api_cal(queue: asyncio.Queue):
    while True:
        api = await queue.get()
        await generate_api_call(api)
        queue.task_done()


def handle_sigint(signum, frame):
    print("\nUser stop", flush=True)
    sys.exit(1)


async def report_process(queue: asyncio.Queue, total: int):
    pbar = tqdm.tqdm(
        total=total,
        bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
        file=sys.stdout,
        desc="Generating...",
    )
    while not queue.empty():
        pbar.n = total - queue.qsize()
        pbar.refresh()
        await asyncio.sleep(1)

    pbar.n = total
    pbar.refresh()
    pbar.close()


async def async_main():
    queue = asyncio.Queue()
    t0 = time.time()
    for trg_name in tgts:
        conn = get_or_create_db(trg_name)
        for api in get_all_apis(conn):
            # 没有参数的api没有测试价值
            if (api.num_normal_arg + api.num_kwonly_arg) == 0:
                continue
            if len(query_api_call_by_full_name(conn, api.full_name)) > 0:
                continue
            queue.put_nowait(api)
    qs = queue.qsize()

    tasks: list[asyncio.Task] = []
    tasks.append(asyncio.create_task(report_process(queue, qs)))
    for _ in range(CHAT_LLM.max_concurrency):
        tasks.append(asyncio.create_task(generate_one_api_cal(queue)))

    await queue.join()

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    dt = time.time() - t0
    print(f"It takes {dt:.2f} seconds to try generating {qs} api calls")


def main():
    signal.signal(signal.SIGINT, handle_sigint)
    asyncio.run(async_main())
    print(
        f"Totally try generating {cnt_try} api calls, {cnt_success} succeded({cnt_success/cnt_try:.2%})"
    )


if __name__ == "__main__":
    main()
