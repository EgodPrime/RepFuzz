# RepFuzz

This repository is the implementation of our paper "Robust and Effective Python Library Fuzzing With Large Language Model" which is submitted to IEEE TDSC for review.

# Setup

```bash
# install RepFuzz with its dependencies
pip install -e .

# (optional) install RepFuzz with its dependencies
pip install -e .[dev]

# (optional) install the puts for experments
bash put_requirements.sh
# if you are using uv, run
# USE_UV=1 bash put_requirements.sh

```

# Quick Start

## 0. Create a safe working dir

```bash
mkdir -p safedir
cd safedir
```

We recommend you to run all the following steps in `safedir` dir since AI will generate arbitrary code.

## I. Edit `src/repfuzz/config.py`

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