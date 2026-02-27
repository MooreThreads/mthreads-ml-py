"""
示例 01: 库基础操作
演示 MTML 库的初始化、版本查询、设备枚举、关闭等基础操作，
以及多次 init/shutdown 循环调用。
"""

from pymtml import *

print("=" * 60)
print(" 示例 01: 库基础操作")
print("=" * 60)

# 1. 初始化
mtmlLibraryInit()
print("[1] 库初始化成功")

# 2. 查询库版本
version = mtmlLibraryGetVersion()
print(f"[2] MTML 库版本: {version}")

# 3. 查询驱动版本
system = mtmlLibraryInitSystem()
driver_ver = mtmlSystemGetDriverVersion(system)
print(f"[3] 驱动版本: {driver_ver}")
mtmlLibraryFreeSystem(system)

# 4. 枚举设备
device_count = mtmlLibraryCountDevice()
print(f"[4] 检测到 {device_count} 个 GPU 设备")

for i in range(device_count):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    uuid = mtmlDeviceGetUUID(device)
    print(f"    设备 {i}: {name} (UUID: {uuid})")

# 5. 按 UUID 获取设备
if device_count > 0:
    device = mtmlLibraryInitDeviceByIndex(0)
    uuid = mtmlDeviceGetUUID(device)
    device_by_uuid = mtmlLibraryInitDeviceByUuid(uuid)
    print(f"[5] 按 UUID 获取设备: {mtmlDeviceGetName(device_by_uuid)}")

# 6. 按 PCI SBDF 获取设备
if device_count > 0:
    pci = mtmlDeviceGetPciInfo(mtmlLibraryInitDeviceByIndex(0))
    device_by_pci = mtmlLibraryInitDeviceByPciSbdf(pci.sbdf)
    print(f"[6] 按 PCI SBDF ({pci.sbdf}) 获取设备: {mtmlDeviceGetName(device_by_pci)}")

# 7. 关闭
mtmlLibraryShutDown()
print("[7] 库关闭成功")

# 8. 多次 init/shutdown 循环
print("[8] 测试多次 init/shutdown 循环:")
for cycle in range(3):
    mtmlLibraryInit()
    count = mtmlLibraryCountDevice()
    mtmlLibraryShutDown()
    print(f"    第 {cycle + 1} 次循环: 检测到 {count} 个设备 ✓")

print("\n完成!")
