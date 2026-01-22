# AGENTS.md

## Project Overview

**pymtml** is Python bindings for the Moore Threads Management Library (MTML) - a C-based API for monitoring and managing Moore Threads GPU devices. It provides:

1. **Native MTML bindings** - Direct Python wrappers for libmtml.so C library functions
2. **NVML compatibility layer** - Drop-in replacement for NVIDIA's pynvml library

Moore Threads GPUs use **MUSA** (Meta-computing Unified System Architecture) as their compute platform, analogous to NVIDIA's CUDA.

### Key Files

- `pymtml.py` - Main library with all MTML bindings and NVML wrapper functions
- `mtml_2.2.0.h` - C header file defining the MTML API (reference for adding new bindings)
- `test_pymtml.py` - Tests for native MTML APIs
- `test_pynvml.py` - Tests for NVML-compatible wrapper APIs
- `test_sglang_compat.py` - Tests for sglang framework compatibility

### NVML Compatibility

Projects using pynvml can switch to pymtml with a single import change:

```python
# Replace: import pynvml
import pymtml as pynvml

# All pynvml.nvml* functions work the same
pynvml.nvmlInit()
device = pynvml.nvmlDeviceGetHandleByIndex(0)
name = pynvml.nvmlDeviceGetName(device)
pynvml.nvmlShutdown()
```

## Build and Test Commands

```bash
# Format code (isort + black)
make format

# Lint code (flake8)
make lint

# Run tests
make test                    # pytest
python test_pymtml.py        # Native MTML API tests
python test_pynvml.py        # NVML wrapper tests
python test_sglang_compat.py # sglang compatibility tests

# Build wheel package
make build

# Clean build artifacts
make clean

# Publish to PyPI
make publish

# Run all (format, lint, test, build)
make all
```

## Code Style Guidelines

- **Formatter**: isort + black (not yapf)
- **Linter**: flake8 with max-line-length=120
- **Naming conventions**:
  - Native MTML functions: `mtmlXxx()` (e.g., `mtmlDeviceGetName`)
  - NVML wrapper functions: `nvmlXxx()` (e.g., `nvmlDeviceGetName`)
  - Constants: `MTML_XXX` or `NVML_XXX`
- **ctypes patterns**: Use `c_uint`, `c_char`, `byref()`, `POINTER()` for C bindings
- **Error handling**: Raise `MTMLError` (aliased as `NVMLError`) for all failures

## Adding New MTML Bindings

1. Find the function signature in `mtml_2.2.0.h`
2. Define any new structs in pymtml.py using `_PrintableStructure`
3. Implement the wrapper function following existing patterns:

```python
def mtmlDeviceGetSomething(device):
    global libHandle
    c_result = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetSomething")
    ret = fn(device, byref(c_result))
    _mtmlCheckReturn(ret)
    return c_result.value
```

4. Add corresponding NVML wrapper if applicable
5. Add test cases to `test_pymtml.py` and/or `test_pynvml.py`

## Testing Instructions

- **Always run tests before committing**: `python test_pymtml.py && python test_pynvml.py`
- **Tests require Moore Threads GPU hardware** with driver and libmtml.so installed
- **Test init/shutdown cycles**: The library supports multiple init/shutdown cycles
- **Check for segfaults**: Library shutdown must not cause crashes

## Security Considerations

- This library loads `libmtml.so` dynamically via ctypes
- No network operations or external data fetching
- GPU operations require appropriate system permissions
- Handle device handles carefully - don't use after shutdown

## Common Patterns

### Library lifecycle
```python
mtmlLibraryInit()      # or nvmlInit()
# ... use library ...
mtmlLibraryShutDown()  # or nvmlShutdown()
```

### Device iteration
```python
count = mtmlLibraryCountDevice()
for i in range(count):
    device = mtmlLibraryInitDeviceByIndex(i)
    # ... query device ...
```

### Sub-component access (GPU, Memory, VPU)
```python
device = mtmlLibraryInitDeviceByIndex(0)
gpu = mtmlDeviceInitGpu(device)
memory = mtmlDeviceInitMemory(device)
# ... use gpu/memory ...
mtmlDeviceFreeGpu(gpu)
mtmlDeviceFreeMemory(memory)
```

## Known Issues

- `nvmlDeviceGetCudaComputeCapability()` returns `(0, 0)` unless torch_musa is available
- Use `patch_torch_c_for_musa()` to patch torch._C with functions from torch_musa._MUSAC
- PCI busId field may be empty from driver; library auto-fills from sbdf if needed

