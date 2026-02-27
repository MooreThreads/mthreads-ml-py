"""
示例 07: ECC 错误查询
演示如何查询 ECC 模式和错误计数。
"""

from pymtml import *

print("=" * 60)
print(" 示例 07: ECC 错误查询")
print("=" * 60)

mtmlLibraryInit()

for i in range(mtmlLibraryCountDevice()):
    device = mtmlLibraryInitDeviceByIndex(i)
    name = mtmlDeviceGetName(device)
    print(f"\n--- 设备 {i}: {name} ---")

    with mtmlMemoryContext(device) as memory:
        # ECC 模式
        try:
            current_mode, pending_mode = mtmlMemoryGetEccMode(memory)
            print(f"  ECC 当前模式: {'启用' if current_mode else '禁用'}")
            print(f"  ECC 待定模式: {'启用' if pending_mode else '禁用'}")
        except MTMLError as e:
            print(f"  ECC 模式: [不可用: {e}]")

        # 已纠正错误 (Volatile)
        try:
            corrected_vol = mtmlMemoryGetEccErrorCounter(
                memory, MTML_MEMORY_ERROR_TYPE_CORRECTED,
                MTML_VOLATILE_ECC, MTML_MEMORY_LOCATION_DRAM)
            print(f"  已纠正错误 (当前会话): {corrected_vol}")
        except MTMLError as e:
            print(f"  已纠正错误 (当前会话): [不可用: {e}]")

        # 未纠正错误 (Volatile)
        try:
            uncorrected_vol = mtmlMemoryGetEccErrorCounter(
                memory, MTML_MEMORY_ERROR_TYPE_UNCORRECTED,
                MTML_VOLATILE_ECC, MTML_MEMORY_LOCATION_DRAM)
            print(f"  未纠正错误 (当前会话): {uncorrected_vol}")
        except MTMLError as e:
            print(f"  未纠正错误 (当前会话): [不可用: {e}]")

        # 已纠正错误 (Aggregate)
        try:
            corrected_agg = mtmlMemoryGetEccErrorCounter(
                memory, MTML_MEMORY_ERROR_TYPE_CORRECTED,
                MTML_AGGREGATE_ECC, MTML_MEMORY_LOCATION_DRAM)
            print(f"  已纠正错误 (累计): {corrected_agg}")
        except MTMLError as e:
            print(f"  已纠正错误 (累计): [不可用: {e}]")

        # 未纠正错误 (Aggregate)
        try:
            uncorrected_agg = mtmlMemoryGetEccErrorCounter(
                memory, MTML_MEMORY_ERROR_TYPE_UNCORRECTED,
                MTML_AGGREGATE_ECC, MTML_MEMORY_LOCATION_DRAM)
            print(f"  未纠正错误 (累计): {uncorrected_agg}")
        except MTMLError as e:
            print(f"  未纠正错误 (累计): [不可用: {e}]")

        # 退役页面
        try:
            retired = mtmlMemoryGetRetiredPagesCount(memory)
            print(f"  退役页面 (单比特ECC): {retired.singleBitEcc}")
            print(f"  退役页面 (双比特ECC): {retired.doubleBitEcc}")
        except MTMLError as e:
            print(f"  退役页面: [不可用: {e}]")

        try:
            pending = mtmlMemoryGetRetiredPagesPendingStatus(memory)
            print(f"  退役页面挂起: {'是' if pending else '否'}")
        except MTMLError as e:
            print(f"  退役页面挂起: [不可用: {e}]")
        try:
            pages_sb = mtmlMemoryGetRetiredPages(
                memory, MTML_PAGE_RETIREMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS, 0
            )
            print("  退役页面列表 (单比特ECC):", len(pages_sb), "条")
        except MTMLError as e:
            print("  退役页面列表 (单比特ECC): [不可用]", e)
        try:
            pages_db = mtmlMemoryGetRetiredPages(
                memory, MTML_PAGE_RETIREMENT_CAUSE_DOUBLE_BIT_ECC_ERROR, 0
            )
            print("  退役页面列表 (双比特ECC):", len(pages_db), "条")
        except MTMLError as e:
            print("  退役页面列表 (双比特ECC): [不可用]", e)

mtmlLibraryShutDown()
print("\n完成!")
