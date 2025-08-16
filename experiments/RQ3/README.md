# Preparation

modify the content of `src/config.py`, change the following attribute:
- CHAT_LLM: set the right base_url and api_key


> Please refer to `RQ3_config.py`

# Experiment Steps

## Loop:

RepFuzz mode : NT, NS, C

## Set `PARSE-user_function_prompt_option`,  `PARSE-builtin_function_prompt_option` and `GENERATION-prompt_option` to one of the mode

## Phase 1: api arguments type inference
```bash
parse_api
```

## Phase 2: generate api calls
```bash
gen_api_call
```

## Result

The result are store in `library_qwen_2.5_7_<mode_suffix>/xxx.db` as SQLite files.