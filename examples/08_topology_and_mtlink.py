"""
示例 08: 拓扑与 MtLink 互连
演示如何查询多 GPU 拓扑关系和 MtLink 互连状态。
注意: 拓扑 API 需要 2 个以上 GPU 才能展示完整功能。
"""

from pymtml import *

print("=" * 60)
print(" 示例 08: 拓扑与 MtLink 互连")
print("=" * 60)

mtmlLibraryInit()

device_count = mtmlLibraryCountDevice()
print(f"\n检测到 {device_count} 个 GPU 设备")

devices = []
for i in range(device_count):
    device = mtmlLibraryInitDeviceByIndex(i)
    devices.append(device)
    name = mtmlDeviceGetName(device)
    print(f"  设备 {i}: {name}")

# MtLink 信息
print(f"\n--- MtLink 信息 ---")
mtlink_state_names = {
    MTML_MTLINK_STATE_DOWN: "断开",
    MTML_MTLINK_STATE_UP: "连接",
    MTML_MTLINK_STATE_DOWNGRADE: "降级",
}

for i, device in enumerate(devices):
    try:
        spec = mtmlDeviceGetMtLinkSpec(device)
        print(f"\n  设备 {i} MtLink 规格:")
        print(f"    版本:     {spec.version}")
        print(f"    带宽:     {spec.bandWidth}")
        print(f"    链路数:   {spec.linkNum}")

        for link in range(spec.linkNum):
            try:
                state = mtmlDeviceGetMtLinkState(device, link)
                state_str = mtlink_state_names.get(state, f"未知({state})")
                print(f"    链路 {link}: {state_str}", end="")

                if state == MTML_MTLINK_STATE_UP:
                    try:
                        remote = mtmlDeviceGetMtLinkRemoteDevice(device, link)
                        remote_name = mtmlDeviceGetName(remote)
                        print(f" -> {remote_name}")
                    except MTMLError:
                        print()
                else:
                    print()
                # 链路能力状态 (capability 通常为 0)
                try:
                    cap_status = mtmlDeviceGetMtLinkCapStatus(device, link, 0)
                    print(f"       MtLinkCapStatus(link={link}, cap=0): {cap_status}")
                except MTMLError:
                    pass
            except MTMLError as e:
                print(f"    链路 {link}: [不可用: {e}]")
    except MTMLError as e:
        print(f"\n  设备 {i}: MtLink 不可用 ({e})")

# 拓扑关系 (需要 2+ GPU)
if device_count >= 2:
    topo_names = {
        MTML_TOPOLOGY_INTERNAL: "同一GPU",
        MTML_TOPOLOGY_SINGLE: "单PCIe交换机",
        MTML_TOPOLOGY_MULTIPLE: "多PCIe交换机",
        MTML_TOPOLOGY_HOSTBRIDGE: "主桥",
        MTML_TOPOLOGY_NODE: "同一NUMA节点",
        MTML_TOPOLOGY_SYSTEM: "跨NUMA节点",
    }

    print(f"\n--- 拓扑关系矩阵 ---")
    for i in range(device_count):
        for j in range(i + 1, device_count):
            try:
                level = mtmlDeviceGetTopologyLevel(devices[i], devices[j])
                level_name = topo_names.get(level, f"未知({level})")
                print(f"  设备 {i} <-> 设备 {j}: {level_name}")
            except MTMLError as e:
                print(f"  设备 {i} <-> 设备 {j}: [不可用: {e}]")

    # P2P 状态
    print(f"\n--- P2P 状态 ---")
    for i in range(device_count):
        for j in range(i + 1, device_count):
            try:
                read_status = mtmlDeviceGetP2PStatus(devices[i], devices[j], MTML_P2P_CAPS_READ)
                write_status = mtmlDeviceGetP2PStatus(devices[i], devices[j], MTML_P2P_CAPS_WRITE)
                read_ok = "OK" if read_status == MTML_P2P_STATUS_OK else f"Status={read_status}"
                write_ok = "OK" if write_status == MTML_P2P_STATUS_OK else f"Status={write_status}"
                print(f"  设备 {i} <-> 设备 {j}: 读={read_ok}, 写={write_ok}")
            except MTMLError as e:
                print(f"  设备 {i} <-> 设备 {j}: [不可用: {e}]")

    # MtLink 布局
    print(f"\n--- MtLink 布局 ---")
    for i in range(device_count):
        for j in range(i + 1, device_count):
            try:
                link_count = mtmlDeviceCountMtLinkLayouts(devices[i], devices[j])
                print(f"  设备 {i} <-> 设备 {j}: {link_count} 条链路")
                if link_count > 0:
                    layouts = mtmlDeviceGetMtLinkLayouts(devices[i], devices[j], link_count)
                    for layout in layouts:
                        print(f"    本地链路ID={layout.localLinkId} <-> 远程链路ID={layout.remoteLinkId}")
            except MTMLError as e:
                print(f"  设备 {i} <-> 设备 {j}: [不可用: {e}]")

    # MtLink 最短路径 (两设备间)
    print(f"\n--- MtLink 最短路径 ---")
    try:
        path_count, path_length = mtmlDeviceCountMtLinkShortestPaths(devices[0], devices[1])
        print(f"  设备 0 -> 设备 1: {path_count} 条路径, 长度 {path_length}")
        if path_count > 0 and path_length > 0:
            paths = mtmlDeviceGetMtLinkShortestPaths(
                devices[0], devices[1], path_count, path_length
            )
            for idx, path in enumerate(paths):
                print(f"    路径 {idx}: {len(path)} 跳")
    except MTMLError as e:
        print(f"  [不可用: {e}]")

    # 按拓扑层级统计设备 / 获取同层级设备
    print(f"\n--- 按拓扑层级设备 ---")
    for level in range(MTML_TOPOLOGY_SYSTEM + 1):
        try:
            count = mtmlDeviceCountDeviceByTopologyLevel(devices[0], level)
            if count > 0:
                level_devs = mtmlDeviceGetDeviceByTopologyLevel(devices[0], level, count)
                print(f"  层级 {level}: {count} 个设备 (GetDeviceByTopologyLevel)")
        except MTMLError:
            pass
else:
    print("\n[提示] 拓扑和 P2P 测试需要 2 个以上 GPU 设备")

mtmlLibraryShutDown()
print("\n完成!")
