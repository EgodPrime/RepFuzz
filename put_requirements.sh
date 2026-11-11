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

# 通用/数据分析库（保留原有中与 IoT 场景无关但仍被测的通用库）
cmd1="$cmd_prefix pip install scipy==1.14.1 dask[dataframe]==2024.12.1 pandas==2.2.3 numpy==2.2.1"
# IoT 应用依赖库（替换原 torch/nltk/sklearn）
cmd2="$cmd_prefix pip install redis requests"

eval $cmd2
eval $cmd1
