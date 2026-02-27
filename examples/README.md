# pymtml 使用示例

本目录包含 pymtml 各类 API 的使用示例，每个示例独立运行。

## 示例列表

| 文件 | 内容 | 说明 |
|------|------|------|
| `01_library_basics.py` | 库基础操作 | 初始化、版本查询、设备枚举、init/shutdown 循环 |
| `02_device_info.py` | 设备信息查询 | 名称、UUID、序列号、PCI、核心数、功耗等 |
| `03_gpu_monitoring.py` | GPU 监控 | 利用率、温度、时钟频率、引擎利用率 |
| `04_memory_monitoring.py` | 显存监控 | 显存用量、带宽、时钟、类型、供应商 |
| `05_vpu_monitoring.py` | VPU 监控 | 视频编解码利用率、容量、会话状态 |
| `06_fan_and_power.py` | 风扇与功耗 | 风扇转速/RPM、设备功耗 |
| `07_ecc_errors.py` | ECC 错误 | ECC 模式、纠正/未纠正错误计数、退役页面 |
| `08_topology_and_mtlink.py` | 拓扑与互连 | MtLink 状态、拓扑层级、P2P 状态（需多卡） |
| `09_nvml_compatibility.py` | NVML 兼容层 | 以 `import pymtml as pynvml` 方式使用全部 NVML API |
| `10_device_paths.py` | 设备路径 | GPU/Primary/Render 路径、显示接口 |
| `11_mpc_and_virtualization.py` | MPC 与虚拟化 | MPC 配置、虚拟化类型和状态 |
| `12_affinity_and_log.py` | 亲和性与日志 | CPU/内存 NUMA 亲和性、日志配置 |
| `13_comprehensive_report.py` | 综合报告 | 类似 nvidia-smi 的一站式信息汇总 |

## 运行方式

```bash
# 运行单个示例
python examples/01_library_basics.py

# 运行所有示例
for f in examples/[0-9]*.py; do echo "--- $f ---"; python "$f"; echo; done
```

## 环境要求

- **Python** 3.7+
- **MTML** 2.2.0+
- **硬件** 摩尔线程 GPU
- **驱动** 已安装摩尔线程 GPU 驱动程序
