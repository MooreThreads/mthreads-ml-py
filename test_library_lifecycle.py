"""Unit tests for process-wide MTML library lifecycle ownership."""

from concurrent.futures import ThreadPoolExecutor
from ctypes import POINTER, c_uint, cast, pointer
from threading import Barrier

import pytest

import pymtml


class FakeMtmlLibrary:
    def __init__(self):
        self.init_calls = []
        self.shutdown_calls = []
        self._handles = []
        self.init_result = pymtml.MTML_SUCCESS
        self.shutdown_result = pymtml.MTML_SUCCESS

    def init(self, handle_out):
        handle_storage = pymtml.struct_c_mtmlLibrary_t()
        handle = pointer(handle_storage)
        cast(handle_out, POINTER(pymtml.c_mtmlLibrary_t))[0] = handle
        self._handles.append((handle_storage, handle))
        self.init_calls.append(handle)
        return self.init_result

    def shutdown(self, handle):
        self.shutdown_calls.append(handle)
        return self.shutdown_result

    def count_devices(self, _handle, count_out):
        cast(count_out, POINTER(c_uint))[0] = 2
        return pymtml.MTML_SUCCESS


@pytest.fixture
def fake_mtml(monkeypatch):
    native = FakeMtmlLibrary()
    functions = {
        "mtmlLibraryInit": native.init,
        "mtmlLibraryShutDown": native.shutdown,
        "mtmlLibraryCountDevice": native.count_devices,
    }

    monkeypatch.setattr(pymtml, "_LoadMtmlLibrary", lambda: None)
    monkeypatch.setattr(pymtml, "_mtmlGetFunctionPointer", functions.__getitem__)
    monkeypatch.setattr(pymtml, "libHandle", pymtml.c_mtmlLibrary_t())
    monkeypatch.setattr(pymtml, "_mtmlLib_refcount", 0)
    return native


def test_nested_init_keeps_native_handle_until_last_shutdown(fake_mtml):
    pymtml.mtmlLibraryInit()
    pymtml.mtmlLibraryInit()

    assert len(fake_mtml.init_calls) == 1
    assert pymtml._mtmlLib_refcount == 2
    assert bool(pymtml.libHandle)

    pymtml.mtmlLibraryShutDown()

    assert fake_mtml.shutdown_calls == []
    assert pymtml._mtmlLib_refcount == 1
    assert bool(pymtml.libHandle)
    assert pymtml.mtmlLibraryCountDevice() == 2

    pymtml.mtmlLibraryShutDown()

    assert len(fake_mtml.shutdown_calls) == 1
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_library_can_reinitialize_after_final_shutdown(fake_mtml):
    pymtml.mtmlLibraryInit()
    pymtml.mtmlLibraryShutDown()
    pymtml.mtmlLibraryInit()

    assert len(fake_mtml.init_calls) == 2
    assert len(fake_mtml.shutdown_calls) == 1
    assert pymtml._mtmlLib_refcount == 1
    assert bool(pymtml.libHandle)
    assert pymtml.mtmlLibraryCountDevice() == 2

    pymtml.mtmlLibraryShutDown()

    assert len(fake_mtml.shutdown_calls) == 2
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_shutdown_without_reference_is_idempotent(fake_mtml):
    pymtml.mtmlLibraryShutDown()

    assert fake_mtml.shutdown_calls == []
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_failed_native_init_does_not_publish_handle_or_reference(fake_mtml):
    fake_mtml.init_result = pymtml.MTML_ERROR_UNKNOWN

    with pytest.raises(pymtml.MTMLError):
        pymtml.mtmlLibraryInit()

    assert len(fake_mtml.init_calls) == 1
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_failed_final_shutdown_preserves_handle_and_reference(fake_mtml):
    pymtml.mtmlLibraryInit()
    active_handle = pymtml.libHandle
    fake_mtml.shutdown_result = pymtml.MTML_ERROR_UNKNOWN

    with pytest.raises(pymtml.MTMLError):
        pymtml.mtmlLibraryShutDown()

    assert len(fake_mtml.shutdown_calls) == 1
    assert pymtml._mtmlLib_refcount == 1
    assert pymtml.libHandle == active_handle

    fake_mtml.shutdown_result = pymtml.MTML_SUCCESS
    pymtml.mtmlLibraryShutDown()

    assert len(fake_mtml.shutdown_calls) == 2
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_concurrent_clients_share_one_native_lifecycle(fake_mtml):
    worker_count = 8
    start = Barrier(worker_count)
    initialized = Barrier(worker_count)
    queried = Barrier(worker_count)

    def use_library():
        start.wait()
        pymtml.mtmlLibraryInit()
        initialized.wait()
        assert pymtml.mtmlLibraryCountDevice() == 2
        queried.wait()
        pymtml.mtmlLibraryShutDown()

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(use_library) for _ in range(worker_count)]
        for future in futures:
            future.result()

    assert len(fake_mtml.init_calls) == 1
    assert len(fake_mtml.shutdown_calls) == 1
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)
