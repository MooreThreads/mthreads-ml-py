"""
示例 06: 风扇与功耗监控
演示如何查询风扇转速和设备功耗。
"""

from pymtml import *

print("=" * 60)
print(" 示例 06: 风扇与功耗监控")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    # 功耗
    power_mw = mtmlDeviceGetPowerUsage(device)
    print(f"  当前功耗: {power_mw} mW ({power_mw / 1000:.1f} W)")

    # 风扇
    try:
        fan_count = mtmlDeviceCountFan(device)
        print(f"  风扇数量: {fan_count}")

        for f in range(fan_count):
            try:
                speed = mtmlDeviceGetFanSpeed(device, f)
                print(f"  风扇 {f} 转速: {speed}%")
            except MTMLError as e:
                print(f"  风扇 {f} 转速: [不可用: {e}]")

            try:
                rpm = mtmlDeviceGetFanRpm(device, f)
                print(f"  风扇 {f} RPM:  {rpm}")
            except MTMLError as e:
                print(f"  风扇 {f} RPM:  [不可用: {e}]")
    except MTMLError as e:
        print(f"  风扇信息: [不可用: {e}]")

mtmlLibraryShutDown()
print("\n完成!")
