"""Unit tests for MTML shared-library selection."""

import pytest

import pymtml


def test_linux_loader_prefers_versioned_library(monkeypatch):
    loaded = object()
    calls = []

    def fake_cdll(name):
        calls.append(name)
        return loaded

    monkeypatch.setattr(pymtml, "CDLL", fake_cdll)

    assert pymtml._LoadLinuxLibrary() is loaded
    assert calls == ["libmtml.so.2"]


def test_linux_loader_falls_back_to_legacy_library(monkeypatch):
    loaded = object()
    calls = []

    def fake_cdll(name):
        calls.append(name)
        if name == "libmtml.so.2":
            raise OSError("versioned library is unavailable")
        return loaded

    monkeypatch.setattr(pymtml, "CDLL", fake_cdll)

    assert pymtml._LoadLinuxLibrary() is loaded
    assert calls == ["libmtml.so.2", "libmtml.so"]


def test_linux_loader_reports_both_failures(monkeypatch):
    calls = []

    def fake_cdll(name):
        calls.append(name)
        if name == "libmtml.so.2":
            raise OSError("versioned load failed")
        raise OSError("legacy load failed")

    monkeypatch.setattr(pymtml, "CDLL", fake_cdll)

    with pytest.raises(OSError) as exc_info:
        pymtml._LoadLinuxLibrary()

    message = str(exc_info.value)
    assert calls == ["libmtml.so.2", "libmtml.so"]
    assert "libmtml.so.2" in message
    assert "versioned load failed" in message
    assert "libmtml.so" in message
    assert "legacy load failed" in message
