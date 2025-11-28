#!/bin/bash

# usage: bash put_requirements.sh
# 环境变量`USE_UV`决定是否使用`uv`前缀安装依赖，1表示使用，0表示不使用

use_uv=0
if [ ! -z "$USE_UV" ]; then
    use_uv=1
fi

cmd_prefix=""
if [ "$use_uv" == "1" ]; then
    cmd_prefix="uv"
fi

cmd1="$cmd_prefix pip install scikit-learn==1.6.0 scipy==1.14.1 dask[dataframe]==2024.12.1 nltk==3.9.1 pandas==2.2.3 numpy==2.2.1"
cmd2="$cmd_prefix pip install torch==2.5.1+cpu --index-url=https://download.pytorch.org/whl/cpu"

eval $cmd2
eval $cmd1
