# RepFuzz: Robust and Effective Python Library Fuzzing With Large Language Model

# Setup

```bash
# install plfuzz with its dependencies
pip install -e .

# (optional) install plfuzz with its dependencies
pip install -e .[dev]

# (optional) install the puts for experments
pip install -r put_requirements.txt

# For developer: do the following things before you commit
black src
isort src
```

# Quick Start

## 0. Create a safe working dir

```bash
mkdir -p safedir
cd safedir
```

We recommend you to run all the following steps in `safedir` dir since AI will generate arbitrary code.

## I. Edit `src/plfuzz/config.py`

1. add the target library name you want to fuzz in `tgts`, don't forget to install the library first.

2. fill the `base_url`, `model_name` and `api_key`, openai-api style LLM service is supported.

3. edit the `LIBRARY_DATA_DIR` to the directory where you want to store the library data.

> A easy way to deploy a LLM quickly is to use [ollama](https://ollama.com/) and run `ollama run <model_name>`, and the `base_url` and `api_key` would be `http://localhost:11434/api/v1` and `ollama` by default.


## II. Parse API
```bash
parse_api
```

## III. Generate API Call For Parsed API
```bash
gen_api_call
```

## IV. Fuzzing
```bash
fuzz_library -l <target library name>
# example
fuzz_library -l numpy

# fuzz all libraries once(at project root dir)
python src/repfuzz/fuzz/fuzz_library.py
```