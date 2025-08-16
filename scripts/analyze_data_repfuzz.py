import re

log_path = "safedir/20250716.log"

start_marker = "There are "
coverage_marker = "Coverage increased"

cov_data: dict[str,list[int]] = {}
res = []

# 2025-07-16 09:50:10.150 | INFO     | __main__:fuzz_one_library:102 - There are 8 api calls for difflib to fuzz.
start_re_str = r"[0-9]{4}-[0-9]{2}-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}.[0-9]{3}).*?There are [0-9]+ api calls for ([a-zA-Z]+) to fuzz"
# 2025-07-16 09:50:10.282 | INFO     | repfuzz.fuzz.fuzz_api:fuzz_api:130 - Coverage increased 1, now: 188
coverage_re_str = r"Coverage increased [0-9]+, now: ([0-9]+)"
# 2025-07-16 09:50:21.396 | INFO     | __main__:fuzz_one_library:135 - [32mFuzzing difflib done
done_re_str  = r"[0-9]{4}-[0-9]{2}-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}.[0-9]{3}).*?Fuzzing [a-zA-Z]+ done"

def read_log():
    with open(log_path) as f:
        cur_lib = None
        st = 0
        et = 0
        while True:
            line = f.readline()
            if not line:
                break
            r1 = re.search(start_re_str, line)
            if r1:
                d, sh, sm, ss, cur_lib = r1.groups()
                if cur_lib not in cov_data:
                    cov_data[cur_lib] = [0]
                # print(f"d={d}, sh={sh}, sm={sm}, ss={ss}")
                st = float(d)*3600*24 + float(sh)*3600+float(sm)*60+float(ss)
                res.append(line)
                continue
            if coverage_marker in line:
                r2 = re.search(coverage_re_str, line)
                cov_data[cur_lib].append(int(r2.group(1)))
                res.append(line)
                continue
            r3 = re.search(done_re_str, line)
            if r3:
                d, sh, sm, ss = r3.groups()
                # print(f"d={d}, sh={sh}, sm={sm}, ss={ss}")
                et = float(d)*3600*24 + float(sh)*3600+float(sm)*60+float(ss)
                dt = et-st
                print(f"{cur_lib}: {cov_data[cur_lib][-1]} {dt:.2f}")

read_log()

# print(cov_data)
# print(res)
# for key,val in cov_data.items():
#     print(f"{key}:{val[-1]}")