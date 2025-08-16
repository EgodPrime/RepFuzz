# Preparation

- dataset is `experiments/RQ4/repfuzz_export_mini.json`, which is random sampled from `data/library_qwen_2.5_7`
- modification of DyFuzz is at `mod-DyFuzz` 
- modification of Fuzz4All is at `mod-Fuzz4All`
- install dcov at `https://github.com/EgodPrime/dcov`

# Experiment

## RepFuzz

```bash
fuzz_data -d ./repfuzz_export_mini.json > ./logs/RepFuzz-new.log 2>&1
```

## DyFuzz

```bash
# down load DyFuzz source
git clone https://github.com/xiaxinmeng/DyFuzz.git

# apply modification
cp <path to DyFuzz>/apifuzzer.py <path to DyFuzz>/apifuzzer.py.bak
cp mod-DyFuzz/apifuzzer.py <path to DyFuzz>/apifuzzer.py
cp mod-DyFuzz/run_repfuzz.py <path to DyFuzz>/run_repfuzz.py

# run
cd DyFuzz
python run_repfuzz.py > ../logs/DyFuzz-new.log 2>&1
```


## Fuzz4All

```bash
# down load Fuzz4All source
git clone https://github.com/fuzz4all/fuzz4all.git

# apply modification
cp -r mod-Fuzz4All/documentation/* <path to fuzz4all>/config/documentation/
cp -r mod-Fuzz4All/target/* <path to fuzz4all>/Fuzz4all/target/
cp repfuzz_export_mini.json <path to fuzz4all>/Fuzz4all/
cp mod-Fuzz4All/full_run/* <path to fuzz4all>/config/full_run/
cp mod-Fuzz4All/fuzz.py <path to fuzz4all>/Fuzz4all/fuzz.py
cp mod-Fuzz4All/make_target.py <path to fuzz4all>/Fuzz4all/make_target.py
cp mod-Fuzz4All/model.py <path to fuzz4all>/Fuzz4all/model.py
cp mod-Fuzz4All/python_white_driver.py <path to fuzz4all>/Fuzz4all/python_white_driver.py
cp mod-Fuzz4All/f4a.py <path to fuzz4all>/Fuzz4all/f4a.py
cp mod-Fuzz4All/f4a.json <path to fuzz4all>/Fuzz4all/f4a.json


# some config

## model.py
if you want to change the model, you need to find in model.py line 2 "client = openai.OpenAI(base_url="http://192.168.2.29:8022/v1", api_key="yb")", you can change the url and "api_key" with new value.
In model.py line 133, you need change the model name which you want to use, and change it at this place like "model="qwen2.5-coder-7b",". 

# run
cd fuzz4all
python f4a.py f4a.json 
```