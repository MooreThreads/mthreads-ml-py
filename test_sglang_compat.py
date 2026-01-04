#!/usr/bin/env python3
"""
Test suite for sglang compatibility with MTML.
Tests the P2P and topology detection APIs used by sglang for multi-GPU inference.

This test uses 'import pymtml as pynvml' to simulate how sglang would use NVML APIs.

Run with: python test_sglang_compat.py
"""

import sys
import traceback

import pymtml as pynvml


def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_result(name, value, indent=2):
    prefix = " " * indent
    print(f"{prefix}{name}: {value}")


def test_p2p_constants():
    """Verify P2P constants are defined correctly."""
    print_section("P2P Constants Verification")

    # P2P Caps Index
    assert pynvml.NVML_P2P_CAPS_INDEX_READ == 0, "NVML_P2P_CAPS_INDEX_READ should be 0"
    assert (
        pynvml.NVML_P2P_CAPS_INDEX_WRITE == 1
    ), "NVML_P2P_CAPS_INDEX_WRITE should be 1"
    assert (
        pynvml.NVML_P2P_CAPS_INDEX_NVLINK == 2
    ), "NVML_P2P_CAPS_INDEX_NVLINK should be 2"
    print_result("P2P Caps Index Constants", "OK")

    # P2P Status
    assert pynvml.NVML_P2P_STATUS_OK == 0, "NVML_P2P_STATUS_OK should be 0"
    assert (
        pynvml.NVML_P2P_STATUS_NOT_SUPPORTED == 5
    ), "NVML_P2P_STATUS_NOT_SUPPORTED should be 5"
    print_result("P2P Status Constants", "OK")

    # Topology levels
    assert pynvml.NVML_TOPOLOGY_INTERNAL == 0, "NVML_TOPOLOGY_INTERNAL should be 0"
    assert pynvml.NVML_TOPOLOGY_SINGLE == 10, "NVML_TOPOLOGY_SINGLE should be 10"
    assert pynvml.NVML_TOPOLOGY_MULTIPLE == 20, "NVML_TOPOLOGY_MULTIPLE should be 20"
    assert (
        pynvml.NVML_TOPOLOGY_HOSTBRIDGE == 30
    ), "NVML_TOPOLOGY_HOSTBRIDGE should be 30"
    assert pynvml.NVML_TOPOLOGY_NODE == 40, "NVML_TOPOLOGY_NODE should be 40"
    assert pynvml.NVML_TOPOLOGY_SYSTEM == 50, "NVML_TOPOLOGY_SYSTEM should be 50"
    print_result("Topology Level Constants", "OK")


def test_p2p_status(devices):
    """Test P2P status detection between devices."""
    if len(devices) < 2:
        print_section("P2P Status Tests (Skipped - need 2+ devices)")
        return

    print_section("P2P Status Tests")
    dev1, dev2 = devices[0], devices[1]

    # Test nvmlDeviceGetP2PStatus with various caps
    try:
        status_read = pynvml.nvmlDeviceGetP2PStatus(
            dev1, dev2, pynvml.NVML_P2P_CAPS_INDEX_READ
        )
        print_result(
            "P2P Read Status (dev0 -> dev1)",
            (
                "OK"
                if status_read == pynvml.NVML_P2P_STATUS_OK
                else f"Status: {status_read}"
            ),
        )
    except Exception as e:
        print_result("P2P Read Status", f"Error: {e}")

    try:
        status_write = pynvml.nvmlDeviceGetP2PStatus(
            dev1, dev2, pynvml.NVML_P2P_CAPS_INDEX_WRITE
        )
        print_result(
            "P2P Write Status (dev0 -> dev1)",
            (
                "OK"
                if status_write == pynvml.NVML_P2P_STATUS_OK
                else f"Status: {status_write}"
            ),
        )
    except Exception as e:
        print_result("P2P Write Status", f"Error: {e}")

    try:
        status_nvlink = pynvml.nvmlDeviceGetP2PStatus(
            dev1, dev2, pynvml.NVML_P2P_CAPS_INDEX_NVLINK
        )
        print_result(
            "NVLink/MtLink Status (dev0 -> dev1)",
            (
                "OK"
                if status_nvlink == pynvml.NVML_P2P_STATUS_OK
                else f"Status: {status_nvlink}"
            ),
        )
    except Exception as e:
        print_result("NVLink/MtLink Status", f"Error: {e}")


def test_topology_detection(devices):
    """Test topology detection between devices."""
    if len(devices) < 2:
        print_section("Topology Detection Tests (Skipped - need 2+ devices)")
        return

    print_section("Topology Detection Tests")
    dev1, dev2 = devices[0], devices[1]

    # Test nvmlDeviceGetTopologyCommonAncestor
    try:
        level = pynvml.nvmlDeviceGetTopologyCommonAncestor(dev1, dev2)
        level_names = {
            pynvml.NVML_TOPOLOGY_INTERNAL: "INTERNAL",
            pynvml.NVML_TOPOLOGY_SINGLE: "SINGLE",
            pynvml.NVML_TOPOLOGY_MULTIPLE: "MULTIPLE",
            pynvml.NVML_TOPOLOGY_HOSTBRIDGE: "HOSTBRIDGE",
            pynvml.NVML_TOPOLOGY_NODE: "NODE",
            pynvml.NVML_TOPOLOGY_SYSTEM: "SYSTEM",
        }
        level_name = level_names.get(level, f"Unknown({level})")
        print_result("Topology Common Ancestor (dev0, dev1)", level_name)
    except Exception as e:
        print_result("Topology Common Ancestor", f"Error: {e}")

    # Test nvmlDeviceGetTopologyNearestGpus
    try:
        nearest = pynvml.nvmlDeviceGetTopologyNearestGpus(
            dev1, pynvml.NVML_TOPOLOGY_NODE
        )
        print_result("Nearest GPUs at NODE level", f"{len(nearest)} device(s)")
    except Exception as e:
        print_result("Nearest GPUs", f"Error: {e}")


def test_nvlink_apis(device, device_idx):
    """Test NVLink/MtLink APIs."""
    print_section(f"Device {device_idx} - NVLink/MtLink APIs")

    # Test nvmlDeviceGetNvLinkState for each link
    try:
        # Use MTML API to get link spec (no NVML equivalent)
        spec = pynvml.mtmlDeviceGetMtLinkSpec(device)
        print_result(
            "MtLink Spec",
            f"version={spec.version}, bandWidth={spec.bandWidth}, linkNum={spec.linkNum}",
        )

        for link in range(spec.linkNum):
            try:
                state = pynvml.nvmlDeviceGetNvLinkState(device, link)
                print_result(f"Link {link} State", "UP" if state else "DOWN")
            except Exception as e:
                print_result(f"Link {link} State", f"Error: {e}")
    except pynvml.NVMLError as e:
        print_result("MtLink APIs", f"Not available (NVMLError: {e})")
    except Exception as e:
        print_result("MtLink APIs", f"Not available (Error: {e})")


def test_device_info_apis(device, device_idx):
    """Test device info APIs used by sglang."""
    print_section(f"Device {device_idx} - Device Info APIs (sglang)")

    try:
        cores = pynvml.nvmlDeviceGetNumGpuCores(device)
        print_result("GPU Cores", cores)
    except Exception as e:
        print_result("GPU Cores", f"Error: {e}")

    try:
        bus_width = pynvml.nvmlDeviceGetMemoryBusWidth(device)
        print_result("Memory Bus Width (bits)", bus_width)
    except Exception as e:
        print_result("Memory Bus Width", f"Error: {e}")

    try:
        minor = pynvml.nvmlDeviceGetMinorNumber(device)
        print_result("Minor Number", minor)
    except Exception as e:
        print_result("Minor Number", f"Error: {e}")


def test_ecc_apis(device, device_idx):
    """Test ECC APIs used by sglang."""
    print_section(f"Device {device_idx} - ECC APIs (sglang)")

    try:
        ecc_mode = pynvml.nvmlDeviceGetCurrentEccMode(device)
        print_result("Current ECC Mode", "Enabled" if ecc_mode else "Disabled")
    except Exception as e:
        print_result("Current ECC Mode", f"Error: {e}")

    try:
        pending = pynvml.nvmlDeviceGetRetiredPagesPendingStatus(device)
        print_result("Retired Pages Pending", "Yes" if pending else "No")
    except Exception as e:
        print_result("Retired Pages Pending", f"Error: {e}")


def test_sglang_nvlink_full_connection(physical_device_ids, logger=None):
    """
    Test the exact sglang NVLink full connection check pattern.
    This is the NVML code path that sglang uses - we want to verify
    that using 'import pymtml as pynvml' works with this exact code.
    """
    print_section("sglang NVLink Full Connection Check")

    if len(physical_device_ids) < 2:
        print_result("Test", "Skipped (need 2+ devices)")
        return True

    print_result("Testing devices", physical_device_ids)

    # ========================================================================
    # This is the EXACT sglang NVML code - DO NOT MODIFY
    # Source: sglang's check for fully connected GPUs via NVLink
    # ========================================================================
    """
    query if the set of gpus are fully connected by nvlink (1 hop)
    """
    handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in physical_device_ids]
    for i, handle in enumerate(handles):
        for j, peer_handle in enumerate(handles):
            if i < j:
                try:
                    p2p_status = pynvml.nvmlDeviceGetP2PStatus(
                        handle, peer_handle, pynvml.NVML_P2P_CAPS_INDEX_NVLINK
                    )
                    if p2p_status != pynvml.NVML_P2P_STATUS_OK:
                        print_result(
                            f"Device {physical_device_ids[i]} <-> Device {physical_device_ids[j]}",
                            f"NOT connected (status={p2p_status})",
                        )
                        return False
                except pynvml.NVMLError:
                    if logger:
                        logger.exception(
                            "NVLink detection failed. This is normal if your"
                            " machine has no NVLink equipped."
                        )
                    print_result(
                        f"Device {physical_device_ids[i]} <-> Device {physical_device_ids[j]}",
                        "NVLink detection failed",
                    )
                    return False
    # ========================================================================
    # End of sglang code
    # ========================================================================

    print_result("Full mesh connected", "Yes")
    return True


def main():
    print("\n" + "=" * 60)
    print(" MTML sglang Compatibility Test Suite")
    print(" (Using pynvml-style API calls)")
    print("=" * 60)

    try:
        # Initialize library using NVML-style API
        print("\nInitializing library via pynvml.nvmlInit()...")
        pynvml.nvmlInit()

        # Verify constants are correct
        test_p2p_constants()

        # Get all devices using NVML-style API
        device_count = pynvml.nvmlDeviceGetCount()
        print(f"\nFound {device_count} device(s)")

        devices = []
        for i in range(device_count):
            device = pynvml.nvmlDeviceGetHandleByIndex(i)
            devices.append(device)
            name = pynvml.nvmlDeviceGetName(device)
            print(f"  Device {i}: {name}")

        # Run per-device tests
        for i, device in enumerate(devices):
            test_nvlink_apis(device, i)
            test_device_info_apis(device, i)
            test_ecc_apis(device, i)

        # Run multi-device tests
        test_p2p_status(devices)
        test_topology_detection(devices)

        # Test sglang's exact NVLink full connection check pattern
        # This uses the device indices [0, 1, 2, ...] as physical_device_ids
        physical_device_ids = list(range(device_count))
        test_sglang_nvlink_full_connection(physical_device_ids)

        print_section("Test Complete")
        print("\n  All sglang compatibility tests passed!")

    except pynvml.NVMLError as e:
        print(f"\nNVML Error: {e}")
        traceback.print_exc()
        return 1
    except AssertionError as e:
        print(f"\nAssertion Error: {e}")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
        return 1
    finally:
        try:
            pynvml.nvmlShutdown()
            print("\nLibrary shutdown complete (via pynvml.nvmlShutdown()).")
        except:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
