"""
示例 11: MPC 与虚拟化
演示如何查询 MPC (Multi-GPU Partitioned Computing) 配置
和虚拟化相关信息。
"""

from pymtml import *

print("=" * 60)
print(" 示例 11: MPC 与虚拟化")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    # 设备属性
    prop = mtmlDeviceGetProperty(device)

    # MPC 信息
    mpc_cap = prop.mpcCapability == MTML_DEVICE_SUPPORT_MPC
    mpc_type_names = {
        MTML_MPC_TYPE_NONE: "无",
        MTML_MPC_TYPE_PARENT: "父设备",
        MTML_MPC_TYPE_INSTANCE: "MPC 实例",
    }
    print(f"  MPC 支持:     {'是' if mpc_cap else '否'}")
    print(f"  MPC 类型:     {mpc_type_names.get(prop.mpcType, f'Unknown({prop.mpcType})')}")

    try:
        mode = mtmlDeviceGetMpcMode(device)
        print(f"  MPC 模式:     {'启用' if mode else '禁用'}")
    except MTMLError as e:
        print(f"  MPC 模式:     [不可用: {e}]")

    try:
        profile_count = mtmlDeviceCountSupportedMpcProfiles(device)
        print(f"  MPC 配置文件: {profile_count} 个")
        if profile_count > 0:
            profiles = mtmlDeviceGetSupportedMpcProfiles(device, profile_count)
            for p in profiles:
                print(f"    ID={p.profileId}, 名称={p.name}, "
                      f"显存={p.memSize / 1024**3:.1f}GB, 核心数={p.gpuCores}")
    except MTMLError as e:
        print(f"  MPC 配置文件: [不可用: {e}]")

    try:
        config_count = mtmlDeviceCountSupportedMpcConfigurations(device)
        print(f"  MPC 配置方案: {config_count} 个")
    except MTMLError as e:
        print(f"  MPC 配置方案: [不可用: {e}]")

    try:
        instance_count = mtmlDeviceCountMpcInstances(device)
        print(f"  MPC 实例数:   {instance_count}")
    except MTMLError as e:
        print(f"  MPC 实例数:   [不可用: {e}]")

    # 虚拟化信息
    virt_cap = prop.virtCapability == MTML_DEVICE_SUPPORT_VIRTUALIZATION
    virt_role_names = {
        MTML_VIRT_ROLE_NONE: "无",
        MTML_VIRT_ROLE_HOST_VIRTDEVICE: "宿主机虚拟设备",
        MTML_VIRT_ROLE_GUEST_VIRTDEVICE: "虚拟机虚拟设备",
    }
    print(f"\n  虚拟化支持:   {'是' if virt_cap else '否'}")
    print(f"  虚拟化角色:   {virt_role_names.get(prop.virtRole, f'Unknown({prop.virtRole})')}")

    try:
        supported = mtmlDeviceCountSupportedVirtTypes(device)
        print(f"  支持的虚拟化类型: {supported} 个")
        if supported > 0:
            virt_types = mtmlDeviceGetSupportedVirtTypes(device, supported)
            for vt in virt_types:
                print(f"    ID={vt.id}, 名称={vt.name}, 类别={vt.deviceClass}")
                print(f"      最大实例数={vt.maxInstances}, 显存={vt.memSize / 1024**3:.1f}GB, "
                      f"核心数={vt.gpuCores}")
    except MTMLError as e:
        print(f"  支持的虚拟化类型: [不可用: {e}]")

    try:
        avail = mtmlDeviceCountAvailVirtTypes(device)
        print(f"  可用的虚拟化类型: {avail} 个")
    except MTMLError as e:
        print(f"  可用的虚拟化类型: [不可用: {e}]")

    try:
        active = mtmlDeviceCountActiveVirtDevices(device)
        print(f"  活跃虚拟设备: {active} 个")
    except MTMLError as e:
        print(f"  活跃虚拟设备: [不可用: {e}]")

mtmlLibraryShutDown()
print("\n完成!")
