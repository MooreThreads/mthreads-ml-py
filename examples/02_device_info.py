"""
示例 02: 设备信息查询
演示如何查询 GPU 设备的基本属性信息。
"""

from pymtml import *

print("=" * 60)
print(" 示例 02: 设备信息查询")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)

    print(f"\n--- 设备 {i} ---")
    print(f"  名称:       {mtmlDeviceGetName(device)}")
    print(f"  索引:       {mtmlDeviceGetIndex(device)}")
    print(f"  UUID:       {mtmlDeviceGetUUID(device)}")
    print(f"  品牌:       {'MTT' if mtmlDeviceGetBrand(device) == MTML_BRAND_MTT else 'Unknown'}")

    try:
        print(f"  序列号:     {mtmlDeviceGetSerialNumber(device)}")
    except MTMLError as e:
        print(f"  序列号:     [不可用: {e}]")

    print(f"  VBIOS 版本: {mtmlDeviceGetVbiosVersion(device)}")

    try:
        print(f"  MtBIOS 版本: {mtmlDeviceGetMtBiosVersion(device)}")
    except MTMLError as e:
        print(f"  MtBIOS 版本: [不可用: {e}]")

    print(f"  GPU 核心数: {mtmlDeviceCountGpuCores(device)}")
    print(f"  功耗:       {mtmlDeviceGetPowerUsage(device)} mW "
          f"({mtmlDeviceGetPowerUsage(device) / 1000:.1f} W)")

    # PCI 信息
    pci = mtmlDeviceGetPciInfo(device)
    print(f"  PCI SBDF:   {pci.sbdf}")
    print(f"  PCI Bus ID: {pci.busId}")
    print(f"  PCI 设备ID: {pci.pciDeviceId:#010x}")
    print(f"  PCIe 代数:  当前 Gen{pci.pciCurGen} / 最大 Gen{pci.pciMaxGen}")
    print(f"  PCIe 宽度:  当前 x{pci.pciCurWidth} / 最大 x{pci.pciMaxWidth}")
    print(f"  PCIe 速率:  当前 {pci.pciCurSpeed:.1f} GT/s / 最大 {pci.pciMaxSpeed:.1f} GT/s")

    # PCIe 插槽信息
    try:
        slot = mtmlDeviceGetPcieSlotInfo(device)
        print(f"  PCIe 插槽:  {slot.slotName} (type={slot.slotType})")
    except MTMLError as e:
        print(f"  PCIe 插槽:  [不可用: {e}]")

    # 设备属性
    prop = mtmlDeviceGetProperty(device)
    virt_cap = "支持" if prop.virtCapability == MTML_DEVICE_SUPPORT_VIRTUALIZATION else "不支持"
    mpc_cap = "支持" if prop.mpcCapability == MTML_DEVICE_SUPPORT_MPC else "不支持"
    print(f"  虚拟化:     {virt_cap}")
    print(f"  MPC:        {mpc_cap}")

mtmlLibraryShutDown()
print("\n完成!")
