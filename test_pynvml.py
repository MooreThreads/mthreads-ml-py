#!/usr/bin/env python3
"""
Test suite for pynvml-equivalent APIs in pymtml.py
Tests the NVML wrapper functions that provide compatibility with nvidia-ml-py (pynvml).

Run with: python test_pynvml.py
"""

import sys
import traceback

# Import pymtml as if it were pynvml
import pymtml as pynvml


def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_result(name, value, indent=2):
    prefix = " " * indent
    print(f"{prefix}{name}: {value}")


def test_api(name, func):
    """Run a test function and catch any errors"""
    try:
        result = func()
        print_result(name, result)
        return True, result
    except pynvml.NVMLError as e:
        print_result(name, f"[NVMLError: {e}]")
        return False, None
    except Exception as e:
        print_result(name, f"[Error: {e}]")
        return False, None


class PynvmlTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def test_library_apis(self):
        print_section("Library APIs")

        test_api("nvmlSystemGetDriverVersion", pynvml.nvmlSystemGetDriverVersion)
        test_api("nvmlDeviceGetCount", pynvml.nvmlDeviceGetCount)
        test_api(
            "nvmlSystemGetCudaDriverVersion", pynvml.nvmlSystemGetCudaDriverVersion
        )

    def test_device_handle_apis(self):
        print_section("Device Handle APIs")

        # Get handle by index
        success, handle = test_api(
            "nvmlDeviceGetHandleByIndex(0)",
            lambda: pynvml.nvmlDeviceGetHandleByIndex(0),
        )
        if not success:
            return None

        # Get UUID for testing GetHandleByUuid
        _, uuid = test_api("nvmlDeviceGetUUID", lambda: pynvml.nvmlDeviceGetUUID(handle))
        if uuid:
            test_api(
                "nvmlDeviceGetHandleByUuid",
                lambda: pynvml.nvmlDeviceGetHandleByUuid(uuid),
            )

        # Get PCI info for testing GetHandleByPciBusId
        _, pci_info = test_api(
            "nvmlDeviceGetPciInfo", lambda: pynvml.nvmlDeviceGetPciInfo(handle)
        )
        if pci_info and hasattr(pci_info, "sbdf"):
            test_api(
                "nvmlDeviceGetHandleByPciBusId",
                lambda: pynvml.nvmlDeviceGetHandleByPciBusId(pci_info.sbdf),
            )

        return handle

    def test_device_info_apis(self, device):
        print_section("Device Info APIs")

        test_api("nvmlDeviceGetIndex", lambda: pynvml.nvmlDeviceGetIndex(device))
        test_api("nvmlDeviceGetName", lambda: pynvml.nvmlDeviceGetName(device))
        test_api("nvmlDeviceGetUUID", lambda: pynvml.nvmlDeviceGetUUID(device))
        test_api("nvmlDeviceGetSerial", lambda: pynvml.nvmlDeviceGetSerial(device))
        test_api("nvmlDeviceGetBrand", lambda: pynvml.nvmlDeviceGetBrand(device))
        test_api(
            "nvmlDeviceGetVbiosVersion", lambda: pynvml.nvmlDeviceGetVbiosVersion(device)
        )
        test_api(
            "nvmlDeviceGetMinorNumber", lambda: pynvml.nvmlDeviceGetMinorNumber(device)
        )
        test_api(
            "nvmlDeviceGetNumGpuCores", lambda: pynvml.nvmlDeviceGetNumGpuCores(device)
        )

    def test_memory_apis(self, device):
        print_section("Memory APIs")

        test_api(
            "nvmlDeviceGetMemoryInfo", lambda: pynvml.nvmlDeviceGetMemoryInfo(device)
        )
        test_api(
            "nvmlDeviceGetBAR1MemoryInfo",
            lambda: pynvml.nvmlDeviceGetBAR1MemoryInfo(device),
        )
        test_api(
            "nvmlDeviceGetMemoryBusWidth",
            lambda: pynvml.nvmlDeviceGetMemoryBusWidth(device),
        )

    def test_utilization_apis(self, device):
        print_section("Utilization APIs")

        test_api(
            "nvmlDeviceGetUtilizationRates",
            lambda: pynvml.nvmlDeviceGetUtilizationRates(device),
        )
        test_api(
            "nvmlDeviceGetEncoderUtilization",
            lambda: pynvml.nvmlDeviceGetEncoderUtilization(device),
        )
        test_api(
            "nvmlDeviceGetDecoderUtilization",
            lambda: pynvml.nvmlDeviceGetDecoderUtilization(device),
        )

    def test_clock_apis(self, device):
        print_section("Clock APIs")

        test_api(
            "nvmlDeviceGetClockInfo (GRAPHICS)",
            lambda: pynvml.nvmlDeviceGetClockInfo(device, pynvml.NVML_CLOCK_GRAPHICS),
        )
        test_api(
            "nvmlDeviceGetClockInfo (SM)",
            lambda: pynvml.nvmlDeviceGetClockInfo(device, pynvml.NVML_CLOCK_SM),
        )
        test_api(
            "nvmlDeviceGetClockInfo (MEM)",
            lambda: pynvml.nvmlDeviceGetClockInfo(device, pynvml.NVML_CLOCK_MEM),
        )
        test_api(
            "nvmlDeviceGetClockInfo (VIDEO)",
            lambda: pynvml.nvmlDeviceGetClockInfo(device, pynvml.NVML_CLOCK_VIDEO),
        )
        test_api(
            "nvmlDeviceGetMaxClockInfo (GRAPHICS)",
            lambda: pynvml.nvmlDeviceGetMaxClockInfo(
                device, pynvml.NVML_CLOCK_GRAPHICS
            ),
        )
        test_api(
            "nvmlDeviceGetMaxClockInfo (SM)",
            lambda: pynvml.nvmlDeviceGetMaxClockInfo(device, pynvml.NVML_CLOCK_SM),
        )
        test_api(
            "nvmlDeviceGetMaxClockInfo (MEM)",
            lambda: pynvml.nvmlDeviceGetMaxClockInfo(device, pynvml.NVML_CLOCK_MEM),
        )

    def test_temperature_power_apis(self, device):
        print_section("Temperature & Power APIs")

        test_api(
            "nvmlDeviceGetTemperature (GPU)",
            lambda: pynvml.nvmlDeviceGetTemperature(
                device, pynvml.NVML_TEMPERATURE_GPU
            ),
        )
        test_api(
            "nvmlDeviceGetPowerUsage", lambda: pynvml.nvmlDeviceGetPowerUsage(device)
        )
        test_api(
            "nvmlDeviceGetPowerManagementLimit",
            lambda: pynvml.nvmlDeviceGetPowerManagementLimit(device),
        )

    def test_fan_apis(self, device):
        print_section("Fan APIs")

        test_api("nvmlDeviceGetFanSpeed", lambda: pynvml.nvmlDeviceGetFanSpeed(device))
        test_api(
            "nvmlDeviceGetFanSpeed_v2 (fan 0)",
            lambda: pynvml.nvmlDeviceGetFanSpeed_v2(device, 0),
        )

    def test_pci_apis(self, device):
        print_section("PCI APIs")

        test_api("nvmlDeviceGetPciInfo", lambda: pynvml.nvmlDeviceGetPciInfo(device))
        # Verify busId is populated (should be filled from sbdf if empty)
        pci_info = pynvml.nvmlDeviceGetPciInfo(device)
        if pci_info.busId and pci_info.busId[0].isalnum():
            print_result("nvmlDeviceGetPciInfo busId populated", pci_info.busId)
        else:
            print_result("nvmlDeviceGetPciInfo busId populated", "[FAIL: busId is empty or invalid]")
        test_api(
            "nvmlDeviceGetPcieThroughput (TX)",
            lambda: pynvml.nvmlDeviceGetPcieThroughput(
                device, pynvml.NVML_PCIE_UTIL_TX_BYTES
            ),
        )
        test_api(
            "nvmlDeviceGetPcieThroughput (RX)",
            lambda: pynvml.nvmlDeviceGetPcieThroughput(
                device, pynvml.NVML_PCIE_UTIL_RX_BYTES
            ),
        )

    def test_compute_apis(self, device):
        print_section("Compute APIs")

        test_api(
            "nvmlDeviceGetComputeMode", lambda: pynvml.nvmlDeviceGetComputeMode(device)
        )
        test_api(
            "nvmlDeviceGetCudaComputeCapability",
            lambda: pynvml.nvmlDeviceGetCudaComputeCapability(device),
        )
        test_api(
            "nvmlDeviceGetComputeRunningProcesses",
            lambda: pynvml.nvmlDeviceGetComputeRunningProcesses(device),
        )
        test_api(
            "nvmlDeviceGetGraphicsRunningProcesses",
            lambda: pynvml.nvmlDeviceGetGraphicsRunningProcesses(device),
        )

    def test_ecc_apis(self, device):
        print_section("ECC APIs")

        test_api("nvmlDeviceGetEccMode", lambda: pynvml.nvmlDeviceGetEccMode(device))
        test_api(
            "nvmlDeviceGetCurrentEccMode",
            lambda: pynvml.nvmlDeviceGetCurrentEccMode(device),
        )
        test_api(
            "nvmlDeviceGetPendingEccMode",
            lambda: pynvml.nvmlDeviceGetPendingEccMode(device),
        )
        test_api(
            "nvmlDeviceGetTotalEccErrors (Corrected/Volatile)",
            lambda: pynvml.nvmlDeviceGetTotalEccErrors(
                device,
                pynvml.NVML_MEMORY_ERROR_TYPE_CORRECTED,
                pynvml.NVML_VOLATILE_ECC,
            ),
        )
        test_api(
            "nvmlDeviceGetRetiredPagesPendingStatus",
            lambda: pynvml.nvmlDeviceGetRetiredPagesPendingStatus(device),
        )

    def test_mode_apis(self, device):
        print_section("Mode APIs")

        test_api(
            "nvmlDeviceGetDisplayMode", lambda: pynvml.nvmlDeviceGetDisplayMode(device)
        )
        test_api(
            "nvmlDeviceGetDisplayActive",
            lambda: pynvml.nvmlDeviceGetDisplayActive(device),
        )
        test_api(
            "nvmlDeviceGetPersistenceMode",
            lambda: pynvml.nvmlDeviceGetPersistenceMode(device),
        )
        test_api(
            "nvmlDeviceGetPerformanceState",
            lambda: pynvml.nvmlDeviceGetPerformanceState(device),
        )
        test_api(
            "nvmlDeviceGetCurrentDriverModel",
            lambda: pynvml.nvmlDeviceGetCurrentDriverModel(device),
        )

    def test_mig_apis(self, device):
        print_section("MIG APIs")

        test_api(
            "nvmlDeviceIsMigDeviceHandle",
            lambda: pynvml.nvmlDeviceIsMigDeviceHandle(device),
        )
        test_api("nvmlDeviceGetMigMode", lambda: pynvml.nvmlDeviceGetMigMode(device))
        test_api(
            "nvmlDeviceGetMaxMigDeviceCount",
            lambda: pynvml.nvmlDeviceGetMaxMigDeviceCount(device),
        )

    def test_topology_apis(self, devices):
        if len(devices) < 2:
            print_section("Topology APIs (Skipped - need 2+ devices)")
            return

        print_section("Topology APIs")
        dev1, dev2 = devices[0], devices[1]

        test_api(
            "nvmlDeviceGetP2PStatus",
            lambda: pynvml.nvmlDeviceGetP2PStatus(
                dev1, dev2, pynvml.NVML_P2P_CAPS_INDEX_READ
            ),
        )
        test_api(
            "nvmlDeviceGetTopologyCommonAncestor",
            lambda: pynvml.nvmlDeviceGetTopologyCommonAncestor(dev1, dev2),
        )

    def test_nvlink_apis(self, device):
        print_section("NVLink APIs")

        test_api(
            "nvmlDeviceGetNvLinkState (link 0)",
            lambda: pynvml.nvmlDeviceGetNvLinkState(device, 0),
        )
        test_api(
            "nvmlDeviceGetNvLinkCapability (link 0)",
            lambda: pynvml.nvmlDeviceGetNvLinkCapability(device, 0, 0),
        )
        test_api(
            "nvmlDeviceGetNvLinkRemotePciInfo (link 0)",
            lambda: pynvml.nvmlDeviceGetNvLinkRemotePciInfo(device, 0),
        )

    def test_reinit_cycle(self):
        """Test that init/shutdown/init cycle works correctly"""
        print_section("Reinit Cycle Test")

        try:
            pynvml.nvmlShutdown()
            print_result("First shutdown", "OK")

            pynvml.nvmlInit()
            print_result("Second init", "OK")

            count = pynvml.nvmlDeviceGetCount()
            print_result("Device count after reinit", count)

            return True
        except Exception as e:
            print_result("Reinit cycle", f"[Error: {e}]")
            return False

    def run_all_tests(self):
        print("\n" + "=" * 60)
        print(" pynvml-equivalent APIs Test Suite")
        print("=" * 60)

        # Test library APIs
        self.test_library_apis()

        # Get device handles
        device = self.test_device_handle_apis()
        if device is None:
            print("\nNo device available, skipping device tests")
            return

        # Collect all devices for topology tests
        device_count = pynvml.nvmlDeviceGetCount()
        devices = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(device_count)]

        # Run device tests
        self.test_device_info_apis(device)
        self.test_memory_apis(device)
        self.test_utilization_apis(device)
        self.test_clock_apis(device)
        self.test_temperature_power_apis(device)
        self.test_fan_apis(device)
        self.test_pci_apis(device)
        self.test_compute_apis(device)
        self.test_ecc_apis(device)
        self.test_mode_apis(device)
        self.test_mig_apis(device)
        self.test_nvlink_apis(device)
        self.test_topology_apis(devices)

        # Test reinit cycle
        self.test_reinit_cycle()

        print_section("Test Complete")


def main():
    try:
        # Initialize library
        print("Initializing NVML (via pymtml)...")
        pynvml.nvmlInit()

        # Run tests
        suite = PynvmlTestSuite()
        suite.run_all_tests()

    except pynvml.NVMLError as e:
        print(f"NVML Error: {e}")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Shutdown
        try:
            pynvml.nvmlShutdown()
            print("\nNVML shutdown complete.")
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())

