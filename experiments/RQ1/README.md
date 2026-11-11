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

---

# Signature-form bucketing (rq1_bucket_analyze.py)

Follow-up analysis for Section III-A-2 / RQ1: bucket the parsed APIs by
signature form and report `#Parsed`, `#Gen` and the generation failure rate
per bucket. It is a **read-only** post-analysis over the stored RQ1 SQLite
results — no experiment (parse / generation / fuzzing) is re-run.

## Prerequisite

The `.db` files are tracked with Git LFS; after a fresh clone fetch them
first:

```bash
git lfs install && git lfs pull
```

The script refuses to read a file that is still an LFS pointer.

## Usage

```bash
# default: data/library_qwen_2.5_7 -> experiments/RQ1/
python experiments/RQ1/rq1_bucket_analyze.py

# custom data directory / output directory
python experiments/RQ1/rq1_bucket_analyze.py \
    --data-dir data/library_qwen_2.5_7 \
    --out-dir experiments/RQ1
```

`--data-dir` contains one `*.db` per library (the RQ1 run, prompt option
`C`). Any directory with the same schema works (e.g. an ablation run such as
`data/library_qwen_2.5_7_gen_NS`); buckets are recomputed from each DB's own
stored source, so different runs stay comparable.

## Outputs

| file | content |
|---|---|
| `rq1_bucket_summary.md` | intro notes + the single table: `bucket`, `#Public`, `#Parsed`, `#Gen`, `gen failure rate` |
| `rq1_bucket_summary.csv` | the same table as CSV (rates as decimals) |

## Bucket definitions

Buckets (a parsed API lands in exactly one; the table adds an `unparsed` row
for public APIs whose parse failed and a `total` row):

| bucket | definition |
|---|---|
| `poskw` | signature contains at least one positional-or-keyword parameter |
| `varargs` | contains `*args` / `**kwargs` but **no** positional-or-keyword parameter |
| `keyword_only` | only keyword-only parameters |
| `no_args` | no parameters at all |
| `c_ext` | stored `api.source` is empty — C-extension APIs (torch/numpy) whose signature only exists in `.pyi` stubs |
| `unknown` | source present but `ast` could not recover the signature (defensive; 0 in the RQ1 run, so the row is omitted) |
| `unparsed` | public APIs with no `api` row (parse failed, so there is no stored source to bucket by) |

Signature flags are extracted with `ast` from the **stored** `api.source`,
not from the currently installed library, so the classification does not
depend on the local pip environment.

## Metric semantics

- `#Public` — the bucket's API count; it equals `#Parsed` wherever `#Parsed` is shown (bucketing requires a successful parse); parse failures show up as the `unparsed` row with `#Public` only, so the column sums to the full public API list.
- `#Parsed` — APIs with an `api` row (a successful parse).
- `#Gen` — APIs with an `api_call` row (generation succeeded).
- `no_args` and `unparsed` report `n/a` for `#Parsed`, `#Gen` and the rate: generation never runs on zero-parameter APIs, and parse failures store neither a bucket nor a generated call.
- `gen_failure_rate = 1 - #Gen / #Parsed`, strictly derived from the two
  columns shown (two decimals). The `total` row's rate covers all parsed
  APIs (including the `n/a` `no_args` bucket), i.e. `1 - 2417 / 3846`.
- Failure classification is **binary** (call present / absent); per-attempt
  failure causes are logged during the run, not stored in the DB.