# pymtml 安装与使用手册

Python Bindings for Moore Threads Management Library (MTML)

---

## 目录

- [1. 项目简介](#1-项目简介)
- [2. 环境要求](#2-环境要求)
- [3. 安装方式](#3-安装方式)
- [4. 快速上手](#4-快速上手)
- [5. 原生 MTML API 详细说明](#5-原生-mtml-api-详细说明)
- [6. NVML 兼容层](#6-nvml-兼容层)
- [7. 上下文管理器](#7-上下文管理器)
- [8. 错误处理](#8-错误处理)
- [9. 常量与枚举](#9-常量与枚举)
- [10. 示例程序与运行输出](#10-示例程序与运行输出)
- [11. 测试](#11-测试)
- [12 常见问题](#12-常见问题)

---

## 1. 项目简介

**pymtml** 是摩尔线程 GPU 管理库 (MTML) 的 Python 绑定，通过 ctypes 动态加载 MTML 共享库（Linux: `libmtml.so`, Windows: `mtml.dll`），提供对摩尔线程 GPU 设备的监控与管理能力。


### 核心特性

| 特性 | 说明 |
| --- | --- |
| **原生 MTML API** | 直接封装 MTML C 库函数（Linux: libmtml.so, Windows: mtml.dll） |
| **NVML 兼容层** | 提供 pynvml 的替代接口，支持一行替换 |
| **上下文管理器** | 提供 `with` 语句管理 GPU/Memory/VPU 子组件生命周期 |
| **多 GPU 支持** | 支持多卡拓扑查询、P2P 状态检测、MtLink 互连检测 |
| **框架兼容** | 兼容 sglang 等 AI 推理框架的 NVML 调用 |

### 文件结构

```text
mthreads-ml-py/
├── pymtml.py              # 核心库，包含所有 MTML 绑定和 NVML 兼容函数
├── mtml_2.2.0.h           # MTML C 语言头文件（API 参考）
├── setup.py               # PyPI 打包配置
├── Makefile               # 构建/测试/发布脚本
├── example.py             # 基本用法示例
├── test_pymtml.py         # 原生 MTML API 测试
├── test_pynvml.py         # NVML 兼容层测试
├── test_sglang_compat.py  # sglang 框架兼容性测试
└── examples/              # 分类 API 使用示例（含运行输出）
    ├── 01_library_basics.py
    ├── 02_device_info.py
    ...
    └── 13_comprehensive_report.py
```

---

## 2. 环境要求

- **Python** 3.7+
- **MTML** 2.2.0+
- **硬件** 摩尔线程 GPU
- **驱动** 已安装摩尔线程 GPU 驱动程序

验证驱动是否安装：

### Linux

```bash
# 检查 MTML 库是否可用
ldconfig -p | grep libmtml

# 检查 GPU 设备
ls /dev/dri/render*
```

### Windows

#### 方式一：检查mtml.dll是否在PATH中

```cmd
where mtml.dll
```
如果MTML已正确安装并加入系统PATH，将会看到类似输出：

```
C:\Program Files\MooreThreads\MTML\bin\mtml.dll
```

#### 方式二：使用Python验证（推荐）

```python
import ctypes

try:
    ctypes.WinDLL("mtml.dll")
    print("MTML runtime is available.")
except OSError as e:
    print("MTML runtime not found:", e)
```
如果 DLL 可以被成功加载，则说明 MTML 运行时已正确安装。


---

## 3. 安装方式

### 方式一：通过 pip 安装（推荐）

```bash
pip install mthreads-ml-py
```

### 方式二：从源码安装

```bash
git clone https://github.com/MooreThreads/mthreads-ml-py.git
cd mthreads-ml-py
pip install -e .
```

### 方式三：构建 wheel 包

```bash
make build          # 构建 wheel
pip install dist/*.whl
```

---

## 4. 快速上手

### 4.1 最简示例

```python
from pymtml import *

mtmlLibraryInit()

device_count = mtmlLibraryCountDevice()
print(f"Found {device_count} GPU(s)")

for i in range(device_count):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    uuid = mtmlDeviceGetUUID(device)
    print(f"Device {i}: {name} ({uuid})")

mtmlLibraryShutDown()
```

### 4.2 查询设备详细信息

```python
from pymtml import *

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)

    # 基本信息
    name = mtmlDeviceGetName(device)
    uuid = mtmlDeviceGetUUID(device)
    print(f"Device {i}: {name} ({uuid})")

    # 显存信息（使用上下文管理器自动管理资源）
    with mtmlMemoryContext(device) as memory:
        total = mtmlMemoryGetTotal(memory)
        used = mtmlMemoryGetUsed(memory)
        print(f"  Memory: {used / 1024**3:.2f} / {total / 1024**3:.2f} GB")

    # GPU 利用率和温度
    with mtmlGpuContext(device) as gpu:
        util = mtmlGpuGetUtilization(gpu)
        temp = mtmlGpuGetTemperature(gpu)
        print(f"  GPU Util: {util}%, Temp: {temp}°C")

mtmlLibraryShutDown()
```

运行输出格式示例：

```text
Found N GPU(s)
Device 0: <设备名称> (<UUID>)
  Memory: <已用> / <总量> GB
  GPU Util: <N>%, Temp: <N>°C
```

### 4.3 作为 pynvml 替代使用

只需修改一行 import 即可将已有 pynvml 代码迁移到摩尔线程平台：

```python
# 替换前：
# import pynvml

# 替换后：
import pymtml as pynvml

# 之后的代码完全不用改动
pynvml.nvmlInit()
device_count = pynvml.nvmlDeviceGetCount()
for i in range(device_count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    name = pynvml.nvmlDeviceGetName(handle)
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"Device {i}: {name}")
    print(f"  Memory: {mem_info.used / 1024**3:.2f} / {mem_info.total / 1024**3:.2f} GB")
    print(f"  Free:   {mem_info.free / 1024**3:.2f} GB")
pynvml.nvmlShutdown()
```

---

## 5. 原生 MTML API 详细说明

### 5.1 库生命周期

| 函数 | 说明 |
| --- | --- |
| `mtmlLibraryInit()` | 初始化 MTML 库，加载 MTML 共享库（Linux: libmtml.so, Windows: mtml.dll） |
| `mtmlLibraryShutDown()` | 关闭库接口（库本身保持加载） |
| `mtmlLibraryGetVersion()` | 获取 MTML 库版本号 |
| `mtmlLibraryCountDevice()` | 获取 GPU 设备数量 |
| `mtmlLibraryInitDeviceByIndex(index)` | 按索引获取设备句柄 |
| `mtmlLibraryInitDeviceByUuid(uuid)` | 按 UUID 获取设备句柄 |
| `mtmlLibraryInitDeviceByPciSbdf(sbdf)` | 按 PCI SBDF 获取设备句柄 |
| `mtmlLibraryInitSystem()` | 初始化系统句柄 |

```python
mtmlLibraryInit()

version = mtmlLibraryGetVersion()
count = mtmlLibraryCountDevice()
print(f"MTML v{version}, {count} device(s)")

system = mtmlLibraryInitSystem()
driver_ver = mtmlSystemGetDriverVersion(system)
print(f"Driver: {driver_ver}")
mtmlLibraryFreeSystem(system)

mtmlLibraryShutDown()
```

### 5.2 设备信息 API

| 函数 | 返回值 | 说明 |
| --- | --- | --- |
| `mtmlDeviceGetIndex(device)` | `int` | 设备索引 |
| `mtmlDeviceGetName(device)` | `str` | 设备名称 |
| `mtmlDeviceGetUUID(device)` | `str` | 设备 UUID |
| `mtmlDeviceGetBrand(device)` | `int` | 品牌枚举值 |
| `mtmlDeviceGetSerialNumber(device)` | `str` | 序列号 |
| `mtmlDeviceGetPciInfo(device)` | `c_mtmlPciInfo_t` | PCI 信息结构体 |
| `mtmlDeviceGetPowerUsage(device)` | `int` | 功耗（毫瓦） |
| `mtmlDeviceGetVbiosVersion(device)` | `str` | VBIOS 版本 |
| `mtmlDeviceGetMtBiosVersion(device)` | `str` | MtBIOS 版本 |
| `mtmlDeviceCountGpuCores(device)` | `int` | GPU 核心数量 |
| `mtmlDeviceGetGpuPath(device)` | `str` | GPU 设备路径 |
| `mtmlDeviceGetPrimaryPath(device)` | `str` | 主设备路径 |
| `mtmlDeviceGetRenderPath(device)` | `str` | 渲染设备路径 |
| `mtmlDeviceGetProperty(device)` | `c_mtmlDeviceProperty_t` | 设备属性 |

```python
device = mtmlLibraryInitDeviceByIndex(0)

name = mtmlDeviceGetName(device)
uuid = mtmlDeviceGetUUID(device)
power = mtmlDeviceGetPowerUsage(device)  # 毫瓦
cores = mtmlDeviceCountGpuCores(device)

pci = mtmlDeviceGetPciInfo(device)
print(f"PCI: {pci.sbdf}, Bus Width: {pci.busWidth}")
print(f"PCIe Gen: {pci.pciCurGen}/{pci.pciMaxGen}")
print(f"PCIe Width: x{pci.pciCurWidth}/x{pci.pciMaxWidth}")
```

### 5.3 GPU API

GPU 是设备的子组件，需要先初始化、使用完后释放。推荐使用上下文管理器。

| 函数 | 返回值 | 说明 |
| --- | --- | --- |
| `mtmlDeviceInitGpu(device)` | gpu 句柄 | 初始化 GPU 子组件 |
| `mtmlDeviceFreeGpu(gpu)` | None | 释放 GPU 子组件 |
| `mtmlGpuGetUtilization(gpu)` | `int` | GPU 利用率（0-100%） |
| `mtmlGpuGetTemperature(gpu)` | `int` | GPU 温度（°C） |
| `mtmlGpuGetClock(gpu)` | `int` | 当前 GPU 时钟频率（MHz） |
| `mtmlGpuGetMaxClock(gpu)` | `int` | 最大 GPU 时钟频率（MHz） |
| `mtmlGpuGetEngineUtilization(gpu, engine)` | `int` | 指定引擎利用率 |

```python
# 方式一：手动管理
gpu = mtmlDeviceInitGpu(device)
print(f"Utilization: {mtmlGpuGetUtilization(gpu)}%")
print(f"Temperature: {mtmlGpuGetTemperature(gpu)}°C")
print(f"Clock: {mtmlGpuGetClock(gpu)} / {mtmlGpuGetMaxClock(gpu)} MHz")
mtmlDeviceFreeGpu(gpu)

# 方式二：上下文管理器（推荐）
with mtmlGpuContext(device) as gpu:
    print(f"Utilization: {mtmlGpuGetUtilization(gpu)}%")
```

GPU 引擎类型枚举：

```python
MTML_GPU_ENGINE_GEOMETRY = 0  # 几何引擎
MTML_GPU_ENGINE_2D       = 1  # 2D 引擎
MTML_GPU_ENGINE_3D       = 2  # 3D 引擎
MTML_GPU_ENGINE_COMPUTE  = 3  # 计算引擎
```

### 5.4 Memory API

| 函数 | 返回值 | 说明 |
| --- | --- | --- |
| `mtmlDeviceInitMemory(device)` | memory 句柄 | 初始化 Memory 子组件 |
| `mtmlDeviceFreeMemory(memory)` | None | 释放 Memory 子组件 |
| `mtmlMemoryGetTotal(memory)` | `int` | 总显存（字节） |
| `mtmlMemoryGetUsed(memory)` | `int` | 已用显存（字节） |
| `mtmlMemoryGetUtilization(memory)` | `int` | 显存利用率（0-100%） |
| `mtmlMemoryGetClock(memory)` | `int` | 当前显存时钟（MHz） |
| `mtmlMemoryGetMaxClock(memory)` | `int` | 最大显存时钟（MHz） |
| `mtmlMemoryGetBusWidth(memory)` | `int` | 显存总线宽度（bits） |
| `mtmlMemoryGetBandwidth(memory)` | `int` | 显存带宽（GB/s） |
| `mtmlMemoryGetSpeed(memory)` | `int` | 显存速率（Mbps） |
| `mtmlMemoryGetVendor(memory)` | `str` | 显存供应商 |
| `mtmlMemoryGetType(memory)` | `int` | 显存类型枚举 |
| `mtmlMemoryGetUsedSystem(memory)` | `int` | 系统已用内存（字节） |

```python
with mtmlMemoryContext(device) as memory:
    total = mtmlMemoryGetTotal(memory)
    used = mtmlMemoryGetUsed(memory)
    free = total - used
    util = mtmlMemoryGetUtilization(memory)
    print(f"Memory: {used/1024**3:.2f}/{total/1024**3:.2f} GB ({util}%)")
    print(f"Bus Width: {mtmlMemoryGetBusWidth(memory)} bits")
    print(f"Bandwidth: {mtmlMemoryGetBandwidth(memory)} GB/s")
    print(f"Vendor: {mtmlMemoryGetVendor(memory)}")
```

### 5.5 VPU API（视频处理单元）

| 函数 | 返回值 | 说明 |
| --- | --- | --- |
| `mtmlDeviceInitVpu(device)` | vpu 句柄 | 初始化 VPU 子组件 |
| `mtmlDeviceFreeVpu(vpu)` | None | 释放 VPU 子组件 |
| `mtmlVpuGetClock(vpu)` | `int` | 当前 VPU 时钟（MHz） |
| `mtmlVpuGetMaxClock(vpu)` | `int` | 最大 VPU 时钟（MHz） |
| `mtmlVpuGetUtilization(vpu)` | `c_mtmlCodecUtil_t` | 编解码利用率 |
| `mtmlVpuGetCodecCapacity(vpu)` | `(int, int)` | (编码容量, 解码容量) |

```python
with mtmlVpuContext(device) as vpu:
    clock = mtmlVpuGetClock(vpu)
    util = mtmlVpuGetUtilization(vpu)
    enc_cap, dec_cap = mtmlVpuGetCodecCapacity(vpu)
    print(f"VPU Clock: {clock} MHz")
    print(f"Encode Util: {util.encodeUtil}%, Decode Util: {util.decodeUtil}%")
    print(f"Codec Capacity: Enc={enc_cap}, Dec={dec_cap}")
```

### 5.6 MtLink API（多 GPU 互连）

| 函数 | 说明 |
| --- | --- |
| `mtmlDeviceGetMtLinkSpec(device)` | 获取 MtLink 规格 |
| `mtmlDeviceGetMtLinkState(device, link)` | 获取指定链路状态 |
| `mtmlDeviceGetMtLinkRemoteDevice(device, link)` | 获取远程连接的设备 |
| `mtmlDeviceCountMtLinkLayouts(dev1, dev2)` | 获取两设备间的链路数 |
| `mtmlDeviceGetMtLinkLayouts(dev1, dev2, count)` | 获取链路布局详情 |

```python
spec = mtmlDeviceGetMtLinkSpec(device)
print(f"MtLink: version={spec.version}, bandwidth={spec.bandWidth}, links={spec.linkNum}")

for i in range(spec.linkNum):
    state = mtmlDeviceGetMtLinkState(device, i)
    state_str = {0: "DOWN", 1: "UP", 2: "DOWNGRADE"}.get(state, "UNKNOWN")
    print(f"  Link {i}: {state_str}")
```

### 5.7 拓扑与 P2P API

| 函数 | 说明 |
| --- | --- |
| `mtmlDeviceGetTopologyLevel(dev1, dev2)` | 获取两设备间拓扑层级 |
| `mtmlDeviceGetP2PStatus(dev1, dev2, cap)` | 获取 P2P 读写状态 |
| `mtmlDeviceCountDeviceByTopologyLevel(dev, level)` | 统计指定层级的设备数 |
| `mtmlDeviceGetDeviceByTopologyLevel(dev, level, count)` | 获取指定层级的设备列表 |

拓扑层级枚举：

```python
MTML_TOPOLOGY_INTERNAL   = 0  # 同一 GPU
MTML_TOPOLOGY_SINGLE     = 1  # 单 PCIe 交换机
MTML_TOPOLOGY_MULTIPLE   = 2  # 多 PCIe 交换机
MTML_TOPOLOGY_HOSTBRIDGE = 3  # 主桥
MTML_TOPOLOGY_NODE       = 4  # 同一 NUMA 节点
MTML_TOPOLOGY_SYSTEM     = 5  # 不同 NUMA 节点
```

### 5.8 ECC API

| 函数 | 说明 |
| --- | --- |
| `mtmlMemoryGetEccMode(memory)` | 获取 ECC 模式 (当前, 待定) |
| `mtmlMemoryGetEccErrorCounter(memory, errorType, counterType, location)` | 获取 ECC 错误计数 |
| `mtmlMemoryGetRetiredPagesCount(memory)` | 获取退役页面计数 |
| `mtmlMemoryGetRetiredPagesPendingStatus(memory)` | 获取退役页面挂起状态 |
| `mtmlMemoryClearEccErrorCounts(memory, counterType)` | 清除 ECC 错误计数 |

```python
with mtmlMemoryContext(device) as memory:
    current_mode, pending_mode = mtmlMemoryGetEccMode(memory)
    print(f"ECC: current={'ON' if current_mode else 'OFF'}, "
          f"pending={'ON' if pending_mode else 'OFF'}")

    corrected = mtmlMemoryGetEccErrorCounter(
        memory, MTML_MEMORY_ERROR_TYPE_CORRECTED,
        MTML_VOLATILE_ECC, MTML_MEMORY_LOCATION_DRAM)
    uncorrected = mtmlMemoryGetEccErrorCounter(
        memory, MTML_MEMORY_ERROR_TYPE_UNCORRECTED,
        MTML_VOLATILE_ECC, MTML_MEMORY_LOCATION_DRAM)
    print(f"ECC Errors: corrected={corrected}, uncorrected={uncorrected}")
```

### 5.9 风扇 API

```python
fan_count = mtmlDeviceCountFan(device)
for i in range(fan_count):
    speed = mtmlDeviceGetFanSpeed(device, i)  # 百分比
    rpm = mtmlDeviceGetFanRpm(device, i)       # RPM
    print(f"Fan {i}: {speed}% ({rpm} RPM)")
```

### 5.10 MPC API（多 GPU 配置分区）

```python
mode = mtmlDeviceGetMpcMode(device)
profile_count = mtmlDeviceCountSupportedMpcProfiles(device)
config_count = mtmlDeviceCountSupportedMpcConfigurations(device)
instance_count = mtmlDeviceCountMpcInstances(device)
```

### 5.11 虚拟化 API

```python
prop = mtmlDeviceGetProperty(device)
if prop.virtCapability == MTML_DEVICE_SUPPORT_VIRTUALIZATION:
    virt_type_count = mtmlDeviceCountSupportedVirtTypes(device)
    active_count = mtmlDeviceCountActiveVirtDevices(device)
    print(f"Virtualization: {virt_type_count} types, {active_count} active")
```

---

## 6. NVML 兼容层

pymtml 提供了完整的 pynvml 兼容接口，支持以 `import pymtml as pynvml` 的方式实现零改动迁移。

### 6.1 NVML 兼容函数映射

| NVML 函数 | MTML 对应 | 说明 |
| --- | --- | --- |
| `nvmlInit()` | `mtmlLibraryInit()` | 初始化 |
| `nvmlShutdown()` | `mtmlLibraryShutDown()` | 关闭 |
| `nvmlDeviceGetCount()` | `mtmlLibraryCountDevice()` | 设备数量 |
| `nvmlDeviceGetHandleByIndex(i)` | `mtmlLibraryInitDeviceByIndex(i)` | 按索引获取设备 |
| `nvmlDeviceGetHandleByUuid(uuid)` | `mtmlLibraryInitDeviceByUuid(uuid)` | 按 UUID 获取设备 |
| `nvmlDeviceGetHandleByPciBusId(id)` | `mtmlLibraryInitDeviceByPciSbdf(id)` | 按 PCI 地址获取设备 |
| `nvmlDeviceGetName(dev)` | `mtmlDeviceGetName(dev)` | 设备名称 |
| `nvmlDeviceGetUUID(dev)` | `mtmlDeviceGetUUID(dev)` | 设备 UUID |
| `nvmlDeviceGetMemoryInfo(dev)` | 内部组合调用 | 返回 `NVMLMemoryInfo(total, free, used)` |
| `nvmlDeviceGetUtilizationRates(dev)` | 内部组合调用 | 返回 `NVMLUtilization(gpu, memory)` |
| `nvmlDeviceGetTemperature(dev, type)` | `mtmlGpuGetTemperature()` | GPU 温度 |
| `nvmlDeviceGetPowerUsage(dev)` | `mtmlDeviceGetPowerUsage()` | 功耗 |
| `nvmlDeviceGetClockInfo(dev, type)` | 按类型分发 | GPU/MEM/VIDEO 时钟 |
| `nvmlDeviceGetFanSpeed(dev)` | `mtmlDeviceGetFanSpeed()` | 风扇转速 |
| `nvmlDeviceGetPciInfo(dev)` | `mtmlDeviceGetPciInfo()` | PCI 信息 |
| `nvmlDeviceGetP2PStatus(d1, d2, cap)` | 多种 MTML 调用组合 | P2P 状态 |
| `nvmlDeviceGetTopologyCommonAncestor(d1, d2)` | `mtmlDeviceGetTopologyLevel()` | 拓扑公共祖先 |
| `nvmlDeviceGetCudaComputeCapability(dev)` | 需 `torch_musa` | MUSA 计算能力 |
| `nvmlSystemGetDriverVersion()` | `mtmlSystemGetDriverVersion()` | 驱动版本 |

### 6.2 NVML 兼容数据类型

```python
# 内存信息（dataclass）
NVMLMemoryInfo(total=25769803776, free=25488990208, used=280813568)

# 利用率信息（dataclass）
NVMLUtilization(gpu=0, memory=1)

# 错误类型别名
NVMLError          = MTMLError
NVMLError_NotFound = MTMLError_NotFound
# ... 等
```

### 6.3 不支持的 NVML 函数

以下函数因硬件差异返回固定值或空值：

| 函数 | 返回值 | 原因 |
| --- | --- | --- |
| `nvmlSystemGetCudaDriverVersion()` | `0` | 摩尔线程使用 MUSA 而非 CUDA |
| `nvmlDeviceGetBAR1MemoryInfo()` | `"N/A"` | 不支持 |
| `nvmlDeviceGetDisplayMode()` | `0` | 不支持 |
| `nvmlDeviceGetPersistenceMode()` | `0` | 不支持 |
| `nvmlDeviceGetPerformanceState()` | `"N/A"` | 不支持 |
| `nvmlDeviceGetPowerManagementLimit()` | `0` | 不支持 |
| `nvmlDeviceGetComputeRunningProcesses()` | `[]` | 不支持 |
| `nvmlDeviceGetMigMode()` | `[0, 0]` | 不支持 MIG |
| `nvmlDeviceGetCudaComputeCapability()` | `(0, 0)` | 需要 `torch_musa` |

---

## 7. 上下文管理器

pymtml 提供三个上下文管理器，自动管理子组件的初始化和释放：

```python
# GPU 上下文管理器
with mtmlGpuContext(device) as gpu:
    util = mtmlGpuGetUtilization(gpu)
    temp = mtmlGpuGetTemperature(gpu)

# Memory 上下文管理器
with mtmlMemoryContext(device) as memory:
    total = mtmlMemoryGetTotal(memory)
    used = mtmlMemoryGetUsed(memory)

# VPU 上下文管理器
with mtmlVpuContext(device) as vpu:
    clock = mtmlVpuGetClock(vpu)
```

使用上下文管理器可以确保即使在发生异常时，子组件资源也能被正确释放，避免资源泄漏。

---

## 8. 错误处理

所有 MTML 函数在失败时抛出 `MTMLError`（别名 `NVMLError`）异常：

```python
try:
    device = mtmlLibraryInitDeviceByIndex(99)  # 不存在的设备
except MTMLError as e:
    print(f"Error code: {e.value}")
    print(f"Error message: {e}")
```

### 错误码

| 常量 | 值 | 说明 |
| --- | --- | --- |
| `MTML_SUCCESS` | 0 | 成功 |
| `MTML_ERROR_DRIVER_NOT_LOADED` | 1 | 驱动未加载 |
| `MTML_ERROR_DRIVER_FAILURE` | 2 | 驱动故障 |
| `MTML_ERROR_INVALID_ARGUMENT` | 3 | 无效参数 |
| `MTML_ERROR_NOT_SUPPORTED` | 4 | 不支持的操作 |
| `MTML_ERROR_NO_PERMISSION` | 5 | 权限不足 |
| `MTML_ERROR_INSUFFICIENT_SIZE` | 6 | 缓冲区不足 |
| `MTML_ERROR_NOT_FOUND` | 7 | 未找到 |
| `MTML_ERROR_INSUFFICIENT_MEMORY` | 8 | 内存不足 |
| `MTML_ERROR_DRIVER_TOO_OLD` | 9 | 驱动版本过旧 |
| `MTML_ERROR_DRIVER_TOO_NEW` | 10 | 驱动版本过新 |
| `MTML_ERROR_TIMEOUT` | 11 | 超时 |
| `MTML_ERROR_RESOURCE_IS_BUSY` | 12 | 资源繁忙 |
| `MTML_ERROR_UNKNOWN` | 999 | 未知错误 |

每个错误码对应一个异常子类，可精确捕获：

```python
try:
    mtmlDeviceGetMtLinkSpec(device)
except MTMLError_NotSupported:
    print("MtLink not supported on this device")
except MTMLError as e:
    print(f"Other error: {e}")
```

---

## 9. 常量与枚举

### 品牌类型

```python
MTML_BRAND_MTT     = 0
MTML_BRAND_UNKNOWN = 1
```

### 显存类型

```python
MTML_MEM_TYPE_LPDDR4 = 0
MTML_MEM_TYPE_GDDR6  = 1
```

### MtLink 状态

```python
MTML_MTLINK_STATE_DOWN      = 0  # 断开
MTML_MTLINK_STATE_UP        = 1  # 连接
MTML_MTLINK_STATE_DOWNGRADE = 2  # 降级
```

### P2P 能力

```python
MTML_P2P_CAPS_READ  = 0  # 读能力
MTML_P2P_CAPS_WRITE = 1  # 写能力
```

### ECC 相关

```python
MTML_MEMORY_ECC_DISABLE = 0
MTML_MEMORY_ECC_ENABLE  = 1

MTML_VOLATILE_ECC  = 0  # 当前会话计数
MTML_AGGREGATE_ECC = 1  # 累计计数

MTML_MEMORY_ERROR_TYPE_CORRECTED   = 0  # 已纠正错误
MTML_MEMORY_ERROR_TYPE_UNCORRECTED = 1  # 未纠正错误

MTML_MEMORY_LOCATION_DRAM = 0x1  # DRAM 位置
```

### NVML 兼容常量

```python
# 时钟类型
NVML_CLOCK_GRAPHICS = 0
NVML_CLOCK_SM       = 1
NVML_CLOCK_MEM      = 2
NVML_CLOCK_VIDEO    = 3

# 温度传感器
NVML_TEMPERATURE_GPU = 0

# 拓扑层级（注意数值与 MTML 不同）
NVML_TOPOLOGY_INTERNAL   = 0
NVML_TOPOLOGY_SINGLE     = 10
NVML_TOPOLOGY_MULTIPLE   = 20
NVML_TOPOLOGY_HOSTBRIDGE = 30
NVML_TOPOLOGY_NODE       = 40
NVML_TOPOLOGY_SYSTEM     = 50

# P2P Caps Index
NVML_P2P_CAPS_INDEX_READ   = 0
NVML_P2P_CAPS_INDEX_WRITE  = 1
NVML_P2P_CAPS_INDEX_NVLINK = 2  # 映射到 MtLink
```

---

## 10. 示例程序与运行输出

`examples/` 目录包含 13 个独立示例，覆盖所有支持的 API 类别。以下为**输出格式示例**（已脱敏，不含具体硬件型号与关键信息）。

### 运行方式

```bash
# 运行单个示例
python examples/01_library_basics.py

# 运行所有示例
for f in examples/[0-9]*.py; do python "$f"; echo; done
```

### 01 — 库基础操作 (`01_library_basics.py`)

演示初始化、版本查询、设备枚举、按 UUID/PCI 获取设备、init/shutdown 循环。

```text
============================================================
 示例 01: 库基础操作
============================================================
[1] 库初始化成功
[2] MTML 库版本: <x.y.z>
[3] 驱动版本: <驱动版本号>
[4] 检测到 N 个 GPU 设备
    设备 0: <设备名称> (UUID: <UUID>)
[5] 按 UUID 获取设备: <设备名称>
[6] 按 PCI SBDF (<段:总线:设备.功能>) 获取设备: <设备名称>
[7] 库关闭成功
[8] 测试多次 init/shutdown 循环:
    第 1 次循环: 检测到 N 个设备 ✓
    第 2 次循环: 检测到 N 个设备 ✓
    第 3 次循环: 检测到 N 个设备 ✓
```

### 02 — 设备信息查询 (`02_device_info.py`)

查询名称、UUID、品牌、序列号、PCI 信息、核心数、功耗、设备属性等。

```text
============================================================
 示例 02: 设备信息查询
============================================================

--- 设备 0 ---
  名称:       <设备名称>
  索引:       0
  UUID:       <UUID>
  品牌:       <MTT | Unknown>
  序列号:     <序列号>
  VBIOS 版本: <x.y.z>
  MtBIOS 版本: <x.y.z>
  GPU 核心数: <N>
  功耗:       <N> mW (<N> W)
  PCI SBDF:   <段:总线:设备.功能>
  PCI Bus ID: <段:总线:设备.功能>
  PCI 设备ID: 0x<十六进制>
  PCIe 代数:  当前 Gen<N> / 最大 Gen<N>
  PCIe 宽度:  当前 x<N> / 最大 x<N>
  PCIe 速率:  当前 <N> GT/s / 最大 <N> GT/s
  PCIe 插槽:  <插槽名> (type=<N>)
  虚拟化:     <支持 | 不支持>
  MPC:        <支持 | 不支持>
```

### 03 — GPU 监控 (`03_gpu_monitoring.py`)

查询 GPU 利用率、温度、时钟频率及各引擎（几何/2D/3D/计算）利用率。

```text
============================================================
 示例 03: GPU 监控
============================================================

--- 设备 0: <设备名称> ---
  GPU 利用率:   <0-100>%
  GPU 温度:     <N>°C
  GPU 时钟:     <当前> / <最大> MHz
  引擎利用率:
    几何引擎: <0-100>%
    2D 引擎: <0-100>%
    3D 引擎: <0-100>%
    计算引擎: <0-100>%
```

### 04 — 显存监控 (`04_memory_monitoring.py`)

查询显存总量/已用/空闲、带宽、总线宽度、时钟、类型、供应商。

```text
============================================================
 示例 04: 显存监控
============================================================

--- 设备 0: <设备名称> ---
  显存总量:     <N> GB (<N> MB)
  已用显存:     <N> GB (<N> MB)
  空闲显存:     <N> GB (<N> MB)
  显存利用率:   <0-100>%
  显存时钟:     <当前> / <最大> MHz
  总线宽度:     <N> bits
  显存带宽:     <N> GB/s
  显存速率:     <N> Mbps
  显存类型:     <LPDDR4 | GDDR6>
  显存供应商:   <供应商名>
  系统占用显存: <N> MB 或 [不可用: Not Supported]
```

### 05 — VPU 监控 (`05_vpu_monitoring.py`)

查询视频处理单元的时钟、编解码利用率、容量和会话状态。

```text
============================================================
 示例 05: VPU 监控
============================================================

--- 设备 0: <设备名称> ---
  VPU 时钟:     <当前> / <最大> MHz
  编码利用率:   <0-100>%
  解码利用率:   <0-100>%
  编码容量:     <N>
  解码容量:     <N>
  活跃编码会话: <N>
  活跃解码会话: <N>
```

### 06 — 风扇与功耗 (`06_fan_and_power.py`)

查询各风扇的转速百分比和 RPM，以及设备功耗。

```text
============================================================
 示例 06: 风扇与功耗监控
============================================================

--- 设备 0: <设备名称> ---
  当前功耗: <N> mW (<N> W)
  风扇数量: <N>
  风扇 0 转速: <0-100>%
  风扇 0 RPM:  <N>
  风扇 1 转速: <0-100>%
  风扇 1 RPM:  <N>
  ...
```

### 07 — ECC 错误查询 (`07_ecc_errors.py`)

查询 ECC 模式、纠正/未纠正错误计数、退役页面。

```text
============================================================
 示例 07: ECC 错误查询
============================================================

--- 设备 0: <设备名称> ---
  ECC 当前模式: <启用 | 禁用>
  ECC 待定模式: <启用 | 禁用>
  已纠正错误 (当前会话): <N> 或 [不可用: Not Supported]
  未纠正错误 (当前会话): <N> 或 [不可用: Not Supported]
  已纠正错误 (累计): <N> 或 [不可用: Not Supported]
  未纠正错误 (累计): <N> 或 [不可用: Not Supported]
  退役页面 (单比特/双比特): <N> / <N> 或 [不可用]
  退役页面挂起: <是 | 否>
```

> 注: 部分型号不支持 ECC，会显示 Not Supported；支持 ECC 的型号会返回实际计数。

### 08 — 拓扑与 MtLink 互连 (`08_topology_and_mtlink.py`)

查询 MtLink 规格与状态、多 GPU 拓扑关系、P2P 状态。

```text
============================================================
 示例 08: 拓扑与 MtLink 互连
============================================================

检测到 N 个 GPU 设备
  设备 0: <设备名称>
  设备 1: <设备名称>
  ...

--- MtLink 信息 ---
  设备 N MtLink 规格: version=<N>, bandWidth=<N>, linkNum=<N>
  链路 0/1/...: <连接 | 断开 | 降级> [ -> <远程设备名> ]

--- 拓扑关系矩阵 --- (需 2+ GPU)
  设备 i <-> 设备 j: <同一GPU | 单PCIe交换机 | ... | 跨NUMA节点>

--- P2P 状态 --- (需 2+ GPU)
  设备 i <-> 设备 j: 读=<OK|...>, 写=<OK|...>
```

> 注: 单卡环境无 MtLink；多卡环境将展示链路状态、拓扑矩阵和 P2P 连通性。

### 09 — NVML 兼容层 (`09_nvml_compatibility.py`)

以 `import pymtml as pynvml` 方式使用全部 NVML 兼容 API。

```text
============================================================
 示例 09: NVML 兼容层 (import pymtml as pynvml)
============================================================
[1] nvmlInit() 成功
[2] 驱动版本: <驱动版本号>
[3] GPU 数量: <N>

--- GPU 0 ---
  名称:     <设备名称>
  UUID:     <UUID>
  索引:     0
  PCI SBDF: <段:总线:设备.功能>
  PCI BusId: <段:总线:设备.功能>
  显存总量: <N> GB
  已用显存: <N> GB
  空闲显存: <N> GB
  GPU 利用率:  <0-100>%
  显存利用率:  <0-100>%
  温度:     <N>°C
  功耗:     <N> W
  GPU 时钟:   <N> MHz
  显存时钟:   <N> MHz
  视频时钟:   <N> MHz
  GPU 最大时钟: <N> MHz
  显存最大时钟: <N> MHz
  风扇转速: <0-100>%
  编码器/解码器利用率: <0-100>%
  GPU 核心数:   <N>
  显存总线宽度: <N> bits
  VBIOS 版本:   <x.y.z>
  Minor Number: <N>
  ECC 模式:     当前=<启用|禁用>, 待定=<启用|禁用>
  MUSA 计算能力: <major.minor> 或 不可用 (需要 torch_musa)

[4] nvmlShutdown() 成功
```

### 10 — 设备路径与显示接口 (`10_device_paths.py`)

查询 GPU/Primary/Render 设备路径及显示接口规格。

```text
============================================================
 示例 10: 设备路径与显示接口
============================================================

--- 设备 0: <设备名称> ---
  GPU 路径:     /dev/mtgpu.<N>
  Primary 路径: /dev/dri/card<N>
  Render 路径:  /dev/dri/renderD<N>
  显示接口数量: <N>
    接口 0: <DisplayPort|HDMI|VGA|...>, 最大分辨率 <宽>x<高>
    接口 1: ...
```

### 11 — MPC 与虚拟化 (`11_mpc_and_virtualization.py`)

查询 MPC 配置分区和虚拟化能力。

```text
============================================================
 示例 11: MPC 与虚拟化
============================================================

--- 设备 0: <设备名称> ---
  MPC 支持:     <是 | 否>
  MPC 类型:     <无 | 父设备 | MPC 实例>
  MPC 模式:     <启用 | 禁用>
  MPC 配置文件: <N> 个 或 [不可用]
  MPC 配置方案: <N> 个 或 [不可用]
  MPC 实例数:   <N> 或 [不可用]

  虚拟化支持:   <是 | 否>
  虚拟化角色:   <无 | 宿主机虚拟设备 | 虚拟机虚拟设备>
  支持的虚拟化类型: <N> 个 或 [不可用]
  可用的虚拟化类型: <N> 个
  活跃虚拟设备: <N> 个
```

> 注: 部分型号不支持 MPC/虚拟化；支持的型号会返回配置与实例信息。

### 12 — CPU 亲和性与日志配置 (`12_affinity_and_log.py`)

查询 GPU 的 CPU/内存 NUMA 亲和性及 MTML 日志配置。

```text
============================================================
 示例 12: CPU 亲和性与日志配置
============================================================

--- 设备 0: <设备名称> ---
  CPU 亲和性掩码: ['0x<hex>', ...]
  CPU 核心列表:   [<核心编号>, ...]
  内存亲和性: [<NUMA 节点>, ...] 或 [不可用]

--- 日志配置 ---
  日志文件: <路径>
  最大大小: <N>
  日志级别: <关闭|致命|错误|警告|信息>
```

### 13 — 综合 GPU 报告 (`13_comprehensive_report.py`)

类似 nvidia-smi 的一站式信息汇总。

```text
========================================================================
  MTML GPU 综合报告
========================================================================
  MTML 版本: <x.y.z>    驱动版本: <版本>    GPU 数量: <N>
========================================================================

  GPU 0: <设备名称>
  ├─ UUID:      <UUID>
  ├─ PCI:       <段:总线:设备.功能>  (Gen<N> x<N>)
  ├─ 功耗:      <N> W
  ├─ 温度:      <N>°C    风扇: <N>%
  ├─ GPU:       利用率 <N>%    时钟 <当前>/<最大> MHz
  └─ 显存:      <已用>/<总量> GB (<N>%)    时钟 <当前>/<最大> MHz

========================================================================
```

---

## 11. 测试

### 运行所有测试

```bash
make test             # 使用 pytest 运行
```

### 逐个运行测试

```bash
python test_pymtml.py        # 原生 MTML API 测试
python test_pynvml.py        # NVML 兼容层测试
python test_sglang_compat.py # sglang 框架兼容性测试
```

### 测试说明

- **test_pymtml.py** — 测试所有原生 MTML API，包括设备查询、GPU/Memory/VPU 子组件、MtLink、ECC、MPC、虚拟化、拓扑等，还包含 init/shutdown 循环测试
- **test_pynvml.py** — 以 `import pymtml as pynvml` 方式测试所有 NVML 兼容函数
- **test_sglang_compat.py** — 测试 sglang 推理框架依赖的关键 API，包括 P2P 常量验证、NVLink/MtLink 检测、拓扑查询

> 注意：所有测试需要摩尔线程 GPU 硬件及驱动。


---

## 12 常见问题

### Q: 运行时报 "Driver Not Loaded"

```text
pymtml.MTMLError_DriverNotLoaded: Driver Not Loaded
```

**原因**：摩尔线程 GPU 驱动未加载或不在当前环境中可用（例如在沙箱、容器中运行时）。

**解决**：确认 GPU 驱动已安装，MTML 库在系统路径中（Linux: `libmtml.so` 在 `LD_LIBRARY_PATH` 中，Windows: `mtml.dll` 在 `PATH` 中或 `mtml/` 目录下）。

### Q: `nvmlDeviceGetCudaComputeCapability()` 返回 `(0, 0)`

**原因**：该函数需要 `torch` 和 `torch_musa` 才能获取 MUSA 计算能力。

**解决**：安装 `torch_musa` 后即可正常返回。

### Q: 如何在 sglang 中使用？

在 sglang 代码中将 `import pynvml` 改为 `import pymtml as pynvml`，其余代码无需修改。pymtml 已实现 sglang 依赖的所有 NVML API，包括 P2P 检测和拓扑查询。

### Q: MtLink 查询返回 N/A

**原因**：当前设备不支持 MtLink（单卡或无 MtLink 硬件）。MtLink 是摩尔线程的多卡互连技术，类似 NVIDIA 的 NVLink。

### Q: 库的 init/shutdown 可以多次调用吗？

可以。pymtml 支持多次 init/shutdown 循环调用，内部通过引用计数管理库生命周期。
