"""Main script to run the fuzzing process."""

import os
import time
import uuid
import click
import dcov
import subprocess
import signal
import traceback
from rich.traceback import install

install()

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from Fuzz4All.make_target import make_target_with_config
from Fuzz4All.target.target import Target
from Fuzz4All.util.util import load_config_file
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager


@contextmanager
def timeout(time):
    # 定义超时处理函数
    def raise_timeout(signum, frame):
        raise TimeoutError(f"Execution timed out after {time} seconds")
    
    # 设置信号处理器
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(time)  # 触发 time 秒后的警报
    try:
        yield
    finally:
        signal.alarm(0)  # 取消警报


def write_to_file(fo, file_name):
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(fo)
    except:
        pass


def fuzz(
    target: Target,
    number_of_iterations: int,
    total_time: int,
    output_folder: str,
    resume: bool,
    otf: bool,
    api_name: str,
):
    target.initialize(api_name, output_folder)
    count = 0
    start_time = time.time()

    if resume:
        n_existing = [int(f.split(".")[0]) for f in os.listdir(output_folder) if f.endswith(".py")]
        if n_existing:
            count = max(n_existing) + 1

    while (
        count < number_of_iterations
        and time.time() - start_time < total_time * 3600
    ):
        fos = target.generate()
        if not fos:
            target.initialize()
            continue
        prev = []
        for index, fo in enumerate(fos):
            file_name = os.path.join(output_folder, f"{uuid.uuid4().hex[:8]}.py")
            write_to_file(fo, file_name)
            count += 1
            # validation on the fly
            if otf:
                f_result, message = target.validate_individual(file_name)
                target.parse_validation_message(f_result, message, file_name)
                prev.append((f_result, fo))
        target.update(prev=prev)


# evaluate against the oracle to discover any potential bugs
# used after the generation
def evaluate_all(target: Target):
    target.validate_all()


@click.group()
@click.option(
    "config_file",
    "--config",
    type=str,
    default=None,
    help="Path to the configuration file.",
)
@click.pass_context
def cli(ctx, config_file):
    """Run the main using a configuration file."""
    if config_file is not None:
        config_dict = load_config_file(config_file)
        ctx.ensure_object(dict)
        ctx.obj["CONFIG_DICT"] = config_dict


@cli.command("main_with_config")
@click.pass_context
@click.option(
    "folder",
    "--folder",
    type=str,
    default="Results/test",
    help="folder to store results",
)
@click.option(
    "cpu",
    "--cpu",
    is_flag=True,
    help="to use cpu",  # this is for GPU resource low situations where only cpu is available
)
@click.option(
    "batch_size",
    "--batch_size",
    type=int,
    default=30,
    help="batch size for the model",
)
@click.option(
    "model_name",
    "--model_name",
    type=str,
    default="bigcode/starcoderbase",
    help="model to use",
)
@click.option(
    "target",
    "--target",
    type=str,
    default="",
    help="specific target to run",
)
def main_with_config(ctx, folder, cpu, batch_size, target, model_name):
    """Run the main using a configuration file."""
    config_dict = ctx.obj["CONFIG_DICT"]
    fuzzing = config_dict["fuzzing"]
    config_dict["fuzzing"]["output_folder"] = folder
    if cpu:
        config_dict["llm"]["device"] = "cpu"
    if batch_size:
        config_dict["llm"]["batch_size"] = batch_size
    if model_name != "":
        config_dict["llm"]["model_name"] = model_name
    if target != "":
        config_dict["fuzzing"]["target_name"] = target
    print(config_dict)

    target = make_target_with_config(config_dict)
    if not fuzzing["evaluate"]:
        # assert (
        #     not os.path.exists(folder) or fuzzing["resume"]
        # ), f"{folder} already exists!"
        os.makedirs(fuzzing["output_folder"], exist_ok=True)
        import json
        from Fuzz4All.util.Logger import LEVEL, Logger
        with open("/root/fuzz4all/Fuzz4All/repfuzz_export_mini.json", "r") as f:
            data = json.load(f)
            yb_logger = Logger("/root/fuzz4all/outputs","f4a_new.log")
            # library = data["difflib"]
            library_name = config_dict["target"]["target_string"]
            library = data[library_name]
            yb_logger.info(f"f4a test {library_name} begin")
            api_names = list(library.keys())
            api_count = len(api_names)
            yb_logger.info(f"{library_name} has {api_count} API")
            for i in range(api_count):
                task_folder = os.path.join(fuzzing["output_folder"], f"task_{i}")
                yb_logger.info(f"f4a test {library_name}.{api_names[i]} begin")
                with ThreadPoolExecutor(max_workers=20) as executor:  # 调整 workers 数量
                    futures = []
                    for _ in range(20):  # 假设 num 是并行任务数
                        # task_folder = os.path.join(fuzzing["output_folder"], f"task_{i}")
                        os.makedirs(task_folder, exist_ok=True)
                        future = executor.submit(
                            fuzz,
                            target=target,
                            number_of_iterations=50,  
                            total_time=fuzzing["total_time"],
                            output_folder=task_folder,
                            resume=fuzzing["resume"],
                            otf=fuzzing["otf"],
                            api_name=api_names[i],
                        )
                        futures.append(future)
                    for future in futures:
                        future.result()
                        
                for filename in os.listdir(task_folder):
                    if filename.endswith(".py"):
                        filename_path = os.path.join(task_folder, filename)
                        full_cmd = ["python", "/root/fuzz4all/python_white_driver.py", library_name, filename_path]
                        res = {
                            'stdout': '',
                            'stderr': '',
                            'return_code': 0,
                            'timeout': False,
                            'exception': None,
                            'success': False
                        }
                    try:
                        process = subprocess.run(
                            full_cmd,
                            check=True,
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        res.update({
                            'stdout': process.stdout,
                            'stderr': process.stderr,
                            'return_code': process.returncode,
                            'success': True
                        })
                    except subprocess.CalledProcessError as e:
                        res.update({
                            'stdout': str(e.stdout),
                            'stderr': str(e.stderr),
                            'return_code': e.returncode,
                            'exception': e
                        })
                    except subprocess.TimeoutExpired as e:
                        res.update({
                            'stdout': str(e.stdout) if e.stdout else '',
                            'stderr': str(e.stderr) if e.stderr else 'Command timed out',
                            'return_code': 1,
                            'timeout': True,
                            'exception': TimeoutError("Command execution timed out")
                        })
                    except Exception as e:  # 捕获所有其他异常（包括语法错误）
                        res.update({
                            'stderr': f"Unexpected error: {traceback.format_exc()}",
                            'return_code': -1,
                            'exception': e
                        })
                yb_logger.info(f"Coverage now: {dcov.count_bits_py()}")
                yb_logger.info(f"f4a test {library_name}.{api_names[i]} done") 

    else:
        evaluate_all(target)


if __name__ == "__main__":
    dcov.open_bitmap_py()
    cli()
