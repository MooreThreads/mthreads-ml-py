"""
示例 12: CPU 亲和性与日志配置
演示如何查询 GPU 的 CPU/内存 NUMA 亲和性，以及获取日志配置。
"""

from pymtml import *

print("=" * 60)
print(" 示例 12: CPU 亲和性与日志配置")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    # CPU 亲和性
    try:
        cpu_set = mtmlDeviceGetCpuAffinityWithinNode(device, 4)
        print(f"  CPU 亲和性掩码: {[hex(x) for x in cpu_set]}")

        # 解析 CPU 核心列表
        cores = []
        for word_idx, word in enumerate(cpu_set):
            for bit in range(64):
                if word & (1 << bit):
                    cores.append(word_idx * 64 + bit)
        if cores:
            if len(cores) > 16:
                print(f"  CPU 核心列表:   {cores[:8]}...{cores[-8:]} (共 {len(cores)} 核心)")
            else:
                print(f"  CPU 核心列表:   {cores}")
    except MTMLError as e:
        print(f"  CPU 亲和性: [不可用: {e}]")

    # 内存亲和性
    try:
        mem_set = mtmlDeviceGetMemoryAffinityWithinNode(device, 4)
        print(f"  内存亲和性掩码: {[hex(x) for x in mem_set]}")

        nodes = []
        for word_idx, word in enumerate(mem_set):
            for bit in range(64):
                if word & (1 << bit):
                    nodes.append(word_idx * 64 + bit)
        print(f"  NUMA 节点:      {nodes}")
    except MTMLError as e:
        print(f"  内存亲和性: [不可用: {e}]")

# 日志配置
print(f"\n--- 日志配置 ---")
try:
    log_config = mtmlLogGetConfiguration()
    log_level_names = {
        MTML_LOG_LEVEL_OFF: "关闭",
        MTML_LOG_LEVEL_FATAL: "致命",
        MTML_LOG_LEVEL_ERROR: "错误",
        MTML_LOG_LEVEL_WARNING: "警告",
        MTML_LOG_LEVEL_INFO: "信息",
    }
    print(f"  日志文件: {log_config.filePath}")
    print(f"  最大大小: {log_config.maxSize}")
    print(f"  日志级别: {log_level_names.get(log_config.logLevel, f'Unknown({log_config.logLevel})')}")
except MTMLError as e:
    print(f"  [不可用: {e}]")

mtmlLibraryShutDown()
print("\n完成!")
