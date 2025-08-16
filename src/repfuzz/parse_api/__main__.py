import asyncio
import importlib
import inspect
import signal
import sys
import time
from types import BuiltinFunctionType, FunctionType, ModuleType

import tqdm
from colorama import Fore

from repfuzz.config import CHAT_LLM, tgts
from repfuzz.database.sqlite_proxy import (
    get_or_create_db,
    query_api_by_full_name,
    set_public_apis,
)
from repfuzz.parse_api.apiparser import parse_api


def traverse_all_apis_in_module(
    mod: ModuleType, top_mod_name: str, mod_has_been_seen: set, queue: set
):
    if id(mod) in mod_has_been_seen:
        return
    mod_has_been_seen.add(id(mod))
    names = dir(mod)
    for name in names:
        if name.startswith("_"):  # care only public modules and functions
            continue
        try:
            obj = getattr(mod, name)
            if isinstance(obj, (FunctionType, BuiltinFunctionType)):
                if obj.__module__ is None:
                    continue
                if any(list(filter(lambda x: x.startswith("_"), obj.__module__.split(".")))):  # type: ignore
                    continue
                if obj.__module__.startswith(top_mod_name):
                    queue.add(obj)
            elif isinstance(obj, ModuleType):
                try:
                    obj_full_name = obj.__name__
                except Exception:
                    clone_obj = mod.__new__(type(obj))
                    clone_obj.__dict__.update(obj.__dict__)
                    obj_full_name = clone_obj.__name__
                if obj_full_name.startswith(top_mod_name):
                    traverse_all_apis_in_module(obj, top_mod_name, mod_has_been_seen.copy(), queue)
        except AttributeError:
            continue


def avoid_repeated_parsing(queue: list, conn):
    repeated_apis = []
    for api in queue:
        full_name = api.__module__ + "." + api.__name__  # full name of the api
        if query_api_by_full_name(conn, full_name):
            repeated_apis.append(api)
    for api in repeated_apis:
        queue.remove(api)


async def parse_one_api(queue: asyncio.Queue):
    while True:
        api = await queue.get()
        try:
            await parse_api(api)
        except Exception as e:
            print(f"{Fore.RED}Error parsing {api.__name__}{Fore.RESET}:{e}")
        queue.task_done()


async def report_process(queue: asyncio.Queue, total: int):
    pbar = tqdm.tqdm(
        total=total,
        bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
        file=sys.stdout,
        desc="Parsing...",
    )
    while not queue.empty():
        pbar.n = total - queue.qsize()
        pbar.refresh()
        await asyncio.sleep(1)

    pbar.n = total
    pbar.refresh()
    pbar.close()


def handle_sigint(signum, frame):
    print("\nUser stop", flush=True)
    sys.exit(1)


async def async_main():
    # sys.stderr = None
    api_list = []
    for trg_name in tgts:
        t_list = set()
        conn = get_or_create_db(trg_name)
        target = importlib.import_module(trg_name)
        traverse_all_apis_in_module(target, trg_name, set(), t_list)
        api_names = [api.__module__ + "." + api.__name__ for api in t_list]
        set_public_apis(conn, api_names)
        print(f"{trg_name} contains {len(t_list)} public functions")
        avoid_repeated_parsing(t_list, conn)
        api_list.extend(t_list)
    print(f"Traversing done, there are {len(api_list)} apis to parse")

    queue = asyncio.Queue()
    for api in api_list:
        queue.put_nowait(api)

    tasks: list[asyncio.Task] = []
    tasks.append(asyncio.create_task(report_process(queue, len(api_list))))
    for _ in range(CHAT_LLM.max_concurrency):
        tasks.append(asyncio.create_task(parse_one_api(queue)))

    await queue.join()

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    print(f"\n{Fore.GREEN}All things done!{Fore.RESET}")


def main():
    signal.signal(signal.SIGINT, handle_sigint)
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
