# MTML Python Bindings (pymtml)

Python bindings for the Moore Threads Management Library (MTML) - a C-based API for monitoring and managing Moore Threads GPU devices.

## Overview

MTML provides programmatic access to GPU metrics and configuration, similar to nvidia-smi for NVIDIA GPUs. This library (`pymtml.py`) wraps the native MTML C library for Python usage.

Moore Threads GPUs use MUSA (Meta-computing Unified System Architecture) as their compute platform, analogous to NVIDIA's CUDA.

## Requirements

- Python 3.7+
- Moore Threads GPU driver with MTML library installed
- The `libmtml.so` shared library must be in the library path

## Installation

```bash
pip install mthreads-ml-py

# Or install from source
git clone https://github.com/MooreThreads/mthreads-ml-py.git
cd mthreads-ml-py
pip install -e .
```

## Quick Start

```python
from pymtml import *

# Initialize the library
mtmlLibraryInit()

# Get device count
device_count = mtmlLibraryCountDevice()
print(f"Found {device_count} GPU(s)")

# Query each device
for i in range(device_count):
    device = mtmlLibraryInitDeviceByIndex(i)

    # Basic info
    name = mtmlDeviceGetName(device)
    uuid = mtmlDeviceGetUUID(device)
    print(f"Device {i}: {name} ({uuid})")

    # Memory info
    memory = mtmlDeviceInitMemory(device)
    total = mtmlMemoryGetTotal(memory)
    used = mtmlMemoryGetUsed(memory)
    print(f"  Memory: {used / 1024**3:.2f} / {total / 1024**3:.2f} GB")
    mtmlDeviceFreeMemory(memory)

    # GPU utilization
    util = mtmlGpuGetUtilization(device)
    temp = mtmlGpuGetTemperature(device)
    print(f"  GPU Util: {util}%, Temp: {temp}°C")

# Shutdown
mtmlLibraryShutDown()
```

## API Categories

### Library APIs
- `mtmlLibraryInit()` - Initialize the library
- `mtmlLibraryShutDown()` - Shutdown the library
- `mtmlLibraryGetVersion()` - Get library version
- `mtmlLibraryCountDevice()` - Get device count
- `mtmlLibraryInitDeviceByIndex(index)` - Get device handle by index
- `mtmlLibraryInitDeviceByUuid(uuid)` - Get device handle by UUID

### Device APIs
- `mtmlDeviceGetIndex(device)` - Get device index
- `mtmlDeviceGetName(device)` - Get device name
- `mtmlDeviceGetUUID(device)` - Get device UUID
- `mtmlDeviceGetBrand(device)` - Get device brand
- `mtmlDeviceGetSerialNumber(device)` - Get serial number
- `mtmlDeviceGetPciInfo(device)` - Get PCI information
- `mtmlDeviceGetPowerUsage(device)` - Get power usage (mW)
- `mtmlDeviceGetVbiosVersion(device)` - Get VBIOS version
- `mtmlDeviceCountGpuCores(device)` - Get GPU core count

### GPU APIs
- `mtmlDeviceInitGpu(device)` - Initialize GPU handle
- `mtmlGpuGetUtilization(device)` - Get GPU utilization (%)
- `mtmlGpuGetTemperature(device)` - Get GPU temperature (°C)
- `mtmlGpuGetClock(device)` - Get current GPU clock (MHz)
- `mtmlGpuGetMaxClock(device)` - Get max GPU clock (MHz)
- `mtmlGpuGetEngineUtilization(gpu, engine)` - Get engine utilization

### Memory APIs
- `mtmlDeviceInitMemory(device)` - Initialize memory handle
- `mtmlMemoryGetTotal(memory)` - Get total memory (bytes)
- `mtmlMemoryGetUsed(memory)` - Get used memory (bytes)
- `mtmlMemoryGetUtilization(device)` - Get memory utilization (%)
- `mtmlMemoryGetClock(device)` - Get memory clock (MHz)
- `mtmlMemoryGetBusWidth(memory)` - Get memory bus width (bits)
- `mtmlMemoryGetBandwidth(memory)` - Get memory bandwidth (GB/s)

### MtLink APIs (Multi-GPU Interconnect)
- `mtmlDeviceGetMtLinkSpec(device)` - Get MtLink specification
- `mtmlDeviceGetMtLinkState(device, link)` - Get link state
- `mtmlDeviceGetMtLinkRemoteDevice(device, link)` - Get remote device
- `mtmlDeviceCountMtLinkLayouts(dev1, dev2)` - Count link layouts between devices

### Topology APIs
- `mtmlDeviceGetTopologyLevel(dev1, dev2)` - Get topology level between devices
- `mtmlDeviceGetP2PStatus(dev1, dev2, cap)` - Get P2P status
- `mtmlDeviceCountDeviceByTopologyLevel(device, level)` - Count devices at topology level
- `mtmlDeviceGetDeviceByTopologyLevel(device, level, count)` - Get devices at topology level

### ECC APIs
- `mtmlMemoryGetEccMode(memory)` - Get ECC mode (current, pending)
- `mtmlMemoryGetEccErrorCounter(memory, errorType, counterType, location)` - Get ECC error count
- `mtmlMemoryGetRetiredPagesCount(memory)` - Get retired pages count
- `mtmlMemoryGetRetiredPagesPendingStatus(memory)` - Get pending status

### VPU APIs (Video Processing Unit)
- `mtmlDeviceInitVpu(device)` - Initialize VPU handle
- `mtmlVpuGetClock(device)` - Get VPU clock (MHz)
- `mtmlVpuGetUtilization(vpu)` - Get VPU utilization
- `mtmlVpuGetCodecCapacity(vpu)` - Get codec capacity

## Topology Levels

```python
MTML_TOPOLOGY_INTERNAL   = 0  # Same GPU
MTML_TOPOLOGY_SINGLE     = 1  # Single PCIe switch
MTML_TOPOLOGY_MULTIPLE   = 2  # Multiple PCIe switches
MTML_TOPOLOGY_HOSTBRIDGE = 3  # Host bridge
MTML_TOPOLOGY_NODE       = 4  # Same NUMA node
MTML_TOPOLOGY_SYSTEM     = 5  # Different NUMA nodes
```

## P2P Capabilities

```python
MTML_P2P_CAPS_READ  = 0  # P2P read capability
MTML_P2P_CAPS_WRITE = 1  # P2P write capability
```

## Error Handling

All functions raise `MTMLError` exceptions on failure:

```python
try:
    device = mtmlLibraryInitDeviceByIndex(99)
except MTMLError as e:
    print(f"Error: {e}")
```

## Running Tests

```bash
# Run comprehensive MTML API tests
python test_pymtml.py

# Run sglang compatibility tests
python test_sglang_compat.py
```

## License

MIT License
