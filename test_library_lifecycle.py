"""Unit tests for process-wide MTML library lifecycle ownership."""

from concurrent.futures import ThreadPoolExecutor
from ctypes import POINTER, c_uint, c_void_p, cast, pointer
from threading import Barrier

import pytest

import pymtml


def handle_address(handle):
    return cast(handle, c_void_p).value


class FakeMtmlLibrary:
    def __init__(self):
        self.init_calls = []
        self.shutdown_calls = []
        self.query_calls = []
        self._handles = []
        self.init_result = pymtml.MTML_SUCCESS
        self.shutdown_result = pymtml.MTML_SUCCESS

    def init(self, handle_out):
        handle_storage = pymtml.struct_c_mtmlLibrary_t()
        handle = pointer(handle_storage)
        cast(handle_out, POINTER(pymtml.c_mtmlLibrary_t))[0] = handle
        self._handles.append((handle_storage, handle))
        self.init_calls.append(handle_address(handle))
        return self.init_result

    def shutdown(self, handle):
        self.shutdown_calls.append(handle_address(handle))
        return self.shutdown_result

    def count_devices(self, handle, count_out):
        self.query_calls.append(handle_address(handle))
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
    monkeypatch.setattr(pymtml, "_mtmlLib_handles", [], raising=False)
    monkeypatch.setattr(pymtml, "_mtmlLib_refcount", 0)
    return native


def test_nested_init_pairs_handles_and_keeps_first_handle_active(fake_mtml):
    pymtml.mtmlLibraryInit()
    pymtml.mtmlLibraryInit()

    assert len(fake_mtml.init_calls) == 2
    assert len(set(fake_mtml.init_calls)) == 2
    assert [handle_address(handle) for handle in pymtml._mtmlLib_handles] == (
        fake_mtml.init_calls
    )
    assert handle_address(pymtml.libHandle) == fake_mtml.init_calls[0]
    assert pymtml._mtmlLib_refcount == 2

    pymtml.mtmlLibraryShutDown()

    assert fake_mtml.shutdown_calls == [fake_mtml.init_calls[1]]
    assert [handle_address(handle) for handle in pymtml._mtmlLib_handles] == [
        fake_mtml.init_calls[0]
    ]
    assert handle_address(pymtml.libHandle) == fake_mtml.init_calls[0]
    assert pymtml._mtmlLib_refcount == 1
    assert pymtml.mtmlLibraryCountDevice() == 2
    assert fake_mtml.query_calls == [fake_mtml.init_calls[0]]

    pymtml.mtmlLibraryShutDown()

    assert fake_mtml.shutdown_calls == list(reversed(fake_mtml.init_calls))
    assert pymtml._mtmlLib_handles == []
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_library_can_reinitialize_after_final_shutdown(fake_mtml):
    pymtml.mtmlLibraryInit()
    first_handle = handle_address(pymtml.libHandle)
    pymtml.mtmlLibraryShutDown()
    pymtml.mtmlLibraryInit()
    second_handle = handle_address(pymtml.libHandle)

    assert first_handle != second_handle
    assert len(fake_mtml.init_calls) == 2
    assert len(fake_mtml.shutdown_calls) == 1
    assert pymtml._mtmlLib_refcount == 1
    assert pymtml.mtmlLibraryCountDevice() == 2

    pymtml.mtmlLibraryShutDown()

    assert len(fake_mtml.shutdown_calls) == 2
    assert pymtml._mtmlLib_handles == []
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_shutdown_without_init_reports_uninitialized(fake_mtml):
    with pytest.raises(pymtml.MTMLError) as exc_info:
        pymtml.mtmlLibraryShutDown()

    assert exc_info.value.value == pymtml.MTML_ERROR_UNINITIALIZED
    assert fake_mtml.shutdown_calls == []
    assert pymtml._mtmlLib_handles == []
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_failed_initial_init_does_not_publish_handle(fake_mtml):
    fake_mtml.init_result = pymtml.MTML_ERROR_UNKNOWN

    with pytest.raises(pymtml.MTMLError):
        pymtml.mtmlLibraryInit()

    assert len(fake_mtml.init_calls) == 1
    assert pymtml._mtmlLib_handles == []
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)


def test_failed_nested_init_preserves_existing_handle(fake_mtml):
    pymtml.mtmlLibraryInit()
    active_handle = handle_address(pymtml.libHandle)
    fake_mtml.init_result = pymtml.MTML_ERROR_UNKNOWN

    with pytest.raises(pymtml.MTMLError):
        pymtml.mtmlLibraryInit()

    assert len(fake_mtml.init_calls) == 2
    assert [handle_address(handle) for handle in pymtml._mtmlLib_handles] == [
        active_handle
    ]
    assert handle_address(pymtml.libHandle) == active_handle
    assert pymtml._mtmlLib_refcount == 1


def test_failed_shutdown_preserves_handle_stack(fake_mtml):
    pymtml.mtmlLibraryInit()
    pymtml.mtmlLibraryInit()
    handles_before = [handle_address(handle) for handle in pymtml._mtmlLib_handles]
    fake_mtml.shutdown_result = pymtml.MTML_ERROR_UNKNOWN

    with pytest.raises(pymtml.MTMLError):
        pymtml.mtmlLibraryShutDown()

    assert fake_mtml.shutdown_calls == [handles_before[-1]]
    assert [handle_address(handle) for handle in pymtml._mtmlLib_handles] == (
        handles_before
    )
    assert handle_address(pymtml.libHandle) == handles_before[0]
    assert pymtml._mtmlLib_refcount == 2


def test_concurrent_clients_pair_all_native_handles(fake_mtml):
    worker_count = 8
    start = Barrier(worker_count)
    initialized = Barrier(worker_count)
    queried = Barrier(worker_count)

    def use_library():
        start.wait(timeout=10)
        pymtml.mtmlLibraryInit()
        initialized.wait(timeout=10)
        assert pymtml.mtmlLibraryCountDevice() == 2
        queried.wait(timeout=10)
        pymtml.mtmlLibraryShutDown()

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(use_library) for _ in range(worker_count)]
        for future in futures:
            future.result()

    assert len(fake_mtml.init_calls) == worker_count
    assert len(set(fake_mtml.init_calls)) == worker_count
    assert fake_mtml.shutdown_calls == list(reversed(fake_mtml.init_calls))
    assert set(fake_mtml.query_calls) == {fake_mtml.init_calls[0]}
    assert pymtml._mtmlLib_handles == []
    assert pymtml._mtmlLib_refcount == 0
    assert not bool(pymtml.libHandle)
