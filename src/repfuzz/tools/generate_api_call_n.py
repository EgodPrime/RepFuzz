import asyncio
import signal
import time

from colorama import Fore

from repfuzz.config import CHAT_LLM, tgts
from repfuzz.database.models import API
from repfuzz.database.sqlite_proxy import (
    get_all_apis,
    get_or_create_db,
    insert_into_api_call,
    query_api_call_by_full_name,
)
from repfuzz.gen_api_call import clean_api_call, handle_sigint
from repfuzz.llm import async_generate
from repfuzz.prompts.gen_prompts import get_gen_prompt


async def generate_api_call(queue: asyncio.Queue, n: int = 1000):
    while True:
        api = await queue.get()
        for _ in range(n):
            api_name = api.full_name
            module_tokens = api_name.split(".")
            conn = get_or_create_db(module_tokens[0])

            prompt = get_gen_prompt(api)

            print(f"{Fore.BLUE}Start generating call to {api_name}{Fore.RESET}")
            api_call = await async_generate(prompt)
            api_call = clean_api_call(api_call)
            insert_into_api_call(conn, api_name, api_call)
            print(f"{Fore.GREEN}Finished generating call to {api_name}{Fore.RESET}")
        queue.task_done()


async def async_main():
    t0 = time.time()
    queue = asyncio.Queue()
    for trg_name in tgts:
        conn = get_or_create_db(trg_name)
        for api in get_all_apis(conn):
            queue.put_nowait(api)

    tasks: list[asyncio.Task] = []
    for _ in range(CHAT_LLM.max_concurrency):
        tasks.append(asyncio.create_task(generate_api_call(queue)))

    await queue.join()

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    dt = time.time() - t0
    print(f"It takes {dt:.2f} seconds to try generating api calls")


def main():
    signal.signal(signal.SIGINT, handle_sigint)
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
