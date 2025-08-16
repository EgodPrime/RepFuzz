import pathlib

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = PROJECT_DIR.joinpath("src", "repfuzz")
DATA_DIR = PROJECT_DIR.joinpath("data")
LIBRARY_DATA_DIR = DATA_DIR.joinpath("library_qwen_2.5_7")
FUZZFILE_PATH = DATA_DIR.joinpath("fuzz.db")


class CHAT_LLM:
    base_url = "http://192.168.2.29:8001/v1" # change this to your own
    # model_name = "LLM-Research/Meta-Llama-3.1-8B-Instruct"
    # model_name = "LLM-Research/Mistral-7B-Instruct-v0.3"
    model_name = "Qwen/Qwen2.5-7B-Instruct" # change this to your own
    # model_name = "ZhipuAI/glm-4-9b-chat"
    # base_url = "http://192.168.1.45:30000/v1"
    # model_name = "glm4-chat"
    api_key = "openai" # change this to your own
    chat = True
    generate = True
    max_concurrency = 5


class PARSE:
    user_function_prompt_option = "C"  # one of [C, NT, NS], default C
    builtin_function_prompt_option = "C"  # one of [C, NT, NS], default C


class GENERATION:
    prompt_option = "C"  # one of [C, NT, NS], default C


class FUZZ:
    iters_per_api = int(1e2)
    iters_per_seed = int(1e1)
    pop_size = 10
    timeout_dir = PROJECT_DIR.joinpath("output", "timeout")
    crash_dir = PROJECT_DIR.joinpath("output", "crash")
    potential_bugs = PROJECT_DIR.joinpath("output", "potential_bugs")


tgts = [
    "difflib",
    "re",
    "locale",
    "ast",
    "sklearn",
    "inspect",
    "scipy",
    "dask",
    "nltk",
    "pandas",
    "numpy",
    "torch",
]

skip = [
    # "sklearn"
]

blacklist = {"nltk": ["nltk.util.parallelize_preprocess"]}
