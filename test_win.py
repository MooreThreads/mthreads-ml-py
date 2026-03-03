from pymtml import *

#init
mtmlLibraryInit()

#get device count
device_count = mtmlLibraryCountDevice()
print(f"Found {device_count} GPU(s)")

#query devices
for i in range(device_count):
    device = mtmlLibraryInitDeviceByIndex(i)

    #Basic info
    name = mtmlDeviceGetName(device)
    uuid = mtmlDeviceGetUUID(device)
    print(f"Device {i}: {name} (UUID: {uuid})")

    #Memory info
    with mtmlMemoryContext(device) as mem_ctx:
        total = mtmlMemoryGetTotal(mem_ctx)
        used = mtmlMemoryGetUsed(mem_ctx)
        print(f"  Memory: {used / (1024**3):.2f} GB used / {total / (1024**3):.2f} GB total")
    
    #GPU1 utilization
    with mtmlGpuContext(device) as gpu_ctx:
        utilization = mtmlGpuGetUtilization(gpu_ctx)
        temp = mtmlGpuGetTemperature(gpu_ctx)
        print(f"  GPU Utilization: {utilization}%, Temperature: {temp}°C")

#cleanup
mtmlLibraryShutDown()