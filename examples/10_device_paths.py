"""
示例 10: 设备路径与显示接口
演示如何查询 GPU、Primary、Render 设备路径及显示接口信息。
"""

from pymtml import *

print("=" * 60)
print(" 示例 10: 设备路径与显示接口")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    # 设备路径
    print(f"  GPU 路径:     {mtmlDeviceGetGpuPath(device)}")
    print(f"  Primary 路径: {mtmlDeviceGetPrimaryPath(device)}")
    print(f"  Render 路径:  {mtmlDeviceGetRenderPath(device)}")

    # 显示接口
    disp_type_names = {
        MTML_DISP_INTF_TYPE_DP: "DisplayPort",
        MTML_DISP_INTF_TYPE_EDP: "eDP",
        MTML_DISP_INTF_TYPE_VGA: "VGA",
        MTML_DISP_INTF_TYPE_HDMI: "HDMI",
        MTML_DISP_INTF_TYPE_LVDS: "LVDS",
    }

    try:
        disp_count = mtmlDeviceCountDisplayInterface(device)
        print(f"  显示接口数量: {disp_count}")
        for d in range(disp_count):
            try:
                spec = mtmlDeviceGetDisplayInterfaceSpec(device, d)
                type_name = disp_type_names.get(spec.type, f"Unknown({spec.type})")
                print(f"    接口 {d}: {type_name}, "
                      f"最大分辨率 {spec.maxResWidth}x{spec.maxResHeight}")
            except MTMLError as e:
                print(f"    接口 {d}: [不可用: {e}]")
    except MTMLError as e:
        print(f"  显示接口: [不可用: {e}]")

mtmlLibraryShutDown()
print("\n完成!")
