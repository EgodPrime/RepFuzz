from repfuzz.database.sqlite_proxy import get_or_create_db
from repfuzz.config import tgts
import json
import random

def sample_apis(json_data:dict, total_samples:int=100):
    # 统计每个库的API数量
    api_counts = {lib: len(apis) for lib, apis in json_data.items()}
    
    # 计算总API数量
    total_apis = sum(api_counts.values())
    
    # 计算每个库的采样数量
    sample_counts = {}
    remaining_samples = total_samples
    for lib, count in api_counts.items():
        # 按比例计算采样数量，至少采样1个
        samples = max(1, int((count / total_apis) * total_samples))
        sample_counts[lib] = samples
        remaining_samples -= samples
    
    # 确保总采样数量为100，调整采样数量
    while remaining_samples > 0:
        for lib in api_counts:
            if remaining_samples > 0 and sample_counts[lib] < api_counts[lib]:
                sample_counts[lib] += 1
                remaining_samples -= 1
    
    # 从每个库中随机采样API
    sampled_apis = {}
    for lib, apis in json_data.items():
        sample = random.sample(list(apis.items()), sample_counts[lib])
        sampled_apis[lib] = {}
        for k,v in sample:
            sampled_apis[lib][k] = v
    
    return sampled_apis

# data = {}

# 查询语句
query = """
SELECT full_name, num_normal_arg, num_kwonly_arg
FROM api;
"""

def save_to_data(row:str, data:dict):
    # tokens = row[0].split('.')
    library_name, api_name = row[0].split('.',1)
    np = int(row[1])
    nk = int(row[2])
    n = np+nk
    v = {
        "pn":[n,n]
    }
    if library_name not in data:
        data[library_name] = {}
    data[library_name][api_name] = v
    # d = data
    # for t in tokens:
    #     if t not in d:
    #         d[t] = {}
    #     d = d[t]
    # d.update(v)


# ## split file version
# for library_name in tgts:
#     data = {}
#     # 连接数据库
#     conn = get_or_create_db(library_name)
#     cursor = conn.cursor()
#     # 执行查询
#     cursor.execute(query)
#     # 获取查询结果
#     rows = cursor.fetchall()
#     for row in rows:
#         save_to_data(row, data)
#     # 关闭连接
#     conn.close()
#     output_file_name = f"{library_name}_export.json"
#     json.dump(data, open(output_file_name, 'w'), indent=2)

## all together version
data = {}
for library_name in tgts:
    # 连接数据库
    conn = get_or_create_db(library_name)
    cursor = conn.cursor()
    # 执行查询
    cursor.execute(query)
    # 获取查询结果
    rows = cursor.fetchall()
    for row in rows:
        save_to_data(row, data)
    # 关闭连接
    conn.close()
output_file_name = f"repfuzz_export_200.json"
sampled_data = sample_apis(data, 200)
json.dump(sampled_data, open(output_file_name, 'w'), indent=2)