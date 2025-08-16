# Preparation

modify the content of `src/config.py`, change the following attribute:
- CHAT_LLM: set the right base_url and api_key
- PARSE: set both `user_function_prompt_option` and `builtin_function_prompt_option` to `C`
- GENERATION: set `prompt_option` to `C`
- FUZZ: set `iters_per_api` to `1000`

> Please refer to `RQ1_config.py`

# Experiment Steps

## Phase 1: api arguments type inference
```bash
parse_api
```

## Phase 2: generate api calls
```bash
gen_api_call
```

## Phase 3: in-memory fuzzing
```bash
fuzz_library
```

## Result

The result are store in `library_qwen_2.5_7/xxx.db` as SQLite files.