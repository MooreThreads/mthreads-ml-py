##
# Python bindings for the MTML library
##
from __future__ import annotations

import string
import sys
import threading
from ctypes import *
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING as _TYPE_CHECKING
from contextlib import contextmanager

if _TYPE_CHECKING:
    from typing_extensions import TypeAlias as _TypeAlias  # Python 3.10+

## C Type mappings ##
## Constants
MTML_LIBRARY_VERSION_BUFFER_SIZE = 32
MTML_DRIVER_VERSION_BUFFER_SIZE = 80
MTML_DEVICE_NAME_BUFFER_SIZE = 32
MTML_DEVICE_UUID_BUFFER_SIZE = 48
MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE = 64
MTML_DEVICE_VBIOS_VERSION_BUFFER_SIZE = MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE
MTML_DEVICE_PATH_BUFFER_SIZE = 64
MTML_DEVICE_PCI_SBDF_BUFFER_SIZE = 32
MTML_VIRT_TYPE_ID_BUFFER_SIZE = 16
MTML_VIRT_TYPE_CLASS_BUFFER_SIZE = 32
MTML_VIRT_TYPE_NAME_BUFFER_SIZE = 32
MTML_VIRT_TYPE_API_BUFFER_SIZE = 16
MTML_LOG_FILE_PATH_BUFFER_SIZE = 200
MTML_MPC_PROFILE_NAME_BUFFER_SIZE = 32
MTML_MPC_CONF_NAME_BUFFER_SIZE = 32
MTML_MPC_CONF_MAX_PROF_NUM = 16
MTML_DEVICE_SLOT_NAME_BUFFER_SIZE = 32
MTML_MEMORY_VENDOR_BUFFER_SIZE = 64
MTML_DEVICE_SERIAL_NUMBER_BUFFER_SIZE = 64
MTML_SYSTEM_DRIVER_VERSION_BUFFER_SIZE = 80
MTML_DEVICE_PCI_BUS_ID_BUFFER_SIZE = 32

## Enums
_mtmlReturn_t = c_uint
MTML_SUCCESS = 0
MTML_ERROR_DRIVER_NOT_LOADED = 1
MTML_ERROR_DRIVER_FAILURE = 2
MTML_ERROR_INVALID_ARGUMENT = 3
MTML_ERROR_NOT_SUPPORTED = 4
MTML_ERROR_NO_PERMISSION = 5
MTML_ERROR_INSUFFICIENT_SIZE = 6
MTML_ERROR_NOT_FOUND = 7
MTML_ERROR_INSUFFICIENT_MEMORY = 8
MTML_ERROR_DRIVER_TOO_OLD = 9
MTML_ERROR_DRIVER_TOO_NEW = 10
MTML_ERROR_TIMEOUT = 11
MTML_ERROR_RESOURCE_IS_BUSY = 12
MTML_ERROR_UNKNOWN = 999
# Additional error codes for compatibility
MTML_ERROR_UNINITIALIZED = 666
MTML_ERROR_FUNCTION_NOT_FOUND = 667
MTML_ERROR_GPU_IS_LOST = 669
MTML_ERROR_LIBRARY_NOT_FOUND = 670

_mtmlBrandType_t = c_uint
MTML_BRAND_MTT = 0
MTML_BRAND_UNKNOWN = 1
MTML_BRAND_COUNT = 2

_mtmlMemoryType_t = c_uint
MTML_MEM_TYPE_LPDDR4 = 0
MTML_MEM_TYPE_GDDR6 = 1

_mtmlCodecType_t = c_uint
MTML_CODEC_TYPE_AVC = 0
MTML_CODEC_TYPE_VC1 = 1
MTML_CODEC_TYPE_MPEG2 = 2
MTML_CODEC_TYPE_MPEG4 = 3
MTML_CODEC_TYPE_H263 = 4
MTML_CODEC_TYPE_DIV3 = 5
MTML_CODEC_TYPE_RV = 6
MTML_CODEC_TYPE_AVS = 7
MTML_CODEC_TYPE_RSVD1 = 8
MTML_CODEC_TYPE_THO = 9
MTML_CODEC_TYPE_VP3 = 10
MTML_CODEC_TYPE_VP8 = 11
MTML_CODEC_TYPE_HEVC = 12
MTML_CODEC_TYPE_VP9 = 13
MTML_CODEC_TYPE_AVS2 = 14
MTML_CODEC_TYPE_RSVD2 = 15
MTML_CODEC_TYPE_AV1 = 16
MTML_CODEC_TYPE_COUNT = 17

_mtmlCodecSessionState_t = c_uint
MTML_CODEC_SESSION_STATE_UNKNOWN = -1
MTML_CODEC_SESSION_STATE_IDLE = 0
MTML_CODEC_SESSION_STATE_ACTIVE = 1
MTML_CODEC_SESSION_STATE_COUNT = 2

_mtmlVirtCapability_t = c_uint
MTML_DEVICE_NOT_SUPPORT_VIRTUALIZATION = 0
MTML_DEVICE_SUPPORT_VIRTUALIZATION = 1

_mtmlVirtRole_t = c_uint
MTML_VIRT_ROLE_NONE = 0
MTML_VIRT_ROLE_HOST_VIRTDEVICE = 1
MTML_VIRT_ROLE_GUEST_VIRTDEVICE = 2
MTML_VIRT_ROLE_COUNT = 3

_mtmlDeviceTopologyLevel_t = c_uint
MTML_TOPOLOGY_INTERNAL = 0
MTML_TOPOLOGY_SINGLE = 1
MTML_TOPOLOGY_MULTIPLE = 2
MTML_TOPOLOGY_HOSTBRIDGE = 3
MTML_TOPOLOGY_NODE = 4
MTML_TOPOLOGY_SYSTEM = 5

_mtmlLogLevel_t = c_uint
MTML_LOG_LEVEL_OFF = 0
MTML_LOG_LEVEL_FATAL = 1
MTML_LOG_LEVEL_ERROR = 2
MTML_LOG_LEVEL_WARNING = 3
MTML_LOG_LEVEL_INFO = 4

_mtmlMpcMode_t = c_uint
MTML_DEVICE_MPC_DISABLE = 0
MTML_DEVICE_MPC_ENABLE = 1

_mtmlMpcCapability_t = c_uint
MTML_DEVICE_NOT_SUPPORT_MPC = 0
MTML_DEVICE_SUPPORT_MPC = 1

_mtmlMpcType_t = c_uint
MTML_MPC_TYPE_NONE = 0
MTML_MPC_TYPE_PARENT = 1
MTML_MPC_TYPE_INSTANCE = 2

_mtmlDeviceP2PStatus_t = c_uint
MTML_P2P_STATUS_OK = 0
MTML_P2P_STATUS_CHIPSET_NOT_SUPPORTED = 1
MTML_P2P_STATUS_GPU_NOT_SUPPORTED = 2
MTML_P2P_STATUS_UNKNOWN = 3

_mtmlDeviceP2PCaps_t = c_uint
MTML_P2P_CAPS_READ = 0
MTML_P2P_CAPS_WRITE = 1

_mtmlGpuEngine_t = c_uint
MTML_GPU_ENGINE_GEOMETRY = 0
MTML_GPU_ENGINE_2D = 1
MTML_GPU_ENGINE_3D = 2
MTML_GPU_ENGINE_COMPUTE = 3
MTML_GPU_ENGINE_MAX = 4

_mtmlEccMode_t = c_uint
MTML_MEMORY_ECC_DISABLE = 0
MTML_MEMORY_ECC_ENABLE = 1

_mtmlPageRetirementCause_t = c_uint
MTML_PAGE_RETIREMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS = 0
MTML_PAGE_RETIREMENT_CAUSE_DOUBLE_BIT_ECC_ERROR = 1
MTML_PAGE_RETIREMENT_CAUSE_MAX = 2

_mtmlRetiredPagesPendingState_t = c_uint
MTML_RETIRED_PAGES_PENDING_STATE_FALSE = 0
MTML_RETIRED_PAGES_PENDING_STATE_TRUE = 1

_mtmlEccCounterType_t = c_uint
MTML_VOLATILE_ECC = 0
MTML_AGGREGATE_ECC = 1
MTML_ECC_COUNTER_TYPE_COUNT = 2

_mtmlMemoryErrorType_t = c_uint
MTML_MEMORY_ERROR_TYPE_CORRECTED = 0
MTML_MEMORY_ERROR_TYPE_UNCORRECTED = 1
MTML_MEMORY_ERROR_TYPE_COUNT = 2

_mtmlMemoryLocation_t = c_uint
MTML_MEMORY_LOCATION_DRAM = 0x1

_mtmlDispIntfType_t = c_uint
MTML_DISP_INTF_TYPE_DP = 0
MTML_DISP_INTF_TYPE_EDP = 1
MTML_DISP_INTF_TYPE_VGA = 2
MTML_DISP_INTF_TYPE_HDMI = 3
MTML_DISP_INTF_TYPE_LVDS = 4
MTML_DISP_INTF_TYPE_MAX = 5

_mtmlMtLinkState_t = c_uint
MTML_MTLINK_STATE_DOWN = 0
MTML_MTLINK_STATE_UP = 1
MTML_MTLINK_STATE_DOWNGRADE = 2


## Library structures
class struct_c_mtmlLibrary_t(Structure):
    pass  # opaque handle


c_mtmlLibrary_t = POINTER(struct_c_mtmlLibrary_t)


## Device structures
class struct_c_mtmlDevice_t(Structure):
    pass  # opaque handle


c_mtmlDevice_t = POINTER(struct_c_mtmlDevice_t)


## FieldValue structures(for nvmlFieldValue_t)
class struct_c_mtmlFieldValue_t(Structure):
    pass  # opaque handle


c_mtmlFieldValue_t = POINTER(struct_c_mtmlFieldValue_t)


## System structures
class struct_c_mtmlSystem_t(Structure):
    pass  # opaque handle


c_mtmlSystem_t = POINTER(struct_c_mtmlSystem_t)


## Memory structures
class struct_c_mtmlMemory_t(Structure):
    pass  # opaque handle


c_mtmlMemory_t = POINTER(struct_c_mtmlMemory_t)


## Gpu structures
class struct_c_mtmlGpu_t(Structure):
    pass  # opaque handle


c_mtmlGpu_t = POINTER(struct_c_mtmlGpu_t)


## Vpu structures
class struct_c_mtmlVpu_t(Structure):
    pass


c_mtmlVpu_t = POINTER(struct_c_mtmlVpu_t)


class mtmlFriendlyObject(object):
    def __init__(self, dictionary):
        for x in dictionary:
            setattr(self, x, dictionary[x])

    def __str__(self):
        return self.__dict__.__str__()


def mtmlStructToFriendlyObject(struct):
    d = {}
    for x in struct._fields_:
        key = x[0]
        value = getattr(struct, key)
        # only need to convert from bytes if bytes, no need to check python version.
        d[key] = value.decode() if isinstance(value, bytes) else value
    obj = mtmlFriendlyObject(d)
    return obj


class _PrintableStructure(Structure):
    """
    Abstract class that produces nicer __str__ output than ctypes.Structure.
    e.g. instead of:
      >>> print str(obj)
      <class_name object at 0x7fdf82fef9e0>
    this class will print
      class_name(field_name: formatted_value, field_name: formatted_value)

    _fmt_ dictionary of <str _field_ name> -> <str format>
    e.g. class that has _field_ 'hex_value', c_uint could be formatted with
      _fmt_ = {"hex_value" : "%08X"}
    to produce nicer output.
    Default formatting string for all fields can be set with key "<default>" like:
      _fmt_ = {"<default>" : "%d MHz"} # e.g all values are numbers in MHz.
    If not set it's assumed to be just "%s"

    Exact format of returned str from this class is subject to change in the future.
    """

    _fmt_ = {}

    def __str__(self):
        result = []
        for x in self._fields_:
            key = x[0]
            value = getattr(self, key)
            fmt = "%s"
            if key in self._fmt_:
                fmt = self._fmt_[key]
            elif "<default>" in self._fmt_:
                fmt = self._fmt_["<default>"]
            result.append(("%s: " + fmt) % (key, value))
        return self.__class__.__name__ + "(" + ", ".join(result) + ")"

    def __getattribute__(self, name):
        res = super(_PrintableStructure, self).__getattribute__(name)
        # need to convert bytes to unicode for python3 don't need to for python2
        # Python 2 strings are of both str and bytes
        # Python 3 strings are not of type bytes
        # ctypes should convert everything to the correct values otherwise
        if isinstance(res, bytes):
            if isinstance(res, str):
                return res
            return res.decode()
        return res

    def __setattr__(self, name, value):
        if isinstance(value, str):
            # encoding a python2 string returns the same value, since python2 strings are bytes already
            # bytes passed in python3 will be ignored.
            value = value.encode()
        super(_PrintableStructure, self).__setattr__(name, value)


## MtLink structures
class c_mtmlMtLinkSpec_t(_PrintableStructure):
    _fields_ = [
        ("version", c_uint),
        ("bandWidth", c_uint),
        ("linkNum", c_uint),
        ("rsvd", c_uint * 4),
    ]


class c_mtmlPciInfo_t(_PrintableStructure):
    _fields_ = [
        ("sbdf", c_char * MTML_DEVICE_PCI_SBDF_BUFFER_SIZE),
        ("segment", c_uint),
        ("bus", c_uint),
        ("device", c_uint),
        ("pciDeviceId", c_uint),
        ("busWidth", c_uint),
        ("pciMaxSpeed", c_float),
        ("pciCurSpeed", c_float),
        ("pciMaxWidth", c_uint),
        ("pciCurWidth", c_uint),
        ("pciMaxGen", c_uint),
        ("pciCurGen", c_uint),
        ("busId", c_char * MTML_DEVICE_PCI_BUS_ID_BUFFER_SIZE),
        ("rsvd", c_uint * 6),
    ]


## Device property structure
class c_mtmlDeviceProperty_t(_PrintableStructure):
    _fields_ = [
        ("virtCapability", c_uint),
        ("virtRole", c_uint),
        ("mpcCapability", c_uint),
        ("mpcType", c_uint),
        ("rsvd", c_uint * 12),
    ]


## PCI slot info structure
class c_mtmlPciSlotInfo_t(_PrintableStructure):
    _fields_ = [
        ("slotType", c_uint),
        ("slotName", c_char * MTML_DEVICE_SLOT_NAME_BUFFER_SIZE),
        ("rsvd", c_uint * 4),
    ]


## Display interface spec structure
class c_mtmlDispIntfSpec_t(_PrintableStructure):
    _fields_ = [
        ("type", c_uint),
        ("maxResWidth", c_uint),
        ("maxResHeight", c_uint),
        ("rsvd", c_uint * 4),
    ]


## Virtualization type structure
class c_mtmlVirtType_t(_PrintableStructure):
    _fields_ = [
        ("id", c_char * MTML_VIRT_TYPE_ID_BUFFER_SIZE),
        ("deviceClass", c_char * MTML_VIRT_TYPE_CLASS_BUFFER_SIZE),
        ("name", c_char * MTML_VIRT_TYPE_NAME_BUFFER_SIZE),
        ("maxInstances", c_uint),
        ("memSize", c_ulonglong),
        ("gpuCores", c_uint),
        ("maxResWidth", c_uint),
        ("maxResHeight", c_uint),
        ("apiType", c_char * MTML_VIRT_TYPE_API_BUFFER_SIZE),
        ("encoderNum", c_uint),
        ("decoderNum", c_uint),
        ("rsvd", c_uint * 4),
    ]


## Codec utilization structure
class c_mtmlCodecUtil_t(_PrintableStructure):
    _fields_ = [
        ("encodeUtil", c_uint),
        ("decodeUtil", c_uint),
        ("rsvd", c_uint * 4),
    ]


## Codec session state structure
class c_mtmlCodecSessionState_t(_PrintableStructure):
    _fields_ = [
        ("sessionId", c_uint),
        ("state", c_uint),
        ("rsvd", c_uint * 4),
    ]


## Codec session metrics structure
class c_mtmlCodecSessionMetrics_t(_PrintableStructure):
    _fields_ = [
        ("width", c_uint),
        ("height", c_uint),
        ("codecType", c_uint),
        ("fps", c_uint),
        ("rsvd", c_uint * 4),
    ]


## Log configuration structure
class c_mtmlLogConfiguration_t(_PrintableStructure):
    _fields_ = [
        ("filePath", c_char * MTML_LOG_FILE_PATH_BUFFER_SIZE),
        ("maxSize", c_uint),
        ("logLevel", c_uint),
        ("rsvd", c_uint * 4),
    ]


## MPC profile structure
class c_mtmlMpcProfile_t(_PrintableStructure):
    _fields_ = [
        ("profileId", c_uint),
        ("name", c_char * MTML_MPC_PROFILE_NAME_BUFFER_SIZE),
        ("memSize", c_ulonglong),
        ("gpuCores", c_uint),
        ("rsvd", c_uint * 4),
    ]


## MPC configuration structure
class c_mtmlMpcConfiguration_t(_PrintableStructure):
    _fields_ = [
        ("id", c_uint),
        ("name", c_char * MTML_MPC_CONF_NAME_BUFFER_SIZE),
        ("profileNum", c_uint),
        ("profileIds", c_uint * MTML_MPC_CONF_MAX_PROF_NUM),
        ("rsvd", c_uint * 4),
    ]


## MtLink layout structure
class c_mtmlMtLinkLayout_t(_PrintableStructure):
    _fields_ = [
        ("localLinkId", c_uint),
        ("remoteLinkId", c_uint),
        ("rsvd", c_uint * 4),
    ]


## Page retirement count structure
class c_mtmlPageRetirementCount_t(_PrintableStructure):
    _fields_ = [
        ("singleBitEcc", c_uint),
        ("doubleBitEcc", c_uint),
        ("rsvd", c_uint * 4),
    ]


## Page retirement structure
class c_mtmlPageRetirement_t(_PrintableStructure):
    _fields_ = [
        ("address", c_ulonglong),
        ("timestamp", c_ulonglong),
        ("rsvd", c_uint * 4),
    ]


## Lib loading ##
mtmlLib = None
libLoadLock = threading.Lock()
libHandle = c_mtmlLibrary_t()
_mtmlLib_refcount = 0  # Incremented on each mtmlInit and decremented on mtmlShutdown


## Error Checking ##
class MTMLError(Exception):
    _valClassMapping = dict()
    # List of currently known error codes
    _errcode_to_string = {
        MTML_ERROR_UNINITIALIZED: "Uninitialized",
        MTML_ERROR_NOT_SUPPORTED: "Not Supported",
        MTML_ERROR_FUNCTION_NOT_FOUND: "Function Not Found",
        MTML_ERROR_UNKNOWN: "Unknown Error",
        MTML_ERROR_INSUFFICIENT_SIZE: "Insufficient Size",
        MTML_ERROR_GPU_IS_LOST: "Gpu Is Lost",
        MTML_ERROR_LIBRARY_NOT_FOUND: "Library Not Found",
        MTML_ERROR_NO_PERMISSION: "No Permission",
        MTML_ERROR_NOT_FOUND: "Not Found",
    }

    def __new__(typ, value):
        """
        Maps value to a proper subclass of MTMLError.
        See _extractMTMLErrorsAsClasses function for more details
        """
        if typ == MTMLError:
            typ = MTMLError._valClassMapping.get(value, typ)
        obj = Exception.__new__(typ)
        obj.value = value
        return obj

    def __str__(self):
        try:
            if self.value not in MTMLError._errcode_to_string:
                MTMLError._errcode_to_string[self.value] = str(
                    mtmlErrorString(self.value)
                )
            return MTMLError._errcode_to_string[self.value]
        except MTMLError:
            return "MTML Error with code %d" % self.value

    def __eq__(self, other):
        return self.value == other.value


def _extractMTMLErrorsAsClasses():
    """
    Generates a hierarchy of classes on top of MTMLError class.

    Each MTML Error gets a new MTMLError subclass. This way try,except blocks can filter appropriate
    exceptions more easily.

    MTMLError is a parent class. Each MTML_ERROR_* gets it's own subclass.
    e.g. MTML_ERROR_ALREADY_INITIALIZED will be turned into MTMLError_AlreadyInitialized
    """
    this_module = sys.modules[__name__]
    mtmlErrorsNames = [x for x in dir(this_module) if x.startswith("MTML_ERROR_")]
    for err_name in mtmlErrorsNames:
        # e.g. Turn MTML_ERROR_ALREADY_INITIALIZED into MTMLError_AlreadyInitialized
        class_name = "MTMLError_" + string.capwords(
            err_name.replace("MTML_ERROR_", ""), "_"
        ).replace("_", "")
        err_val = getattr(this_module, err_name)

        def gen_new(val):
            def new(typ, *args):
                obj = MTMLError.__new__(typ, val)
                return obj

            return new

        new_error_class = type(class_name, (MTMLError,), {"__new__": gen_new(err_val)})
        new_error_class.__module__ = __name__
        setattr(this_module, class_name, new_error_class)
        MTMLError._valClassMapping[err_val] = new_error_class


_extractMTMLErrorsAsClasses()


def _mtmlCheckReturn(ret):
    if ret != MTML_SUCCESS:
        raise MTMLError(ret)
    return ret


## Function access ##
_mtmlGetFunctionPointer_cache = (
    dict()
)  # function pointers are cached to prevent unnecessary libLoadLock locking


def _mtmlGetFunctionPointer(name):
    global mtmlLib

    if name in _mtmlGetFunctionPointer_cache:
        return _mtmlGetFunctionPointer_cache[name]

    libLoadLock.acquire()
    try:
        # ensure library was loaded
        if mtmlLib == None:
            raise MTMLError(MTML_ERROR_FUNCTION_NOT_FOUND)
        try:
            _mtmlGetFunctionPointer_cache[name] = getattr(mtmlLib, name)
            return _mtmlGetFunctionPointer_cache[name]
        except AttributeError:
            raise MTMLError(MTML_ERROR_FUNCTION_NOT_FOUND)
    finally:
        # lock is always freed
        libLoadLock.release()


## string/bytes conversion for ease of use
def convertStrBytes(func):
    """
    In python 3, strings are unicode instead of bytes, and need to be converted for ctypes
    Args from caller: (1, 'string', <__main__.c_mtmlDevice_t at 0xFFFFFFFF>)
    Args passed to function: (1, b'string', <__main__.c_mtmlDevice_t at 0xFFFFFFFF)>
    ----
    Returned from function: b'returned string'
    Returned to caller: 'returned string'
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # encoding a str returns bytes in python 2 and 3
        args = [arg.encode() if isinstance(arg, str) else arg for arg in args]
        res = func(*args, **kwargs)
        # In python 2, str and bytes are the same
        # In python 3, str is unicode and should be decoded.
        # Ctypes handles most conversions, this only effects c_char and char arrays.
        if isinstance(res, bytes):
            if isinstance(res, str):
                return res
            return res.decode()
        return res

    if sys.version_info >= (3,):
        return wrapper
    return func


## C function wrappers ##
def _LoadMtmlLibrary():
    """
    Load the library if it isn't loaded already
    """
    global mtmlLib

    if mtmlLib == None:
        # lock to ensure only one caller loads the library
        libLoadLock.acquire()

        try:
            # ensure the library still isn't loaded
            if mtmlLib == None:
                try:
                    # assume linux
                    mtmlLib = CDLL("libmtml.so")
                except OSError as ose:
                    _mtmlCheckReturn(MTML_ERROR_FUNCTION_NOT_FOUND)
                if mtmlLib == None:
                    _mtmlCheckReturn(MTML_ERROR_FUNCTION_NOT_FOUND)
        finally:
            # lock is always freed
            libLoadLock.release()


def mtmlLibraryInit():
    _LoadMtmlLibrary()

    #
    # Initialize the library
    #
    global libHandle
    fn = _mtmlGetFunctionPointer("mtmlLibraryInit")
    ret = fn(byref(libHandle))
    _mtmlCheckReturn(ret)

    # Atomically update refcount
    global _mtmlLib_refcount
    libLoadLock.acquire()
    _mtmlLib_refcount += 1
    libLoadLock.release()
    return None


def mtmlLibraryShutDown():
    #
    # Leave the library loaded, but shutdown the interface
    #
    global libHandle
    if libHandle is None:
        return None

    fn = _mtmlGetFunctionPointer("mtmlLibraryShutDown")
    ret = fn(libHandle)
    _mtmlCheckReturn(ret)

    # Reset libHandle to a fresh instance to allow reinitialization
    # and prevent dangling references during garbage collection
    libHandle = c_mtmlLibrary_t()

    # Atomically update refcount
    global _mtmlLib_refcount
    libLoadLock.acquire()
    if 0 < _mtmlLib_refcount:
        _mtmlLib_refcount -= 1
    libLoadLock.release()
    return None


@convertStrBytes
def mtmlErrorString(result):
    fn = _mtmlGetFunctionPointer("mtmlErrorString")
    fn.restype = c_char_p  # otherwise return is an int
    ret = fn(result)
    return ret


def mtmlLibraryCountDevice():
    global libHandle
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlLibraryCountDevice")
    ret = fn(libHandle, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlLibraryInitDeviceByIndex(index):
    global libHandle
    c_index = c_uint(index)
    c_device = c_mtmlDevice_t()
    fn = _mtmlGetFunctionPointer("mtmlLibraryInitDeviceByIndex")
    ret = fn(libHandle, c_index, byref(c_device))
    _mtmlCheckReturn(ret)
    return c_device


@convertStrBytes
def mtmlLibraryInitDeviceByUuid(uuid):
    global libHandle
    c_uuid = c_char_p(uuid)
    c_device = c_mtmlDevice_t()
    fn = _mtmlGetFunctionPointer("mtmlLibraryInitDeviceByUuid")
    ret = fn(libHandle, c_uuid, byref(c_device))
    _mtmlCheckReturn(ret)
    return c_device


@convertStrBytes
def mtmlLibraryInitDeviceByPciSbdf(pciSbdf):
    global libHandle
    c_pciSbdf = c_char_p(pciSbdf)
    c_device = c_mtmlDevice_t()
    fn = _mtmlGetFunctionPointer("mtmlLibraryInitDeviceByPciSbdf")
    ret = fn(libHandle, c_pciSbdf, byref(c_device))
    _mtmlCheckReturn(ret)
    return c_device


def mtmlLibraryInitSystem():
    global libHandle
    c_system = c_mtmlSystem_t()
    fn = _mtmlGetFunctionPointer("mtmlLibraryInitSystem")
    ret = fn(libHandle, byref(c_system))
    _mtmlCheckReturn(ret)
    return c_system


def mtmlDeviceInitMemory(device):
    global libHandle
    c_memory = c_mtmlMemory_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceInitMemory")
    ret = fn(device, byref(c_memory))
    _mtmlCheckReturn(ret)
    return c_memory


def mtmlDeviceInitGpu(device):
    global libHandle
    c_gpu = c_mtmlGpu_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceInitGpu")
    ret = fn(device, byref(c_gpu))
    _mtmlCheckReturn(ret)
    return c_gpu


def mtmlDeviceInitVpu(device):
    global libHandle
    c_vpu = c_mtmlVpu_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceInitVpu")
    ret = fn(device, byref(c_vpu))
    _mtmlCheckReturn(ret)
    return c_vpu


def mtmlDeviceGetIndex(device):
    global libHandle
    c_index = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetIndex")
    ret = fn(device, byref(c_index))
    _mtmlCheckReturn(ret)
    return c_index.value


@convertStrBytes
def mtmlDeviceGetName(device):
    global libHandle
    c_name = create_string_buffer(MTML_DEVICE_NAME_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetName")
    ret = fn(device, c_name, c_uint(MTML_DEVICE_NAME_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_name.value


def mtmlDeviceGetPciInfo(device):
    global libHandle
    c_pciinfo = c_mtmlPciInfo_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetPciInfo")
    ret = fn(device, byref(c_pciinfo))
    _mtmlCheckReturn(ret)
    # If busId is empty or invalid (contains non-printable chars), fill it with sbdf
    bus_id = c_pciinfo.busId
    if not bus_id or not bus_id[0].isalnum():
        c_pciinfo.busId = c_pciinfo.sbdf
    return c_pciinfo

@convertStrBytes
def mtmlDeviceGetSerialNumber(device):
    global libHandle
    c_serial = create_string_buffer(MTML_DEVICE_SERIAL_NUMBER_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetSerialNumber")
    ret = fn(device, c_uint(MTML_DEVICE_SERIAL_NUMBER_BUFFER_SIZE), c_serial)
    _mtmlCheckReturn(ret)
    return c_serial.value


def mtmlDeviceGetPowerUsage(device):
    global libHandle
    c_power = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetPowerUsage")
    ret = fn(device, byref(c_power))
    _mtmlCheckReturn(ret)
    return c_power.value


@convertStrBytes
def mtmlDeviceGetUUID(device):
    c_uuid = (c_char * MTML_DEVICE_UUID_BUFFER_SIZE)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetUUID")
    ret = fn(device, byref(c_uuid), MTML_DEVICE_UUID_BUFFER_SIZE)
    _mtmlCheckReturn(ret)
    return c_uuid.value


def mtmlDeviceGetMtLinkSpec(device):
    c_mtLinkSpec = c_mtmlMtLinkSpec_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMtLinkSpec")
    ret = fn(device, byref(c_mtLinkSpec))
    _mtmlCheckReturn(ret)
    return c_mtLinkSpec


def mtmlDeviceGetMtLinkState(device, linkIndex):
    c_mtLinkState = _mtmlMtLinkState_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMtLinkState")
    ret = fn(device, linkIndex, byref(c_mtLinkState))
    _mtmlCheckReturn(ret)
    return c_mtLinkState.value


def mtmlDeviceGetMtLinkRemoteDevice(device, linkIndex):
    c_device = c_mtmlDevice_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMtLinkRemoteDevice")
    ret = fn(device, linkIndex, byref(c_device))
    _mtmlCheckReturn(ret)
    return c_device


def mtmlMemoryGetTotal(memory):
    global libHandle
    c_total = c_uint64()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetTotal")
    ret = fn(memory, byref(c_total))
    _mtmlCheckReturn(ret)
    return c_total.value


def mtmlMemoryGetUsed(memory):
    global libHandle
    c_used = c_uint64()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetUsed")
    ret = fn(memory, byref(c_used))
    _mtmlCheckReturn(ret)
    return c_used.value


def mtmlMemoryGetClock(memory):
    global libHandle
    c_clock = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetClock")
    ret = fn(memory, byref(c_clock))
    _mtmlCheckReturn(ret)
    return c_clock.value


def mtmlMemoryGetMaxClock(memory):
    global libHandle
    c_clock = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetMaxClock")
    ret = fn(memory, byref(c_clock))
    _mtmlCheckReturn(ret)
    return c_clock.value


def mtmlMemoryGetUtilization(memory):
    global libHandle
    utilization = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetUtilization")
    ret = fn(memory, byref(utilization))
    _mtmlCheckReturn(ret)
    return utilization.value


def mtmlGpuGetUtilization(gpu):
    global libHandle
    utilization = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlGpuGetUtilization")
    ret = fn(gpu, byref(utilization))
    _mtmlCheckReturn(ret)
    return utilization.value


def mtmlGpuGetClock(gpu):
    global libHandle
    c_clock = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlGpuGetClock")
    ret = fn(gpu, byref(c_clock))
    _mtmlCheckReturn(ret)
    return c_clock.value


def mtmlGpuGetMaxClock(gpu):
    global libHandle
    c_clock = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlGpuGetMaxClock")
    ret = fn(gpu, byref(c_clock))
    _mtmlCheckReturn(ret)
    return c_clock.value


def mtmlGpuGetTemperature(gpu):
    global libHandle
    c_temp = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlGpuGetTemperature")
    ret = fn(gpu, byref(c_temp))
    _mtmlCheckReturn(ret)
    return c_temp.value


def mtmlVpuGetClock(vpu):
    global libHandle
    c_clock = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetClock")
    ret = fn(vpu, byref(c_clock))
    _mtmlCheckReturn(ret)
    return c_clock.value


def mtmlVpuGetMaxClock(vpu):
    global libHandle
    c_clock = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetMaxClock")
    ret = fn(vpu, byref(c_clock))
    _mtmlCheckReturn(ret)
    return c_clock.value

@convertStrBytes
def mtmlSystemGetDriverVersion(system):
    c_version = create_string_buffer(MTML_SYSTEM_DRIVER_VERSION_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlSystemGetDriverVersion")
    ret = fn(system, c_version, c_uint(MTML_SYSTEM_DRIVER_VERSION_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_version.value


@convertStrBytes
def mtmlLibraryGetVersion():
    global libHandle
    c_version = create_string_buffer(MTML_LIBRARY_VERSION_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlLibraryGetVersion")
    ret = fn(libHandle, c_version, c_uint(MTML_LIBRARY_VERSION_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_version.value


def mtmlLibraryFreeSystem(system):
    fn = _mtmlGetFunctionPointer("mtmlLibraryFreeSystem")
    ret = fn(system)
    _mtmlCheckReturn(ret)
    return None


def mtmlLibraryFreeDevice(device):
    fn = _mtmlGetFunctionPointer("mtmlLibraryFreeDevice")
    ret = fn(device)
    _mtmlCheckReturn(ret)
    return None


def mtmlDeviceFreeGpu(gpu):
    fn = _mtmlGetFunctionPointer("mtmlDeviceFreeGpu")
    ret = fn(gpu)
    _mtmlCheckReturn(ret)
    return None


def mtmlDeviceFreeMemory(memory):
    fn = _mtmlGetFunctionPointer("mtmlDeviceFreeMemory")
    ret = fn(memory)
    _mtmlCheckReturn(ret)
    return None


def mtmlDeviceFreeVpu(vpu):
    fn = _mtmlGetFunctionPointer("mtmlDeviceFreeVpu")
    ret = fn(vpu)
    _mtmlCheckReturn(ret)
    return None


def mtmlDeviceGetBrand(device):
    c_brand = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetBrand")
    ret = fn(device, byref(c_brand))
    _mtmlCheckReturn(ret)
    return c_brand.value


@convertStrBytes
def mtmlDeviceGetGpuPath(device):
    c_path = create_string_buffer(MTML_DEVICE_PATH_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetGpuPath")
    ret = fn(device, c_path, c_uint(MTML_DEVICE_PATH_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_path.value


@convertStrBytes
def mtmlDeviceGetPrimaryPath(device):
    c_path = create_string_buffer(MTML_DEVICE_PATH_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetPrimaryPath")
    ret = fn(device, c_path, c_uint(MTML_DEVICE_PATH_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_path.value


@convertStrBytes
def mtmlDeviceGetRenderPath(device):
    c_path = create_string_buffer(MTML_DEVICE_PATH_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetRenderPath")
    ret = fn(device, c_path, c_uint(MTML_DEVICE_PATH_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_path.value


@convertStrBytes
def mtmlDeviceGetVbiosVersion(device):
    c_version = create_string_buffer(MTML_DEVICE_VBIOS_VERSION_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetVbiosVersion")
    ret = fn(device, c_version, c_uint(MTML_DEVICE_VBIOS_VERSION_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_version.value


@convertStrBytes
def mtmlDeviceGetMtBiosVersion(device):
    c_version = create_string_buffer(MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMtBiosVersion")
    ret = fn(device, c_version, c_uint(MTML_DEVICE_MTBIOS_VERSION_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_version.value


def mtmlDeviceGetProperty(device):
    c_prop = c_mtmlDeviceProperty_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetProperty")
    ret = fn(device, byref(c_prop))
    _mtmlCheckReturn(ret)
    return c_prop


def mtmlDeviceCountFan(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountFan")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetFanSpeed(device, index):
    c_speed = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetFanSpeed")
    ret = fn(device, c_uint(index), byref(c_speed))
    _mtmlCheckReturn(ret)
    return c_speed.value


def mtmlDeviceGetFanRpm(device, fanIndex):
    c_rpm = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetFanRpm")
    ret = fn(device, c_uint(fanIndex), byref(c_rpm))
    _mtmlCheckReturn(ret)
    return c_rpm.value


def mtmlDeviceGetPcieSlotInfo(device):
    c_slotInfo = c_mtmlPciSlotInfo_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetPcieSlotInfo")
    ret = fn(device, byref(c_slotInfo))
    _mtmlCheckReturn(ret)
    return c_slotInfo


def mtmlDeviceCountDisplayInterface(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountDisplayInterface")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetDisplayInterfaceSpec(device, intfIndex):
    c_spec = c_mtmlDispIntfSpec_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetDisplayInterfaceSpec")
    ret = fn(device, c_uint(intfIndex), byref(c_spec))
    _mtmlCheckReturn(ret)
    return c_spec


def mtmlDeviceCountGpuCores(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountGpuCores")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


## Virtualization APIs
def mtmlDeviceCountSupportedVirtTypes(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountSupportedVirtTypes")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetSupportedVirtTypes(device, count):
    c_types = (c_mtmlVirtType_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetSupportedVirtTypes")
    ret = fn(device, c_types, c_uint(count))
    _mtmlCheckReturn(ret)
    return list(c_types)


def mtmlDeviceCountAvailVirtTypes(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountAvailVirtTypes")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetAvailVirtTypes(device, count):
    c_types = (c_mtmlVirtType_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetAvailVirtTypes")
    ret = fn(device, c_types, c_uint(count))
    _mtmlCheckReturn(ret)
    return list(c_types)


def mtmlDeviceCountAvailVirtDevices(device, virtType):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountAvailVirtDevices")
    ret = fn(device, byref(virtType), byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceCountActiveVirtDevices(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountActiveVirtDevices")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetActiveVirtDeviceUuids(device, entryLength, entryCount):
    c_uuids = create_string_buffer(entryLength * entryCount)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetActiveVirtDeviceUuids")
    ret = fn(device, c_uuids, c_uint(entryLength), c_uint(entryCount))
    _mtmlCheckReturn(ret)
    # Parse the buffer into a list of UUIDs
    uuids = []
    for i in range(entryCount):
        uuid = c_uuids[i * entryLength : (i + 1) * entryLength].decode().rstrip("\x00")
        if uuid:
            uuids.append(uuid)
    return uuids


def mtmlDeviceCountMaxVirtDevices(device, virtType):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountMaxVirtDevices")
    ret = fn(device, byref(virtType), byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


@convertStrBytes
def mtmlDeviceInitVirtDevice(device, uuid):
    c_uuid = c_char_p(uuid)
    c_virtDev = c_mtmlDevice_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceInitVirtDevice")
    ret = fn(device, c_uuid, byref(c_virtDev))
    _mtmlCheckReturn(ret)
    return c_virtDev


def mtmlDeviceFreeVirtDevice(virtDev):
    fn = _mtmlGetFunctionPointer("mtmlDeviceFreeVirtDevice")
    ret = fn(virtDev)
    _mtmlCheckReturn(ret)
    return None


def mtmlDeviceGetVirtType(virtDev):
    c_type = c_mtmlVirtType_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetVirtType")
    ret = fn(virtDev, byref(c_type))
    _mtmlCheckReturn(ret)
    return c_type


@convertStrBytes
def mtmlDeviceGetPhyDeviceUuid(virtDev):
    c_uuid = create_string_buffer(MTML_DEVICE_UUID_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetPhyDeviceUuid")
    ret = fn(virtDev, c_uuid, c_uint(MTML_DEVICE_UUID_BUFFER_SIZE))
    _mtmlCheckReturn(ret)
    return c_uuid.value


## Topology APIs
def mtmlDeviceGetTopologyLevel(dev1, dev2):
    c_level = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetTopologyLevel")
    ret = fn(dev1, dev2, byref(c_level))
    _mtmlCheckReturn(ret)
    return c_level.value


def mtmlDeviceCountDeviceByTopologyLevel(device, level):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountDeviceByTopologyLevel")
    ret = fn(device, c_uint(level), byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetDeviceByTopologyLevel(device, level, count):
    c_devices = (c_mtmlDevice_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetDeviceByTopologyLevel")
    ret = fn(device, c_uint(level), c_uint(count), c_devices)
    _mtmlCheckReturn(ret)
    return list(c_devices)


def mtmlDeviceGetP2PStatus(dev1, dev2, p2pCap):
    c_status = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetP2PStatus")
    ret = fn(dev1, dev2, c_uint(p2pCap), byref(c_status))
    _mtmlCheckReturn(ret)
    return c_status.value


## GPU engine utilization API
def mtmlGpuGetEngineUtilization(gpu, engine):
    c_util = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlGpuGetEngineUtilization")
    ret = fn(gpu, c_uint(engine), byref(c_util))
    _mtmlCheckReturn(ret)
    return c_util.value

@contextmanager
def mtmlGpuContext(device):
    c_gpu = None
    try:
        c_gpu = mtmlDeviceInitGpu(device)
        yield c_gpu
    finally:
        if c_gpu is not None:
            mtmlDeviceFreeGpu(c_gpu)


## Memory APIs
def mtmlMemoryGetUsedSystem(memory):
    c_used = c_ulonglong()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetUsedSystem")
    ret = fn(memory, byref(c_used))
    _mtmlCheckReturn(ret)
    return c_used.value


def mtmlMemoryGetBusWidth(memory):
    c_width = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetBusWidth")
    ret = fn(memory, byref(c_width))
    _mtmlCheckReturn(ret)
    return c_width.value


def mtmlMemoryGetBandwidth(memory):
    c_bandwidth = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetBandwidth")
    ret = fn(memory, byref(c_bandwidth))
    _mtmlCheckReturn(ret)
    return c_bandwidth.value


def mtmlMemoryGetSpeed(memory):
    c_speed = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetSpeed")
    ret = fn(memory, byref(c_speed))
    _mtmlCheckReturn(ret)
    return c_speed.value


@convertStrBytes
def mtmlMemoryGetVendor(memory):
    c_vendor = create_string_buffer(MTML_MEMORY_VENDOR_BUFFER_SIZE)
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetVendor")
    ret = fn(memory, c_uint(MTML_MEMORY_VENDOR_BUFFER_SIZE), c_vendor)
    _mtmlCheckReturn(ret)
    return c_vendor.value


def mtmlMemoryGetType(memory):
    c_type = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetType")
    ret = fn(memory, byref(c_type))
    _mtmlCheckReturn(ret)
    return c_type.value

@contextmanager
def mtmlMemoryContext(device):
    c_memory = None
    try:
        c_memory = mtmlDeviceInitMemory(device)
        yield c_memory
    finally:
        if c_memory is not None:
            mtmlDeviceFreeMemory(c_memory)

## VPU APIs
def mtmlVpuGetUtilization(vpu):
    c_util = c_mtmlCodecUtil_t()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetUtilization")
    ret = fn(vpu, byref(c_util))
    _mtmlCheckReturn(ret)
    return c_util


def mtmlVpuGetCodecCapacity(vpu):
    c_encCap = c_uint()
    c_decCap = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetCodecCapacity")
    ret = fn(vpu, byref(c_encCap), byref(c_decCap))
    _mtmlCheckReturn(ret)
    return (c_encCap.value, c_decCap.value)


def mtmlVpuGetEncoderSessionStates(vpu, length):
    c_states = (c_mtmlCodecSessionState_t * length)()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetEncoderSessionStates")
    ret = fn(vpu, c_states, c_uint(length))
    _mtmlCheckReturn(ret)
    return list(c_states)


def mtmlVpuGetEncoderSessionMetrics(vpu, sessionId):
    c_metrics = c_mtmlCodecSessionMetrics_t()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetEncoderSessionMetrics")
    ret = fn(vpu, c_uint(sessionId), byref(c_metrics))
    _mtmlCheckReturn(ret)
    return c_metrics


def mtmlVpuGetDecoderSessionStates(vpu, length):
    c_states = (c_mtmlCodecSessionState_t * length)()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetDecoderSessionStates")
    ret = fn(vpu, c_states, c_uint(length))
    _mtmlCheckReturn(ret)
    return list(c_states)


def mtmlVpuGetDecoderSessionMetrics(vpu, sessionId):
    c_metrics = c_mtmlCodecSessionMetrics_t()
    fn = _mtmlGetFunctionPointer("mtmlVpuGetDecoderSessionMetrics")
    ret = fn(vpu, c_uint(sessionId), byref(c_metrics))
    _mtmlCheckReturn(ret)
    return c_metrics

@contextmanager
def mtmlVpuContext(device):
    c_vpu = None
    try:
        c_vpu = mtmlDeviceInitVpu(device)
        yield c_vpu
    finally:
        if c_vpu is not None:
            mtmlDeviceFreeVpu(c_vpu)

## Log configuration APIs
def mtmlLogSetConfiguration(configuration):
    fn = _mtmlGetFunctionPointer("mtmlLogSetConfiguration")
    ret = fn(byref(configuration))
    _mtmlCheckReturn(ret)
    return None


def mtmlLogGetConfiguration():
    c_config = c_mtmlLogConfiguration_t()
    fn = _mtmlGetFunctionPointer("mtmlLogGetConfiguration")
    ret = fn(byref(c_config))
    _mtmlCheckReturn(ret)
    return c_config


## MPC APIs
def mtmlDeviceSetMpcMode(device, mode):
    fn = _mtmlGetFunctionPointer("mtmlDeviceSetMpcMode")
    ret = fn(device, c_uint(mode))
    _mtmlCheckReturn(ret)
    return None


def mtmlDeviceGetMpcMode(device):
    c_mode = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcMode")
    ret = fn(device, byref(c_mode))
    _mtmlCheckReturn(ret)
    return c_mode.value


def mtmlDeviceCountSupportedMpcProfiles(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountSupportedMpcProfiles")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetSupportedMpcProfiles(device, count):
    c_profiles = (c_mtmlMpcProfile_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetSupportedMpcProfiles")
    ret = fn(device, c_uint(count), c_profiles)
    _mtmlCheckReturn(ret)
    return list(c_profiles)


def mtmlDeviceCountSupportedMpcConfigurations(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountSupportedMpcConfigurations")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetSupportedMpcConfigurations(device, count):
    c_configs = (c_mtmlMpcConfiguration_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetSupportedMpcConfigurations")
    ret = fn(device, c_uint(count), c_configs)
    _mtmlCheckReturn(ret)
    return list(c_configs)


def mtmlDeviceGetMpcConfiguration(device):
    c_config = c_mtmlMpcConfiguration_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcConfiguration")
    ret = fn(device, byref(c_config))
    _mtmlCheckReturn(ret)
    return c_config


@convertStrBytes
def mtmlDeviceGetMpcConfigurationByName(device, configName):
    c_configName = c_char_p(configName)
    c_config = c_mtmlMpcConfiguration_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcConfigurationByName")
    ret = fn(device, c_configName, byref(c_config))
    _mtmlCheckReturn(ret)
    return c_config


def mtmlDeviceSetMpcConfiguration(device, configId):
    fn = _mtmlGetFunctionPointer("mtmlDeviceSetMpcConfiguration")
    ret = fn(device, c_uint(configId))
    _mtmlCheckReturn(ret)
    return None


def mtmlDeviceCountMpcInstancesByProfileId(device, profileId):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountMpcInstancesByProfileId")
    ret = fn(device, c_uint(profileId), byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetMpcInstancesByProfileId(device, profileId, count):
    c_instances = (c_mtmlDevice_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcInstancesByProfileId")
    ret = fn(device, c_uint(profileId), c_uint(count), c_instances)
    _mtmlCheckReturn(ret)
    return list(c_instances)


def mtmlDeviceCountMpcInstances(device):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountMpcInstances")
    ret = fn(device, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetMpcInstances(device, count):
    c_instances = (c_mtmlDevice_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcInstances")
    ret = fn(device, c_uint(count), c_instances)
    _mtmlCheckReturn(ret)
    return list(c_instances)


def mtmlDeviceGetMpcInstanceByIndex(device, index):
    c_instance = c_mtmlDevice_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcInstanceByIndex")
    ret = fn(device, c_uint(index), byref(c_instance))
    _mtmlCheckReturn(ret)
    return c_instance


def mtmlDeviceGetMpcParentDevice(mpcInstance):
    c_parent = c_mtmlDevice_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcParentDevice")
    ret = fn(mpcInstance, byref(c_parent))
    _mtmlCheckReturn(ret)
    return c_parent


def mtmlDeviceGetMpcProfileInfo(mpcInstance):
    c_profile = c_mtmlMpcProfile_t()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcProfileInfo")
    ret = fn(mpcInstance, byref(c_profile))
    _mtmlCheckReturn(ret)
    return c_profile


def mtmlDeviceGetMpcInstanceIndex(mpcInstance):
    c_index = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMpcInstanceIndex")
    ret = fn(mpcInstance, byref(c_index))
    _mtmlCheckReturn(ret)
    return c_index.value


## MtLink additional APIs
def mtmlDeviceGetMtLinkCapStatus(device, linkId, capability):
    c_status = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMtLinkCapStatus")
    ret = fn(device, c_uint(linkId), c_uint(capability), byref(c_status))
    _mtmlCheckReturn(ret)
    return c_status.value


def mtmlDeviceCountMtLinkShortestPaths(localDevice, remoteDevice):
    c_pathCount = c_uint()
    c_pathLength = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountMtLinkShortestPaths")
    ret = fn(localDevice, remoteDevice, byref(c_pathCount), byref(c_pathLength))
    _mtmlCheckReturn(ret)
    return (c_pathCount.value, c_pathLength.value)


def mtmlDeviceGetMtLinkShortestPaths(localDevice, remoteDevice, pathCount, pathLength):
    c_paths = (c_mtmlDevice_t * (pathCount * pathLength))()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMtLinkShortestPaths")
    ret = fn(localDevice, remoteDevice, c_uint(pathCount), c_uint(pathLength), c_paths)
    _mtmlCheckReturn(ret)
    # Return as 2D list
    paths = []
    for i in range(pathCount):
        path = [c_paths[i * pathLength + j] for j in range(pathLength)]
        paths.append(path)
    return paths


def mtmlDeviceCountMtLinkLayouts(localDevice, remoteDevice):
    c_count = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlDeviceCountMtLinkLayouts")
    ret = fn(localDevice, remoteDevice, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlDeviceGetMtLinkLayouts(localDevice, remoteDevice, linkCount):
    c_layouts = (c_mtmlMtLinkLayout_t * linkCount)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMtLinkLayouts")
    ret = fn(localDevice, remoteDevice, c_uint(linkCount), c_layouts)
    _mtmlCheckReturn(ret)
    return list(c_layouts)


## Affinity APIs
def mtmlDeviceGetMemoryAffinityWithinNode(device, nodeSetSize):
    c_nodeSet = (c_ulong * nodeSetSize)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetMemoryAffinityWithinNode")
    ret = fn(device, c_uint(nodeSetSize), c_nodeSet)
    _mtmlCheckReturn(ret)
    return list(c_nodeSet)


def mtmlDeviceGetCpuAffinityWithinNode(device, cpuSetSize):
    c_cpuSet = (c_ulong * cpuSetSize)()
    fn = _mtmlGetFunctionPointer("mtmlDeviceGetCpuAffinityWithinNode")
    ret = fn(device, c_uint(cpuSetSize), c_cpuSet)
    _mtmlCheckReturn(ret)
    return list(c_cpuSet)


## Device reset API
def mtmlDeviceReset(device):
    fn = _mtmlGetFunctionPointer("mtmlDeviceReset")
    ret = fn(device)
    _mtmlCheckReturn(ret)
    return None


## ECC APIs
def mtmlMemoryGetEccMode(memory):
    c_currentMode = c_uint()
    c_pendingMode = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetEccMode")
    ret = fn(memory, byref(c_currentMode), byref(c_pendingMode))
    _mtmlCheckReturn(ret)
    return (c_currentMode.value, c_pendingMode.value)


def mtmlMemoryGetRetiredPagesCount(memory):
    c_count = c_mtmlPageRetirementCount_t()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetRetiredPagesCount")
    ret = fn(memory, byref(c_count))
    _mtmlCheckReturn(ret)
    return c_count


def mtmlMemoryGetRetiredPages(memory, cause, count):
    c_pages = (c_mtmlPageRetirement_t * count)()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetRetiredPages")
    ret = fn(memory, c_uint(cause), c_uint(count), c_pages)
    _mtmlCheckReturn(ret)
    return list(c_pages)


def mtmlMemoryGetRetiredPagesPendingStatus(memory):
    c_pending = c_uint()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetRetiredPagesPendingStatus")
    ret = fn(memory, byref(c_pending))
    _mtmlCheckReturn(ret)
    return c_pending.value


def mtmlMemoryGetEccErrorCounter(memory, errorType, counterType, locationType):
    c_count = c_ulonglong()
    fn = _mtmlGetFunctionPointer("mtmlMemoryGetEccErrorCounter")
    ret = fn(
        memory,
        c_uint(errorType),
        c_uint(counterType),
        c_uint(locationType),
        byref(c_count),
    )
    _mtmlCheckReturn(ret)
    return c_count.value


def mtmlMemoryClearEccErrorCounts(memory, counterType):
    fn = _mtmlGetFunctionPointer("mtmlMemoryClearEccErrorCounts")
    ret = fn(memory, c_uint(counterType))
    _mtmlCheckReturn(ret)
    return None


def mtmlLibrarySetMpcConfigurationInBatch(devices, mpcConfigIds):
    count = len(devices)
    c_devices = (c_mtmlDevice_t * count)(*devices)
    c_configIds = (c_uint * count)(*mpcConfigIds)
    fn = _mtmlGetFunctionPointer("mtmlLibrarySetMpcConfigurationInBatch")
    global libHandle
    ret = fn(libHandle, c_uint(count), c_devices, c_configIds)
    _mtmlCheckReturn(ret)
    return None


# nvml wrapper layer ###########################################################
# NVML constants and types###########################################
NVML_SUCCESS = MTML_SUCCESS
NVML_ERROR_NOT_SUPPORTED = MTML_ERROR_NOT_SUPPORTED
NVML_ERROR_UNINITIALIZED = MTML_ERROR_UNINITIALIZED
NVML_ERROR_FUNCTION_NOT_FOUND = MTML_ERROR_FUNCTION_NOT_FOUND
NVML_ERROR_INSUFFICIENT_SIZE = MTML_ERROR_INSUFFICIENT_SIZE
NVML_ERROR_GPU_IS_LOST = MTML_ERROR_GPU_IS_LOST
NVML_ERROR_LIBRARY_NOT_FOUND = MTML_ERROR_LIBRARY_NOT_FOUND
NVML_ERROR_NO_PERMISSION = MTML_ERROR_NO_PERMISSION
NVML_ERROR_NOT_FOUND = MTML_ERROR_NOT_FOUND
NVML_ERROR_UNKNOWN = MTML_ERROR_UNKNOWN


_nvmlClockType_t = c_uint
NVML_CLOCK_GRAPHICS = 0
NVML_CLOCK_SM = 1
NVML_CLOCK_MEM = 2
NVML_CLOCK_VIDEO = 3
NVML_CLOCK_COUNT = 4

_nvmlTemperatureSensors_t = c_uint
NVML_TEMPERATURE_GPU = 0
NVML_TEMPERATURE_COUNT = 1

_nvmlDriverModel_t = c_uint
NVML_DRIVER_WDDM = 0
NVML_DRIVER_WDM = 1
NVML_DRIVER_MCDM = 2

_nvmlMemoryErrorType_t = c_uint
NVML_MEMORY_ERROR_TYPE_CORRECTED = 0
NVML_MEMORY_ERROR_TYPE_UNCORRECTED = 1
NVML_MEMORY_ERROR_TYPE_COUNT = 2

_nvmlEccCounterType_t = c_uint
NVML_VOLATILE_ECC = 0
NVML_AGGREGATE_ECC = 1
NVML_ECC_COUNTER_TYPE_COUNT = 2

_nvmlComputeMode_t = c_uint
NVML_COMPUTEMODE_DEFAULT = 0
NVML_COMPUTEMODE_EXCLUSIVE_THREAD = 1  ## Support Removed
NVML_COMPUTEMODE_PROHIBITED = 2
NVML_COMPUTEMODE_EXCLUSIVE_PROCESS = 3
NVML_COMPUTEMODE_COUNT = 4

_nvmlPcieUtilCounter_t = c_uint
NVML_PCIE_UTIL_TX_BYTES = 0
NVML_PCIE_UTIL_RX_BYTES = 1
NVML_PCIE_UTIL_COUNT = 2

NVML_NVLINK_MAX_LINKS = 18
# NVLink Link Count
NVML_FI_DEV_NVLINK_LINK_COUNT = 91

# NVLink Throughput Counters
NVML_FI_DEV_NVLINK_THROUGHPUT_DATA_TX = 138  # NVLink TX Data throughput in KiB
NVML_FI_DEV_NVLINK_THROUGHPUT_DATA_RX = 139  # NVLink RX Data throughput in KiB
NVML_FI_DEV_NVLINK_THROUGHPUT_RAW_TX = 140  # NVLink TX Data + protocol overhead in KiB
NVML_FI_DEV_NVLINK_THROUGHPUT_RAW_RX = 141  # NVLink RX Data + protocol overhead in KiB

# P2P Capability Index (maps to MtLink for MTML)
_nvmlGpuP2PCapsIndex_t = c_uint
NVML_P2P_CAPS_INDEX_READ = 0
NVML_P2P_CAPS_INDEX_WRITE = 1
NVML_P2P_CAPS_INDEX_NVLINK = 2  # Maps to MtLink for MTML
NVML_P2P_CAPS_INDEX_ATOMICS = 3
NVML_P2P_CAPS_INDEX_PROP = 4
NVML_P2P_CAPS_INDEX_PCI = 4
NVML_P2P_CAPS_INDEX_UNKNOWN = 5

# P2P Status
_nvmlGpuP2PStatus_t = c_uint
NVML_P2P_STATUS_OK = 0
NVML_P2P_STATUS_CHIPSET_NOT_SUPPORED = 1
NVML_P2P_STATUS_CHIPSET_NOT_SUPPORTED = NVML_P2P_STATUS_CHIPSET_NOT_SUPPORED
NVML_P2P_STATUS_GPU_NOT_SUPPORTED = 2
NVML_P2P_STATUS_IOH_TOPOLOGY_NOT_SUPPORTED = 3
NVML_P2P_STATUS_DISABLED_BY_REGKEY = 4
NVML_P2P_STATUS_NOT_SUPPORTED = 5
NVML_P2P_STATUS_UNKNOWN = 6

# GPU Topology Level
_nvmlGpuTopologyLevel_t = c_uint
NVML_TOPOLOGY_INTERNAL = 0
NVML_TOPOLOGY_SINGLE = 10
NVML_TOPOLOGY_MULTIPLE = 20
NVML_TOPOLOGY_HOSTBRIDGE = 30
NVML_TOPOLOGY_NODE = 40  # NVML calls this NODE
NVML_TOPOLOGY_SYSTEM = 50

_nvmlValueType_t = c_uint
NVML_VALUE_TYPE_DOUBLE = 0
NVML_VALUE_TYPE_UNSIGNED_INT = 1
NVML_VALUE_TYPE_UNSIGNED_LONG = 2
NVML_VALUE_TYPE_UNSIGNED_LONG_LONG = 3
NVML_VALUE_TYPE_SIGNED_LONG_LONG = 4
NVML_VALUE_TYPE_SIGNED_INT = 5
NVML_VALUE_TYPE_UNSIGNED_SHORT = 6
NVML_VALUE_TYPE_COUNT = 7

NVMLError_FunctionNotFound: _TypeAlias = MTMLError_FunctionNotFound
NVMLError_GpuIsLost: _TypeAlias = MTMLError_GpuIsLost
NVMLError_InvalidArgument: _TypeAlias = MTMLError_NotFound
NVMLError_LibraryNotFound: _TypeAlias = MTMLError_LibraryNotFound
NVMLError_NoPermission: _TypeAlias = MTMLError_NoPermission
NVMLError_NotFound: _TypeAlias = MTMLError_NotFound
NVMLError_NotSupported: _TypeAlias = MTMLError_NotSupported
NVMLError_Unknown: _TypeAlias = MTMLError_Unknown

c_nvmlFieldValue_t = c_mtmlFieldValue_t
c_nvmlDevice_t = c_mtmlDevice_t


@dataclass(frozen=True)
class NVMLMemoryInfo:
    total: int
    free: int
    used: int


@dataclass(frozen=True)
class NVMLUtilization:
    gpu: int
    memory: int


class NVMLError(MTMLError):
    def __new__(typ, value):
        obj = super().__new__(MTMLError, value)

        if not isinstance(obj, NVMLError):
            obj.__class__ = NVMLError

        return obj


def nvmlStructToFriendlyObject(struct):
    return mtmlStructToFriendlyObject(struct)


def nvmlInit():
    return nvmlInitWithFlags(0)


def nvmlInitWithFlags(flags):
    return mtmlLibraryInit()


def nvmlShutdown():
    return mtmlLibraryShutDown()


def nvmlExceptionClass(nvmlErrorCode):
    if nvmlErrorCode not in NVMLError._valClassMapping:
        raise ValueError("nvmlErrorCode %s is not valid" % nvmlErrorCode)
    return NVMLError._valClassMapping[nvmlErrorCode]


def nvmlSystemGetDriverVersion():
    c_system = mtmlLibraryInitSystem()
    return mtmlSystemGetDriverVersion(c_system)


def nvmlDeviceGetCount():
    return mtmlLibraryCountDevice()


def nvmlDeviceGetHandleByIndex(index):
    return mtmlLibraryInitDeviceByIndex(index)


def nvmlDeviceGetHandleByUuid(uuid):
    return mtmlLibraryInitDeviceByUuid(uuid)


def nvmlDeviceGetHandleByPciBusId(pciBusId):
    return mtmlLibraryInitDeviceByPciSbdf(pciBusId)


def nvmlDeviceGetIndex(device):
    return mtmlDeviceGetIndex(device)


def nvmlDeviceGetName(device):
    return mtmlDeviceGetName(device)


def nvmlDeviceGetUUID(device):
    return mtmlDeviceGetUUID(device)


def nvmlDeviceGetPciInfo(device):
    return mtmlDeviceGetPciInfo(device)


def nvmlDeviceGetSerial(device):
    return mtmlDeviceGetSerialNumber(device)


def nvmlDeviceGetMemoryInfo(device):
    with mtmlMemoryContext(device) as c_memory:
        total = mtmlMemoryGetTotal(c_memory)
        used = mtmlMemoryGetUsed(c_memory)
        return NVMLMemoryInfo(total=total, free=(total - used), used=used)


def nvmlDeviceGetUtilizationRates(device):
    with mtmlGpuContext(device) as c_gpu:
        gpu = mtmlGpuGetUtilization(c_gpu)
    with mtmlMemoryContext(device) as c_memory:
        memory = mtmlMemoryGetUtilization(c_memory)
    return NVMLUtilization(gpu=gpu, memory=memory)


def nvmlDeviceGetClockInfo(device, type):
    if type == NVML_CLOCK_GRAPHICS or type == NVML_CLOCK_SM:
        with mtmlGpuContext(device) as c_gpu:
            return mtmlGpuGetClock(c_gpu)
    elif type == NVML_CLOCK_VIDEO:
        with mtmlVpuContext(device) as c_vpu:
            return mtmlVpuGetClock(c_vpu)
    elif type == NVML_CLOCK_MEM:
        with mtmlMemoryContext(device) as c_memory:
            return mtmlMemoryGetClock(c_memory)
    else:
        return 0


def nvmlDeviceGetMaxClockInfo(device, type):
    if type == NVML_CLOCK_GRAPHICS or type == NVML_CLOCK_SM:
        with mtmlGpuContext(device) as c_gpu:
            return mtmlGpuGetMaxClock(c_gpu)
    elif type == NVML_CLOCK_VIDEO:
        with mtmlVpuContext(device) as c_vpu:
            return mtmlVpuGetMaxClock(c_vpu)
    elif type == NVML_CLOCK_MEM:
        with mtmlMemoryContext(device) as c_memory:
            return mtmlMemoryGetMaxClock(c_memory)
    else:
        return 0


def nvmlDeviceGetTemperature(device, type):
    with mtmlGpuContext(device) as c_gpu:
        return mtmlGpuGetTemperature(c_gpu)


def nvmlDeviceGetPowerUsage(device):
    return mtmlDeviceGetPowerUsage(device)


# cannot expose this function directly since _nvmlGetFunctionPointer will retrive the function pointer from the mtml library directly.
# it will cause a MTMLError_FunctionNotFound exception when we get nvml function pointer from the mtml library.
# def _nvmlGetFunctionPointer(name):
#     return _mtmlGetFunctionPointer(name)


def nvmlDeviceGetFanSpeed(device):
    try:
        return mtmlDeviceGetFanSpeed(device, 0)
    except MTMLError:
        return 0


def nvmlDeviceGetFanSpeed_v2(device, fan):
    try:
        return mtmlDeviceGetFanSpeed(device, fan)
    except MTMLError:
        return 0


def nvmlDeviceGetBAR1MemoryInfo(device):
    # Not Support
    return "N/A"


def nvmlDeviceGetEncoderUtilization(device):
    try:
        with mtmlVpuContext(device) as vpu:
            util = mtmlVpuGetUtilization(vpu)
            return [util.encodeUtil, 0]  # samplingPeriodUs not available
    except MTMLError:
        return [0, 0]


def nvmlDeviceGetDecoderUtilization(device):
    try:
        with mtmlVpuContext(device) as vpu:
            util = mtmlVpuGetUtilization(vpu)
            return [util.decodeUtil, 0]  # samplingPeriodUs not available
    except MTMLError:
        return [0, 0]


def nvmlSystemGetCudaDriverVersion():
    # Not Support
    return 0


def nvmlDeviceGetDisplayMode(device):
    # Not Support
    return 0


def nvmlDeviceGetCurrentDriverModel(device):
    # Not Support
    return 3


def nvmlDeviceGetPersistenceMode(device):
    # Not Support
    return 0


def nvmlDeviceGetPerformanceState(device):
    # Not Support
    return "N/A"


def nvmlDeviceGetTotalEccErrors(device, errorType, counterType):
    try:
        with mtmlMemoryContext(device) as memory:
            return mtmlMemoryGetEccErrorCounter(
                memory, errorType, counterType, MTML_MEMORY_LOCATION_DRAM
            )
    except MTMLError:
        return 0


def nvmlDeviceGetPowerManagementLimit(device):
    # Not Support
    return 0


def nvmlDeviceGetPcieThroughput(device, type):
    # Not Support
    return 0


def nvmlDeviceGetFieldValues(handle, fieldIds):
    # Not Support
    return []


def nvmlDeviceGetDisplayActive(device):
    # not support
    return 0


def nvmlDeviceGetComputeMode(device):
    # not support
    return 5


def nvmlDeviceGetCudaComputeCapability(device):
    """
    Get MUSA (Meta-computing Unified System Architecture) compute capability
    for Moore Threads GPU. Returns (major, minor) tuple.

    Uses torch.musa.get_device_capability via torchada (torch + torch_musa)
    to get the correct MUSA capability.
    """
    try:
        import torch
        import torch_musa

        # Get device index from the device handle
        # We need to find which device index this handle corresponds to
        device_count = mtmlLibraryCountDevice()
        for idx in range(device_count):
            handle = mtmlLibraryInitDeviceByIndex(idx)
            if mtmlDeviceGetUUID(handle) == mtmlDeviceGetUUID(device):
                major, minor = torch.musa.get_device_capability(idx)
                return (major, minor)
        # If no match found, try device 0
        major, minor = torch.musa.get_device_capability(0)
        return (major, minor)
    except ImportError:
        # torch or torch_musa not available
        return (0, 0)
    except Exception:
        return (0, 0)


def nvmlDeviceIsMigDeviceHandle(device):
    # not support
    return 0


def nvmlDeviceGetMigMode(device):
    # Not Support
    # [currentMode, pendingMode]
    return [0, 0]


def nvmlDeviceGetComputeRunningProcesses(device):
    # Not Support
    return []


def nvmlDeviceGetGraphicsRunningProcesses(device):
    # Not Support
    return []


def nvmlDeviceGetProcessUtilization(device, timeStamp):
    # Not Support
    return []


def nvmlDeviceGetMaxMigDeviceCount(device):
    # Not Support
    return 0


def nvmlDeviceGetMigDeviceHandleByIndex(device, index):
    # Not Support
    return "N/A"


def nvmlDeviceGetDeviceHandleFromMigDeviceHandle(device):
    # Not Support
    return "N/A"


def nvmlDeviceGetGpuInstanceId(device):
    # Not Support
    return 0


def nvmlDeviceGetComputeInstanceId(device):
    # Not Support
    return 0


def nvmlDeviceGetP2PStatus(device1, device2, p2pIndex):
    """
    Get P2P status between two devices.
    Maps NVML P2P caps to MTML P2P caps.

    For NVML_P2P_CAPS_INDEX_NVLINK, this performs detailed MtLink detection
    to check if two devices are connected via MtLink (1 hop).
    """
    try:
        # Map NVML P2P index to MTML P2P caps
        if p2pIndex == NVML_P2P_CAPS_INDEX_READ:
            mtml_cap = MTML_P2P_CAPS_READ
        elif p2pIndex == NVML_P2P_CAPS_INDEX_WRITE:
            mtml_cap = MTML_P2P_CAPS_WRITE
        elif p2pIndex == NVML_P2P_CAPS_INDEX_NVLINK:
            # For NVLink check, use MtLink status
            # This performs the same MtLink detection logic used in sglang's MUSA branch

            # First check topology - if same device, they're connected
            try:
                level = mtmlDeviceGetTopologyLevel(device1, device2)
                if level == MTML_TOPOLOGY_INTERNAL:
                    return NVML_P2P_STATUS_OK
            except MTMLError:
                pass

            # Check MtLink connectivity by iterating through links
            # This is the detailed check: for each link on device1, check if
            # the remote device matches device2's UUID
            try:
                peer_uuid = mtmlDeviceGetUUID(device2)
                link_spec = mtmlDeviceGetMtLinkSpec(device1)
                for link_idx in range(link_spec.linkNum):
                    try:
                        if (
                            mtmlDeviceGetMtLinkState(device1, link_idx)
                            != MTML_MTLINK_STATE_UP
                        ):
                            continue
                        remote_handle = mtmlDeviceGetMtLinkRemoteDevice(
                            device1, link_idx
                        )
                        if remote_handle:
                            remote_uuid = mtmlDeviceGetUUID(remote_handle)
                            if remote_uuid == peer_uuid:
                                return NVML_P2P_STATUS_OK
                    except MTMLError:
                        continue
            except MTMLError:
                pass

            # Fallback: try mtmlDeviceCountMtLinkLayouts as a secondary check
            try:
                link_count = mtmlDeviceCountMtLinkLayouts(device1, device2)
                if link_count > 0:
                    return NVML_P2P_STATUS_OK
            except MTMLError:
                pass

            return NVML_P2P_STATUS_NOT_SUPPORTED
        else:
            # For other P2P caps, use MTML P2P status
            mtml_cap = MTML_P2P_CAPS_READ

        status = mtmlDeviceGetP2PStatus(device1, device2, mtml_cap)
        # Map MTML status to NVML status
        if status == MTML_P2P_STATUS_OK:
            return NVML_P2P_STATUS_OK
        elif status == MTML_P2P_STATUS_CHIPSET_NOT_SUPPORTED:
            return NVML_P2P_STATUS_CHIPSET_NOT_SUPPORTED
        elif status == MTML_P2P_STATUS_GPU_NOT_SUPPORTED:
            return NVML_P2P_STATUS_GPU_NOT_SUPPORTED
        else:
            return NVML_P2P_STATUS_UNKNOWN
    except MTMLError:
        return NVML_P2P_STATUS_NOT_SUPPORTED


def nvmlDeviceGetTopologyCommonAncestor(device1, device2):
    """
    Get the common ancestor topology level between two devices.
    Maps MTML topology levels to NVML topology levels.
    """
    try:
        level = mtmlDeviceGetTopologyLevel(device1, device2)
        # Map MTML topology level to NVML topology level
        if level == MTML_TOPOLOGY_INTERNAL:
            return NVML_TOPOLOGY_INTERNAL
        elif level == MTML_TOPOLOGY_SINGLE:
            return NVML_TOPOLOGY_SINGLE
        elif level == MTML_TOPOLOGY_MULTIPLE:
            return NVML_TOPOLOGY_MULTIPLE
        elif level == MTML_TOPOLOGY_HOSTBRIDGE:
            return NVML_TOPOLOGY_HOSTBRIDGE
        elif level == MTML_TOPOLOGY_NODE:
            return NVML_TOPOLOGY_NODE
        elif level == MTML_TOPOLOGY_SYSTEM:
            return NVML_TOPOLOGY_SYSTEM
        else:
            return NVML_TOPOLOGY_SYSTEM
    except MTMLError:
        return NVML_TOPOLOGY_SYSTEM


def nvmlDeviceGetTopologyNearestGpus(device, level):
    """
    Get GPUs at or nearer than the given topology level.
    """
    try:
        # Map NVML level to MTML level
        if level >= NVML_TOPOLOGY_SYSTEM:
            mtml_level = MTML_TOPOLOGY_SYSTEM
        elif level >= NVML_TOPOLOGY_NODE:
            mtml_level = MTML_TOPOLOGY_NODE
        elif level >= NVML_TOPOLOGY_HOSTBRIDGE:
            mtml_level = MTML_TOPOLOGY_HOSTBRIDGE
        elif level >= NVML_TOPOLOGY_MULTIPLE:
            mtml_level = MTML_TOPOLOGY_MULTIPLE
        elif level >= NVML_TOPOLOGY_SINGLE:
            mtml_level = MTML_TOPOLOGY_SINGLE
        else:
            mtml_level = MTML_TOPOLOGY_INTERNAL

        count = mtmlDeviceCountDeviceByTopologyLevel(device, mtml_level)
        if count > 0:
            return mtmlDeviceGetDeviceByTopologyLevel(device, mtml_level, count)
        return []
    except MTMLError:
        return []


def nvmlDeviceGetNvLinkState(device, link):
    """
    Get NVLink state - maps to MtLink state for MTML.
    """
    try:
        state = mtmlDeviceGetMtLinkState(device, link)
        return 1 if state else 0
    except MTMLError:
        return 0


def nvmlDeviceGetNvLinkCapability(device, link, capability):
    """
    Get NVLink capability - maps to MtLink cap status for MTML.
    """
    try:
        return mtmlDeviceGetMtLinkCapStatus(device, link, capability)
    except MTMLError:
        return 0


def nvmlDeviceGetNvLinkRemotePciInfo(device, link):
    """
    Get NVLink remote PCI info - maps to MtLink for MTML.
    """
    try:
        remote_device = mtmlDeviceGetMtLinkRemoteDevice(device, link)
        return mtmlDeviceGetPciInfo(remote_device)
    except MTMLError:
        return None


def nvmlDeviceGetNumGpuCores(device):
    """Get number of GPU cores."""
    try:
        return mtmlDeviceCountGpuCores(device)
    except MTMLError:
        return 0


def nvmlDeviceGetMemoryBusWidth(device):
    """Get memory bus width in bits."""
    try:
        memory = mtmlDeviceInitMemory(device)
        return mtmlMemoryGetBusWidth(memory)
    except MTMLError:
        return 0


def nvmlDeviceGetVbiosVersion(device):
    """Get VBIOS version."""
    try:
        return mtmlDeviceGetVbiosVersion(device)
    except MTMLError:
        return ""


def nvmlDeviceGetBrand(device):
    """Get device brand."""
    try:
        return mtmlDeviceGetBrand(device)
    except MTMLError:
        return MTML_BRAND_UNKNOWN


def nvmlDeviceGetMinorNumber(device):
    """Get device minor number (render node number)."""
    try:
        # Parse from render path: /dev/dri/renderD128 -> 128
        render_path = mtmlDeviceGetRenderPath(device)
        if isinstance(render_path, bytes):
            render_path = render_path.decode()
        # Extract number from path like /dev/dri/renderD128
        import re

        match = re.search(r"renderD(\d+)", render_path)
        if match:
            return int(match.group(1))
        return 0
    except (MTMLError, Exception):
        return 0


def nvmlDeviceGetCpuAffinity(device, cpuSetSize):
    """Get CPU affinity for device."""
    try:
        return mtmlDeviceGetCpuAffinityWithinNode(device, cpuSetSize)
    except MTMLError:
        return [0] * cpuSetSize


def nvmlDeviceGetMemoryAffinity(device, nodeSetSize, scope):
    """Get memory affinity for device."""
    try:
        return mtmlDeviceGetMemoryAffinityWithinNode(device, nodeSetSize)
    except MTMLError:
        return [0] * nodeSetSize


def nvmlDeviceGetCpuAffinityWithinScope(device, cpuSetSize, scope):
    """Get CPU affinity within scope for device."""
    try:
        return mtmlDeviceGetCpuAffinityWithinNode(device, cpuSetSize)
    except MTMLError:
        return [0] * cpuSetSize


def nvmlDeviceGetEccMode(device):
    """Get ECC mode - returns (current, pending)."""
    try:
        memory = mtmlDeviceInitMemory(device)
        return mtmlMemoryGetEccMode(memory)
    except MTMLError:
        return (0, 0)


def nvmlDeviceGetCurrentEccMode(device):
    """Get current ECC mode."""
    return nvmlDeviceGetEccMode(device)[0]


def nvmlDeviceGetPendingEccMode(device):
    """Get pending ECC mode."""
    return nvmlDeviceGetEccMode(device)[1]


def nvmlDeviceGetRetiredPagesPendingStatus(device):
    """Get retired pages pending status."""
    try:
        memory = mtmlDeviceInitMemory(device)
        return mtmlMemoryGetRetiredPagesPendingStatus(memory)
    except MTMLError:
        return 0
