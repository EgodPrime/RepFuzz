# Preparation

modify the content of `src/config.py`, change the following attribute:
- CHAT_LLM: set the right base_url and api_key
- PARSE: set both `user_function_prompt_option` and `builtin_function_prompt_option` to `C`
- GENERATION: set `prompt_option` to `C`

> Please refer to `RQ2_config.py`

# Experiment Steps

## Loop:

model list : Qwen-2.5-1.5B-Instruct, Qwen-2.5-3B-Instruct, Qwen-2.5-7B-Instruct, Qwen2.5-14B-Instruct, GLM-4-9B, LLAMA-3.1-8B, Mistral-7B

## Set `CHAT_LLM-model_name` to one of the model list

> Make sure you have deploy these models, one recommendation tool is vllm

## Phase 1: api arguments type inference
```bash
parse_api
```

## Phase 2: generate api calls
```bash
gen_api_call
```

## Result

The result are store in `<model_name>/xxx.db` as SQLite files.