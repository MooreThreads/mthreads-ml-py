"""
示例 09: NVML 兼容层
演示如何使用 'import pymtml as pynvml' 替代 pynvml，
实现对现有 NVML 代码的无缝迁移。
"""

import pymtml as pynvml

print("=" * 60)
print(" 示例 09: NVML 兼容层 (import pymtml as pynvml)")
print("=" * 60)

# 初始化 (NVML 风格)
pynvml.nvmlInit()
print("[1] nvmlInit() 成功")

# 系统信息
driver_ver = pynvml.nvmlSystemGetDriverVersion()
print(f"[2] 驱动版本: {driver_ver}")

# 设备枚举
device_count = pynvml.nvmlDeviceGetCount()
print(f"[3] GPU 数量: {device_count}")

for i in range(device_count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    print(f"\n--- GPU {i} ---")

    # 基本信息
    name = pynvml.nvmlDeviceGetName(handle)
    uuid = pynvml.nvmlDeviceGetUUID(handle)
    index = pynvml.nvmlDeviceGetIndex(handle)
    print(f"  名称:     {name}")
    print(f"  UUID:     {uuid}")
    print(f"  索引:     {index}")

    # PCI 信息
    pci = pynvml.nvmlDeviceGetPciInfo(handle)
    print(f"  PCI SBDF: {pci.sbdf}")
    print(f"  PCI BusId: {pci.busId}")

    # 显存信息 (返回 NVMLMemoryInfo dataclass)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"  显存总量: {mem.total / 1024**3:.2f} GB")
    print(f"  已用显存: {mem.used / 1024**3:.2f} GB")
    print(f"  空闲显存: {mem.free / 1024**3:.2f} GB")

    # 利用率 (返回 NVMLUtilization dataclass)
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    print(f"  GPU 利用率:  {util.gpu}%")
    print(f"  显存利用率:  {util.memory}%")

    # 温度
    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    print(f"  温度:     {temp}°C")

    # 功耗
    power = pynvml.nvmlDeviceGetPowerUsage(handle)
    print(f"  功耗:     {power / 1000:.1f} W")

    # 时钟频率
    gpu_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
    mem_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
    vid_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_VIDEO)
    print(f"  GPU 时钟:   {gpu_clock} MHz")
    print(f"  显存时钟:   {mem_clock} MHz")
    print(f"  视频时钟:   {vid_clock} MHz")

    gpu_max = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
    mem_max = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_MEM)
    print(f"  GPU 最大时钟: {gpu_max} MHz")
    print(f"  显存最大时钟: {mem_max} MHz")

    # 风扇
    fan = pynvml.nvmlDeviceGetFanSpeed(handle)
    print(f"  风扇转速: {fan}%")

    # 编解码器
    enc = pynvml.nvmlDeviceGetEncoderUtilization(handle)
    dec = pynvml.nvmlDeviceGetDecoderUtilization(handle)
    print(f"  编码器利用率: {enc[0]}%")
    print(f"  解码器利用率: {dec[0]}%")

    # 其他 NVML 兼容接口
    print(f"  GPU 核心数:   {pynvml.nvmlDeviceGetNumGpuCores(handle)}")
    print(f"  显存总线宽度: {pynvml.nvmlDeviceGetMemoryBusWidth(handle)} bits")
    print(f"  VBIOS 版本:   {pynvml.nvmlDeviceGetVbiosVersion(handle)}")
    print(f"  Minor Number: {pynvml.nvmlDeviceGetMinorNumber(handle)}")

    # ECC
    ecc_current, ecc_pending = pynvml.nvmlDeviceGetEccMode(handle)
    print(f"  ECC 模式:     当前={'启用' if ecc_current else '禁用'}, "
          f"待定={'启用' if ecc_pending else '禁用'}")

    # MUSA 计算能力 (需要 torch_musa)
    major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
    if major > 0:
        print(f"  MUSA 计算能力: {major}.{minor}")
    else:
        print(f"  MUSA 计算能力: 不可用 (需要 torch_musa)")

    # NVLink/MtLink 状态 (链路 0)
    try:
        nvlink_state = pynvml.nvmlDeviceGetNvLinkState(handle, 0)
        print(f"  NvLink/MtLink 链路0: {'UP' if nvlink_state else 'DOWN'}")
    except pynvml.NVMLError:
        print(f"  NvLink/MtLink 链路0: [不可用]")
    try:
        cap = pynvml.nvmlDeviceGetNvLinkCapability(handle, 0, 0)
        print(f"  NvLink/MtLink 链路0 能力(0): {cap}")
    except pynvml.NVMLError:
        pass
    try:
        remote_pci = pynvml.nvmlDeviceGetNvLinkRemotePciInfo(handle, 0)
        if remote_pci:
            print(f"  NvLink/MtLink 链路0 远端 PCI: {remote_pci.busId}")
    except pynvml.NVMLError:
        pass

# 多 GPU 时: P2P 与拓扑 (NVML 接口)
if device_count >= 2:
    print(f"\n--- 多 GPU: P2P 与拓扑 (NVML) ---")
    h0 = pynvml.nvmlDeviceGetHandleByIndex(0)
    h1 = pynvml.nvmlDeviceGetHandleByIndex(1)
    try:
        p2p_read = pynvml.nvmlDeviceGetP2PStatus(h0, h1, pynvml.NVML_P2P_CAPS_INDEX_READ)
        p2p_write = pynvml.nvmlDeviceGetP2PStatus(h0, h1, pynvml.NVML_P2P_CAPS_INDEX_WRITE)
        p2p_nvlink = pynvml.nvmlDeviceGetP2PStatus(h0, h1, pynvml.NVML_P2P_CAPS_INDEX_NVLINK)
        print(f"  P2P 读: {p2p_read}, 写: {p2p_write}, NvLink/MtLink: {p2p_nvlink}")
    except pynvml.NVMLError as e:
        print(f"  P2P: [不可用: {e}]")
    try:
        topo_ancestor = pynvml.nvmlDeviceGetTopologyCommonAncestor(h0, h1)
        print(f"  拓扑公共祖先层级: {topo_ancestor}")
    except pynvml.NVMLError as e:
        print(f"  拓扑公共祖先: [不可用: {e}]")
    try:
        nearest = pynvml.nvmlDeviceGetTopologyNearestGpus(h0, pynvml.NVML_TOPOLOGY_NODE)
        print(f"  同 NUMA 节点邻近 GPU 数: {len(nearest)}")
    except pynvml.NVMLError as e:
        print(f"  拓扑邻近 GPU: [不可用: {e}]")

# 关闭
pynvml.nvmlShutdown()
print(f"\n[4] nvmlShutdown() 成功")
print("\n完成!")
