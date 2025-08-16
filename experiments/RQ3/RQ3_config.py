import pathlib

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = PROJECT_DIR.joinpath("src", "repfuzz")
DATA_DIR = PROJECT_DIR.joinpath("data")
LIBRARY_DATA_DIR = DATA_DIR.joinpath("library_qwen_2.5_7")
FUZZFILE_PATH = DATA_DIR.joinpath("fuzz.db")


class CHAT_LLM:
    base_url = "<base_url>"
    model_name = "Qwen/Qwen2.5-7B-Instruct"
    api_key = "<API_KEY>"
    chat = True
    generate = True
    max_concurrency = 5


class PARSE:
    user_function_prompt_option = "C"  # one of [C, NT, NS], default C
    builtin_function_prompt_option = "C"  # one of [C, NT, NS], default C


class GENERATION:
    prompt_option = "C"  # one of [C, NT, NS], default C


class FUZZ:
    iters_per_api = int(1e3)
    iters_per_seed = int(1e1)
    pop_size = 10
    timeout_dir = PROJECT_DIR.joinpath("output", "timeout")
    crash_dir = PROJECT_DIR.joinpath("output", "crash")
    potential_bugs = PROJECT_DIR.joinpath("output", "potential_bugs")


tgts = [
    "sklearn",
    "inspect",
    "scipy",
    "dask",
    "difflib",
    "re",
    "locale",
    "ast",
    "nltk",
    "pandas",
    "numpy",
    "torch",
]

skip = [
    # "sklearn"
]

blacklist = {"nltk": ["nltk.util.parallelize_preprocess"]}
