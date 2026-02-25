"""
示例 05: VPU (视频处理单元) 监控
演示如何查询 VPU 时钟、编解码利用率和容量信息。
"""

from pymtml import *

print("=" * 60)
print(" 示例 05: VPU 监控")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    try:
        with mtmlVpuContext(device) as vpu:
            # 时钟
            clock = mtmlVpuGetClock(vpu)
            max_clock = mtmlVpuGetMaxClock(vpu)
            print(f"  VPU 时钟:     {clock} / {max_clock} MHz")

            # 编解码利用率
            util = mtmlVpuGetUtilization(vpu)
            print(f"  编码利用率:   {util.encodeUtil}%")
            print(f"  解码利用率:   {util.decodeUtil}%")

            # 编解码容量
            enc_cap, dec_cap = mtmlVpuGetCodecCapacity(vpu)
            print(f"  编码容量:     {enc_cap}")
            print(f"  解码容量:     {dec_cap}")

            # 编码器会话状态
            try:
                enc_states = mtmlVpuGetEncoderSessionStates(vpu, 8)
                active_enc = sum(1 for s in enc_states if s.state == MTML_CODEC_SESSION_STATE_ACTIVE)
                print(f"  活跃编码会话: {active_enc}")
                for s in enc_states:
                    if s.state == MTML_CODEC_SESSION_STATE_ACTIVE:
                        metrics = mtmlVpuGetEncoderSessionMetrics(vpu, s.sessionId)
                        print(f"    编码会话 {s.sessionId}: {metrics.width}x{metrics.height}, "
                              f"codec={metrics.codecType}, fps={metrics.fps}")
                        break
            except MTMLError:
                print(f"  活跃编码会话: [不可用]")

            # 解码器会话状态
            try:
                dec_states = mtmlVpuGetDecoderSessionStates(vpu, 8)
                active_dec = sum(1 for s in dec_states if s.state == MTML_CODEC_SESSION_STATE_ACTIVE)
                print(f"  活跃解码会话: {active_dec}")
                for s in dec_states:
                    if s.state == MTML_CODEC_SESSION_STATE_ACTIVE:
                        metrics = mtmlVpuGetDecoderSessionMetrics(vpu, s.sessionId)
                        print(f"    解码会话 {s.sessionId}: {metrics.width}x{metrics.height}, "
                              f"codec={metrics.codecType}, fps={metrics.fps}")
                        break
            except MTMLError:
                print(f"  活跃解码会话: [不可用]")

    except MTMLError as e:
        print(f"  VPU 不可用: {e}")

mtmlLibraryShutDown()
print("\n完成!")
