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
    td_repfuzz, cd_repfuzz = parse_log_v2("../RQ5/logs/RepFuzz-20250730.log")
    repfuzz_last_index = len(td_repfuzz) - 1
    td_wo_phase1, cd_wo_phase1 = parse_log_v2("./logs/RepFuzz-wo1-202512011011.log")
    wo_phase1_last_index = len(td_wo_phase1) - 1
    td_wo_phase2, cd_wo_phase2 = parse_log_v2("./logs/RepFuzz-wo2-202512011034.log")
    wo_phase2_last_index = len(td_wo_phase2) - 1
    td_wo_phase3, cd_wo_phase3 = parse_log_v2("./logs/RepFuzz-wo3-202512011047.log")
    wo_phase3_last_index = len(td_wo_phase3) - 1

    plt.figure(0, (10,4))
    plt.subplot(1,2,1)
    # 画出主曲线
    plt.plot(td_repfuzz, label="RepFuzz", color="red")
    plt.plot(td_wo_phase1, label="RepFuzz-wo1", color='green')
    plt.plot(td_wo_phase2, label="RepFuzz-wo2", color="blue")
    plt.plot(td_wo_phase3, label="RepFuzz-wo3", color="orange")
    # 最后一个点加粗
    plt.plot(repfuzz_last_index, td_repfuzz[-1], "ro", markersize=5)
    plt.plot(wo_phase1_last_index, td_wo_phase1[-1], "go", markersize=5)
    plt.plot(wo_phase2_last_index, td_wo_phase2[-1], "bo", markersize=5)
    plt.plot(wo_phase3_last_index, td_wo_phase3[-1], "o", color="orange", markersize=5)
    # 在最后一个点右上方添加数值
    plt.text(
        repfuzz_last_index + 1, td_repfuzz[-1] + 1, f"{td_repfuzz[-1]:.2f}", color="red", fontsize=10
    )
    plt.text(
        wo_phase1_last_index + 1, td_wo_phase1[-1] + 1, f"{td_wo_phase1[-1]:.2f}", color="green", fontsize=10
    )
    plt.text(
        wo_phase2_last_index + 1, td_wo_phase2[-1] + 1, f"{td_wo_phase2[-1]:.2f}", color="blue", fontsize=10
    )
    plt.text(
        wo_phase3_last_index + 1, td_wo_phase3[-1] + 1, f"{td_wo_phase3[-1]:.2f}", color="orange", fontsize=10
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
    plt.plot(cd_wo_phase1, label="RepFuzz-wo1", color="green")
    plt.plot(cd_wo_phase2, label="RepFuzz-wo2", color="blue")
    plt.plot(cd_wo_phase3, label="RepFuzz-wo3", color="orange")
    # 最后一个点加粗
    plt.plot(repfuzz_last_index, cd_repfuzz[-1], "ro", markersize=5)
    plt.plot(wo_phase1_last_index, cd_wo_phase1[-1], "go", markersize=5)
    plt.plot(wo_phase2_last_index, cd_wo_phase2[-1], "bo", markersize=5)
    plt.plot(wo_phase3_last_index, cd_wo_phase3[-1], "o", color="orange", markersize=5)
    # 在最后一个点右上方添加数值
    plt.text(
        repfuzz_last_index + 1, cd_repfuzz[-1] + 1, f"{cd_repfuzz[-1]}", color="red", fontsize=10
    )
    plt.text(
        wo_phase1_last_index + 1, cd_wo_phase1[-1] + 1, f"{cd_wo_phase1[-1]}", color="green", fontsize=10
    )
    plt.text(
        wo_phase2_last_index + 1, cd_wo_phase2[-1] + 1, f"{cd_wo_phase2[-1]}", color="blue", fontsize=10
    )
    plt.text(
        wo_phase3_last_index + 1, cd_wo_phase3[-1] + 1, f"{cd_wo_phase3[-1]}", color="orange", fontsize=10
    )
    plt.legend()
    plt.grid(axis="y")
    plt.xlabel("API iteration")
    plt.ylabel("Line coverage")
    plt.title("Line coverage over API iteration")
    plt.tight_layout()
    # plt.savefig("line_coverage_over_api.jpg")
    plt.savefig("RQ6.jpg", dpi=300)
