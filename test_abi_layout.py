"""ctypes ABI layout checks against the bundled MTML 2.x header."""

from ctypes import alignment, c_uint, sizeof

import pymtml


def test_mtml_structure_sizes_match_header_abi():
    expected_sizes = {
        pymtml.c_mtmlMtLinkSpec_t: 28,
        pymtml.c_mtmlPciSlotInfo_t: 52,
        pymtml.c_mtmlDeviceProperty_t: 8,
        pymtml.c_mtmlDispIntfSpec_t: 48,
        pymtml.c_mtmlVirtType_t: 136,
        pymtml.c_mtmlCodecUtil_t: 24,
        pymtml.c_mtmlCodecSessionState_t: 4,
        pymtml.c_mtmlCodecSessionMetrics_t: 48,
        pymtml.c_mtmlLogConsoleConfiguration_t: 12,
        pymtml.c_mtmlLogSystemConfiguration_t: 12,
        pymtml.c_mtmlLogFileConfiguration_t: 216,
        pymtml.c_mtmlLogCallbackConfiguration_t: 24,
        pymtml.c_mtmlLogConfiguration_t: 296,
        pymtml.c_mtmlMpcProfile_t: 88,
        pymtml.c_mtmlMpcConfiguration_t: 196,
        pymtml.c_mtmlMtLinkLayout_t: 24,
        pymtml.c_mtmlPageRetirementCount_t: 8,
        pymtml.c_mtmlPageRetirement_t: 56,
        pymtml.c_mtmlPageRetirementPending_t: 64,
    }

    for structure, expected_size in expected_sizes.items():
        assert sizeof(structure) == expected_size, structure.__name__


def test_mtml_structure_alignments_match_header_abi():
    expected_alignments = {
        pymtml.c_mtmlMtLinkSpec_t: 4,
        pymtml.c_mtmlPciInfo_t: 4,
        pymtml.c_mtmlPciSlotInfo_t: 4,
        pymtml.c_mtmlDeviceProperty_t: 4,
        pymtml.c_mtmlDispIntfSpec_t: 4,
        pymtml.c_mtmlVirtType_t: 4,
        pymtml.c_mtmlCodecUtil_t: 4,
        pymtml.c_mtmlCodecSessionState_t: 4,
        pymtml.c_mtmlCodecSessionMetrics_t: 4,
        pymtml.c_mtmlLogConsoleConfiguration_t: 4,
        pymtml.c_mtmlLogSystemConfiguration_t: 4,
        pymtml.c_mtmlLogFileConfiguration_t: 4,
        pymtml.c_mtmlLogCallbackConfiguration_t: 8,
        pymtml.c_mtmlLogConfiguration_t: 8,
        pymtml.c_mtmlMpcProfile_t: 8,
        pymtml.c_mtmlMpcConfiguration_t: 4,
        pymtml.c_mtmlMtLinkLayout_t: 4,
        pymtml.c_mtmlPageRetirementCount_t: 4,
        pymtml.c_mtmlPageRetirement_t: 8,
        pymtml.c_mtmlPageRetirementPending_t: 8,
    }

    for structure, expected_alignment in expected_alignments.items():
        assert alignment(structure) == expected_alignment, structure.__name__


def test_mtml_structure_offsets_match_header_abi():
    expected_offsets = {
        pymtml.c_mtmlMtLinkSpec_t: {"bandWidth": 4, "linkNum": 8, "rsvd": 12},
        pymtml.c_mtmlPciInfo_t: {
            "pciSubsystemId": 48,
            "busWidth": 52,
            "pciMaxSpeed": 56,
            "rsvd": 80,
        },
        pymtml.c_mtmlPciSlotInfo_t: {"slotName": 4, "rsvd": 36},
        pymtml.c_mtmlDeviceProperty_t: {"rsvd2": 4},
        pymtml.c_mtmlDispIntfSpec_t: {"maxRefreshRate": 12, "rsvd": 16},
        pymtml.c_mtmlVirtType_t: {
            "name": 16,
            "api": 48,
            "frameBuffer": 72,
            "maxInstances": 84,
            "rsvd": 92,
        },
        pymtml.c_mtmlCodecUtil_t: {"encUtil": 8, "rsvd": 16},
        pymtml.c_mtmlCodecSessionMetrics_t: {
            "hResolution": 8,
            "codecType": 28,
            "rsvd": 32,
        },
        pymtml.c_mtmlLogConfiguration_t: {
            "systemConfig": 12,
            "fileConfig": 24,
            "callbackConfig": 240,
            "rsvd": 264,
        },
        pymtml.c_mtmlLogFileConfiguration_t: {
            "file": 4,
            "size": 204,
            "rsvd": 208,
        },
        pymtml.c_mtmlLogCallbackConfiguration_t: {"callback": 8, "rsvd": 16},
        pymtml.c_mtmlMpcProfile_t: {
            "memorySizeMB": 8,
            "name": 16,
            "rsvd": 48,
        },
        pymtml.c_mtmlMpcConfiguration_t: {"profileId": 36, "rsvd": 100},
        pymtml.c_mtmlMtLinkLayout_t: {"remoteLinkId": 4, "rsvd": 8},
        pymtml.c_mtmlPageRetirementCount_t: {"dbeCount": 4},
        pymtml.c_mtmlPageRetirement_t: {"address": 8, "rsvd": 16},
        pymtml.c_mtmlPageRetirementPending_t: {
            "timestamps": 8,
            "address": 16,
            "rsvd": 24,
        },
    }

    for structure, field_offsets in expected_offsets.items():
        for field_name, expected_offset in field_offsets.items():
            assert getattr(structure, field_name).offset == expected_offset


def test_pci_info_matches_header_and_exposes_bus_id_alias():
    assert pymtml.c_mtmlPciInfo_t.pciSubsystemId.offset == 48
    assert pymtml.c_mtmlPciInfo_t.busWidth.offset == 52
    assert pymtml.c_mtmlPciInfo_t.rsvd.offset == 80
    assert sizeof(pymtml.c_mtmlPciInfo_t) == 104

    pci_info = pymtml.c_mtmlPciInfo_t()
    pci_info.sbdf = b"00000000:01:00.0"
    assert pci_info.busId == pci_info.sbdf


def test_compatibility_aliases_use_header_backing_fields():
    prop = pymtml.c_mtmlDeviceProperty_t()
    prop.virtCapability = 1
    prop.virtRole = 2
    prop.mpcCapability = 1
    prop.mpcType = 2
    prop.mtLinkCapability = 1
    assert (prop.virtCapability, prop.virtRole) == (1, 2)
    assert (prop.mpcCapability, prop.mpcType) == (1, 2)
    assert prop.mtLinkCapability == 1
    assert c_uint.from_buffer_copy(prop).value == 0x155

    profile = pymtml.c_mtmlMpcProfile_t()
    profile.id = 7
    profile.coreCount = 12
    profile.memorySizeMB = 4096
    assert profile.profileId == 7
    assert profile.gpuCores == 12
    assert profile.memSize == 4096 * 1024 * 1024

    retired = pymtml.c_mtmlPageRetirementCount_t()
    retired.sbeCount = 3
    retired.dbeCount = 4
    assert retired.singleBitEcc == 3
    assert retired.doubleBitEcc == 4


def test_device_property_bitfield_masks_match_header_abi():
    fields = {
        "virtCap": (1, 0x1),
        "virtRole": (7, 0xE),
        "mpcCap": (1, 0x10),
        "mpcType": (7, 0xE0),
        "mtLinkCap": (1, 0x100),
        "rsvd": ((1 << 23) - 1, 0xFFFFFE00),
    }

    for field_name, (value, expected_mask) in fields.items():
        prop = pymtml.c_mtmlDeviceProperty_t()
        setattr(prop, field_name, value)
        assert c_uint.from_buffer_copy(prop).value == expected_mask


def test_mpc_profile_count_stops_at_header_sentinel():
    configuration = pymtml.c_mtmlMpcConfiguration_t()
    configuration.profileId[0] = 4
    configuration.profileId[1] = 1
    configuration.profileId[2] = -1
    assert configuration.profileNum == 2


def test_signed_codec_session_state_preserves_unknown_value():
    assert pymtml._mtmlCodecSessionState_t(-1).value == -1
    assert pymtml.c_mtmlCodecSessionState_t(-1).value == -1


def test_codec_session_state_wrapper_preserves_public_shape(monkeypatch):
    def fake_get_states(_vpu, states, length):
        assert length.value == 2
        states[0] = pymtml.MTML_CODEC_SESSION_STATE_IDLE
        states[1] = pymtml.MTML_CODEC_SESSION_STATE_ACTIVE
        return pymtml.MTML_SUCCESS

    monkeypatch.setattr(
        pymtml, "_mtmlGetFunctionPointer", lambda _name: fake_get_states
    )

    states = pymtml.mtmlVpuGetEncoderSessionStates(None, 2)
    assert [(state.sessionId, state.state) for state in states] == [(0, 0), (1, 1)]
