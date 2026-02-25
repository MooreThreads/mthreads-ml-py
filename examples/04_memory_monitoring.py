"""
示例 04: 显存监控
演示如何查询显存使用情况、带宽、时钟等信息。
"""

from pymtml import *

print("=" * 60)
print(" 示例 04: 显存监控")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    with mtmlMemoryContext(device) as memory:
        total = mtmlMemoryGetTotal(memory)
        used = mtmlMemoryGetUsed(memory)
        free = total - used
        util = mtmlMemoryGetUtilization(memory)

        print(f"  显存总量:     {total / 1024**3:.2f} GB ({total / 1024**2:.0f} MB)")
        print(f"  已用显存:     {used / 1024**3:.2f} GB ({used / 1024**2:.0f} MB)")
        print(f"  空闲显存:     {free / 1024**3:.2f} GB ({free / 1024**2:.0f} MB)")
        print(f"  显存利用率:   {util}%")

        # 时钟
        clock = mtmlMemoryGetClock(memory)
        max_clock = mtmlMemoryGetMaxClock(memory)
        print(f"  显存时钟:     {clock} / {max_clock} MHz")

        # 带宽和总线
        bus_width = mtmlMemoryGetBusWidth(memory)
        bandwidth = mtmlMemoryGetBandwidth(memory)
        speed = mtmlMemoryGetSpeed(memory)
        print(f"  总线宽度:     {bus_width} bits")
        print(f"  显存带宽:     {bandwidth} GB/s")
        print(f"  显存速率:     {speed} Mbps")

        # 类型和供应商
        mem_type = mtmlMemoryGetType(memory)
        type_names = {MTML_MEM_TYPE_LPDDR4: "LPDDR4", MTML_MEM_TYPE_GDDR6: "GDDR6"}
        print(f"  显存类型:     {type_names.get(mem_type, f'Unknown({mem_type})')}")

        try:
            vendor = mtmlMemoryGetVendor(memory)
            print(f"  显存供应商:   {vendor}")
        except MTMLError as e:
            print(f"  显存供应商:   [不可用: {e}]")

        # 系统使用量
        try:
            sys_used = mtmlMemoryGetUsedSystem(memory)
            print(f"  系统占用显存: {sys_used / 1024**2:.2f} MB")
        except MTMLError as e:
            print(f"  系统占用显存: [不可用: {e}]")

mtmlLibraryShutDown()
print("\n完成!")
