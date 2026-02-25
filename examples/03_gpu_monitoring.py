"""
示例 03: GPU 监控
演示如何查询 GPU 利用率、温度、时钟频率及各引擎利用率。
"""

from pymtml import *

print("=" * 60)
print(" 示例 03: GPU 监控")
print("=" * 60)

mtmlLibraryInit()

engine_names = {
    MTML_GPU_ENGINE_GEOMETRY: "几何引擎",
    MTML_GPU_ENGINE_2D: "2D 引擎",
    MTML_GPU_ENGINE_3D: "3D 引擎",
    MTML_GPU_ENGINE_COMPUTE: "计算引擎",
}

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    with mtmlGpuContext(device) as gpu:
        # 基本指标
        util = mtmlGpuGetUtilization(gpu)
        temp = mtmlGpuGetTemperature(gpu)
        clock = mtmlGpuGetClock(gpu)
        max_clock = mtmlGpuGetMaxClock(gpu)

        print(f"  GPU 利用率:   {util}%")
        print(f"  GPU 温度:     {temp}°C")
        print(f"  GPU 时钟:     {clock} / {max_clock} MHz")

        # 各引擎利用率
        print(f"  引擎利用率:")
        for engine_id, engine_name in engine_names.items():
            try:
                engine_util = mtmlGpuGetEngineUtilization(gpu, engine_id)
                print(f"    {engine_name}: {engine_util}%")
            except MTMLError as e:
                print(f"    {engine_name}: [不可用: {e}]")

mtmlLibraryShutDown()
print("\n完成!")
