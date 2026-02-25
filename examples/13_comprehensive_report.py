"""
示例 13: 综合 GPU 报告
类似 nvidia-smi 的综合信息展示，一次性输出所有关键指标。

兼容性说明：
- 本示例针对 MTML >= 2.2.0 设计，但会显式处理旧版本运行库的兼容性。
- 若用户无法升级到最新 MTML，部分 API 可能不可用；不可用项会显示为 N/A，
  而不会导致脚本报错，便于在旧环境下仍能查看可用信息。
"""

from pymtml import *


def _safe(fn, default=None, *args, **kwargs):
    """调用可能在新版 MTML 才提供的 API；若不存在或失败则返回 default。"""
    try:
        return fn(*args, **kwargs)
    except MTMLError:
        return default


print("=" * 72)
print("  MTML GPU 综合报告")
print("=" * 72)

mtmlLibraryInit()

# 系统信息（版本/驱动在旧 MTML 上可能不可用）
version = _safe(mtmlLibraryGetVersion, "unknown")
driver_ver = "N/A"
system = _safe(mtmlLibraryInitSystem)
if system is not None:
    try:
        driver_ver = mtmlSystemGetDriverVersion(system)
    except MTMLError:
        pass
    _safe(mtmlLibraryFreeSystem, None, system)

device_count = mtmlLibraryCountDevice()
if version == "unknown":
    print("  MTML 版本: (运行时可能 < 2.2.0，部分项将显示 N/A)")
else:
    print("  MTML 版本: {}  (目标 API 2.2.0+，旧运行库下部分项为 N/A)".format(version))
print("  驱动版本: {}    GPU 数量: {}".format(driver_ver, device_count))
print("=" * 72)

for i in range(device_count):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    uuid = mtmlDeviceGetUUID(device)

    power = _safe(mtmlDeviceGetPowerUsage, None, device)
    power_str = "{:.1f} W".format(power / 1000) if power is not None else "N/A"

    gpu_util = gpu_temp = gpu_clock = gpu_max_clock = None
    gpu_ctx = _safe(mtmlGpuContext, None, device)
    if gpu_ctx is not None:
        try:
            with gpu_ctx as gpu:
                gpu_util = _safe(mtmlGpuGetUtilization, None, gpu)
                gpu_temp = _safe(mtmlGpuGetTemperature, None, gpu)
                gpu_clock = _safe(mtmlGpuGetClock, None, gpu)
                gpu_max_clock = _safe(mtmlGpuGetMaxClock, None, gpu)
        except MTMLError:
            pass
    gpu_util_str = "{}%".format(gpu_util) if gpu_util is not None else "N/A"
    gpu_temp_str = "{}°C".format(gpu_temp) if gpu_temp is not None else "N/A"
    gpu_clock_str = "{}/{} MHz".format(gpu_clock, gpu_max_clock) if (gpu_clock is not None and gpu_max_clock is not None) else "N/A"

    mem_total = mem_used = mem_util = mem_clock = mem_max_clock = None
    mem_ctx = _safe(mtmlMemoryContext, None, device)
    if mem_ctx is not None:
        try:
            with mem_ctx as memory:
                mem_total = mtmlMemoryGetTotal(memory)
                mem_used = mtmlMemoryGetUsed(memory)
                mem_util = _safe(mtmlMemoryGetUtilization, None, memory)
                mem_clock = _safe(mtmlMemoryGetClock, None, memory)
                mem_max_clock = _safe(mtmlMemoryGetMaxClock, None, memory)
        except MTMLError:
            pass
    if mem_total is not None and mem_used is not None:
        mem_str = "{:.2f}/{:.2f} GB".format(mem_used / 1024**3, mem_total / 1024**3)
        if mem_util is not None:
            mem_str += " ({}%)".format(mem_util)
        mem_str += "    时钟 " + (
            "{}/{} MHz".format(mem_clock, mem_max_clock) if (mem_clock is not None and mem_max_clock is not None) else "N/A"
        )
    else:
        mem_str = "N/A"

    try:
        fan_speed = mtmlDeviceGetFanSpeed(device, 0)
        fan_str = "{}%".format(fan_speed)
    except MTMLError:
        fan_str = "N/A"

    pci = _safe(mtmlDeviceGetPciInfo, None, device)
    if pci is not None:
        pci_str = "{}  (Gen{} x{})".format(pci.sbdf, pci.pciCurGen, pci.pciCurWidth)
    else:
        pci_str = "N/A"

    print("""
  GPU {}: {}
  ├─ UUID:      {}
  ├─ PCI:       {}
  ├─ 功耗:      {}
  ├─ 温度:      {}    风扇: {}
  ├─ GPU:       利用率 {}    时钟 {}
  └─ 显存:      {}""".format(
        i, name, uuid, pci_str, power_str, gpu_temp_str, fan_str, gpu_util_str, gpu_clock_str, mem_str
    ))

print()
print("=" * 72)

mtmlLibraryShutDown()
