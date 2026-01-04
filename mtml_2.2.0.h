/**
 * Copyright ©2020-2022 Moore Threads Technology Co., Ltd ("Moore Threads"). All rights reserved.
 *
 * This software ("this software and its documentations" or "the software") is
 * protected by Copyright and the information contained herein is confidential.
 *
 * The software contained herein is PROPRIETARY to Moore Threads and is being provided under the terms and 
 * conditions of a form of Moore Threads software license agreement by and
 * between Moore Threads and Licensee ("License Agreement") or electronically
 * accepted by Licensee. Notwithstanding any terms or conditions to
 * the contrary in the License Agreement, copy or disclosure
 * of the software to any third party without the express
 * written consent of Moore Threads is prohibited.
 *
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, MOORE THREADS MAKES NO REPRESENTATION ABOUT ANY WARRANTIES, INCLUDING BUT NOT LIMITED TO THE
 * SUITABILITY OF THE SOFTWARE FOR ANY PURPOSE. IT IS
 * PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
 * MOORE THREADS DISCLAIMS ALL WARRANTIES WITH REGARD TO THE
 * SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
 * NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, IN NO EVENT SHALL MOORE THREADS BE LIABLE FOR ANY
 * SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
 * WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
 * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THE SOFTWARE.
 **/

#ifndef MTML_H_
#define MTML_H_

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_MSC_VER)
    #ifdef MTML_EXPORT
        #define MTML_API __declspec(dllexport)
    #else
        #define MTML_API __declspec(dllimport)
    #endif
#else
    #define MTML_API __attribute__ ((visibility ("default")))
#endif

#if defined (__GNUC__)
    #define MTML_DEPRECATED(msg) __attribute__ ((deprecated(msg)))
#elif defined(_MSC_VER)
    #define MTML_DEPRECATED(msg) __declspec(deprecated(msg))
#else
    #define MTML_DEPRECATED(msg)
#endif

/** 
 * @mainpage notitle
 * 
 * @section desc Basic concepts
 *
 * @subsection supported_platforms Supported platforms
 * <table style="margin-left:10px;">
 * <tr><th>CPU architecture<th>OS
 * <tr><td>x86_64<td>Ubuntu 20.04, UOS 20, Kylin V10, and Windows 10 Pro 21H2
 * <tr><td>AArch64<td>Kylin V10 SP1
 * </table>
 * 
 * @subsection opaque Opaque data types
 * The MTML library works with several core opaque data types. Each data type represents a specific functional entity that a user can interact with. 
 * Most functions defined below take one or more opaque objects as its input parameters. Therefore, it is important for a
 * user to have a good understanding of them.
 * - \b MtmlLibrary represents the MTML library itself and plays as the entry point to access and create other opaque objects.
 * - \b MtmlSystem represents the system environment in which the library is running.
 * - \b MtmlDevice represents the Moore Threads device (including virtual devices) that is installed in the system. 
 * - \b MtmlGpu represents the graphic unit of a Moore Threads device, which is responsible for the 3D and compute workloads.
 * - \b MtmlMemory represents the memory units that reside on a Moore Threads device.
 * - \b MtmlVpu represents the video codec unit of a Moore Threads device which handles the video encoding and decoding task.
 * 
 * The relationship among the above opaque data types is hierarchical, which means some type 'contains' other types. The hierarchy of opaque data types 
 * mentioned above can be summarized as follows. \n
 \verbatim
 Library 
    |--- System 
    |--- Device 
           |--- GPU
           |--- Memory
           |--- VPU
 \endverbatim
 * 
 * 
 * @subsection init Initialization and freeing
 * It is important to properly initialize an opaque object before using it as an argument to invoke other functions. The hierarchical 
 * relationships among opaque data types determine the initialization order of them. For example, to initialize an MtmlGpu struct, a user should 
 * firstly initialize a MtmlLibrary struct, then initialize the MtmlDevice struct from the MtmlLibrary, and finally initialize the MtmlGpu
 * struct from the MtmlDevice struct.
 * 
 * Initialization of an opaque object is accomplished by calling an mtml***Init***() function. If opaque object1 and object2 point to the same resource,
 * the expression (object1 == object2) will always evaluate to true.
 * 
 * 
 * @subsection virtualization Virtualization
 * It is recommended to build some fundamental concepts before using the device virtualization management feature provided by the MTML library.
 * There are two major functionalities with regards to the virtualization feature: virtualization type management and virtual device management. 
 * More specifically, several concepts shall be introduced:
 * - \b Virtualizability - This is a concept used to describe whether a physical device supports virtualization. Therefore, a virtualizable device is
 * defined as a physical device from which virtual resources can be created.
 * - \b Virtualization \b Type - A virtualization type is a specification template that confines virtual resource (for example, device memory) allocation. 
 * Typically, a virtualizable device supports several virtualization types, therefore virtual devices (see below) with corresponding specifications can 
 * be created.
 * - \b Virtual \b Device - A virtual device is created from a virtualizable device according to a specified virtualization type. It is key to
 * remember that a virtual device is a a host-only concept. That means you can initialize an MtmlDevice opaque object that represents a virtual device
 * only if the MTML library is running in a virtualization-enabled host environment. 
 * 
 * 
 * @subsection codec Codec session
 * A codec session is an independent encoding/decoding process of a video stream. The concurrent codec sessions number that can be supported by 
 * the video codec unit of a Moore Threads device is called \b codec \b capacity. The \b decodeCapacity and \b encodeCapacity represent 
 * the maximum limit of concurrent decoder sessions and encoder sessions, respectively.
 * 
 * Each codec session is identifiable from a unique integral value, called \b session \b ID. For decoder sessions, the session ID ranges
 * from \b 0 ~ \b (decodeCapacity-1), while it ranges from \b 0 ~ \b (encodeCapacity-1) for encoder sessions.
 * 
 * Another important aspect of a codec session is its \b state. The definition of the state of a codec session is as follows:
 * - \b Inactive \b (Idle): There is no video workload assigned to this session.
 * - \b Active: A video encoding/decoding workload is assigned to this session.
 * At any given time point, the state of a codec session can be queried. If a codec session is in an active state, its metrics information
 * then can be queried.
 * 
 * Refer to the videoMonApp() sample in sample/basic/basic_sample.cpp for a workable sample code.
 * 
 * 
 * @subsection mpc Multiple Primary Core (MPC)
 * MPC, short for Multiple Primary Core, is a Moore Threads proprietary GPU hardware virtualization technology that supports dividing a single powerful GPU device into
 * multiple less powerful GPU devices with physical resource isolation capability. 
 * In simple terms, when MPC is enabled on a device, multiple devices known as \b MPC \b instances exist in the system, 
 * even though only a single physical device is installed. Each MPC instance owns a portion of the GPU core and video memory resources of the physical device. 
 * These instances can be used independently, providing the functionality as if multiple physical devices are installed. To manage the MPC instances, a mimic
 * device known as the \b MPC \b parent is introduced for each MPC-enabled physical device. The MPC parent serves as the control for MPC functions and acts 
 * as a global level management access point.
 * In a system with a single MPC-capable physical device, if MPC is enabled, there will be N+1 devices accessible through mtml APIs. 
 * This includes N MPC instance devices and 1 MPC parent device, due to the reasons mentioned earlier.
 * 
 * The number of MPC parent devices remains fixed, but the number of MPC instances can be configured according to user requirements. 
 * To determine the maximum number of MPC instances that can be created from a single physical device, it is necessary to understand 
 * the concepts of \b MPC \b profile and \b MPC \b configuration.
 * 
 * \b MPC \b profiles define the resource allocation schema for MPC instance devices. Therefore, MPC instances created based on the same MPC profile will have the same resources
 * assigned to them. The most significant attributes defined by the MPC profie are the allocated amount of GPU core and memory (VRAM). These attributes are directly reflected in 
 * the name of the MPC profie.
 * 
 * For example, an MPC profile named '4c+8gb' indicates that an MPC instance created using this profile will be allocated with 4 GPU cores and 8 GB of video memory. 
 * Typically, an MPC-capable physical device supports a range of MPC profiles that can be used to define the characteristics of MPC instances. 
 * The available MPC profiles may vary among different models of physical devices.
 * 
 * Since the total amount of resources available on a physical device remains constant, it is crucial to select an appropriate scheme to divide those resources among MPC 
 * instances to ensure that no resources are left unused.
 * 
 * This is where \b MPC \b configuration comes into play. An MPC configuration is a combination of MPC profiles that can be applied to a specific MPC-capable physical device to create MPC instances. 
 * Multiple MPC configurations are pre-set to cover all possible resource division plans supported by a specific MPC-capable physical device.
 * 
 * For example, let's consider an MPC-capable physical device that has 8 GPU cores and 32 GB of video memory. The supported MPC profiles for this device are as follows:
 * MPC profile name         Description
 * 8c+32gb                  Specifies an MPC instance with 8 GPU cores and 32 GB of video memory.
 * 4c+16gb                  Specifies an MPC instance with 4 GPU cores and 16 GBof  video memory.
 * 2c+8gb                   Specifies an MPC instance with 2 GPU cores and 8 GB of video memory.
 * 1c+4gb                   Specifies an MPC instance with 1 GPU core and 4 GB of video memory.
 * 
 * The supported MPC configurations are as follows:
 * MPC configuration name       MPC profiles contained                  Description
 * 8-8                          8c+32gb                                 Includes a single MPC instance with 8 GPU cores and 32 GB of video memory.
 * 8-44                         (4c+16gb)*2                             Includes two MPC instances, each with 4 GPU cores and 16 GB of video memory.
 * 8-422                        4c+16gb, (2c+8gb)*2                     Includes one MPC instance with 4 GPU cores and 16 GB of video memory, along with two MPC instances, each with 2 GPU cores and 8 GB of video memory.
 * 8-4211                       4c+16gb, 2c+8gb, (1c+4gb)*2             Includes one MPC instance with 4 GPU cores and 16 GB of video memory, one MPC instance with 2 GPU cores and 8 GB of video memory, and two MPC instances, each with 1 GPU core and 4 GB of video memory.
 * 8-41111                      4c+16gb, (1c+4gb)*4                     Includes one MPC instance with 4 GPU cores and 16 GB of video memory, along with four MPC instances, each with 1 GPU core and 4 GB of video memory.
 * 8-2222                       (2c+8gb)*4                              Includes four MPC instances, each with 2 GPU cores and 8 GB of video memory.
 * 8-22211                      (2c+8gb)*3, (1c+4gb)*2                  Includes three MPC instances, each with 2 GPU cores and 8 GB of video memory, along with two MPC instances, each with 1 GPU core and 4 GB of video memory.
 * 8-221111                     (2c+8gb)*2, (1c+4gb)*4                  Includes two MPC instances, each with 2 GPU cores and 8 GB of video memory, along with four MPC instances, each with 1 GPU core and 4 GB of video memory.
 * 8-2111111                    2c+8gb, (1c+4gb)*6                      Includes one MPC instance with 2 GPU cores and 8 GB of video memory, along with six MPC instances, each with 1 GPU core and 4 GB of video memory.
 * 8-11111111                   (1c+4gb)*8                              Includes eight MPC instances, each with 1 GPU core and 4 GB of video memory.
 * 
 * By default, MPC-capable GPU devices are in a disabled state when the system boots up or when the device driver is re-installed. 
 * In this disabled state, the devices can be used as regular GPU devices without MPC functionality. If the installed driver supports MPC, 
 * the MPC feature can be enabled on these devices using the libmtml API or the mthreads-gmi utility. Once MPC is enabled on a physical device, 
 * there will be only one MPC instance created by default, which will have access to all the resources of that physical device, except for the MPC parent device. 
 * In the example mentioned earlier, the only MPC instance created would be based on the 8c+32gb MPC profile, indicating that the default MPC Configuration applied is 8-8.
 * 
 * Enabling or disabling the feature and modifying the MPC configuration on an MPC-capable device can lead to changes in the device numbering within the system.
 * These changes in device numbering affect the device enumeration and ordering logic used by libmtml. As a consequence, after performing these operations,  
 * it is necessary to re-initialize libmtml by shutting it down and then initializing it again. This re-initialization ensures that libmtml functions correctly with 
 * the updated set of devices. 
 * The documentation of the related MTML APIs contains important instructions that users should carefully consider when using them.
 */

/***************************************************************************************************/
/** @defgroup mtml1 Constant Definitions
 * This group introduces constant definitions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the MTML library version string (including a null terminator).
 */
#define MTML_LIBRARY_VERSION_BUFFER_SIZE            32

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the driver version string (including a null terminator).
 */
#define MTML_DRIVER_VERSION_BUFFER_SIZE             80

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the device name string (including a null terminator).
 */
#define MTML_DEVICE_NAME_BUFFER_SIZE                32

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the UUID string of a device (including a null terminator).
 */
#define MTML_DEVICE_UUID_BUFFER_SIZE                48

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the MTBIOS version string (including a null terminator).
 */
#define MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE      64

/**
 * @deprecated Renamed to \ref MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE
 */
#define MTML_DEVICE_VBIOS_VERSION_BUFFER_SIZE       MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE

/**
 *Recommended buffer size in bytes that is guaranteed to be enough to hold the device path string (including a null terminator).
 */
#define MTML_DEVICE_PATH_BUFFER_SIZE                64

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the PCI SBDF string of a device (including a null terminator).
 */
#define MTML_DEVICE_PCI_SBDF_BUFFER_SIZE            32

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the ID string of a virtualization type (including a null terminator).
 */
#define MTML_VIRT_TYPE_ID_BUFFER_SIZE               16

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the class string of a virtualization type (including a null terminator).
 */
#define MTML_VIRT_TYPE_CLASS_BUFFER_SIZE            32

 /**
  * Recommended buffer size in bytes that is guaranteed to be enough to hold the name string of a virtualization type (including a null terminator).
  */
#define MTML_VIRT_TYPE_NAME_BUFFER_SIZE             32

 /**
  * Recommended buffer size in bytes that is guaranteed to be enough to hold the API string of a virtualization type (including a null terminator).
  */
#define MTML_VIRT_TYPE_API_BUFFER_SIZE              16

/**
 * Format string for PCI BUS ID.
 */
#define MTML_DEVICE_PCI_BUS_ID_FMT                  "%08X:%02X:%02X.0"

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the the name string of a filepath (including a null terminator).
 */
#define MTML_LOG_FILE_PATH_BUFFER_SIZE              200 

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the name string of a profile name (including a null terminator).
 */
#define MTML_MPC_PROFILE_NAME_BUFFER_SIZE           32

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the name string of a configuration name (including a null terminator).
 */
#define MTML_MPC_CONF_NAME_BUFFER_SIZE              32

/**
 * Indicates the maximum number of profiles that can be accommodated in the current configuration.
 */
#define MTML_MPC_CONF_MAX_PROF_NUM                  16

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the name string of a device slot name (including a null terminator).
 */
#define MTML_DEVICE_SLOT_NAME_BUFFER_SIZE           32

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the name string of a memory vendor (including a null terminator).
 */
#define MTML_MEMORY_VENDOR_BUFFER_SIZE              64

/**
 * Recommended buffer size in bytes that is guaranteed to be enough to hold the name string of a device serial number (including a null terminator).
 */
#define MTML_DEVICE_SERIAL_NUMBER_BUFFER_SIZE       64

/** 
 * Return values for MTML API calls. 
 */
typedef enum {
    MTML_SUCCESS = 0,               //!< The operation was successful.
    MTML_ERROR_DRIVER_NOT_LOADED,   //!< The Moore Threads driver is not loaded.
    MTML_ERROR_DRIVER_FAILURE,      //!< Access to the driver failed.
    MTML_ERROR_INVALID_ARGUMENT,    //!< One or more supplied arguments are invalid.
    MTML_ERROR_NOT_SUPPORTED,       //!< The requested operation is not available on the target device.
    MTML_ERROR_NO_PERMISSION,       //!< The current user does not have permission to operate.
    MTML_ERROR_INSUFFICIENT_SIZE,   //!< The space allocated by the user is insufficient to hold the requested data.
    MTML_ERROR_NOT_FOUND,           //!< A query to find a resource was unsuccessful.
    MTML_ERROR_INSUFFICIENT_MEMORY, //!< There is not enough system memory to finish the operation.
    MTML_ERROR_DRIVER_TOO_OLD,      //!< An operation is failed due to the installed driver is too old.
    MTML_ERROR_DRIVER_TOO_NEW,      //!< An operation is failed due to the installed driver is too new.
    MTML_ERROR_TIMEOUT,             //!< User provided timeout passed.
    MTML_ERROR_RESOURCE_IS_BUSY,    //!< Current start is invalid and ignored.
    MTML_ERROR_UNKNOWN = 999        //!< An internal unspecified error occurred.
} MtmlReturn;

/**
 * The brand of the device.
 */
typedef enum {
    MTML_BRAND_MTT = 0,         //!< MTT series.
    MTML_BRAND_UNKNOWN,         //!< An unknown brand.

    // Keep this on the last line.
    MTML_BRAND_COUNT            //!< The number of brands.
} MtmlBrandType;

/** 
 * The memory types.
 */
typedef enum {
    MTML_MEM_TYPE_LPDDR4,
    MTML_MEM_TYPE_GDDR6,
} MtmlMemoryType;

/**
 * The video codec types.
 */
typedef enum {
    MTML_CODEC_TYPE_AVC   = 0,
    MTML_CODEC_TYPE_VC1   = 1,
    MTML_CODEC_TYPE_MPEG2 = 2,
    MTML_CODEC_TYPE_MPEG4 = 3,
    MTML_CODEC_TYPE_H263  = 4,
    MTML_CODEC_TYPE_DIV3  = 5,
    MTML_CODEC_TYPE_RV    = 6,
    MTML_CODEC_TYPE_AVS   = 7,
    MTML_CODEC_TYPE_RSVD1 = 8,  //!< Invalid value.
    MTML_CODEC_TYPE_THO   = 9,
    MTML_CODEC_TYPE_VP3   = 10,
    MTML_CODEC_TYPE_VP8   = 11,
    MTML_CODEC_TYPE_HEVC  = 12,
    MTML_CODEC_TYPE_VP9   = 13,
    MTML_CODEC_TYPE_AVS2  = 14,
    MTML_CODEC_TYPE_RSVD2 = 15, //!< Invalid value.
    MTML_CODEC_TYPE_AV1   = 16,

    // Keep this on the last line.
    MTML_CODEC_TYPE_COUNT
} MtmlCodecType;

/**
 * The video codec session states.
 */
typedef enum {
    MTML_CODEC_SESSION_STATE_UNKNOWN    = -1,
    MTML_CODEC_SESSION_STATE_IDLE       = 0,
    MTML_CODEC_SESSION_STATE_ACTIVE,

    // Keep this on the last line.
    MTML_CODEC_SESSION_STATE_COUNT
} MtmlCodecSessionState;

/**
 * Virtualization capabilities.
 */
typedef enum {
    MTML_DEVICE_NOT_SUPPORT_VIRTUALIZATION = 0,         //!< The device does not support virtualization.
    MTML_DEVICE_SUPPORT_VIRTUALIZATION                  //!< The device supports virtualization.
} MtmlVirtCapability;

/**
 * The role of a virtualized device.
 */
typedef enum {
    MTML_VIRT_ROLE_NONE,                    //!< The device is not a virtual device or its virtualization role is unknown.
    MTML_VIRT_ROLE_HOST_VIRTDEVICE,         //!< The device is a virtual device that visible on the host operating system
    MTML_VIRT_ROLE_GUEST_VIRTDEVICE,         //!< The device is a virtual device that visible on the guest operating system
                                            //!< type of a physical device. This role is only reported in the host OS.

    // Keep this on the last line.
    MTML_VIRT_ROLE_COUNT,                   //!< The number of virtualization roles.
} MtmlVirtRole;

typedef enum {
    MTML_TOPOLOGY_INTERNAL = 0,     //!< Topology path that is created internally, for example 2 devices on a single S2000 card.
    MTML_TOPOLOGY_SINGLE = 1,       //!< Topology path that contains at most one PCIe switch/bridge.
    MTML_TOPOLOGY_MULTIPLE = 2,     //!< Topology path that contains multiple PCIe switches/bridges (but no host bridge).
    MTML_TOPOLOGY_HOSTBRIDGE = 3,   //!< Topology path that contains PCIe switches/bridges as well as a single host bridge.
    MTML_TOPOLOGY_NODE = 4,         //!< Topology path that contains PCIe switches/bridges as well as multiple host bridges within a NUMA node.
    MTML_TOPOLOGY_SYSTEM = 5,       //!< Topology path that contains PCIe switches/bridges as well as multiple host bridges across NUMA nodes.
} MtmlDeviceTopologyLevel;

/**
 * All supported log levels.
 */
typedef enum {
    MTML_LOG_LEVEL_OFF = 0,    //!< Logs at all level is disable.
    MTML_LOG_LEVEL_FATAL,      //!< Very severe error event that will presumably lead the application to abort.
    MTML_LOG_LEVEL_ERROR,      //!< Error information but will continue application to keep running.
    MTML_LOG_LEVEL_WARNING,    //!< Information representing errors in application but application will keep running.
    MTML_LOG_LEVEL_INFO,       //!< Mainly useful to represent current progress of application.
} MtmlLogLevel;

/**
 * MPC mode.
 */
typedef enum {
    MTML_DEVICE_MPC_DISABLE = 0,  //!< Disables Multi Primary Core mode.
    MTML_DEVICE_MPC_ENABLE        //!< Enables Multi Primary Core mode.
} MtmlMpcMode;

/**
 * MPC capability.
 */
typedef enum {
    MTML_DEVICE_NOT_SUPPORT_MPC = 0,    //!< The device has no MPC capability.
    MTML_DEVICE_SUPPORT_MPC             //!< The device has MPC capability.
} MtmlMpcCapability;

/**
 * The role of a mpc device.
 */
typedef enum {
    MTML_MPC_TYPE_NONE,        //!< Device that does not support or has disabled the MPC feature.
    MTML_MPC_TYPE_PARENT,      //!< Device from which MPC instances can be created.
    MTML_MPC_TYPE_INSTANCE,    //!< MPC instance device.
} MtmlMpcType;
 
/***********************************/
/** @}
 */
/***********************************/



/***************************************************************************************************/
/** @defgroup mtml2 Functional Structure Definitions
 * This group introduces functional structures.
 *  @{
 */
/***************************************************************************************************/

/**
 * PCI information about a device.
 */
typedef struct {
    char sbdf[MTML_DEVICE_PCI_SBDF_BUFFER_SIZE];       //!< The tuple segment:bus:device.function PCI identifier (&amp; NULL terminator).
    unsigned int segment;                              //!< The PCI segment group(domain) on which the device's bus resides, 0 to 0xffffffff.
    unsigned int bus;                                  //!< The bus on which the device resides, 0 to 0xff.
    unsigned int device;                               //!< The device ID on the bus, 0 to 31.
    unsigned int pciDeviceId;                          //!< The combined 16-bit device ID and 16-bit vendor ID.
    unsigned int pciSubsystemId;                       //!< The 32-bit sub system device ID.
    unsigned int busWidth;                             //!< @deprecated This value set to zero.
    float pciMaxSpeed;                                 //!< The maximum link speed (transfer rate per lane) of the device. The unit is GT/s.
    float pciCurSpeed;                                 //!< The current link speed (transfer rate per lane) of the device. The unit is GT/s.
    unsigned int pciMaxWidth;                          //!< The maximum link width of the device.
    unsigned int pciCurWidth;                          //!< The current link width of the device.
    unsigned int pciMaxGen;                            //!< The maximum supported generation of the device.
    unsigned int pciCurGen;                            //!< The current generation of the device.
    int rsvd[6];                                       //!< Reserved for future extension.
} MtmlPciInfo;

/**
 * PCI slot information about a device.
 */
typedef struct {
    unsigned int slotId;                                                //!< The unique ID of the PCI slot.
    char         slotName[MTML_DEVICE_SLOT_NAME_BUFFER_SIZE];           //!< The name of the PCI slot.
    unsigned int rsvd[4];                                               //!< Reserved for future extension.
} MtmlPciSlotInfo;

/** 
 * Codec utilization percentage on a device.
 */
typedef struct {
    unsigned int util;              //!< The codec's overall utilization rate over the sampling period.
    unsigned int period;            //!< The sampling period of time, in microseconds.
    unsigned int encUtil;           //!< The encoder utilization rate over the sampling period.
    unsigned int decUtil;           //!< The decoder utilization rate over the sampling period.
    int rsvd[2];                    //!< Reserved for future extension.
} MtmlCodecUtil;

/** 
 * Codec session metrics.
 */
typedef struct {
    unsigned int id;            //!< The unique identifier of the code session.
    unsigned int pid;           //!< The process ID. 0 represents an idle session, otherwise the session is considered active.
    unsigned int hResolution;   //!< The horizontal resolution in pixels. 
                                //!< This refers to the coded size, which may differ from the storage size displayed in video applications like FFmpeg.
    unsigned int vResolution;   //!< The vertical resolution in pixels.
                                //!< This refers to the coded size, which may differ from the storage size displayed in video applications like FFmpeg.
    unsigned int frameRate;     //!< The number of frames per second.
    unsigned int bitRate;       //!< The number of bits per second.
    unsigned int latency;       //!< The codec latency in microseconds.
    MtmlCodecType codecType;    //!< Type of codec. For example, H.265 and AV1.
    int rsvd[4];                //!< Reserved for future extension.
} MtmlCodecSessionMetrics;

/**
 * The type of virtualization that describes the specification of a virtualized device.
 */
typedef struct {
    char id[MTML_VIRT_TYPE_ID_BUFFER_SIZE];         //!< The ID of the virtualization type. For example, mtgpu-2008.
    char name[MTML_VIRT_TYPE_NAME_BUFFER_SIZE];     //!< The name of the virtualization type. For example, mtgpu-8g.
    char api[MTML_VIRT_TYPE_API_BUFFER_SIZE];       //!< The API type of the virtualization type. For example, vfio-pci.
    unsigned int horizontalResolution;              //!< The maximum number of pixels in the X dimension.
    unsigned int verticalResolution;                //!< The maximum number of pixels in the Y dimension.
    unsigned int frameBuffer;                       //!< The frame buffer size in megabytes.
    unsigned int maxEncodeNum;                      //!< The maximum number of encode.
    unsigned int maxDecodeNum;                      //!< The maximum number of decode.
    unsigned int maxInstances;                      //!< The maximum number of vGPU instances per physical GPU.
    unsigned int maxVirtualDisplay;                 //!< The number of display heads.
    int rsvd[11];                                   //!< Reserved for future extension.
} MtmlVirtType;

/**
 * The property of a device.
 *
 * NOTE:
 * A physical device that does not support virtualization (for example, S10) might still be able to be used in pass-through manner.
 * For such device, its 'virtCap' field is '0 - non-virtualizable'.
 */
typedef struct {
    unsigned int virtCap : 1;       //!< This field indicates the virtualization capability of a device (whether a device supports to be 
                                    //!< virtualized) : 0 indicates non-virtualizable and 1 indicates virtualizable. Refer to \ref MtmlVirtCapability.
    unsigned int virtRole : 3;      //!< This field indicates the role that this device is playing in a virtualization-supported 
                                    //!< environment. Refer to \ref MtmlVirtRole.
    unsigned int mpcCap : 1;        //!< This field indicates whether this device has MPC capability. 
                                    //!< 0 indicates not having MPC capability, and 1 indicates having MPC capability. Refer to \ref MtmlMpcCapability.
    unsigned int mpcType : 3;       //!< This field indicates this device's MPC type.
                                    //!< 0 indicates non-MPC type, 1 indicates MPC parent type, and 2 indicates MPC instance type. Refer to \ref MtmlMpcType.
    unsigned int mtLinkCap : 1;     //!< This field indicates whether this device has MtLink capability.
                                    //!< 0 indicates not supporting MtLink capability, and 1 indicates supporting MtLink capability. Refer to \ref MtmlMtLinkCapability.
    unsigned int rsvd : 23;         //!< Reserved for future extension.
    unsigned int rsvd2 : 32;        //!< Reserved for future extension.
} MtmlDeviceProperty;

/**
 * Configuration for the MTML logger.
 */
typedef struct {
    struct {
        MtmlLogLevel level;                             //!< Configures the level of logger.
        int rsvd[2];                                    //!< Reserved for future extensions.
    } consoleConfig;                                    //!< Logs are output to stdout.
    struct {
        MtmlLogLevel level;                             //!< Configures the level of logger.
        int rsvd[2];                                    //!< Reserved for future extensions.
    } systemConfig;                                     //!< Logs are output to syslog, which is supported only for Linux.
    struct {
        MtmlLogLevel level;                             //!< Configures the level of logger.
        char file[MTML_LOG_FILE_PATH_BUFFER_SIZE];      //!< Sets the file for log output. MTML will keep the file open if this field is set to a valid path.
                                                        //!< Sets it to an empty string in case a previously opened file needs to be closed.
        unsigned int size;                              //!< Sets max log size in file, which will be clean when it over size.
        int rsvd[2];                                    //!< Reserved for future extensions.
    } fileConfig;                                       //!< Logs are output to a user-specified file.
    struct {
        MtmlLogLevel level;                             //!< Configures the level of logger.
        void (*callback)(const char*, unsigned int);    //!< Callback will acquire all logs.
        int rsvd[2];                                    //!< Reserved for future extensions.
    } callbackConfig;                                   //!< Logs are output to a user-specified callback.
    int rsvd[8];                                        //!< Reserved for future extensions.
} MtmlLogConfiguration;

/* P2P capability status.*/
typedef enum {
    MTML_P2P_STATUS_OK = 0,
    MTML_P2P_STATUS_CHIPSET_NOT_SUPPORTED,
    MTML_P2P_STATUS_GPU_NOT_SUPPORTED,
    MTML_P2P_STATUS_UNKNOWN
} MtmlDeviceP2PStatus;

/* P2P capability. */
typedef enum {
    MTML_P2P_CAPS_READ = 0,
    MTML_P2P_CAPS_WRITE
} MtmlDeviceP2PCaps;

/**
 * MPC instance profile information.
 */
typedef struct
{
    unsigned int id;                             //!< Profile ID within the device.
    unsigned int coreCount;                      //!< MPC core count.
    unsigned long long memorySizeMB;             //!< Memory size in MBytes.
    char name[MTML_MPC_PROFILE_NAME_BUFFER_SIZE];//!< Profile name.
    unsigned int rsvd[10];
} MtmlMpcProfile;

/**
 * MPC device configuration information.
 */
typedef struct
{
    unsigned int id;                          //!< Configuration id within the device.
    char name[MTML_MPC_CONF_NAME_BUFFER_SIZE];//!< Configuration name.
    int profileId[MTML_MPC_CONF_MAX_PROF_NUM];//!< Profile IDs are included in the configuration ID. Use -1 to distinguish. For example, 4111-4-1-1-1.
                                              //!< indicates that current configuration consists of one profile ID 4 and three profile ID 1.
    unsigned int rsvd[24];
} MtmlMpcConfiguration;

/**
 * Specifications for an MtLink connection.
 */
typedef struct {
    unsigned int version;                     //!< Version of MtLink, combining major, minor, and patch components.
                                              //!< Version calculation: version = 10000 * major + 100 * minor + patch.
    unsigned int bandWidth;                   //!< Bandwidth per link in GB/s.
    unsigned int linkNum;                     //!< Maximum number of supported links.
    unsigned int rsvd[4];                     //!< Reserved for future extensions.
} MtmlMtLinkSpec;

/**
 * Possible states of an MtLink connection.
 */
typedef enum {
    MTML_MTLINK_STATE_DOWN = 0,               //!< The link is inactive.
    MTML_MTLINK_STATE_UP,                     //!< The link is active.
    MTML_MTLINK_STATE_DOWNGRADE               //!< The link is downgrade.
} MtmlMtLinkState;

/**
 * Capabilities of an MtLink connection.
 */
typedef enum {
    MTML_MTLINK_CAP_P2P_ACCESS = 0,           //!< Peer-to-peer device access.
    MTML_MTLINK_CAP_P2P_ATOMICS,              //!< Support for P2P atomics.

    MTML_MTLINK_CAP_COUNT
} MtmlMtLinkCap;

/**
 * Status of an MtLink capability.
 */
typedef enum {
    MTML_MTLINK_CAP_STATUS_NOT_SUPPORTED = 0,
    MTML_MTLINK_CAP_STATUS_OK
} MtmlMtLinkCapStatus;

/**
 * Information about the layout of an MtLink connection.
 */
typedef struct {
    unsigned int localLinkId;
    unsigned int remoteLinkId;
    unsigned int rsvd[4];
} MtmlMtLinkLayout;

/**
 * MtLink capability of a device.
 */
typedef enum {
    MTML_DEVICE_NOT_SUPPORT_MTLINK = 0,    //!< The device does not support MtLink capability.
    MTML_DEVICE_SUPPORT_MTLINK             //!< The device supports MtLink capability.
} MtmlMtLinkCapability;

/* The display interface types. */
typedef enum {
    MTML_DISP_INTF_TYPE_DP,
    MTML_DISP_INTF_TYPE_EDP,
    MTML_DISP_INTF_TYPE_VGA,
    MTML_DISP_INTF_TYPE_HDMI,
    MTML_DISP_INTF_TYPE_LVDS,
    MTML_DISP_INTF_TYPE_MAX
} MtmlDispIntfType;

/* The display interface specifications. */
typedef struct {
    MtmlDispIntfType type;      // Type of display interface.
    unsigned int maxHoriRes;    // Maximum supported horizontal resolution.
    unsigned int maxVertRes;    // Maximum supported vertical resolution.
    float maxRefreshRate;       // Maximum refresh rate.
    unsigned int rsvd[8];       // Reserved for future extension.
} MtmlDispIntfSpec;


/**
 * GPU engine.
 */
typedef enum {
    MTML_GPU_ENGINE_GEOMETRY,
    MTML_GPU_ENGINE_2D,
    MTML_GPU_ENGINE_3D,
    MTML_GPU_ENGINE_COMPUTE,
 
    // Keep this last
    MTML_GPU_ENGINE_MAX
} MtmlGpuEngine;

/**
 * ECC mode.
 */
typedef enum {
    MTML_MEMORY_ECC_DISABLE = 0,  //!< Disables Memory ECC mode.
    MTML_MEMORY_ECC_ENABLE        //!< Enables Memory ECC mode.
} MtmlEccMode;

/**
 * Causes for page retirement
 */
typedef enum {
    MTML_PAGE_RETIREMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS = 0, //!< Page was retired due to multiple single bit ECC error
    MTML_PAGE_RETIREMENT_CAUSE_DOUBLE_BIT_ECC_ERROR = 1,           //!< Page was retired due to double bit ECC error
  
    // Keep this last
    MTML_PAGE_RETIREMENT_CAUSE_MAX
} MtmlPageRetirementCause;

/**
 * ECC mode.
 */
typedef struct {
    unsigned int sbeCount;           //!< single bit ECC error count
    unsigned int dbeCount;           //!< double bit ECC error count
} MtmlPageRetirementCount;

/**
 * Retired Pages pending state enum.
 */
typedef enum {
    MTML_RETIRED_PAGES_PENDING_STATE_FALSE    = 0,
    MTML_RETIRED_PAGES_PENDING_STATE_TRUE     = 1
} MtmlRetiredPagesPendingState;

typedef struct {
    unsigned long long timestamps;                                //!< retired page start time
    unsigned long long address;                                   //!< retired page physical address
    unsigned int rsvd[10];
} MtmlPageRetirement;

typedef struct {
    MtmlPageRetirementCause cause;
    unsigned long long timestamps;                                //!< retired page start time
    unsigned long long address;                                   //!< retired page physical address
    unsigned int rsvd[10];
} MtmlPageRetirementPending;

/**
 * ECC counter types.
 *
 * Note: Volatile counts are reset each time the driver loads. On Windows this is once per boot. On Linux this can be more frequent.
 *       Aggregate counts exist continuously afther the persistence mode is enabled.
 */
typedef enum {
    MTML_VOLATILE_ECC      = 0,      //!< Volatile counts are reset each time the driver loads.
    MTML_AGGREGATE_ECC     = 1,      //!< Aggregate counts persist across reboots (i.e. for the lifetime of the device)
 
    // Keep this last
    MTML_ECC_COUNTER_TYPE_COUNT      //!< Count of memory counter types
} MtmlEccCounterType;

/**
 * Memory error types
 */
typedef enum {
    /**
     * A memory error that was corrected
     *
     * For ECC errors, these are single bit errors
     */
    MTML_MEMORY_ERROR_TYPE_CORRECTED = 0,
 
    /**
     * A memory error that was not corrected
     *
     * For ECC errors, these are double bit errors
     */
    MTML_MEMORY_ERROR_TYPE_UNCORRECTED = 1,
 
    // Keep this last
    MTML_MEMORY_ERROR_TYPE_COUNT //!< Count of memory error types
} MtmlMemoryErrorType;

/**
 * See \ref mtmlMemoryGetEccErrorCounter
 */
typedef enum {
    MTML_MEMORY_LOCATION_DRAM = 0x1,  //!< DRAM
} MtmlMemoryLocation;

/***********************************/
/** @}
 */
/***********************************/



/***************************************************************************************************/
/** @defgroup mtml3 Opaque Data Structure Definitions
 * This group introduces opaque data structures.
 *  @{
 */
/***************************************************************************************************/

/**
 * GPU opaque data structure.
 */
typedef struct MtmlGpu MtmlGpu;

/**
 * Memory opaque data structure.
 */
typedef struct MtmlMemory MtmlMemory;

/**
 * VPU opaque data structure.
 */
typedef struct MtmlVpu MtmlVpu;

/**
 * Device opaque data structure.
 */
typedef struct MtmlDevice MtmlDevice;

/**
 * System opaque data structure.
 */
typedef struct MtmlSystem MtmlSystem;

/**
 * Library opaque data structure.
 */
typedef struct MtmlLibrary MtmlLibrary;

/***********************************/
/** @}
 */
/***********************************/



/***************************************************************************************************/
/** @defgroup mtml4 Library Functions
 * This group introduces library functions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Initializes an library opaque object and prepares resources. Upon success, the initialized object can be used for further
 * access to other functions. An library opaque object is the top-level entry-point from which user code can
 * access other functions provided by the MTML library.
 *
 * For all products.
 * 
 * The output data is allocated internally by the MTML library. Use \ref mtmlLibraryShutDown() to release its resources
 * when it is not needed any longer. If multiple MtmlLibrary pointers are initialized by calling this API multiple times, the library
 * will not be shut down until the corresponding number of mtmlLibraryShutDown() calls have been made with those pointers. The order in which the MtmlLibrary 
 * pointers are released using the mtmlLibraryShutDown() API does not necessarily have to match the order in which they were initialized using the API.
 * 
 * @param lib                                       [out] A double pointer to the library opaque object that is allocated and initialized.
 * 
 * @warning Providing this function with a \a lib that has already been initialized causes memory leak.
 * 
 * @return 
 *         - \ref MTML_SUCCESS                      if an library opaque object has been properly initialized.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a lib is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLibraryInit(MtmlLibrary **lib);

/**
 * Shuts down the library opaque object that is previously initialized by \ref mtmlLibraryInit() and releases its resources.
 * The \a lib pointer cannot be used anymore after this function returns.
 * 
 * For all products. 
 * 
 * The internal resources are shared by all library opaque objects globally. Therefore, to thoroughly shut down the library,
 * all library opaque objects returned via previous mtmlLibraryInit() API invocations shall be passed to this API respectively.
 *
 * @param lib                                       [in] A pointer to the library opaque object that needs to be shut down.
 * 
 * @return 
 *         - \ref MTML_SUCCESS                      if MTML has been properly shut down.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a lib is NULL.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLibraryShutDown(MtmlLibrary *lib);

/**
 * Retrieves the version of the specified MtmlLibrary opaque data. 
 * 
 * For all products. 
 *
 * The version identifier is an alphanumeric string and null-terminator guaranteed.
 * 
 * @param lib                                       [in] The pointer to library opaque data.
 * @param version                                   [out] The reference in which to return the version identifier.
 * @param length                                    [in] The length of the buffer pointed by \a version. See \ref MTML_LIBRARY_VERSION_BUFFER_SIZE 
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a version has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a version or \a lib is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small to hold the version string.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLibraryGetVersion(const MtmlLibrary *lib, char* version, unsigned int length);

/**
 * Initializes a MtmlSystem opaque pointer that is bound to a library opaque object.
 * 
 * For all products. 
 * 
 * The initialized MtmlSystem opaque object can be used with system-related functions.
 * 
 * @param lib                                       [in] The pointer to library opaque data.
 * @param sys                                       [out] The double pointer to the system opaque data that shall be allocated and initialized.
 * 
 * @warning Providing this function with a \a sys that has already been initialized causes memory leak.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a sys has been initialized.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a lib or \a sys is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLibraryInitSystem(const MtmlLibrary *lib, MtmlSystem **sys);

/**
 * @deprecated Releases the resources managed by the MtmlSystem opaque object and makes it unusable.
 * 
 * For all products.
 * 
 * @param sys                                       [in] The pointer to the system opaque object that shall be freed.
 * @return
 *         - \ref MTML_SUCCESS                      if \a sys has been freed.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a sys is NULL.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MTML_DEPRECATED("Not required anymore.")
MtmlReturn MTML_API mtmlLibraryFreeSystem(MtmlSystem *sys);

 /**
 * Retrieves the number of devices that can be accessed by the library opaque object.
 * 
 * @param lib                                       [in] The pointer to the library opaque object.
 * @param count                                     [out] The reference in which to return the number of accessible devices.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a count or \a lib is NULL.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLibraryCountDevice(const MtmlLibrary *lib, unsigned int *count);

/**
 * Initializes a device opaque object to represent a device that is designated by its index. 
 * The index ranges from (0) to (deviceCount - 1), where deviceCount is retrieved from \ref mtmlLibraryCountDevice().
 * 
 * For all products.
 *
 * The initialized device opaque object can be used with device-related functions.
 *
 * @param lib                                       [in] The pointer to the library opaque object.
 * @param index                                     [in] The index of the target device.
 * @param dev                                       [out] The double pointer to the device opaque object that shall be allocated and initialized.
 * 
 * @warning Providing this function with a \a dev that has already been initialized causes memory leak.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a device has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a index is invalid, or either \a lib or \a dev is NULL.
 *         - \ref MTML_ERROR_NOT_FOUND              if no device with the specified \a index is found.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 *
 * @see mtmlLibraryCountDevice
 * 
 */
MtmlReturn MTML_API mtmlLibraryInitDeviceByIndex(const MtmlLibrary *lib, unsigned int index, MtmlDevice **dev);

/**
 * Initializes a device opaque object to represent a device that is designated by its UUID. See \ref mtmlDeviceGetUUID() for more information
 * about the device's UUID.
 * 
 * For all products.
 *
 * The initialized device opaque object can be used with device-related functions.
 *
 * @param lib                                       [in] The pointer to the library opaque object.
 * @param uuid                                      [in] The UUID of the target device.
 * @param dev                                       [out] The double pointer to the device opaque object that shall be allocated and initialized.
 * 
 * @warning Providing this function with a \a dev that has already been initialized causes memory leak.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a device has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a library, \a uuid, or \a dev is NULL.
 *         - \ref MTML_ERROR_NOT_FOUND              if no device with the specified \a uuid is found.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLibraryInitDeviceByUuid(const MtmlLibrary *library, const char *uuid, MtmlDevice **dev);

/**
 * Initializes a device opaque object to represent a device that is designated by its PCI Sbdf.
 * The PCI Sbdf format like 00000000:3a:00.0 refer to \ref MtmlPciInfo::sbdf.
 *
 * For all products.
 *
 * @param lib                                       [in] The pointer to the library opaque object.
 * @param pciSbdf                                   [in] The PCI bus id of the target device.
 * @param device                                    [out] Reference in which to return the device handle.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a device has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a pciSbdf is invalid, \a library or \a dev is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_NOT_FOUND              if no device with the specified \a pciSbdf is found.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlLibraryInitDeviceByPciSbdf(const MtmlLibrary* lib, const char* pciSbdf, MtmlDevice** dev);

/**
 * Sets the MPC configuration for multiple devices in one shot. If MPC mode is disabled on any supported device, this
 * function will enable it before applying the configuration. This function might take a relatively long time to
 * return on success, during which any other concurrent operation may encounter failure or undefined behavior. Therefore,
 * it is recommended to pause any other API calls before calling this function. If configuring MPC mode fails for any device
 * in the batch, this function will attempt to roll back previous devices to MPC disable status.
 *
 * \b IMPORTANT: After calling this function, all opaque pointers (MtmlDevice, MtmlGpu, etc., but not including the
 * MtmlLibrary pointer itself) allocated by the library will become invalid. Continuing to use those
 * pointers is undefined behavior.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported in Linux only.
 *
 * @param lib                                       [in] The pointer to the library opaque object.
 * @param count                                     [in] The size of \a devices.
 * @param devices                                   [in] The identifiers of the target devices.
 * @param mpcConfigIds                              [in] The MPC configuration IDs for \a devices.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mpc configuration has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a library, \a devices, or \a mpcConfigIds is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the device does not support MPC or the MPC configuration ID is illegal.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if an error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                for any unexpected error.
 */
MtmlReturn MTML_API mtmlLibrarySetMpcConfigurationInBatch(const MtmlLibrary* lib, unsigned int count, MtmlDevice** devices, unsigned int* mpcConfigIds);

/**
 * @deprecated Releases the resources managed by the device opaque object and makes it unusable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the device opaque object that shall be freed.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a dev has been freed.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a Virtual Device.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MTML_DEPRECATED("Not required anymore.")
MtmlReturn MTML_API mtmlLibraryFreeDevice(MtmlDevice *dev);

/***********************************/
/** @}
 */
/***********************************/



/***************************************************************************************************/
/** @defgroup mtml5 System Functions
 * This group introduces system functions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Retrieves the version of the driver that is installed on the current platform.
 *
 * For all products.
 *
 * The version identifier is an alphanumeric string.
 *
 * @param sys                                       [in] The pointer to the system opaque object.
 * @param version                                   [out] The reference in which to return the version identifier.
 * @param length                                    [in] The buffer size pointed by \a version. See \ref MTML_DRIVER_VERSION_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a version has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a sys or \a version is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlSystemGetDriverVersion(const MtmlSystem *sys, char *version, unsigned int length);

/***********************************/
/** @}
 */
/***********************************/


/***************************************************************************************************/
/** @defgroup mtml6 Device Functions
 * This group introduces device functions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Initializes a GPU opaque object to represent a specific graphic core on the target device that is designated by its index.
 * 
 * For all products.
 *
 * The initialized GPU opaque object can be used with GPU-related functions.
 *
 * @param dev                                       [in] The pointer to the device opaque object.
 * @param gpu                                       [out] The double pointer to the GPU opaque object that shall be allocated and initialized.
 * 
 * @warning Providing this function with a \a gpu that has already been initialized causes memory leak.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a gpu has been initialized successfully.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a gpu is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceInitGpu(const MtmlDevice *dev, MtmlGpu **gpu);

/**
 * @deprecated the resources managed by the GPU opaque object and makes it unusable.
 *  * For all products.
 * 
 * @param gpu                                       [in] The pointer to the GPU opaque object that shall be freed.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a gpu has been freed.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a gpu is NULL.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MTML_DEPRECATED("Not required anymore.")
MtmlReturn MTML_API mtmlDeviceFreeGpu(MtmlGpu *gpu);

/**
 * Initializes a memory opaque object to represent the memory on the target device.
 * 
 * For all products.
 *
 * The initialized memory opaque object can be used with memory-related functions.
 *
 * @param dev                                       [in] The pointer to the device opaque object.
 * @param mem                                       [out] The double pointer to the memory opaque object that shall be allocated and initialized.
 * 
 * @warning Providing this function with a \a mem that has already been initialized causes memory leak.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a mem has been initialized successfully.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a mem is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 *
 */
MtmlReturn MTML_API mtmlDeviceInitMemory(const MtmlDevice *dev, MtmlMemory **mem);

/**
 * @deprecated the resources managed by the memory opaque object and makes it unusable.
 * 
 * For all products.
 * 
 * @param mem                                       [in] The pointer to the memory opaque object that shall be freed.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a mem has been freed.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem is NULL.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MTML_DEPRECATED("Not required anymore.")
MtmlReturn MTML_API mtmlDeviceFreeMemory(MtmlMemory *mem);

/**
 * Initializes a VPU opaque object to represent the video codec on the target device.
 * 
 * For all products.
 *
 * The initialized VPU opaque object can be used with codec-related functions.
 *
 * @param dev                                       [in] The pointer to the device opaque object.
 * @param vpu                                       [out] The double pointer to the memory opaque object that shall be allocated and initialized.
 * 
 * @warning Providing this function with a \a vpu that has already been initialized causes memory leak.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a vpu has been successfully initialized.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a vpu is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is an MPC parent device.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceInitVpu(const MtmlDevice *dev, MtmlVpu **vpu);

/**
 * @deprecated the resources managed by the VPU opaque object and makes it unusable.
 * 
 * For all products.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object that shall be freed.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a vpu has been freed.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu is NULL.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MTML_DEPRECATED("Not required anymore.")
MtmlReturn MTML_API mtmlDeviceFreeVpu(MtmlVpu *vpu);

/**
 * Retrieves the index associated with the specified device.
 * 
 * For all products.
 *
 * @param dev                                       [in] The pointer to the device opaque object.
 * @param index                                     [out] The index of the target device.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a index has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a index is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev does not support to be accessed by \a index. For example, the host virtual device.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetIndex(const MtmlDevice *dev, unsigned int *index);

/**
 * Retrieves the UUID of a specified device. The UUID is a hexadecimal string in the 
 * form of xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, where each 'x' is an ASCII character that represents a hexidecimal
 * digit. The UUID is globally unique for every single device thus can be used to identify different devices
 * physically.
 *
 * For all products.
 *
 *
 * @param dev                                       [in] The identifier of the target device.
 * @param uuid                                      [out] The reference in which to return the UUID.
 * @param length                                    [in] The size of buffer pointed by \a uuid. See \ref MTML_DEVICE_UUID_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a uuid has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a uuid is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetUUID(const MtmlDevice *dev, char *uuid, unsigned int length);

/**
 * Retrieves the brand of a device.
 *
 * For all products. 
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param type                                      [out] The reference in which to return the product brand type. See \ref MtmlBrandType.
 *
 * @return 
 *         - \ref MTML_SUCCESS                      if \a name has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev is invalid or \a type is NULL.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 */
MtmlReturn MTML_API mtmlDeviceGetBrand(const MtmlDevice *dev, MtmlBrandType *type);

/**
 * Retrieves the name of a device.
 *
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param name                                      [out] The reference in which to return the product name.
 * @param length                                    [in] The size of buffer pointed by \a name. See MTML_DEVICE_NAME_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a name has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a name is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetName(const MtmlDevice *dev, char *name, unsigned int length);

/**
 * Retrieves the PCI attributes of a device.
 * 
 * For all products.
 *
 * See \ref MtmlPciInfo for details on the available PCI information.
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param pci                                       [out] The reference in which to return the PCI info.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a pci has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a pci is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetPciInfo(const MtmlDevice *dev, MtmlPciInfo *pci);

/**
 * Retrieves the power usage for a device in milliwatts (mW) and its associated circuitry.
 *
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param power                                     [out] The reference in which to return the power usage information.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a power has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a power is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetPowerUsage(const MtmlDevice *dev, unsigned int *power);

/**
 * Retrieves the GPU paths of a device.
 *
 * For all products.
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param path                                      [out] The reference in which to return the target device path.
 * @param length                                    [in] The size of buffer pointed by \a path. See #MTML_DEVICE_PATH_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a path has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a path is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a virtual device.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetGpuPath(const MtmlDevice* dev, char* path,unsigned int length);

/**
 * Retrieves the primary paths of a device.
 *
 * For all products.
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param path                                      [out] The reference in which to return the target device path.
 * @param length                                    [in] The size of buffer pointed by \a path. See #MTML_DEVICE_PATH_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a path has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a path is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetPrimaryPath(const MtmlDevice* dev, char* path, unsigned int length);

/**
 * Retrieves the render paths of a device.
 *
 * For all products.
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param path                                      [out] The reference in which to return the target device path.
 * @param length                                    [in] The size of buffer pointed by \a path. See #MTML_DEVICE_PATH_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a path has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a path is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetRenderPath(const MtmlDevice* dev, char* path, unsigned int length);

/**
 * @deprecated Renamed to \ref mtmlDeviceGetMtBiosVersion as the name describes the situation more accurately.
 * 
 * Retrieves the version of the device's VBIOS.
 *
 * For all products.
 *
 * The version identifier is an alphanumeric string.
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param version                                   [out] The reference in which to return the version identifier.
 * @param length                                    [in] The size of buffer pointed by \a version. See \ref MTML_DEVICE_VBIOS_VERSION_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a version has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a version is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MTML_DEPRECATED("use mtmlDeviceGetMtBiosVersion instead") 
MtmlReturn MTML_API mtmlDeviceGetVbiosVersion(const MtmlDevice* dev, char* version, unsigned int length);

/**
 * Retrieves the version of the device's MTBIOS firmware.
 *
 * For all products.
 *
 * The version identifier is an alphanumeric string.
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param version                                   [out] The reference in which to return the version identifier.
 * @param length                                    [in] The size of buffer pointed by \a version. See \ref MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a version has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a version is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is a virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetMtBiosVersion(const MtmlDevice* dev, char* version, unsigned int length);

/**
 * Retrieves the properties of a device.
 * 
 * For all products.
 *
 * @param dev                                       [in] The pointer to the target device.
 * @param prop                                      [out] The reference in which to return the target device properties.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a prop has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a prop is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetProperty(const MtmlDevice *dev,  MtmlDeviceProperty *prop);

/**
 * Retrieves the number of fans on a device.
 * @note The value returned is the number of fan control channels on the device.
 *
 * For all discrete products with dedicated fans.
 *
 * @param dev                                       [in] The pointer of the target device.
 * @param count                                     [out] The reference in which to return the fan count.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceCountFan(const MtmlDevice* dev, unsigned int* count);

/**
 * Retrieves the intended operating speed of the device's specified fan.
 * The reported speed is the intended fan speed. If the fan is physically blocked and unable to spin,
 * the output will not match the actual fan speed.
 *
 * For all discrete products with dedicated fans.
 *
 * The fan speed is expressed as a percentage of the product's maximum noise tolerance fan speed.
 * This value may exceed 100% in certain cases.
 *
 * @param dev                                       [in] The pointer of the target device.
 * @param index                                     [in] The index of the target fan, zero indexed.
 * @param speed                                     [out] The reference in which to return the fan speed percentage.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a speed has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a speed is NULL, or \a index is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetFanSpeed(const MtmlDevice* dev, unsigned int index, unsigned int* speed);

/**
 * Retrieves the intended operating speed of the device's specified fan.
 * The reported speed is the intended fan speed. If the fan is physically blocked and unable to spin,
 * the output will not match the actual fan speed.
 *
 * For all discrete products with dedicated fans.
 *
 * The fan speed is a real-time speed value that means revolutions per minute(rpm).
 *
 * @param dev                                       [in] The pointer of the target device.
 * @param fanIndex                                  [in] The index of the target fan, zero indexed.
 * @param fanRpm                                    [out] The reference in which to return the fan real speed.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a speed has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a speed is NULL, or \a index is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetFanRpm(const MtmlDevice* dev, unsigned int fanIndex, unsigned int* fanRpm);

/**
 * Retrieves the phyiscal slot info of the PCIe interface to which the specified device is connected.
 *
 * @param dev                                       [in] The pointer to device opaque data.
 * @param slotInfo                                  [out] The reference in which to return the slot info.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a slotInfo has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a slotInfo is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetPcieSlotInfo(const MtmlDevice* dev, MtmlPciSlotInfo* slotInfo);

/**
 * Retrieves the number of display interfaces of the specified device.
 *
 * For all products.
 *
 * @param device                                    [in] The pointer to device opaque data.
 * @param count                                     [out] The reference in which to return the number.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceCountDisplayInterface(const MtmlDevice* device, unsigned int* count);

/**
 * Retrieves the specification data of the specified display interface of a device.
 *
 * For all products.
 *
 * @param device                                    [in] The pointer to device opaque data.
 * @param intfIndex                                 [in] The index of the display interface to be queried.
 * @param dispIntfSpec                              [out] The reference in which to return the spec data.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a dispIntfSpec has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a dispIntfSpec is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetDisplayInterfaceSpec(const MtmlDevice* device, unsigned int intfIndex, MtmlDispIntfSpec* dispIntfSpec);

/**
 * Retrieves the serial number of the specified device.
 * 
 * For all products.
 *
 * @param device                                    [in] The pointer to device opaque data.
 * @param length                                    [in] The size of \a serial number buffer in byte.
 *                                                       See \ref MTML_DEVICE_SERIAL_NUMBER_BUFFER_SIZE.
 * @param serialNumber                              [out] The reference in which to return the serial number.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a serialNumber has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a serialNumber is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetSerialNumber(const MtmlDevice* device, unsigned int length, char* serialNumber);

/**
 * Gets the device's core count.
 *
 * @param device                                    [in] The identifier of the target device.
 * @param numCores                                  [out] The number of cores for the specified device.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if Gpu core count is successfully retrieved.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device is invalid, or \a numCores is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if this query is not supported by the device.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 *
 */
MtmlReturn MTML_API mtmlDeviceCountGpuCores(const MtmlDevice* device, unsigned int* numCores);

/***********************************/
/** @}
 */
/***********************************/



/***************************************************************************************************/
/** @defgroup mtml7 Device Virtualization Functions
 * This group introduces device virtualization functions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Gets the number of all virtualization types supported by a virtualizable device. 
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param count                                     [out] The reference in which to return the number of supported virtualization types.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceCountSupportedVirtTypes(const MtmlDevice *dev, unsigned int *count);
 
/**
 * Gets the list of virtualization types supported by a virtualizable device. 
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param types                                     [out] The reference in which to return the supported virtualization types.
 * @param count                                     [in] The size of the array pointed by \a types.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a types has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a types is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a count is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetSupportedVirtTypes(const MtmlDevice *dev, MtmlVirtType *types, unsigned int count);
 
/**
 * Gets the number of virtualization types, from which a virtual device can be created, of a virtualizable device. 
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param count                                     [out] The reference in which to return the number of available virtualization types.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceCountAvailVirtTypes(const MtmlDevice *dev, unsigned int *count);
 
/**
 * Gets the list of virtualization types, from which a virtual device can be created, of a virtualizable device.
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param types                                     [out] The reference in which to return the available virtualization types.
 * @param count                                     [in] The size of the array pointed by \a types.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a types has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a types is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a count is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetAvailVirtTypes(const MtmlDevice *dev, MtmlVirtType *types, unsigned int count);
 
/**
 * Gets the number of virtual devices that can be created from a specified virtualization type supported by a virtualizable device.
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param type                                      [in] The specified virtualization type.
 * @param count                                     [out] The reference in which to return the number of available virtualization types.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a type or \a count is NULL.
                                                    or \a type is invalid or not supported.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceCountAvailVirtDevices(const MtmlDevice *dev, const MtmlVirtType *type, unsigned int *count);
 
/**
 * Gets the number of active virtual devices created on a virtualizable device. 
 * A virtual device is active if it has been allocated resources as per its virtualization type.
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param count                                     [out] The reference in which to return the number of active virtual devices.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceCountActiveVirtDevices(const MtmlDevice *dev, unsigned int *count);

/**
 * Gets the list of UUIDs of all active virtual devices created on a virtualizable device.
 * The UUID strings are output in the \a uuids parameter, which shall be a pointer to a continuous memory block whose size is enough to
 * all content. The memory block is treated as a series of head-tail adjacent buffers (entry), while each of the buffer is \a entryLength
 * bytes in size. The number of the buffers is defined by \a entryCount, thus the total size of the memory block pointed by \a uuids shall
 * be equal or greater than \a entryLength * \a entryCount. Each buffer within the memory block is responsible for holding one UUID string with a
 * null-terminator, so it's the caller's responsibility to ensure there are enough buffers to hold all UUID strings and also each buffer is
 * enough in size to hold a single UUID string.
 * If the \a entryCount is greater than the actual number of active virtual devices, the extra entries are filled with empty strings.
 * A virtual device is active if it has been allocated resources as per its virtualization type. 
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param uuids                                     [out] A pointer to the memory block tha holds all ouput UUID strings.
 * @param entryLength                               [in] The size of each entry (each buffer) in \a uuids.
 * @param entryCount                                [in] The number of entries in \a uuids.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a uuids has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a uuids is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a entrylength or \a entryCount is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetActiveVirtDeviceUuids(const MtmlDevice *dev, char *uuids, unsigned int entryLength, unsigned int entryCount);

/**
 * Retrieves the maximum number of vGPU devices creatable on a device for given vGPU type.
 *
 * For all products.
 *
 * @param dev                                       [in] The identifier of the target device.
 * @param type                                      [in] Handle to vGPU type.
 * @param virtDevicesCount                          [out] Pointer to get the max number of vGPU instances,
 *                                                        which can be created on a deicve for given vgpuTypeId.
 * @return
 *         - \ref MTML_SUCCESS                      successful completion.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a type is invalid, or is not supported on target device,
 *                                                  or \a dev or \a virtDeviceCount is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is not a virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceCountMaxVirtDevices(const MtmlDevice* dev, const MtmlVirtType* type, unsigned int* virtDevicesCount);
 
/**
 * Initializes an active virtual device that can be specified by the UUID from a virtualizable device. 
 * A virtual device is active if it has been allocated resources as per its virtualization type.
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @warning Providing this function with a \a virtDev that has already been initialized causes memory leak.
 * 
 * @param dev                                       [in] The pointer to the target device.
 * @param uuid                                      [in] The UUID string of a virtual device.
 * @param virtDev                                   [out] The double pointer to the memory opaque object that shall be allocated and initialized.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a virtDev has been initialized.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev or \a uuid or \a virtDev is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev is non-virtualizable.
 *         - \ref MTML_ERROR_INSUFFICIENT_MEMORY    if the system is running out of memory.
 *         - \ref MTML_ERROR_NOT_FOUND              if there is no Virtual Device found with \a uuid.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceInitVirtDevice(const MtmlDevice *dev, const char *uuid, MtmlDevice **virtDev);

/**
 * @deprecated the resources managed by the opaque object of a virtual device and makes it unusable. 
 * This function is ONLY applicable to a device that supports to be virtualized.
 * Refer to \a MtmlDeviceProperty.virtCap to determine whether a device is virtualizable.
 * 
 * For all products.
 * 
 * @param virtDev                                   [in] The pointer to a device opaque object that shall be freed.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a virtDev has been freed.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a virtDev is NULL or not a virtDev.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a virtDev is not a Virtual Device.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MTML_DEPRECATED("Not required anymore.")
MtmlReturn MTML_API mtmlDeviceFreeVirtDevice(MtmlDevice *virtDev);
 
/**
 * Gets the virtualization type based on which a virtual device is created.
 * This function is ONLY applicable to virtual devices.
 * A virtual device can be initialized by \ref mtmlDeviceInitVirtDevice() and always has a virtualization role
 * of #MTML_VIRT_ROLE_HOST_VIRTDEVICE. Refer to \ref MtmlVirtRole for more information.
 * 
 * For all products.
 * 
 * @param virtDev                                   [in] The pointer to the target virtual device.
 * @param type                                      [out] The reference to which the virtualization type is returned.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a type has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a virtDev or \a type is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a virtDev is not a Virtual Device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetVirtType(const MtmlDevice *virtDev, MtmlVirtType *type);

/**
 * Gets the physical device from which a virtual device is created.
 * This function is ONLY applicable to virtual devices.
 * A virtual device can be initialized by \ref mtmlDeviceInitVirtDevice() and always has a virtualization role
 * of #MTML_VIRT_ROLE_HOST_VIRTDEVICE. Refer to \ref MtmlVirtRole for more information.
 * 
 * For all products.
 * 
 * @param virtDev                                   [in] The pointer to the target virtual device.
 * @param uuid                                      [out] The reference to which the UUID of the physical device is returned.
 * @param length                                    [in] The size of the buffer pointed by \a uuid, in bytes.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a version has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a virtDev or \a uuid is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a virtDev is not a virtual device.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetPhyDeviceUuid(const MtmlDevice *virtDev, char *uuid, unsigned int length);

/***********************************/
/** @}
 */
/***********************************/

/***************************************************************************************************/
/** @defgroup mtml8 P2P Functions
 * This group introduces P2P functions.
 *  @{
 */
 /***************************************************************************************************/

/**
 * Retrieves the Topology Level between a given pair of devices.
 * For all products.
 * Supported on Linux only.
 *
 * @param dev1                                      [in] The identifier of the first device.
 * @param dev2                                      [in] The identifier of the second device.
 * @param level                                     [out] A \ref mtmlDeviceTopologyLevel that indicates the level.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a level has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev1, or \a dev2 is invalid, or \a level is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the device or OS does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                an error has occurred in underlying topology discovery.
 */
MtmlReturn MTML_API mtmlDeviceGetTopologyLevel(const MtmlDevice* dev1, const MtmlDevice* dev2, MtmlDeviceTopologyLevel* level);

/**
 * Retrieve the set of device's count that are nearest to a given device at a specific interconnectivity level.
 * For all products.
 * Supported on Linux only.
 *
 * @param dev                                       [in] The identifier of the target device.
 * @param level                                     [in] The \ref MtmlDeviceTopologyLevel level to search for other devices.
 * @param count                                     [out] The reference in which to return the number of topology nearest devices.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev, or \a level is invalid, or \a count is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the device or OS does not support this feature.
 *         - \ref MTML_ERROR_UNKNOWN                an error has occurred in underlying topology discovery.
 */
MtmlReturn MTML_API mtmlDeviceCountDeviceByTopologyLevel(const MtmlDevice* dev, MtmlDeviceTopologyLevel level, unsigned int* count);

/**
 * Retrieves the set of devices that are nearest to a given device at a specific interconnectivity level.
 * 
 * For all products.
 * Supported on Linux only.
 *
 * @param dev                                       [in] The identifier of the target device.
 * @param level                                     [in] The \ref MtmlDeviceTopologyLevel level to search for other devices.
 * @param count                                     [in] The reference in which to return the number of topology nearest devices, refer to /a mtmlDeviceCountDeviceByTopologyLevel.
 * @param deviceArray                               [out] An array of device handles for devices found at \a level.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a deviceArray has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev, \a level, or \a count is invalid, or \a deviceArray is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a count is too small.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the device or OS does not support this feature.
 *         - \ref MTML_ERROR_UNKNOWN                an error has occurred in underlying topology discovery.
 */
MtmlReturn MTML_API mtmlDeviceGetDeviceByTopologyLevel(const MtmlDevice* dev, MtmlDeviceTopologyLevel level, unsigned int count, MtmlDevice** deviceArray);

/**
 * Retrieves the status for a given p2p capability between a given pair of devices.
 *
 * @param dev1                                      [in] The first device.
 * @param dev2                                      [in] The second device.
 * @param p2pCap                                    [in] P2P capability being looked for between \a dev1 and \a dev2.
 * @param p2pStatus                                 [out] Reference in which to return the status of the \a p2pCap
 *                                                         between \a dev1 and \a dev2.
 * @return
 *         - \ref MTML_SUCCESS                      if \a p2pStatus has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a dev1 or \a dev2 or \a p2pCap is invalid or \a p2pStatus is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a dev1 or \a dev2 is virtual device.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetP2PStatus(const MtmlDevice* dev1, const MtmlDevice* dev2, MtmlDeviceP2PCaps p2pCap, MtmlDeviceP2PStatus* p2pStatus);


/***********************************/
/** @}
 */
 /***********************************/



/***************************************************************************************************/
/** @defgroup mtml9 GPU Functions
 * This group introduces GPU functions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Retrieves the current utilization rate for the device's graphic core.
 *
 * For all products.
 *
 * @param gpu                                       [in] The pointer to the GPU opaque object.
 * @param utilization                               [out] The reference in which to return the utilization information.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a utilization has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a gpu or \a utilization is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlGpuGetUtilization(const MtmlGpu *gpu,  unsigned int* utilization);

/**
 * Retrieves the current temperature readings for the device's graphic core, in degrees Celsius. 
 *
 *
 * @param gpu                                       [in] The pointer to the GPU opaque object.
 * @param temp                                      [out] The reference in which to return the temperature reading.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a temp has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a gpu or \a temp is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlGpuGetTemperature(const MtmlGpu *gpu, int* temp);


/**
 * Retrieves the current clock speed for the device's graphic core.
 *
 * For all products.
 * 
 * @param gpu                                       [in] The pointer to the GPU opaque object.
 * @param clockMhz                                  [out] The reference in which to return the clock speed in MHz.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a clockMhz has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a gpu or \a clockMhz is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlGpuGetClock(const MtmlGpu *gpu, unsigned int *clockMhz);

/**
 * Retrieves the maximum supported clock speed for the device's graphic core.
 *
 * For all products except S3000E.
 * 
 * @param gpu                                       [in] The pointer to the GPU opaque object.
 * @param clockMhz                                  [out] The reference in which to return the clock speed in MHz.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a clockMhz has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a gpu or \a clockMhz is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlGpuGetMaxClock(const MtmlGpu *gpu, unsigned int *clockMhz);

/**
 * Retrieves the current engine utilization rate for the device's graphic core.
 *
 * For all products.
 * Supported on Linux only.
 *
 * @param gpu                                       [in] The pointer to the GPU opaque object.
 * @param engine                                    [in] The type of gpu engine value. See \ref MtmlGpuEngine.
 * @param utilization                               [out] The reference in which to return the utilization information.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a utilization has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a gpu or \a utilization is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlGpuGetEngineUtilization(const MtmlGpu *gpu, MtmlGpuEngine engine, unsigned int* utilization);


/***********************************/
/** @}
 */
/***********************************/



/***************************************************************************************************/
/** @defgroup mtml10 Memory Functions
 * This group introduces memory functions.
 *  @{
 */
/***************************************************************************************************/


/**
 * Retrieves the amount of total memory available on the device, in bytes.
 *
 * For all products.
 *
 * @param mem                                       [in] The pointer to the memory opaque object.
 * @param total                                     [out] The reference in which to return the total memory size.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a total has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem is NULL or \a total is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetTotal(const MtmlMemory *mem, unsigned long long *total);

/**
 * Retrieves the amount of used memory on the device, in bytes.
 *
 * For all products.
 * 
 * @param mem                                       [in] The pointer to the memory opaque object.
 * @param used                                      [out] The reference in which to return the used memory size.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a used has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem is NULL or \a used is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetUsed(const MtmlMemory *mem, unsigned long long *used);

/**
 * Retrieves the amount of system shared memory used on the device, in bytes.
 *
 * For all products.
 * 
 * @param mem                                       [in] The pointer to the memory opaque object.
 * @param used                                      [out] The reference in which to return the system shared memory used size.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a used has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem is NULL or \a used is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetUsedSystem(const MtmlMemory *mem, unsigned long long *used);

/**
 * Retrieves the current memory utilization rate for the device.
 *
 * For all products.
 * 
 * @param mem                                       [in] The pointer to the memory opaque object.
 * @param utilization                               [out] The reference in which to return the utilization information.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a utilization has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a utilization is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetUtilization(const MtmlMemory *mem,  unsigned int *utilization);

/**
 * Retrieves the current clock speed for the memory of a device.
 * 
 * For all products.
 * 
 * @param mem                                       [in] The pointer to the memory opaque object.
 * @param clockMhz                                  [out] The reference in which to return the clock speed in MHz.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a clockMhz has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a clockMhz is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetClock(const MtmlMemory *mem, unsigned int *clockMhz);

/**
 * Retrieves the maximum supported clock speed for the memory of a device.
 * 
 * For all products except S3000E.
 * 
 * @param mem                                       [in] The pointer to the memory opaque object.
 * @param clockMhz                                  [out] The reference in which to return the clock speed in MHz.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a clockMhz has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a clockMhz is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetMaxClock(const MtmlMemory *mem, unsigned int *clockMhz);

/**
 * Retrieves the memory bus width of a device.
 *
 * For all products.
 * 
 * @param mem                                       [in] The identifier of the target device.
 * @param busWidth                                  [out] The memory bus width of the device.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if the memory bus width is successfully retrieved.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a busWidth is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetBusWidth(const MtmlMemory* mem, unsigned int* busWidth);

/**
 * Retrieves the total memory bandwidth of the specified device. The bandwidth is represented in GBps.
 *
 * @param mem                                       [in] The pointer to memory opaque data.
 * @param bandwidth                                 [out] The reference in which to return the bandwidth.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if the memory bandwidth is successfully retrieved.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a bandwidth is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetBandwidth(const MtmlMemory* mem, unsigned int* bandwidth);

/**
 * Retrieves the memory speed of the specified device. The memory speed is represented in Mbps.
 *
 * @param mem                                       [in] The pointer to memory opaque data.
 * @param speed                                     [out] The reference in which to return the speed.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if the memory speed is successfully retrieved.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a speed is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetSpeed(const MtmlMemory* mem, unsigned int* speed);

/**
 * Retrieves the memory chip vendor name of the device.
 *
 * @param mem                                       [in] The pointer to memory opaque data.
 * @param length                                    [in] The size of \a vendor buffer in byte. See \ref MTML_MEMORY_VENDOR_BUFFER_SIZE.
 * @param vendor                                    [out] The reference in which to return the name.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if the memory vendor is successfully retrieved.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a vendor is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetVendor(const MtmlMemory* mem, unsigned int length, char* vendor);

/**
 * Retrieves the memory type of the device.
 *
 * @param mem                                       [in] The pointer to memory opaque data.
 * @param type                                      [out] The reference in which to return the type.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if the memory type is successfully retrieved.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mem or \a type is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetType(const MtmlMemory* mem, MtmlMemoryType* type);

/***********************************/
/** @}
 */
/***********************************/



/***************************************************************************************************/
/** @defgroup mtml11 VPU Functions
 * This group introduces VPU functions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Retrieves the current utilization rates for the specified VPU.
 *
 * For all products.
 *
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param utilization                               [out] The reference in which to return the utilization information.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a utilization has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu is NULL or \a utilization is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a vpu points to a virtual VPU.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetUtilization(const MtmlVpu *vpu,  MtmlCodecUtil *utilization);

/**
 * Retrieves the current clock speed for the specified VPU.
 *
 * For all products.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param clockMhz                                  [out] The reference in which to return the clock speed in MHz.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a clockMhz has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu or \a clockMhz is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a vpu points to a virtual VPU.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetClock(const MtmlVpu *vpu, unsigned int *clockMhz);

/**
 * Retrieves the maximum supported clock speed for the specified VPU.
 *
 * For all products except S3000E.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param clockMhz                                  [out] The reference in which to return the clock speed in MHz.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a clockMhz has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu or \a clockMhz is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a vpu points to a virtual VPU.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetMaxClock(const MtmlVpu *vpu, unsigned int *clockMhz);

/**
 * Retrieves the capacity, that is, maximum number of supported concurrent codec sessions, of the specified VPU. 
 * A codec session is the processing of an independent video stream, which can be categorized into an encoder 
 * session and a decoder session. An encoder session refers to the video encoding processing, while a decoder 
 * session represents the decoding processing.
 *  
 * An encoder session can be referred by its ID (session ID), which ranges from 0 to \a encodeCapacity - 1.
 * A decoder session can be referred by its ID (session ID), which ranges from 0 to \a decodeCapacity - 1.
 *
 * For all products.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param encodeCapacity                            [out] The reference in which to return the concurrent session capacity for encoding.
 * @param decodeCapacity                            [out] The reference in which to return the concurrent session capacity for decoding.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a encodeCapacity or \a decodeCapacity has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu or \a encodeCapacity or \a decodeCapacity is NULL.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetCodecCapacity(const MtmlVpu *vpu, unsigned int *encodeCapacity, unsigned int *decodeCapacity);

/**
 * Retrieves the state of each encoder session on a specified VPU. The output \a states is an array of \ref MtmlCodecSessionState, 
 * in which each element represents the state of a single encoder session. The state of an encoder session is populated at the
 * position where the array index equals the session ID, that is, \a states[x] will be the state of encoder session x.
 * If the size of the \a states array N is less than the encoder session capacity, the state of the first N (i.e., session IDs
 * ranging from 0 to N-1) sessions will be returned. Otherwise, if N is greater than the encoder session capacity, 
 * the extra space of the \a states array will be populated with MTML_CODEC_SESSION_STATE_UNKNOWN. The encoder session capacity of a VPU can 
 * be retrieved from \ref mtmlVpuGetCodecCapacity(), which can be used as the proper size for the \a states array to hold the 
 * state of all encoder sessions.
 * 
 * For all products.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param states                                    [out] The reference in which to return the state of encoder sessions.
 * @param length                                    [in] The size of the \a state array.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a states has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu or \a states is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is 0.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetEncoderSessionStates(const MtmlVpu *vpu, MtmlCodecSessionState *states, unsigned int length);

/**
 * Retrieves the metrics of the specified encoder session. If the session is not active (there is no system 
 * process attached to the session), the pid field of the output \a metrics struct is set to zero. Otherwise, 
 * the session is considered active and the output \a metrics struct is populated with valid data.
 * 
 * @note The latency field in the output struct is always 0 for this version.
 * @note In case that the \a vpu argument is a virtual VPU, the pid field in the output 
 *       struct is always 0 for this version.
 *
 * For all products.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param sessionId                                 [in] The ID of the session whose metrics shall be queried.
 * @param metrics                                   [out] The pointer to the output struct to hold the session metrics.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a metrics has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu or \a metrics is NULL, or \a sessionId is invalid.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetEncoderSessionMetrics(const MtmlVpu *vpu, unsigned int sessionId, MtmlCodecSessionMetrics *metrics);

/**
 * Retrieves the state of each decoder session on a specified VPU. The output \a states is an array of \ref MtmlCodecSessionState, 
 * in which each element represents the state of a single decoder session. The state of an decoder session is populated at the
 * position where the array index equals the session ID, that is, \a states[x] will be the state of decoder session x.
 * If the size of the \a states array N is less than the decoder session capacity, the state of the first N (i.e., session IDs
 * ranging from 0 to N-1) sessions will be returned. Otherwise, if N is greater than the decoder session capacity, 
 * the extra space of the \a states array will be populated with MTML_CODEC_SESSION_STATE_UNKNOWN. The decoder session capacity of a VPU can 
 * be retrieved from \ref mtmlVpuGetCodecCapacity(), which can be used as the proper size for the \a states array to hold the 
 * state of all decoder sessions.
 * 
 * For all products.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param states                                    [out] The reference in which to return the state of decoder sessions.
 * @param length                                    [in] The size of the \a state array.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a states has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu or \a states is NULL.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a length is 0.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetDecoderSessionStates(const MtmlVpu *vpu, MtmlCodecSessionState *states, unsigned int length);

/**
 * Retrieves the metrics of the specified decoder session. If the session is not active (there is no system 
 * process attached to the session), the pid field of the output \a metrics struct is set to zero. Otherwise, 
 * the session is considered active and the output \a metrics struct is populated with valid data.
 * 
 * @note The latency field in the output struct is always 0.
 * @note In case that the \a vpu argument is a virtual VPU, the pid field in in the output  
 *       struct is always 0 for this version.
 *
 * For all products.
 * 
 * @param vpu                                       [in] The pointer to the VPU opaque object.
 * @param sessionId                                 [in] The ID of the session whose metrics shall be queried.
 * @param metrics                                   [out] The pointer to the output struct to hold the session metrics.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a metrics has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a vpu or \a metrics is NULL, or \a sessionId is invalid.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlVpuGetDecoderSessionMetrics(const MtmlVpu *vpu, unsigned int sessionId, MtmlCodecSessionMetrics *metrics);

/***********************************/
/** @}
 */
/***********************************/


/***************************************************************************************************/
/** @defgroup mtml12 Logging Functions
 * This group introduces logging functions.
 *  @{
 */
/***************************************************************************************************/

/**
 * Configures the MTML logger.
 *
 * @param configuration                             [in] The configuration of the MTML logger.
 * @return
 *          - \ref MTML_SUCCESS                     if MTML's logger has been configured.
 *          - \ref MTML_ERROR_INVALID_ARGUMENT      if \a level is illegal.
 *          - \ref MTML_ERROR_NOT_SUPPORTED         if file is not available.
 *          - \ref MTML_ERROR_UNKNOWN               if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLogSetConfiguration(const MtmlLogConfiguration *configuration);
 
/**
 * Gets the configuration of the MTML logger.
 *
 * @param configuration                             [out] The configuration of MTML logger.
 * @return
 *          - \ref MTML_SUCCESS                     if the configuration of the MTML logger has been get.
 *          - \ref MTML_ERROR_UNKNOWN               if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlLogGetConfiguration(MtmlLogConfiguration *configuration);

/***********************************/
/** @}
 */
/***********************************/

/***************************************************************************************************/
/** @defgroup mtml13 Error Reporting
 * This group introduces helper functions for error reporting routines.
 *  @{
 */
/***************************************************************************************************/

/**
 * Helper method for converting MTML error codes into readable strings.
 *
 * For all products.
 *
 * @param result                               MTML error code to convert.
 *
 * @return String representation of the error.
 *
 */
const MTML_API char* mtmlErrorString(MtmlReturn result);

/***********************************/
/** @}
 */
/***********************************/

/***************************************************************************************************/
/** @defgroup mtml14 MPC Functions
 * This chapter describes MTML operations that are associated with Multi Primary Core (MPC) management.
 *  @{
 */
/***************************************************************************************************/

/**
 * Sets MPC mode for the device. This mode determines whether an MPC instance can be created or a device can be configured.
 *
 * \b IMPORTANT: After calling this API, all opaque pointers (such as MtmlDevice, MtmlGpu, etc., excluding the MtmlLibrary pointer itself) 
 * allocated by the library will become invalid. Therefore, continuing to use those pointers will result in undefined behavior.
 * The user should free all of those pointers and shut down the library by calling the \ref mtmlLibraryShutdown API once this API call returns. 
 * Afterward, if needed, the user can re-initialize the library and obtain fresh opaque pointers as required, starting from a clean state.
 * 
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param device                                    [in] The identifier of the target device.
 * @param mode                                      [in] The mode to be set. See \ref MtmlMpcMode.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mode is set successfully.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a mode or is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceSetMpcMode(const MtmlDevice* device, MtmlMpcMode mode);

/**
 * Get MPC mode for the device.
 *
 * For CHUNXIAO or newer fully supported devices.
 *
 * @param device                                    [in] The identifier of the target device.
 * @param currentMode                               [out] Returns the current mode. See \ref MtmlMpcMode.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a currentMode has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a currentMode is invalid.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcMode(const MtmlDevice* device, MtmlMpcMode* currentMode);

/**
 * Get support profiles count for given device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported in Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param count                                     [out] Returns device's supported profiles number.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or \a profile is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceCountSupportedMpcProfiles(const MtmlDevice* parentDevice, unsigned int* count);

/**
 * Gets supported profiles for the given device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param count                                     [in] The size of buffer pointed by \a info. See \ref mtmlDeviceCountSupportedMpcProfiles.
 * @param info                                      [out] Returns the supported profile info.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a info has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a info is invalid.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a count is too small.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or \a profile is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetSupportedMpcProfiles(const MtmlDevice* parentDevice, unsigned int count, MtmlMpcProfile* info);

/**
 * Retrieves the number of supported configuration for the given device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param count                                     [out] The reference in which to return the number of configuration.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceCountSupportedMpcConfigurations(const MtmlDevice* parentDevice, unsigned int* count);

/**
 * Retrieve support configuration info for given device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param count                                     [in] The size of buffer pointed by \a info. see \ref mtmlDeviceCountSupportedMpcConfigurations.
 * @param info                                      [out] Returns the support configuration info.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a info has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a parentDevice or \a info is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a parentDevice does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a count is small.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetSupportedMpcConfigurations(const MtmlDevice* parentDevice, unsigned int count, MtmlMpcConfiguration* info);

/**
 * Retrieves current configuration info for the target device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param config                                    [out] Returns current configuration.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a config has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a parentDevice or \a config is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a parentDevice does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcConfiguration(const MtmlDevice* parentDevice, MtmlMpcConfiguration* config);

/**
 * Retrieves configuration info corresponding to the configuration name for the target device.
 * This interface will only return the configurations supported by the current device. See \ref mtmlDeviceGetSupportedMpcConfigurations.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param configName                                [in] Reference to the configuration name.
 * @param config                                    [out] Returns configuration.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a config has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a parentDevice, \a configName or \a config is NULL.
 *         - \ref MTML_ERROR_NOT_FOUND              if \a configName not found in the current device.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a parentDevice does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcConfigurationByName(const MtmlDevice* parentDevice, const char* configName, MtmlMpcConfiguration* config);

/**
 * Sets the effective MPC configuration of a device.
 * 
 * \b IMPORTANT: After calling this API, all opaque pointers (MtmlDevice, MtmlGpu, etc, but not including MtmlLibrary pointer itself) allocated 
 * by the library will become invalid, thus continuous using of those pointers is undefined behavior. 
 * The user shall properly free all those pointers and shutdown the library by calling \ref mtmlLibraryShutdown API once this API
 * returns. It is possible for the user to re-initialize the library then get opaque pointers as required just like a fresh start.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param id                                        [in] Point to configuration id.See \ref mtmlDeviceGetSupportedMpcConfigurations.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a id config successfully.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a parentDevice or \a id is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceSetMpcConfiguration(const MtmlDevice* parentDevice, unsigned int id);

/**
 * Get pre-existing MPC instances count for given profile ID.
 * 
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param profileId                                 [in] The profile ID. See \ref mtmlDeviceGetSupportProfile.
 * @param count                                     [out] Returns pre-existing MPC instances count with target profile ID.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device, \a profileId or \a count is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceCountMpcInstancesByProfileId(const MtmlDevice* parentDevice, unsigned int profileId, unsigned int* count);

/**
 * Get pre-existing MPC instances for given profile ID.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported in Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param profileId                                 [in] The profile ID. See \ref mtmlDeviceGetSupportProfile.
 * @param count                                     [in] The size of buffer pointed by \a mpcInstance.
                                                         See \ref mtmlDeviceCountMpcInstancesByProfileId.
 * @param mpcInstance                               [out] Returns pre-existing MPC instances with target profile ID.
 *
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mpcInstance has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device, \a profileId or \a mpcDevice is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a count is too small.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcInstancesByProfileId(const MtmlDevice* parentDevice, unsigned int profileId, unsigned int count, MtmlDevice** mpcInstance);

/**
 * Get pre-existing MPC instances count for given device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param count                                     [out] The count of pre-existing MPC instances.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a count are invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceCountMpcInstances(const MtmlDevice* parentDevice, unsigned int* count);

/**
 * Get pre-existing MPC instances for given device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param count                                     [in] The size of buffer pointed by by \a mpcInstance. See \ref mtmlDeviceCountMpcInstances.
 * @param mpcInstance                               [out] Returns pre-existing MPC devices.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mpcInstance has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a mpcInstance is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a count is too small.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcInstances(const MtmlDevice* parentDevice, unsigned int count, MtmlDevice** mpcInstance);

/**
 * Gets the MPC instance for the given index under its parent MPC device.
 *
 * If the MPC instance is destroyed, either explicitly or due to the destruction, resetting, or unbinding of the parent device, the request for the MPC instance must be made again.
 * resetting or unbinding the parent device must be requested again.
 * Handles may be reused and their properties can change in the process.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported in Linux only.
 *
 * @param parentDevice                              [in] Reference to the parent MPC device.
 * @param index                                     [in] Index of the MPC instance.
 * @param mpcInstance                               [out] Reference to the MPC instance.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mpcInstance has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device, \a index or \a mpcInstance is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not have MPC mode enabled or does not support MPC mode.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcInstanceByIndex(const MtmlDevice* parentDevice, unsigned int index, MtmlDevice** mpcInstance);

/**
 * Gets the MPC parent device from an MPC instance.
 * In certain environments, such as when libmtml is running in a container where the corresponding parent device is not mapped, 
 * this API may return an unknown error. However, it is important to note that the instance device itself should still function 
 * properly without any issues. In such cases, it becomes the responsibility of the caller application to decide how to interpret 
 * and handle the error appropriately.
 * 
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param mpcInstance                               [in] Reference to the MPC instance.
 * @param parentDevice                              [out] Reference to the MPC parent device.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a device has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mpcInstance or \a device is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a mpcInstance does not point to an MPC instance.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcParentDevice(const MtmlDevice* mpcInstance, MtmlDevice** parentDevice);

/**
 * Gets MPC instance's profile info.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param mpcInstance                               [in] Reference to the MPC instance.
 * @param profileInfo                               [out] MPC instance profile ID.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a profileInfo has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mpcInstance or \a profileInfo is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a mpcInstance does not point to an MPC instance.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcProfileInfo(const MtmlDevice* mpcInstance, MtmlMpcProfile* profileInfo);

/**
 * Gets MPC instance index under its parent device.
 *
 * For CHUNXIAO or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param mpcInstance                               [in] Reference to the MPC instance.
 * @param index                                     [out] The index of the MPC instance.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a index has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a mpcInstance or \a index is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a mpcInstance does not point to an MPC instance.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMpcInstanceIndex(const MtmlDevice* mpcInstance, unsigned int* index);

/***********************************/
/** @}
 */
 /***********************************/

/***************************************************************************************************/
/** @defgroup mtml15 MtLink Functions
 * This group introduces device MtLink functions.
 *  @{
 */
 /***************************************************************************************************/

/**
 * Retrieves MtLink specifications of a specified device.
 * For QUYUAN or newer fully supported devices.
 *
 * @param device                                    [in] The pointer to the target device.
 * @param spec                                      [out] The reference in which to return the specifications.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a spec has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a spec is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetMtLinkSpec(const MtmlDevice* device, MtmlMtLinkSpec* spec);

/**
 * Retrieves the state of the specified link.
 * For QUYUAN or newer fully supported devices.
 *
 * @param device                                    [in] The pointer to the target device.
 * @param linkId                                    [in] Specifies the link ID to be queried.
 * @param state                                     [out] \a MtmlMtlinkState where MTML_MTLINK_STATE_DOWN indicates that
 *                                                  the link is inactive and MTML_MTLINK_STATE_UP indicates it is active.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a state has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a state is NULL or \a linkId is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetMtLinkState(const MtmlDevice* device, unsigned int linkId, MtmlMtLinkState* state);

/**
* Retrieves the status of the requested capability for the specified link of a device.
* Refer to the \a MtmlMtLinkCap structure for the specific capabilities that can be queried.
*
* For QUYUAN or newer fully supported devices.
*
* @param device                                     [in] The pointer to the target device.
* @param linkId                                     [in] Specifies the link ID to be queried.
* @param capability                                 [in] Specifies the \a MtmlMtlinkCap to be queried.
* @param status                                     [out] The result indicating the availability status of the queried capability. See \ref MtmlMtlinkCapStatus.
*
* @return
*          - \ref MTML_SUCCESS                      if \a status has been populated.
*          - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or \a status is NULL.
*          - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not support this feature.
*          - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
*          - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
*/
MtmlReturn MTML_API mtmlDeviceGetMtLinkCapStatus(const MtmlDevice* device, unsigned int linkId, MtmlMtLinkCap capability, MtmlMtLinkCapStatus* status);

/**
* Retrieves the handle of a remote device directly connected via the specified link.
*
* For QUYUAN or newer fully supported devices.
*
* @param device                                     [in] The pointer to the target device.
* @param linkId                                     [in] Specifies the link ID to be queried.
* @param remoteDevice                               [out] The remote device handle.
*
* @return
*          - \ref MTML_SUCCESS                      if \a remoteDevice has been populated.
*          - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device or remoteDevice is NULL or \a linkId is invalid.
*          - \ref MTML_ERROR_NOT_SUPPORTED          if \a device does not support this feature.
*          - \ref MTML_ERROR_NOT_FOUND              if \a remoteDevice with \a linkId is not found.
*          - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
*          - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
*/
MtmlReturn MTML_API mtmlDeviceGetMtLinkRemoteDevice(const MtmlDevice* device, unsigned int linkId, MtmlDevice** remoteDevice);

/**
* Retrieves the number of shortest paths between two devices and the length of the path.
* The length of a path is defined as the number of nodes traversed from the local device to the remote device, including both the local device and the remote device themselves.
* For example, if the path is: localDevice -> device1 -> device2 -> remoteDevice, then \a pathLength is 4.
*
* For QUYUAN or newer fully supported devices.
*
* @param localDevice                                [in] The pointer to the local device.
* @param remoteDevice                               [in] The pointer to the remote device.
* @param pathCount                                  [out] Number of shortest paths between local and remote devices.
* @param pathLength                                 [out] Number of devices forming the shortest path.
*
* @return
*          - \ref MTML_SUCCESS                      if \a pathCount and \a pathLength has been populated.
*          - \ref MTML_ERROR_INVALID_ARGUMENT       if \a localDevice or \a remoteDevice or \a pathCount or \a pathLength is NULL.
*          - \ref MTML_ERROR_NOT_SUPPORTED          if \a localDevice or \a remoteDevice does not support this feature.
*          - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
*          - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
*/
MtmlReturn MTML_API mtmlDeviceCountMtLinkShortestPaths(const MtmlDevice* localDevice, const MtmlDevice* remoteDevice, unsigned int* pathCount, unsigned int* pathLength);

/**
* Retrieves all the shortest paths between two devices.
* Note: Each path is represented as a one-dimensional array of device handles, where the
* first element is the 'localDevice' handle and the subsequent elements are device handles forming the path
* until the last element, which is the 'remoteDevice' handle. For example, a path might be like: {localDevice, device1, device2, remoteDevice}
* To accommodate the output of this API, a 2-dimensional array of type MtmlDevice* is required.
* For a visual representation: MtmlDevice* path[pathCount][pathLength]. For \a pathCount and \a pathLength, see \ref mtmlDeviceCountMtlinkShortestPaths.
*
* For QUYUAN or newer fully supported devices.
*
* @param localDevice                                [in] The pointer to the local device.
* @param remoteDevice                               [in] The pointer to the remote device.
* @param pathCount                                  [in] Number of shortest paths between local and remote devices. See \ref mtmlDeviceCountMtlinkShortestPaths.
* @param pathLength                                 [in] Number of devices forming the shortest path. See \ref mtmlDeviceCountMtlinkShortestPaths.
* @param paths                                      [out] The reference in which to return the paths.
*
* @return
*          - \ref MTML_SUCCESS                      if \a paths has been populated.
*          - \ref MTML_ERROR_INVALID_ARGUMENT       if \a localDevice or \a remoteDevice or \a paths is NULL.
*          - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a pathCount or \a pathLength is too small.
*          - \ref MTML_ERROR_NOT_SUPPORTED          if \a localDevice or \a remoteDevice does not support this feature.
*          - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
*          - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
*/
MtmlReturn MTML_API mtmlDeviceGetMtLinkShortestPaths(const MtmlDevice* localDevice, const MtmlDevice* remoteDevice, unsigned int pathCount, unsigned int pathLength, MtmlDevice** paths);

/**
 * Retrieves the number of links between two directly connected devices.
 *
 * For QUYUAN or newer fully supported devices.
 *
 * @param localDevice                               [in] The pointer to the local device.
 * @param remoteDevice                              [in] The pointer to the remote device.
 * @param linkCount                                 [out] The reference where the number of links is stored.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a linkCount has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a localDevice or \a remoteDevice or \a linkCount is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a localDevice or \a remoteDevice does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceCountMtLinkLayouts(const MtmlDevice* localDevice, const MtmlDevice* remoteDevice, unsigned int* linkCount);

/**
 * Retrieves the links between two directly connected devices.
 *
 * For QUYUAN or newer fully supported devices.
 *
 * @param localDevice                               [in] The pointer to the local device.
 * @param remoteDevice                              [in] The pointer to the destination device.
 * @param linkCount                                 [in] The number of links.
 * @param layouts                                   [out] The buffer in which to return the links data.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a layouts has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a localDevice or \a remoteDevice or layouts is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a localDevice or \a remoteDevice does not support this feature.
 *         - \ref MTML_ERROR_INSUFFICIENT_SIZE      if \a linkCount is too small.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceGetMtLinkLayouts(const MtmlDevice* localDevice, const MtmlDevice* remoteDevice, unsigned int linkCount, MtmlMtLinkLayout* layouts);

/***********************************/
/** @}
 */
 /***********************************/

/***************************************************************************************************/
/** @defgroup mtml16 Affinity Functions
 * This group introduces device Affinity functions.
 *  @{
 */
 /***************************************************************************************************/

/**
 * Retrieves an array of unsigned ints (sized to nodeSetSize) of bitmasks with
 * the ideal memory affinity within for the device.
 * For example, if NUMA node 0, 1 are ideal for the device and nodeSetSize == 1,
 *     result[0] = 0x3.
 *
 * \note If requested scope is not applicable to the target topology, the API
 *       will fall back to reporting the memory affinity for the immediate non-I/O
 *       ancestor of the device.
 *
 * For SUDI or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param device                                    [in] The identifier of the target device.
 * @param nodeSetSize                               [in] The size of the nodeSet array that is safe to access.
 * @param nodeSet                                   [out] Array reference in which to return a bitmask of NODEs, 64 NODEs per
 *                                                  unsigned long on 64-bit machines, 32 on 32-bit machines.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a NUMA node Affinity has been filled.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device is invalid, nodeSetSize == 0, or nodeSet is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the device does not support this feature.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetMemoryAffinityWithinNode(const MtmlDevice* device, unsigned int nodeSetSize, unsigned long* nodeSet);

/**
 * Retrieves an array of unsigned ints (sized to cpuSetSize) of bitmasks with the ideal CPU affinity for the device.
 * For example, in 32-bit machines if processors 0, 1, 33, and 34 are ideal for the device and cpuSetSize == 2,
 *     result[0] = 0x3, result[1] = 0x6.
 *
 * For SUDI or newer fully supported devices.
 * Supported on Linux only.
 *
 * @param device                                    [in] The identifier of the target device.
 * @param cpuSetSize                                [in] The size of the cpuSet array that is safe to access.
 * @param cpuSet                                    [out] Array reference in which to return a bitmask of CPUs, 64 CPUs per
 *                                                      unsigned long on 64-bit machines, 32 on 32-bit machines.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a cpuSet has been filled.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device is invalid, cpuSetSize == 0, or cpuSet is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the device does not support this feature.
 *         - \ref MTML_ERROR_UNKNOWN                on any unexpected error.
 */
MtmlReturn MTML_API mtmlDeviceGetCpuAffinityWithinNode(const MtmlDevice* device, unsigned int cpuSetSize, unsigned long* cpuSet);


/**
 * Trigger reset of the whole Device.
 *
 * \b IMPORTANT: Before calling this API, make sure that there is no GPU load on the current environment.
 * 
 * For all devices.
 * Supported on Linux only.
 *
 * @param device                                    [in] The pointer of the target device.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if reset successed.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a device is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if the operation is not supported.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlDeviceReset(const MtmlDevice* device);

/**
 * Set the ECC mode for the memory.
 *
 * For PINGHU or newer fully supported devices.
 *
 * This operation takes effect after the next reboot.
 *
 * @param mem                                       [in] The identifier of the target memory.
 * @param mode                                      [in] The mode to be set. See \ref MtmlEccMode.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mode has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a memory is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a memory does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 *
 */
 MtmlReturn MTML_API mtmlMemorySetEccMode(const MtmlMemory* mem, MtmlEccMode mode);

/**
 * Retrieves the current and pending ECC modes for the memory.
 *
 * For PINGHU or newer fully supported devices.
 * 
 * Requires ECC Mode to be enabled.
 *
 * @param mem                                       [in] The identifier of the target memory.
 * @param currentMode                               [out] Reference in which to return the current ECC mode. See \ref MtmlEccMode.
 * @param pendingMode                               [out] Reference in which to return the pending state. See \ref MtmlEccMode.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a currentMode and \a pendingMode has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a memory or \a currentMode is NULL or \a pendingMode is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a memory does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetEccMode(const MtmlMemory* mem, MtmlEccMode *currentMode, MtmlEccMode *pendingMode);

/**
 * Get the retired pages count for given memory.
 *
 * For PINGHU or newer fully supported devices.
 * 
 * Requires ECC Mode to be enabled.
 *
 * @param mem                                       [in] The identifier of the target memory.
 * @param count                                     [out] Returns memory's retired pages' number.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a count has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a memory or \a count is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a memory does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetRetiredPagesCount(const MtmlMemory* mem, MtmlPageRetirementCount* count);

/**
 * Returns the list of retired pages by source, including pages that are pending retirement
 * The address information provided from this API is the hardware address of the page that was retired.
 *
 * For PINGHU or newer fully supported devices.
 * 
 * Requires ECC Mode to be enabled.
 *
 * @param mem                                       [in] The identifier of the target memory.
 * @param cause                                     [in] The cause of retirement. See \ref MtmlPageRetirementCause.
 * @param count                                     [in] The size of buffer pointed by \a pageRetirements. See \ref mtmlMemoryGetRetiredPagesCount.
 * @param pageRetirements                           [out] Reference in which to return the page retirement infos. See \ref MtmlPageRetirement.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a pageRetirements has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a memory or \a pageRetirements is NULL or \a cause or \a count is invalid.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a memory does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetRetiredPages(const MtmlMemory* mem, MtmlPageRetirementCause cause, unsigned int count, MtmlPageRetirement *pageRetirements);

/**
 * Verify if there are any pages awaiting retirement that require a reboot to complete the process.
 *
 * For PINGHU or newer fully supported devices.
 * 
 * Requires ECC Mode to be enabled.
 *
 * @param mem                                       [in] The identifier of the target memory.
 * @param isPending                                 [out] Reference in which to return the pending status. See \ref MtmlRetiredPagesPendingState.
 * 
 * @return
 *         - \ref MTML_SUCCESS                      if \a isPending has been populated.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a memory or \a isPending is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a memory does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 */
MtmlReturn MTML_API mtmlMemoryGetRetiredPagesPendingStatus(const MtmlMemory* mem, MtmlRetiredPagesPendingState *isPending);
 
/**
 * Retrieves the requested memory ecc error counter for the device.
 * 
 * For PINGHU or newer fully supported devices.
 * 
 * Requires ECC Mode to be enabled.
 *
 * @param mem                                  The identifier of the target memory
 * @param errorType                            Flag that specifies the type of the errors.
 * @param counterType                          Flag that specifies the counter-type of the errors.
 * @param locationType                         Specifies the bitmasks of the location of the counter.
 * @param eccCounts                            Reference in which to return the specified ECC errors
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mode has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a memory is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a memory does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 *
 */
MtmlReturn MTML_API mtmlMemoryGetEccErrorCounter(const MtmlMemory* mem, MtmlMemoryErrorType errorType, MtmlEccCounterType counterType, MtmlMemoryLocation locationType, unsigned long long* eccCounts);

/**
 * Clear the ECC error and other memory error counts for the memory.
 *
 * For PINGHU or newer fully supported devices.
 *
 * Requires ECC Mode to be enabled.
 *
 * Sets all of the specified ECC counters to 0, including both detailed and total counts.
 *
 * This operation takes effect immediately.
 *
 * @param mem                                       [in] The identifier of the target memory.
 * @param counterType                               [in] Flag that indicates which type of errors should be cleared.
 *
 * @return
 *         - \ref MTML_SUCCESS                      if \a mode has been set.
 *         - \ref MTML_ERROR_INVALID_ARGUMENT       if \a memory is NULL.
 *         - \ref MTML_ERROR_NOT_SUPPORTED          if \a memory does not support this feature.
 *         - \ref MTML_ERROR_DRIVER_FAILURE         if any error occurred when accessing the driver.
 *         - \ref MTML_ERROR_DRIVER_TOO_OLD         if the driver version is too old.
 *         - \ref MTML_ERROR_DRIVER_TOO_NEW         if the driver version is too new.
 *         - \ref MTML_ERROR_UNKNOWN                if any unexpected error occurred.
 *
 */
MtmlReturn MTML_API mtmlMemoryClearEccErrorCounts(const MtmlMemory* mem, MtmlEccCounterType counterType);

/***********************************/
/** @}
 */
 /***********************************/

#ifdef __cplusplus
}   // extern "C"
#endif

#endif // MTML_H_
