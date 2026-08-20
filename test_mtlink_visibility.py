from types import SimpleNamespace

import pymtml


def test_nvlink_p2p_prefers_pairwise_layout_query(monkeypatch):
    local = object()
    peer = object()

    monkeypatch.setattr(
        pymtml,
        "mtmlDeviceGetTopologyLevel",
        lambda device1, device2: pymtml.MTML_TOPOLOGY_SINGLE,
    )
    monkeypatch.setattr(
        pymtml, "mtmlDeviceCountMtLinkLayouts", lambda device1, device2: 2
    )

    def unexpected_link_scan(device):
        raise AssertionError("pairwise layout detection should avoid link scanning")

    monkeypatch.setattr(pymtml, "mtmlDeviceGetMtLinkSpec", unexpected_link_scan)

    status = pymtml.nvmlDeviceGetP2PStatus(
        local, peer, pymtml.NVML_P2P_CAPS_INDEX_NVLINK
    )

    assert status == pymtml.NVML_P2P_STATUS_OK


def test_nvlink_p2p_skips_hidden_peers_when_layout_query_is_unavailable(monkeypatch):
    local = object()
    peer = object()
    visible_peer = object()

    monkeypatch.setattr(
        pymtml,
        "mtmlDeviceGetTopologyLevel",
        lambda device1, device2: pymtml.MTML_TOPOLOGY_SINGLE,
    )

    def unsupported_layout_query(device1, device2):
        raise pymtml.MTMLError_NotSupported(pymtml.MTML_ERROR_NOT_SUPPORTED)

    monkeypatch.setattr(
        pymtml, "mtmlDeviceCountMtLinkLayouts", unsupported_layout_query
    )
    monkeypatch.setattr(
        pymtml, "mtmlDeviceGetMtLinkSpec", lambda device: SimpleNamespace(linkNum=2)
    )
    monkeypatch.setattr(
        pymtml,
        "mtmlDeviceGetMtLinkState",
        lambda device, link: pymtml.MTML_MTLINK_STATE_UP,
    )

    def get_remote(device, link):
        if link == 0:
            raise pymtml.MTMLError_NotFound(pymtml.MTML_ERROR_NOT_FOUND)
        return visible_peer

    monkeypatch.setattr(pymtml, "mtmlDeviceGetMtLinkRemoteDevice", get_remote)
    monkeypatch.setattr(
        pymtml,
        "mtmlDeviceGetUUID",
        lambda device: b"visible-peer" if device in (peer, visible_peer) else b"hidden",
    )

    status = pymtml.nvmlDeviceGetP2PStatus(
        local, peer, pymtml.NVML_P2P_CAPS_INDEX_NVLINK
    )

    assert status == pymtml.NVML_P2P_STATUS_OK
