#!/usr/bin/env python3
"""
Comprehensive test suite for pymtml.py MTML API bindings
Run with: python test_pymtml.py
"""

import sys
import traceback
import os

from pymtml import *


def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_result(name, value, indent=2):
    prefix = " " * indent
    print(f"{prefix}{name}: {value}")


def test_error(name, func):
    """Run a test function and catch any errors"""
    try:
        result = func()
        print_result(name, result)
        return True
    except MTMLError as e:
        print_result(name, f"[MTMLError: {e}]")
        return False
    except Exception as e:
        print_result(name, f"[Error: {e}]")
        return False


class MtmlTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def test_library_apis(self):
        print_section("Library APIs")

        test_error("Library Version", mtmlLibraryGetVersion)
        test_error("Device Count", mtmlLibraryCountDevice)

        # Initialize system
        try:
            system = mtmlLibraryInitSystem()
            test_error("Driver Version", lambda: mtmlSystemGetDriverVersion(system))
            mtmlLibraryFreeSystem(system)
            print_result("Free System", "OK")
        except MTMLError as e:
            print_result("System APIs", f"[MTMLError: {e}]")

    def test_device_basic_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - Basic APIs")

        test_error("Index", lambda: mtmlDeviceGetIndex(device))
        test_error("Name", lambda: mtmlDeviceGetName(device))
        test_error("UUID", lambda: mtmlDeviceGetUUID(device))
        test_error("Brand", lambda: mtmlDeviceGetBrand(device))
        test_error("Serial Number", lambda: mtmlDeviceGetSerialNumber(device))
        test_error("Power Usage (mW)", lambda: mtmlDeviceGetPowerUsage(device))
        test_error("GPU Path", lambda: mtmlDeviceGetGpuPath(device))
        test_error("Primary Path", lambda: mtmlDeviceGetPrimaryPath(device))
        test_error("Render Path", lambda: mtmlDeviceGetRenderPath(device))
        test_error("VBIOS Version", lambda: mtmlDeviceGetVbiosVersion(device))
        test_error("MtBios Version", lambda: mtmlDeviceGetMtBiosVersion(device))
        test_error("GPU Cores Count", lambda: mtmlDeviceCountGpuCores(device))

    def test_device_pci_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - PCI APIs")

        test_error("PCI Info", lambda: mtmlDeviceGetPciInfo(device))
        # Verify busId is populated (should be filled from sbdf if empty)
        pci_info = mtmlDeviceGetPciInfo(device)
        if pci_info.busId and pci_info.busId[0].isalnum():
            print_result("PCI Info busId populated", pci_info.busId)
        else:
            print_result(
                "PCI Info busId populated", "[FAIL: busId is empty or invalid]"
            )
        test_error("PCIe Slot Info", lambda: mtmlDeviceGetPcieSlotInfo(device))

    def test_device_fan_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - Fan APIs")

        try:
            fan_count = mtmlDeviceCountFan(device)
            print_result("Fan Count", fan_count)
            for i in range(fan_count):
                test_error(
                    f"Fan {i} Speed (%)", lambda i=i: mtmlDeviceGetFanSpeed(device, i)
                )
                test_error(f"Fan {i} RPM", lambda i=i: mtmlDeviceGetFanRpm(device, i))
        except MTMLError as e:
            print_result("Fan APIs", f"[MTMLError: {e}]")

    def test_device_display_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - Display APIs")

        try:
            count = mtmlDeviceCountDisplayInterface(device)
            print_result("Display Interface Count", count)
            for i in range(count):
                test_error(
                    f"Display {i} Spec",
                    lambda i=i: mtmlDeviceGetDisplayInterfaceSpec(device, i),
                )
        except MTMLError as e:
            print_result("Display APIs", f"[MTMLError: {e}]")

    def test_device_property_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - Property APIs")
        test_error("Device Property", lambda: mtmlDeviceGetProperty(device))

    def test_gpu_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - GPU APIs")

        try:
            gpu = mtmlDeviceInitGpu(device)
            test_error("GPU Utilization (%)", lambda: mtmlGpuGetUtilization(gpu))
            test_error("GPU Temperature (C)", lambda: mtmlGpuGetTemperature(gpu))
            test_error("GPU Clock (MHz)", lambda: mtmlGpuGetClock(gpu))
            test_error("GPU Max Clock (MHz)", lambda: mtmlGpuGetMaxClock(gpu))

            # Test engine utilization
            for engine in range(MTML_GPU_ENGINE_MAX):
                engine_names = ["Geometry", "2D", "3D", "Compute"]
                test_error(
                    f"{engine_names[engine]} Engine Util (%)",
                    lambda e=engine: mtmlGpuGetEngineUtilization(gpu, e),
                )

            mtmlDeviceFreeGpu(gpu)
        except MTMLError as e:
            print_result("GPU APIs", f"[MTMLError: {e}]")

    def test_memory_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - Memory APIs")

        try:
            memory = mtmlDeviceInitMemory(device)
            test_error("Total Memory (bytes)", lambda: mtmlMemoryGetTotal(memory))
            test_error("Used Memory (bytes)", lambda: mtmlMemoryGetUsed(memory))
            test_error("System Used Memory", lambda: mtmlMemoryGetUsedSystem(memory))
            test_error(
                "Memory Utilization (%)", lambda: mtmlMemoryGetUtilization(memory)
            )
            test_error("Memory Clock (MHz)", lambda: mtmlMemoryGetClock(memory))
            test_error("Memory Max Clock (MHz)", lambda: mtmlMemoryGetMaxClock(memory))
            test_error("Memory Bus Width (bits)", lambda: mtmlMemoryGetBusWidth(memory))
            test_error(
                "Memory Bandwidth (GB/s)", lambda: mtmlMemoryGetBandwidth(memory)
            )
            test_error("Memory Speed (Mbps)", lambda: mtmlMemoryGetSpeed(memory))
            test_error("Memory Vendor", lambda: mtmlMemoryGetVendor(memory))
            test_error("Memory Type", lambda: mtmlMemoryGetType(memory))
            mtmlDeviceFreeMemory(memory)
        except MTMLError as e:
            print_result("Memory APIs", f"[MTMLError: {e}]")

    def test_vpu_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - VPU APIs")

        try:
            vpu = mtmlDeviceInitVpu(device)
            test_error("VPU Clock (MHz)", lambda: mtmlVpuGetClock(vpu))
            test_error("VPU Max Clock (MHz)", lambda: mtmlVpuGetMaxClock(vpu))
            test_error("VPU Utilization", lambda: mtmlVpuGetUtilization(vpu))
            test_error("Codec Capacity", lambda: mtmlVpuGetCodecCapacity(vpu))
            mtmlDeviceFreeVpu(vpu)
        except MTMLError as e:
            print_result("VPU APIs", f"[MTMLError: {e}]")

    def test_mtlink_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - MtLink APIs")

        test_error("MtLink Spec", lambda: mtmlDeviceGetMtLinkSpec(device))

        try:
            spec = mtmlDeviceGetMtLinkSpec(device)
            for i in range(spec.linkNum):
                test_error(
                    f"Link {i} State", lambda i=i: mtmlDeviceGetMtLinkState(device, i)
                )
                test_error(
                    f"Link {i} Remote Device",
                    lambda i=i: mtmlDeviceGetMtLinkRemoteDevice(device, i),
                )
        except MTMLError as e:
            print_result("MtLink APIs", f"[MTMLError: {e}]")

    def test_ecc_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - ECC APIs")

        try:
            memory = mtmlDeviceInitMemory(device)
            if not os.getenv("CI_MTML_SKIP_ECC") == "1":
                test_error("ECC Mode", lambda: mtmlMemoryGetEccMode(memory))
            test_error(
                "Retired Pages Count", lambda: mtmlMemoryGetRetiredPagesCount(memory)
            )
            test_error(
                "Retired Pages Pending",
                lambda: mtmlMemoryGetRetiredPagesPendingStatus(memory),
            )
            test_error(
                "ECC Corrected Errors",
                lambda: mtmlMemoryGetEccErrorCounter(
                    memory,
                    MTML_MEMORY_ERROR_TYPE_CORRECTED,
                    MTML_VOLATILE_ECC,
                    MTML_MEMORY_LOCATION_DRAM,
                ),
            )
            test_error(
                "ECC Uncorrected Errors",
                lambda: mtmlMemoryGetEccErrorCounter(
                    memory,
                    MTML_MEMORY_ERROR_TYPE_UNCORRECTED,
                    MTML_VOLATILE_ECC,
                    MTML_MEMORY_LOCATION_DRAM,
                ),
            )
            mtmlDeviceFreeMemory(memory)
        except MTMLError as e:
            print_result("ECC APIs", f"[MTMLError: {e}]")

    def test_mpc_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - MPC APIs")

        test_error("MPC Mode", lambda: mtmlDeviceGetMpcMode(device))
        test_error(
            "Supported MPC Profiles Count",
            lambda: mtmlDeviceCountSupportedMpcProfiles(device),
        )
        test_error(
            "Supported MPC Configurations Count",
            lambda: mtmlDeviceCountSupportedMpcConfigurations(device),
        )
        test_error("MPC Instances Count", lambda: mtmlDeviceCountMpcInstances(device))
        test_error(
            "Current MPC Configuration", lambda: mtmlDeviceGetMpcConfiguration(device)
        )

    def test_virtualization_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - Virtualization APIs")

        test_error(
            "Supported Virt Types Count",
            lambda: mtmlDeviceCountSupportedVirtTypes(device),
        )
        test_error(
            "Available Virt Types Count", lambda: mtmlDeviceCountAvailVirtTypes(device)
        )
        test_error(
            "Active Virt Devices Count",
            lambda: mtmlDeviceCountActiveVirtDevices(device),
        )

    def test_topology_apis(self, devices):
        if len(devices) < 2:
            print_section("Topology APIs (Skipped - need 2+ devices)")
            return

        print_section("Topology APIs")
        dev1, dev2 = devices[0], devices[1]
        test_error(
            "Topology Level (dev0, dev1)",
            lambda: mtmlDeviceGetTopologyLevel(dev1, dev2),
        )
        test_error(
            "P2P Status Read",
            lambda: mtmlDeviceGetP2PStatus(dev1, dev2, MTML_P2P_CAPS_READ),
        )
        test_error(
            "P2P Status Write",
            lambda: mtmlDeviceGetP2PStatus(dev1, dev2, MTML_P2P_CAPS_WRITE),
        )

    def test_nvml_wrapper_apis(self, device, device_idx):
        print_section(f"Device {device_idx} - NVML Wrapper APIs")

        test_error("nvmlDeviceGetIndex", lambda: nvmlDeviceGetIndex(device))
        test_error("nvmlDeviceGetName", lambda: nvmlDeviceGetName(device))
        test_error("nvmlDeviceGetUUID", lambda: nvmlDeviceGetUUID(device))
        test_error("nvmlDeviceGetPciInfo", lambda: nvmlDeviceGetPciInfo(device))
        test_error("nvmlDeviceGetSerial", lambda: nvmlDeviceGetSerial(device))
        test_error("nvmlDeviceGetMemoryInfo", lambda: nvmlDeviceGetMemoryInfo(device))
        test_error(
            "nvmlDeviceGetUtilizationRates",
            lambda: nvmlDeviceGetUtilizationRates(device),
        )
        test_error(
            "nvmlDeviceGetTemperature",
            lambda: nvmlDeviceGetTemperature(device, NVML_TEMPERATURE_GPU),
        )
        test_error("nvmlDeviceGetPowerUsage", lambda: nvmlDeviceGetPowerUsage(device))
        test_error("nvmlDeviceGetFanSpeed", lambda: nvmlDeviceGetFanSpeed(device))
        test_error(
            "nvmlDeviceGetClockInfo (Graphics)",
            lambda: nvmlDeviceGetClockInfo(device, NVML_CLOCK_GRAPHICS),
        )
        test_error(
            "nvmlDeviceGetClockInfo (Memory)",
            lambda: nvmlDeviceGetClockInfo(device, NVML_CLOCK_MEM),
        )
        test_error(
            "nvmlDeviceGetClockInfo (Video)",
            lambda: nvmlDeviceGetClockInfo(device, NVML_CLOCK_VIDEO),
        )
        test_error(
            "nvmlDeviceGetEncoderUtilization",
            lambda: nvmlDeviceGetEncoderUtilization(device),
        )
        test_error(
            "nvmlDeviceGetDecoderUtilization",
            lambda: nvmlDeviceGetDecoderUtilization(device),
        )
        test_error(
            "nvmlDeviceGetTotalEccErrors",
            lambda: nvmlDeviceGetTotalEccErrors(
                device, NVML_MEMORY_ERROR_TYPE_CORRECTED, NVML_VOLATILE_ECC
            ),
        )

    def run_all_tests(self):
        print("\n" + "=" * 60)
        print(" MTML Python Bindings Test Suite")
        print("=" * 60)

        # Test library APIs
        self.test_library_apis()

        # Get device count and test each device
        device_count = mtmlLibraryCountDevice()
        print(f"\nFound {device_count} device(s)")

        devices = []
        for i in range(device_count):
            device = mtmlLibraryInitDeviceByIndex(i)
            devices.append(device)

            self.test_device_basic_apis(device, i)
            self.test_device_pci_apis(device, i)
            self.test_device_fan_apis(device, i)
            self.test_device_display_apis(device, i)
            self.test_device_property_apis(device, i)
            self.test_gpu_apis(device, i)
            self.test_memory_apis(device, i)
            self.test_vpu_apis(device, i)
            self.test_mtlink_apis(device, i)
            self.test_ecc_apis(device, i)
            self.test_mpc_apis(device, i)
            self.test_virtualization_apis(device, i)
            self.test_nvml_wrapper_apis(device, i)

        # Multi-device tests
        self.test_topology_apis(devices)

        # Note: Don't free devices here - they will be freed when library shuts down
        # Calling mtmlLibraryFreeDevice causes segfault in some driver versions

        print_section("Test Complete")


def test_init_shutdown_cycle():
    """Test that library can be initialized and shutdown multiple times."""
    print_section("Init/Shutdown Cycle Test")

    for i in range(3):
        print(f"  Cycle {i + 1}: Init...")
        mtmlLibraryInit()
        count = mtmlLibraryCountDevice()
        print(f"  Cycle {i + 1}: Device count = {count}")
        print(f"  Cycle {i + 1}: Shutdown...")
        mtmlLibraryShutDown()

    print("  Init/Shutdown cycle test: PASSED")


def main():
    try:
        # Initialize MTML library
        print("Initializing MTML library...")
        mtmlLibraryInit()

        # Run tests
        suite = MtmlTestSuite()
        suite.run_all_tests()

    except MTMLError as e:
        print(f"MTML Error: {e}")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Shutdown
        try:
            mtmlLibraryShutDown()
            print("\nMTML library shutdown complete.")
        except:
            pass

    # Test init/shutdown cycle (after main tests complete)
    try:
        test_init_shutdown_cycle()
    except Exception as e:
        print(f"Init/Shutdown cycle test FAILED: {e}")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
