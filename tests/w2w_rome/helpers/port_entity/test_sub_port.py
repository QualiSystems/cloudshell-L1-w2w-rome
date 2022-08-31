import pytest

from w2w_rome.helpers.port_entity import SubPort


@pytest.mark.parametrize(
    "line",
    (
        # v1
        "E1[1AE1]         Unlocked     Enabled     Connected  2       W2[1AW2]       A1",
        # v2
        "1AE1             Unlocked     Enabled     Connected  17      W2[1AW2]      E1,A1",
    ),
)
def test_sub_port_a(line):
    ports = SubPort.parse_sub_ports(line, "")

    assert len(ports) == 1
    port = ports[0]

    assert port.direction == "E"
    assert port.sub_port_id == "1"
    assert port.blade_letter == "A"
    assert port.sub_port_name == "E1"
    assert port.locked is False
    assert port.enabled is True
    assert port.connected is True
    assert port.connected_to_direction == "W"
    assert port.connected_to_sub_port_id == "2"
    assert port.logical == "A1"
    assert port.port_name == "A1"
    assert port.original_logical_name == port.logical


@pytest.mark.parametrize(
    "line",
    (
        # v1
        "E129[1BE1]       Unlocked     Enabled     Disconnected  0               B129",
        # v2
        "1BE1       Unlocked     Enabled     Disconnected  0                E129,B129",
    ),
)
def test_sub_port_b(line):
    ports = SubPort.parse_sub_ports(line, "")

    assert len(ports) == 1
    port = ports[0]

    assert port.direction == "E"
    assert port.sub_port_id == "129"
    assert port.blade_letter == "B"
    assert port.sub_port_name == "E129"
    assert port.locked is False
    assert port.enabled is True
    assert port.connected is False
    assert port.connected_to_direction == ""
    assert port.connected_to_sub_port_id == ""
    assert port.logical == "B129"
    assert port.port_name == "B129"
    assert port.original_logical_name == port.logical


@pytest.mark.parametrize(
    "line",
    (
        # v1
        "E1[1AE1]     Unlocked     Enabled     Connected     5       W4[1AW4]       Q1",
        # v2
        "1AE1         Unlocked     Enabled     Connected     5       W4[1AW4]       E1,Q1",
    ),
)
def test_sub_port_q(line):
    ports = SubPort.parse_sub_ports(line, "")

    assert len(ports) == 1
    port = ports[0]

    assert port.direction == "E"
    assert port.sub_port_id == "1"
    assert port.blade_letter == "Q"
    assert port.sub_port_name == "E1"
    assert port.locked is False
    assert port.enabled is True
    assert port.connected is True
    assert port.connected_to_direction == "W"
    assert port.connected_to_sub_port_id == "4"
    assert port.logical == "Q1"
    assert port.port_name == "Q1"
    assert port.original_logical_name == port.logical


@pytest.mark.parametrize(
    "line",
    (
        # v1
        "E2[1AE2]     Unlocked     Enabled     Connected     68      W1[1AW1]       P2",
        # v2
        "1AE2         Unlocked     Enabled     Connected     68      W1[1AW1]       E2,P2",
    ),
)
def test_sub_port_p(line):
    """P is Q128"""
    ports = SubPort.parse_sub_ports(line, "")

    assert len(ports) == 1
    port = ports[0]

    assert port.direction == "E"
    assert port.sub_port_id == "2"
    assert port.blade_letter == "Q"
    assert port.sub_port_name == "E2"
    assert port.locked is False
    assert port.enabled is True
    assert port.connected is True
    assert port.connected_to_direction == "W"
    assert port.connected_to_sub_port_id == "1"
    assert port.logical == "Q2"
    assert port.port_name == "Q2"
    assert port.original_logical_name == "P2"


@pytest.mark.parametrize(
    "line",
    (
        # v1
        "E2[1AE2]     Unlocked     Enabled     Connected     36      W2[1AW2]       Y2",
        # v2
        "1AE2         Unlocked     Enabled     Connected     36      W2[1AW2]       E2,Y2",
    ),
)
def test_sub_port_y(line):
    ports = SubPort.parse_sub_ports(line, "")

    assert len(ports) == 1
    port = ports[0]

    assert port.direction == "E"
    assert port.sub_port_id == "2"
    assert port.blade_letter == "Y"
    assert port.sub_port_name == "E2"
    assert port.locked is False
    assert port.enabled is True
    assert port.connected is True
    assert port.connected_to_direction == "W"
    assert port.connected_to_sub_port_id == "2"
    assert port.logical == "Y2"
    assert port.port_name == "Y2"
    assert port.original_logical_name == port.logical


@pytest.mark.parametrize(
    "line",
    (
        # v1
        "E130[1BE2] Unlocked     Enabled     Connected     21      W130[1BW2]     X2",
        # v2
        "1BE2       Unlocked     Enabled     Connected     21      W130[1BW2]     E130,X2",
    ),
)
def test_sub_port_x(line):
    ports = SubPort.parse_sub_ports(line, "")

    assert len(ports) == 1
    port = ports[0]

    assert port.direction == "E"
    assert port.sub_port_id == "130"
    assert port.blade_letter == "X"
    assert port.sub_port_name == "E130"
    assert port.locked is False
    assert port.enabled is True
    assert port.connected is True
    assert port.connected_to_direction == "W"
    assert port.connected_to_sub_port_id == "130"
    assert port.logical == "X2"
    assert port.port_name == "X2"
    assert port.original_logical_name == port.logical
