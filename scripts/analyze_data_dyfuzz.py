import re

log_path = "/root/DyFuzz/20250718.log"
library_marker = "DyFuzz test"
coverage_marker = "Coverage increased"

cov_data: dict[str,list[int]] = {}
res = []

library_re_str = r"DyFuzz test ([a-zA-Z]+)"
coverage_re_str = r"Coverage increased [0-9]+, now: ([0-9]+)"

# 2025-07-18 09:07:17.384 | INFO     | __main__:<module>:160 - DyFuzz test difflib
start_re_str = r"[0-9]{4}-[0-9]{2}-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}.[0-9]{3}).*?DyFuzz test ([a-zA-Z]+)"
# 2025-07-18 09:07:17.480 | INFO     | __main__:fuzzapi:229 - Coverage increased 77, now: 77
coverage_re_str = r"Coverage increased [0-9]+, now: ([0-9]+)"
# 2025-07-16 09:50:21.396 | INFO     | __main__:fuzz_one_library:135 - DyFuzz done difflib
done_re_str  = r"[0-9]{4}-[0-9]{2}-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}.[0-9]{3}).*?DyFuzz done [a-zA-Z]+"

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
                continue

read_log()

# print(cov_data)
# print(res)
for key,val in cov_data.items():
    print(f"{key}:{val[-1]}")