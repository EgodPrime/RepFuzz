# Preparation

- dataset is `experiments/RQ5/repfuzz_export_mini.json`, which is random sampled from `data/library_qwen_2.5_7`
- install dcov at `https://github.com/EgodPrime/dcov` via `pip install git+https://github.com/EgodPrime/dcov.git@pure-python`

# Experiment

## baseline: RepFuzz

> Reuse the results from RQ5

## RepFuzz without Phase 1

```bash
# make a copy of `data/library_qwen_2.5_7` to `data/library_qwen_2.5_7_wo_phase1`.
cd ${REPFUZZ_ROOT}
cp -r data/library_qwen_2.5_7 data/library_qwen_2.5_7_wo_phase1

# Modify `src/repfuzz/config.py`, set `LIBRARY_DATA_DIR` to `DATA_DIR.joinpath("library_qwen_2.5_7_wo_phase1")`
vim src/repfuzz/config.py

# remove already generaed API calls
python src/repfuzz/tools/remove_all_api_call.py

# Modify `src/repfuzz/config.py`, set `GENERATION.prompt_option="wo_phase1"`
vim src/repfuzz/config.py

# Generate API calls
gen_api_call

# Fuzzing
cd experiments/RQ6
mkdir -p safe_dir && cd safe_dir
python ../../../src/repfuzz/fuzz/fuzz_data -d ../RQ5/repfuzz_export_mini.json > ../logs/RepFuzz-wo1-$(date +%Y%m%d%H%M).log 2>&1
```

## RepFuzz without Phase 2

> Since w/o Phase 2 is equivalent to generating API calls without NS, we can directly reuse the generated API calls from RQ5.

```bash
# make a copy of `data/library_qwen_2.5_7_gen_NS` to `data/library_qwen_2.5_7_wo_phase2`.
cd ${REPFUZZ_ROOT}
cp -r data/library_qwen_2.5_7_gen_NS data/library_qwen_2.5_7_wo_phase2


# Modify `src/repfuzz/config.py`, set `LIBRARY_DATA_DIR` to `DATA_DIR.joinpath("library_qwen_2.5_7_wo_phase2")`
vim src/repfuzz/config.py

# Fuzzing
cd experiments/RQ6
mkdir -p safe_dir && cd safe_dir
python ../../../src/repfuzz/fuzz/fuzz_data -d ../RQ5/repfuzz_export_mini.json > ../logs/RepFuzz-wo2-$(date +%Y%m%d%H%M).log 2>&1
```

## RepFuzz without Phase 3

> This group only executes all the generated API calls once without iterative fuzzing.

```bash
# make a copy of `data/library_qwen_2.5_7` to `data/library_qwen_2.5_7_wo_phase3`.
cd ${REPFUZZ_ROOT}
cp -r data/library_qwen_2.5_7 data/library_qwen_2.5_7_wo_phase3

# Modify `src/repfuzz/config.py`, set `LIBRARY_DATA_DIR` to `DATA_DIR.joinpath("library_qwen_2.5_7_wo_phase3")`
# Besides, set `FUZZ.iters_per_api = 0`
vim src/repfuzz/config.py

# Fuzzing
cd experiments/RQ6
mkdir -p safe_dir && cd safe_dir
python ../../../src/repfuzz/fuzz/fuzz_data -d ../RQ5/repfuzz_export_mini.json > ../logs/RepFuzz-wo3-$(date +%Y%m%d%H%M).log 2>&1
```


