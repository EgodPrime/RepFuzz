import datetime
import re
from matplotlib import pyplot as plt

def parse_log_v2(log_path: str) -> tuple[list[float], list[int]]:
    # 2025-07-30 08:22:44.036 | INFO     | __main__:<module>:200 - Coverage now: 96145
    re_str = r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}\.\d{3}).*?Coverage now: (\d+)"
    time_data = []
    coverage_data = []
    with open(log_path, "r") as f:
        for line in f:
            match = re.search(re_str, line)
            if match:
                year, month, day, hour, minute, second, coverage = match.groups()
                year = int(year)
                month = int(month)
                day = int(day)
                hour = int(hour)
                minute = int(minute)
                second = float(second)
                coverage = int(coverage)

                # 构建 datetime 对象
                dt = datetime.datetime(year, month, day, hour, minute, 0)
                timestamp = dt.timestamp() + second

                time_data.append(timestamp)
                coverage_data.append(coverage)

    # normalize time
    time_data = [t - time_data[0] for t in time_data]
    return time_data, coverage_data


if __name__ == "__main__":
    td_repfuzz, cd_repfuzz = parse_log_v2("./logs/RepFuzz-20250730.log")
    td_dyfuzz, cd_dyfuzz = parse_log_v2("./logs/DyFuzz-20250730.log")
    td_f4a,cd_f4a = parse_log_v2("./logs/Fuzz4All-20250808.log")
    repfuzz_last_index = len(td_repfuzz) - 1
    dyfuzz_last_index = len(td_dyfuzz) - 1
    f4a_last_index = len(td_f4a) - 1

    plt.figure(0, (10,4))
    plt.subplot(1,2,1)
    # 画出主曲线
    plt.plot(td_repfuzz, label="RepFuzz", color="red")
    plt.plot(td_f4a, label="Fuzz4All", color='green')
    plt.plot(td_dyfuzz, label="DyFuzz", color="blue")
    # 最后一个点加粗
    plt.plot(repfuzz_last_index, td_repfuzz[-1], "ro", markersize=5)
    plt.plot(f4a_last_index, td_f4a[-1], "go", markersize=5)
    plt.plot(dyfuzz_last_index, td_dyfuzz[-1], "bo", markersize=5)
    # 在最后一个点右上方添加数值
    plt.text(
        repfuzz_last_index + 1, td_repfuzz[-1] + 1, f"{td_repfuzz[-1]:.2f}", color="red", fontsize=10
    )
    plt.text(
        f4a_last_index + 1, td_f4a[-1] + 1, f"{td_f4a[-1]:.2f}", color="green", fontsize=10
    )
    plt.text(
        dyfuzz_last_index + 1, td_dyfuzz[-1] + 1, f"{td_dyfuzz[-1]:.2f}", color="blue", fontsize=10
    )
    plt.legend()
    plt.grid(axis="y")
    plt.xlabel("API iteration")
    plt.ylabel("Time(s)")
    plt.title("Time cost over API iteration")
    plt.tight_layout()
    # plt.savefig("time_over_api.jpg")

    # plt.figure()
    plt.subplot(1,2,2)
    # 画出主曲线
    plt.plot(cd_repfuzz, label="RepFuzz", color="red")
    plt.plot(cd_f4a, label="Fuzz4All", color="green")
    plt.plot(cd_dyfuzz, label="DyFuzz", color="blue")
    # 最后一个点加粗
    plt.plot(repfuzz_last_index, cd_repfuzz[-1], "ro", markersize=5)
    plt.plot(f4a_last_index, cd_f4a[-1], "go", markersize=5)
    plt.plot(dyfuzz_last_index, cd_dyfuzz[-1], "bo", markersize=5)
    # 在最后一个点右上方添加数值
    plt.text(
        repfuzz_last_index + 1, cd_repfuzz[-1] + 1, f"{cd_repfuzz[-1]}", color="red", fontsize=10
    )
    plt.text(
        f4a_last_index + 1, cd_f4a[-1] + 1, f"{cd_f4a[-1]}", color="green", fontsize=10
    )
    plt.text(
        dyfuzz_last_index + 1, cd_dyfuzz[-1] + 1, f"{cd_dyfuzz[-1]}", color="blue", fontsize=10
    )
    plt.legend()
    plt.grid(axis="y")
    plt.xlabel("API iteration")
    plt.ylabel("Line coverage")
    plt.title("Line coverage over API iteration")
    plt.tight_layout()
    # plt.savefig("line_coverage_over_api.jpg")
    plt.savefig("RQ5.jpg")
