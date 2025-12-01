import os
import random
import sys
from multiprocessing.connection import Connection
from typing import Callable

import tqdm
from loguru import logger
import dcov
from colorama import Fore

from repfuzz.config import FUZZ
from repfuzz.database.sqlite_proxy import get_or_create_db, insert_into_fuzzed_api
from repfuzz.fuzz.execution_watcher import watch
from repfuzz.mutator import mutate_param_list
from repfuzz.tools.custom_obj_str import objjson

current_api = ""
c_conn: Connection = None
black_set = set()


def handle_error(error: Exception):
    """
    Currently only crash is watched...and it does not need to be handled.
    """
    # traceback.print_exc(file=sys.stdout)
    # logger.info("",flush=True)
    pass


@watch(error_handler=handle_error)
def execute_once(api: Callable, *args, **kwargs):
    """
    Execute the API with the given arguments.

    This function watches for errors, such as crashes, and handles them according
    to the `handle_error` function.

    Args:
        api: The API to be executed.
        *args: Variable number of positional arguments to be passed to the API.
        **kwargs: Variable number of keyword arguments to be passed to the API.
    """
    api(*args, **kwargs)


def convert_to_param_list(*args, **kwargs) -> list:
    param_list = list(args) + list(kwargs.values())  # convert args and kwargs to list.
    return param_list


def reconvert_param_list(param_list, *args, **kwargs) -> tuple[tuple, dict]:
    args = tuple(param_list[: len(args)])
    kwargs = {k: v for k, v in zip(kwargs.keys(), param_list[len(args) :])}
    return args, kwargs


def fuzz_api(api: Callable, *args, **kwargs) -> None:
    """
    Fuzz a given api with random mutants and argument permutations.

    This function executes the provided function with a set of random inputs,
    incrementally increasing the mutation rate to improve code coverage.
    If the function has no arguments, it executes only once.
    If the function has been previously fuzzed and timed out, it is skipped.

    Args:
        api: The function to be fuzzed.
        *args: Variable number of positional arguments to be passed to the function.
        **kwargs: Variable number of keyword arguments to be passed to the function.

    Returns:
        None
    """
    full_name = f"{api.__module__}.{api.__name__}"
    top_mod_name = api.__module__.split(".")[0]
    conn = get_or_create_db(top_mod_name)
    insert_into_fuzzed_api(conn, full_name)

    if full_name in black_set:
        logger.info(
            f"Skip {full_name} as it has always been timed out."
        )
        return

    param_list = convert_to_param_list(*args, **kwargs)  # convert args and kwargs to list.
    if len(param_list) == 0:
        logger.info(
            f"{full_name} has no arguments, execute only once."
        )
        c_conn.recv()
        execute_once(api, *args, **kwargs)
        c_conn.send(0)
        return
    
    logger.info(f"Start fuzz {full_name}")

    current_api.value = full_name
    # pbar = tqdm.tqdm(
    #     total=FUZZ.iters_per_api,
    #     bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
    #     file=sys.__stdout__,
    #     desc=f"Fuzz {full_name}: ",
    # )

    """
    FUZZ.iters_per_api: The number of mutations for each API.
    FUZZ.iters_per_seed: The number of mutations for each seed.
    FUZZ.iters_per_api // FUZZ.iters_per_seed: The number of seeds for each API.
    Seed is randomly selected from the population `pop`.
    """
    for i in range(FUZZ.iters_per_api // FUZZ.iters_per_seed):
        for j in range(FUZZ.iters_per_seed):  # for each seed, generate multiple mutations.
            mt_param_list = mutate_param_list(param_list)
            args, kwargs = reconvert_param_list(
                mt_param_list, *args, **kwargs
            )  # convert back to args and kwargs.
            with open("/tmp/fuzz.py", "w") as f:
                f.write(f"import {api.__module__}\n")
                f.write(f"args={objjson(args)}\n")
                f.write(f"kwargs={objjson(kwargs)}\n")
                f.write(f"{api.__module__}.{api.__name__}(*args, **kwargs)\n")
            p0 = dcov.count_bitmap_py()
            c_conn.recv()  # wait for the signal from the parent
            execute_once(api, *args, **kwargs)
            c_conn.send(0)  # signal to the parent that the execution is done.
            p1 = dcov.count_bitmap_py()
            if p1 > p0:
                logger.info(f"Coverage increased {p1-p0}, now: {p1}")
    #     pbar.update(FUZZ.iters_per_seed)
    # pbar.close()