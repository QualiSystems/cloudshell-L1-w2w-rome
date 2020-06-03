import re

from mock import MagicMock, patch

from w2w_rome.helpers.errors import (
    BaseRomeException,
    ConnectionPortsError,
    NotSupportedError,
)
from w2w_rome.helpers.port_entity import SubPort

from tests.w2w_rome.base import (
    DEFAULT_PROMPT,
    PORT_SHOW_MATRIX_A,
    PORT_SHOW_MATRIX_A_CHANGED_PORT,
    PORT_SHOW_MATRIX_B,
    PORT_SHOW_MATRIX_Q,
    PORT_SHOW_MATRIX_Q128_1,
    PORT_SHOW_MATRIX_Q128_2,
    PORT_SHOW_MATRIX_Q128_2_CHANGED_PORT,
    PORT_SHOW_MATRIX_XY,
    PORT_SHOW_MATRIX_XY_CHANGED_PORT,
    BaseRomeTestCase,
    CliEmulator,
    Command,
)

CONNECTION_PENDING_EMPTY = """ROME[TECH]# connection show pending
Connection execution status: enabled

no request in process

======= ========= ========= ================== ======= ===================
Request Port1     Port2     Command            Source  User
======= ========= ========= ================== ======= ===================

ROME[TECH]# """


def get_connection_pending(src_port, dst_port):
    return """ROME[TECH]# 08-18-2019 12:37 CONNECTING...
connection show pending
Connection execution status: delayed due to command in process
                             Perform "homing run"

Command in process:
connect, ports: {}-{}, status: in process with payload

======= ========= ========= ================== ======= ===================
Request Port1     Port2     Command            Source  User
======= ========= ========= ================== ======= ===================

ROME[TECH]# """.format(
        src_port, dst_port
    )


def set_port_connected(sub_port_name, connected_to_sub_port_name, port_show_output):
    sub_port_match = re.search(
        r"^{}\[.+$".format(sub_port_name), port_show_output, re.MULTILINE
    )
    connected_sub_port_match = re.search(
        r"^{}\[.+$".format(connected_to_sub_port_name), port_show_output, re.MULTILINE
    )

    if sub_port_match is None:
        raise ValueError("Didn't find the sub port {}".format(sub_port_name))
    if connected_sub_port_match is None:
        raise ValueError(
            "Didn't find the sub port {}".format(connected_to_sub_port_name)
        )

    sub_port = SubPort.from_line(sub_port_match.group(), "")
    connected_sub_port = SubPort.from_line(connected_sub_port_match.group(), "")

    sub_port.connected = True
    sub_port.connected_to_direction = connected_sub_port.direction
    sub_port.connected_to_sub_port_id = connected_sub_port.sub_port_id

    connected_sub_port.connected = True
    connected_sub_port.connected_to_direction = sub_port.direction
    connected_sub_port.connected_to_sub_port_id = sub_port.sub_port_id

    port_show_output = port_show_output.replace(
        sub_port_match.group(), sub_port.table_view()
    )
    port_show_output = port_show_output.replace(
        connected_sub_port_match.group(), connected_sub_port.table_view()
    )
    return port_show_output


def set_port_disconnected(sub_port_name, port_show_output):
    sub_port_match = re.search(
        r"^{}\[.+$".format(sub_port_name), port_show_output, re.MULTILINE
    )

    if sub_port_match is None:
        raise ValueError("Didn't find the sub port {}".format(sub_port_name))

    sub_port = SubPort.from_line(sub_port_match.group(), "")

    connected_sub_port_match = re.search(
        r"^{}\[.+$".format(sub_port.connected_to_sub_port_name),
        port_show_output,
        re.MULTILINE,
    )
    if connected_sub_port_match is not None:
        connected_sub_port = SubPort.from_line(connected_sub_port_match.group(), "")
        connected_sub_port.connected = False
        connected_sub_port.connected_to_direction = ""
        connected_sub_port.connected_to_sub_port_id = ""
        port_show_output = port_show_output.replace(
            connected_sub_port_match.group(), connected_sub_port.table_view()
        )

    sub_port.connected = False
    sub_port.connected_to_direction = ""
    sub_port.connected_to_sub_port_id = ""
    port_show_output = port_show_output.replace(
        sub_port_match.group(), sub_port.table_view()
    )

    return port_show_output


@patch("cloudshell.cli.session.ssh_session.paramiko", MagicMock())
@patch(
    "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer",
    MagicMock(return_value=""),
)
class RomeTestMapUni(BaseRomeTestCase):
    def test_map_uni_with_a_few_dst_ports(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/010".format(address)
        dst_ports = ["{}/1/{}".format(address, port_num) for port_num in (12, 14, 16)]

        emu = CliEmulator()
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
            BaseRomeException, r"(?i)is not allowed for multiple dst ports"
        ):
            self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    def test_map_uni_with_connected_ports(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/001".format(address)
        dst_ports = ["{}/1/002".format(address)]

        emu = CliEmulator(
            [Command("", DEFAULT_PROMPT), Command("port show", PORT_SHOW_MATRIX_A)]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    def test_map_uni(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_ports = ["{}/1/004".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_A)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create E3 to W4",
                    """ROME[TECH]# connection create E3 to W4
OK - request added to pending queue (E3-W4)
ROME[TECH]# 08-05-2019 09:20 CONNECTING...
08-05-2019 09:20 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect

""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    def test_map_uni_changed_ports(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/135".format(address)
        dst_ports = ["{}/1/255".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected(
            "E135", "W255", PORT_SHOW_MATRIX_A_CHANGED_PORT
        )
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create E135 to W255",
                    """ROME[TECH]# connection create E135 to W255
OK - request added to pending queue (E135-W255)
ROME[TECH]# 08-05-2019 09:20 CONNECTING...
08-05-2019 09:20 CONNECTION OPERATION SUCCEEDED:E135[1BE129]<->W255[1BW127] OP:connect

""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    def test_map_uni_a_few_checks(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_ports = ["{}/1/004".format(address)]

        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_A)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create E3 to W4",
                    """ROME[TECH]# connection create E3 to W4""",
                ),
                Command("connection show pending", get_connection_pending("E3", "W4"),),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    def test_map_uni_failed(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/006".format(address)
        dst_ports = ["{}/1/004".format(address)]

        self.driver_commands._mapping_timeout = 0.1
        self.driver_commands._mapping_check_delay = 0.1

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create E6 to W4",
                    """ROME[TECH]# 08-05-2019 09:32 
Ports details:
[E6[1AE6]] [W4[1AW4]]
08-05-2019 09:32 OPERATION VALIDATION FAILED:E6-W4 requestType=connect

ROME[TECH]# 
""",  # noqa: W291
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", PORT_SHOW_MATRIX_A),
            ]
        )

        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
            ConnectionPortsError, "Cannot connect port A6 to port A4"
        ):
            self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    def test_map_uni_for_matrix_q(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/03".format(address)
        dst_ports = ["{}/1/04".format(address)]

        emu = CliEmulator()
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
            NotSupportedError, "MapUni for matrix Q doesn't supported"
        ):
            self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    def test_map_uni_for_matrix_xy(self):
        host = "192.168.122.10"
        address = "{}:XY".format(host)
        user = "user"
        password = "password"
        src_port = "{}/Y/011".format(address)
        dst_ports = ["{}/X/014".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected("E11", "W14", PORT_SHOW_MATRIX_XY)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_XY),
                Command(
                    "connection create E11 to W14",
                    """ROME[TECH]# connection create E11 to W14
OK - request added to pending queue (E11-W14)
ROME[TECH]# 08-05-2019 09:20 CONNECTING...
08-05-2019 09:20 CONNECTION OPERATION SUCCEEDED:E11[1AE11]<->W14[1AW14] OP:connect

""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()


@patch("cloudshell.cli.session.ssh_session.paramiko", MagicMock())
@patch(
    "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer",
    MagicMock(return_value=""),
)
class RomeTestMapBidi(BaseRomeTestCase):
    def test_map_bidi_with_connected_ports(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/249".format(address)
        dst_port = "{}/1/253".format(address)

        emu = CliEmulator(
            [Command("", DEFAULT_PROMPT), Command("port show", PORT_SHOW_MATRIX_B)]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    def test_map_bidi_one_connection(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/001".format(address)
        dst_port = "{}/1/002".format(address)
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected("E2", "W1", PORT_SHOW_MATRIX_A)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create A1 to A2",
                    """ROME[TECH]# connection create A1 to A2
OK - request added to pending queue (A1-A2)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SKIPPED(already done):E1[1AE1]<->W2[1AW2] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W1[1AW1] OP:connect
08-06-2019 09:01 Connection A1<->A2 completed successfully
""",  # noqa: E501
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    def test_map_bidi(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_port = "{}/1/004".format(address)
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_A)
        connected_port_show_a = set_port_connected("E4", "W3", connected_port_show_a)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create A3 to A4",
                    """ROME[TECH]# connection create A3 to A4
OK - request added to pending queue (A3-A4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E4[1AE2]<->W3[1AW3] OP:connect
08-06-2019 09:01 Connection A3<->A4 completed successfully
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    def test_map_bidi_failed(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_port = "{}/1/004".format(address)
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_A)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create A3 to A4",
                    """ROME[TECH]# connection create A3 to A4
OK - request added to pending queue (A3-A4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect
08-06-2019 09:01 CONNECTION OPERATION FAILED:E4[1AE2]<->W3[1AW3] OP:connect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
                Command(
                    "connection disconnect A3 from A4",
                    """ROME[TECH]# connection disconnect A3 from A4
OK - request added to pending queue (A3-A4)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
            ConnectionPortsError, "Cannot connect port A3 to port A4"
        ):
            self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    def test_map_bidi_a_few_checks(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_port = "{}/1/004".format(address)

        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_a = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_A)
        connected_port_show_a = set_port_connected("E4", "W3", connected_port_show_a)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_A),
                Command(
                    "connection create A3 to A4",
                    """ROME[TECH]# connection create A3 to A4
OK - request added to pending queue (A3-A4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E4[1AE2]<->W3[1AW3] OP:connect
08-06-2019 09:01 Connection A3<->A4 completed successfully
""",
                ),
                Command("connection show pending", get_connection_pending("A3", "A4")),
                Command("connection show pending", get_connection_pending("A3", "A4")),
                Command("connection show pending", get_connection_pending("A3", "A4")),
                Command("connection show pending", get_connection_pending("A3", "A4")),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    def test_map_bidi_q_ports(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_port = "{}/1/004".format(address)
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show = set_port_connected("E5", "W8", PORT_SHOW_MATRIX_Q)
        connected_port_show = set_port_connected("E6", "W7", connected_port_show)
        connected_port_show = set_port_connected("E133", "W136", connected_port_show)
        connected_port_show = set_port_connected("E134", "W135", connected_port_show)
        connected_port_show = set_port_connected("E7", "W6", connected_port_show)
        connected_port_show = set_port_connected("E8", "W5", connected_port_show)
        connected_port_show = set_port_connected("E135", "W134", connected_port_show)
        connected_port_show = set_port_connected("E136", "W133", connected_port_show)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q),
                Command(
                    "connection create Q3 to Q4",
                    """ROME[TECH]# connection create Q3 to Q4
OK - request added to pending queue (Q3-Q4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E5[1AE5]<->W8[1AW8] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E6[1AE5]<->W7[1AW7] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E133[1BE133]<->W136[1BW136] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E134[1BE134]<->W135[1BW135] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E7[1AE7]<->W6[1AW6] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E8[1AE8]<->W5[1AW5] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E135[1AB135]<->W134[1BW134] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E136[1AB136]<->W133[1BW133] OP:connect
08-06-2019 09:01 Connection Q3<->Q4 completed successfully
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    def test_map_bidi_q128_ports(self):
        first_host = "192.168.122.10"
        second_host = "192.168.122.11"
        address = "{}:{}:Q".format(first_host, second_host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_port = "{}/1/004".format(address)
        self.driver_commands._mapping_check_delay = 0.1

        port_show_q1 = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_Q128_1)
        port_show_q1 = set_port_connected("E131", "W132", port_show_q1)
        port_show_q1 = set_port_connected("E4", "W3", port_show_q1)
        port_show_q1 = set_port_connected("E132", "W131", port_show_q1)

        port_show_q2 = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_Q128_2)
        port_show_q2 = set_port_connected("E131", "W132", port_show_q2)
        port_show_q2 = set_port_connected("E4", "W3", port_show_q2)
        port_show_q2 = set_port_connected("E132", "W131", port_show_q2)
        emu1 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_1),
                Command(
                    "connection create P3 to P4",
                    """ROME[TECH]# connection create P3 to P4
OK - request added to pending queue (P3-P4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E131[1BE131]<->W132[1BW132] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E4[1AE4]<->W3[1AW3] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E132[1BE132]<->W131[1BW131] OP:connect
08-06-2019 09:01 Connection P3<->P4 completed successfully
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", port_show_q1),
            ]
        )
        emu2 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_2),
                Command(
                    "connection create P3 to P4",
                    """ROME[TECH]# connection create P3 to P4
OK - request added to pending queue (P3-P4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E131[1BE131]<->W132[1BW132] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E4[1AE4]<->W3[1AW3] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E132[1BE132]<->W131[1BW131] OP:connect
08-06-2019 09:01 Connection P3<->P4 completed successfully
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", port_show_q2),
            ]
        )
        self.send_line_func_map.update(
            {first_host: emu1.send_line, second_host: emu2.send_line}
        )
        self.receive_all_func_map.update(
            {first_host: emu1.receive_all, second_host: emu2.receive_all}
        )

        with self.patch_sessions():
            self.driver_commands.login(address, user, password)

        self.driver_commands.map_bidi(src_port, dst_port)

        emu1.check_calls()
        emu2.check_calls()

    def test_map_bidi_q128_failed(self):
        first_host = "192.168.122.10"
        second_host = "192.168.122.11"
        address = "{}:{}:Q".format(first_host, second_host)
        user = "user"
        password = "password"
        src_port = "{}/1/003".format(address)
        dst_port = "{}/1/004".format(address)
        self.driver_commands._mapping_check_delay = 0.1

        port_show_q1 = set_port_connected("E3", "W4", PORT_SHOW_MATRIX_Q128_1)
        port_show_q1 = set_port_connected("E131", "W132", port_show_q1)
        port_show_q1 = set_port_connected("E4", "W3", port_show_q1)
        port_show_q1 = set_port_connected("E132", "W131", port_show_q1)

        emu1 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_1),
                Command(
                    "connection create P3 to P4",
                    """ROME[TECH]# connection create P3 to P4
OK - request added to pending queue (P3-P4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E131[1BE131]<->W132[1BW132] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E4[1AE4]<->W3[1AW3] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E132[1BE132]<->W131[1BW131] OP:connect
08-06-2019 09:01 Connection P3<->P4 completed successfully
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", port_show_q1),
                Command(
                    "connection disconnect P3 from P4",
                    """ROME[TECH]# connection disconnect E1 from W2
OK - request added to pending queue (E1-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W2[1AW2] OP:disconnect
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1BE129]<->W130[1BW130] OP:disconnect
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1BE130]<->W129[1BW129] OP:disconnect
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W1[1AW1] OP:disconnect
""",  # noqa: E501
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
            ]
        )
        emu2 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_2),
                Command("connection create P3 to P4", DEFAULT_PROMPT),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", PORT_SHOW_MATRIX_Q128_2),
                Command("connection disconnect P3 from P4", DEFAULT_PROMPT),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
            ]
        )
        self.send_line_func_map.update(
            {first_host: emu1.send_line, second_host: emu2.send_line}
        )
        self.receive_all_func_map.update(
            {first_host: emu1.receive_all, second_host: emu2.receive_all}
        )

        with self.patch_sessions():
            self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
            ConnectionPortsError, "Cannot connect port P3 to port P4"
        ):
            self.driver_commands.map_bidi(src_port, dst_port)

        emu1.check_calls()
        emu2.check_calls()

    def test_map_bidi_xy(self):
        host = "192.168.122.10"
        address = "{}:XY".format(host)
        user = "user"
        password = "password"
        src_port = "{}/Y/013".format(address)
        dst_port = "{}/X/014".format(address)
        self.driver_commands._mapping_check_delay = 0.1

        connected_port_show_xy = set_port_connected("E13", "W14", PORT_SHOW_MATRIX_XY)
        connected_port_show_a = set_port_connected(
            "E142", "W141", connected_port_show_xy
        )
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_XY),
                Command(
                    "connection create Y13 to X14",
                    """ROME[TECH]# connection create Y13 to X14
OK - request added to pending queue (Y13-X14)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E13[1AE13]<->W14[1AW14] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E142[1BE142]<->W141[1BW141] OP:connect
08-06-2019 09:01 Connection Y13<->X14 completed successfully
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", connected_port_show_a),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()


@patch("cloudshell.cli.session.ssh_session.paramiko", MagicMock())
@patch(
    "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer",
    MagicMock(return_value=""),
)
class RomeTestMapClear(BaseRomeTestCase):
    def test_map_clear_matrix_b(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        ports = ["{}/1/{}".format(address, port_id) for port_id in (249, 218, 246)]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_port_show_b = set_port_disconnected("E246", PORT_SHOW_MATRIX_B)
        disconnected_port_show_b = set_port_disconnected(
            "E249", disconnected_port_show_b
        )
        disconnected_port_show_b = set_port_disconnected(
            "E253", disconnected_port_show_b
        )
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_B),
                Command(
                    "connection disconnect E246 from W247",
                    """ROME[TECH]# connection disconnect E246 from W247
OK - request added to pending queue (E246-W247)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E246[1AE246]<->W247[1AW247] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E249 from W253",
                    """ROME[TECH]# connection disconnect E249 from W253
OK - request added to pending queue (E249-W253)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E249[1AE249]<->W253[1AW253] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E253 from W249",
                    """ROME[TECH]# connection disconnect E253 from W249
OK - request added to pending queue (E253-W249)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E253[1AE253]<->W249[1AW249] OP:disconnect
""",  # noqa: E501
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_port_show_b),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear(ports)

        emu.check_calls()

    def test_map_clear_matrix_b_a_few_checks(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        ports = ["{}/1/{}".format(address, port_id) for port_id in (249, 218, 246)]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_port_show_b = set_port_disconnected("E246", PORT_SHOW_MATRIX_B)
        disconnected_port_show_b = set_port_disconnected(
            "E249", disconnected_port_show_b
        )
        disconnected_port_show_b = set_port_disconnected(
            "E253", disconnected_port_show_b
        )
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_B),
                Command(
                    "connection disconnect E246 from W247",
                    """ROME[TECH]# connection disconnect E246 from W247
OK - request added to pending queue (E246-W247)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E246[1AE246]<->W247[1AW247] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E249 from W253",
                    """ROME[TECH]# connection disconnect E249 from W253
OK - request added to pending queue (E249-W253)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E249[1AE249]<->W253[1AW253] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E253 from W249",
                    """ROME[TECH]# connection disconnect E253 from W249
OK - request added to pending queue (E253-W249)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E253[1AE253]<->W249[1AW249] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection show pending", get_connection_pending("E253", "W249")
                ),
                Command(
                    "connection show pending", get_connection_pending("E253", "W249")
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_port_show_b),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear(ports)

        emu.check_calls()

    def test_map_clear_matrix_q(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        ports = ["{}/1/1".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_ports_show = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q)
        disconnected_ports_show = set_port_disconnected("E2", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E3", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E4", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E129", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E130", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E131", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E132", disconnected_ports_show)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q),
                Command(
                    "connection disconnect E1 from W4",
                    """ROME[TECH]# connection disconnect E1 from W4
OK - request added to pending queue (E1-W4)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W4[1AW4] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W132",
                    """ROME[TECH]# connection disconnect E129 from W132
OK - request added to pending queue (E129-W132)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1AE129]<->W2[1AW132] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E130 from W131",
                    """ROME[TECH]# connection disconnect E130 from W131
OK - request added to pending queue (E130-W131)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1AE130]<->W131[1AW131] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E131 from W130",
                    """ROME[TECH]# connection disconnect E131 from W130
OK - request added to pending queue (E131-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E131[1AE131]<->W130[1AW130] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E132 from W129",
                    """ROME[TECH]# connection disconnect E132 from W129
OK - request added to pending queue (E132-W129)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E132[1AE132]<->W129[1AW129] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E2 from W3",
                    """ROME[TECH]# connection disconnect E2 from W3
OK - request added to pending queue (E2-W3)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W3[1AW3] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E3 from W2",
                    """ROME[TECH]# connection disconnect E3 from W2
OK - request added to pending queue (E3-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W2[1AW2] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E4 from W1",
                    """ROME[TECH]# connection disconnect E4 from W1
OK - request added to pending queue (E4-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E4[1AE4]<->W1[1AW1] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_ports_show),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear(ports)

        emu.check_calls()

    def test_map_clear_matrix_q128(self):
        first_host = "192.168.122.10"
        second_host = "192.168.122.11"
        address = "{}:{}:Q".format(first_host, second_host)
        user = "user"
        password = "password"
        ports = ["{}/1/1".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        ports_show_1 = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q128_1)
        ports_show_1 = set_port_disconnected("E2", ports_show_1)
        ports_show_1 = set_port_disconnected("E129", ports_show_1)
        ports_show_1 = set_port_disconnected("E130", ports_show_1)

        ports_show_2 = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q128_2)
        ports_show_2 = set_port_disconnected("E2", ports_show_2)
        ports_show_2 = set_port_disconnected("E129", ports_show_2)
        ports_show_2 = set_port_disconnected("E130", ports_show_2)
        emu1 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_1),
                Command(
                    "connection disconnect E1 from W2",
                    """ROME[TECH]# connection disconnect E1 from W2
OK - request added to pending queue (E1-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W2[1AW2] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W130",
                    """ROME[TECH]# connection disconnect E129 from W130
OK - request added to pending queue (E129-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1BE129]<->W130[1BW130] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E130 from W129",
                    """ROME[TECH]# connection disconnect E130 from W129
OK - request added to pending queue (E130-W129)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1BE130]<->W129[1BW129] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E2 from W1",
                    """ROME[TECH]# connection disconnect E2 from W1
OK - request added to pending queue (E2-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W1[1AW1] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", ports_show_1),
            ]
        )
        emu2 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_2),
                Command(
                    "connection disconnect E1 from W2",
                    """ROME[TECH]# connection disconnect E1 from W2
OK - request added to pending queue (E1-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W2[1AW2] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W130",
                    """ROME[TECH]# connection disconnect E129 from W130
OK - request added to pending queue (E129-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1BE129]<->W130[1BW130] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E130 from W129",
                    """ROME[TECH]# connection disconnect E130 from W129
OK - request added to pending queue (E130-W129)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1BE130]<->W129[1BW129] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E2 from W1",
                    """ROME[TECH]# connection disconnect E2 from W1
OK - request added to pending queue (E2-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W1[1AW1] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", ports_show_2),
            ]
        )

        self.send_line_func_map.update(
            {first_host: emu1.send_line, second_host: emu2.send_line}
        )
        self.receive_all_func_map.update(
            {first_host: emu1.receive_all, second_host: emu2.receive_all}
        )

        with self.patch_sessions():
            self.driver_commands.login(address, user, password)

        self.driver_commands.map_clear(ports)

        emu1.check_calls()
        emu2.check_calls()

    def test_map_clear_matrix_q128_changed_port(self):
        first_host = "192.168.122.10"
        second_host = "192.168.122.11"
        address = "{}:{}:Q".format(first_host, second_host)
        user = "user"
        password = "password"
        ports = ["{}/1/1".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        ports_show_1 = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q128_1)
        ports_show_1 = set_port_disconnected("E2", ports_show_1)
        ports_show_1 = set_port_disconnected("E129", ports_show_1)
        ports_show_1 = set_port_disconnected("E130", ports_show_1)

        ports_show_2 = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q128_2_CHANGED_PORT)
        ports_show_2 = set_port_disconnected("E2", ports_show_2)
        ports_show_2 = set_port_disconnected("E129", ports_show_2)
        ports_show_2 = set_port_disconnected("E130", ports_show_2)
        emu1 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_1),
                Command(
                    "connection disconnect E1 from W2",
                    """ROME[TECH]# connection disconnect E1 from W2
OK - request added to pending queue (E1-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W2[1AW2] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W130",
                    """ROME[TECH]# connection disconnect E129 from W130
OK - request added to pending queue (E129-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1BE129]<->W130[1BW130] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E130 from W129",
                    """ROME[TECH]# connection disconnect E130 from W129
OK - request added to pending queue (E130-W129)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1BE130]<->W129[1BW129] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E2 from W1",
                    """ROME[TECH]# connection disconnect E2 from W1
OK - request added to pending queue (E2-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W1[1AW1] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", ports_show_1),
            ]
        )
        emu2 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_2_CHANGED_PORT),
                Command(
                    "connection disconnect E1 from W2",
                    """ROME[TECH]# connection disconnect E1 from W2
OK - request added to pending queue (E1-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W2[1AW2] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W130",
                    """ROME[TECH]# connection disconnect E129 from W130
OK - request added to pending queue (E129-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1BE129]<->W130[1BW130] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E130 from W129",
                    """ROME[TECH]# connection disconnect E130 from W129
OK - request added to pending queue (E130-W129)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1BE130]<->W129[1BW129] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E2 from W1",
                    """ROME[TECH]# connection disconnect E2 from W1
OK - request added to pending queue (E2-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W1[1AW1] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", ports_show_2),
            ]
        )

        self.send_line_func_map.update(
            {first_host: emu1.send_line, second_host: emu2.send_line}
        )
        self.receive_all_func_map.update(
            {first_host: emu1.receive_all, second_host: emu2.receive_all}
        )

        with self.patch_sessions():
            self.driver_commands.login(address, user, password)

        self.driver_commands.map_clear(ports)

        emu1.check_calls()
        emu2.check_calls()

    def test_map_clear_matrix_xy(self):
        host = "192.168.122.10"
        address = "{}:XY".format(host)
        user = "user"
        password = "password"
        ports = [p.format(address) for p in ("{}/Y/001", "{}/X/007")]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_port_show_xy = set_port_disconnected("E1", PORT_SHOW_MATRIX_XY)
        disconnected_port_show_xy = set_port_disconnected(
            "E129", disconnected_port_show_xy
        )
        disconnected_port_show_xy = set_port_disconnected(
            "E135", disconnected_port_show_xy
        )
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_XY),
                Command(
                    "connection disconnect E1 from W1",
                    """ROME[TECH]# connection disconnect E1 from W1
OK - request added to pending queue (E1-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1A1]<->W1[1AW1] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W129",
                    """ROME[TECH]# connection disconnect E129 from W129
OK - request added to pending queue (E129-W129)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1AE129]<->W129[1AW129] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E135 from W135",
                    """ROME[TECH]# connection disconnect E135 from W135
OK - request added to pending queue (E135-W135)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E135[1AE135]<->W135[1AW135] OP:disconnect
""",  # noqa: E501
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_port_show_xy),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear(ports)

        emu.check_calls()

    def test_map_clear_matrix_xy_changed_port(self):
        host = "192.168.122.10"
        address = "{}:XY".format(host)
        user = "user"
        password = "password"
        ports = ["{}/Y/002".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_port_show_xy = set_port_disconnected(
            "E2", PORT_SHOW_MATRIX_XY_CHANGED_PORT
        )
        disconnected_port_show_xy = set_port_disconnected(
            "E130", disconnected_port_show_xy
        )
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_XY_CHANGED_PORT),
                Command(
                    "connection disconnect E130 from W130",
                    """ROME[TECH]# connection disconnect E130 from W130
OK - request added to pending queue (E130-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1AE130]<->W130[1AW130] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E2 from W2",
                    """ROME[TECH]# connection disconnect E2 from W2
OK - request added to pending queue (E2-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W2[1AW2] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_port_show_xy),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear(ports)

        emu.check_calls()


@patch("cloudshell.cli.session.ssh_session.paramiko", MagicMock())
@patch(
    "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer",
    MagicMock(return_value=""),
)
class RomeTestMapClearTo(BaseRomeTestCase):
    def test_map_clear_to_matrix_b(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/249".format(address)
        dst_ports = ["{}/1/253".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_port_show_b = set_port_disconnected("E249", PORT_SHOW_MATRIX_B)
        disconnected_port_show_b = set_port_disconnected(
            "W249", disconnected_port_show_b
        )
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_B),
                Command(
                    "connection disconnect E249 from W253",
                    """ROME[TECH]# connection disconnect E249 from W253
OK - request added to pending queue (E249-W253)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E249[1AE249]<->W253[1AW253] OP:disconnect
""",  # noqa: E501
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_port_show_b),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear_to(src_port, dst_ports)

        emu.check_calls()

    def test_map_clear_to_matrix_b_a_few_checks(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/249".format(address)
        dst_ports = ["{}/1/253".format(address)]

        self.driver_commands._mapping_check_delay = 0.1

        disconnected_port_show_b = set_port_disconnected("E249", PORT_SHOW_MATRIX_B)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_B),
                Command(
                    "connection disconnect E249 from W253",
                    """ROME[TECH]# connection disconnect E249 from W253
OK - request added to pending queue (E249-W253)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E249[1AE249]<->W253[1AW253] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection show pending", get_connection_pending("E249", "W253")
                ),
                Command(
                    "connection show pending", get_connection_pending("E249", "W253")
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_port_show_b),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear_to(src_port, dst_ports)

        emu.check_calls()

    def test_map_clear_to_matrix_q(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        src_port = "{}/1/1".format(address)
        dst_ports = ["{}/1/2".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_ports_show = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q)
        disconnected_ports_show = set_port_disconnected("E2", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E129", disconnected_ports_show)
        disconnected_ports_show = set_port_disconnected("E130", disconnected_ports_show)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q),
                Command(
                    "connection disconnect E1 from W4",
                    """ROME[TECH]# connection disconnect E1 from W4
OK - request added to pending queue (E1-W4)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W4[1AW4] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W132",
                    """ROME[TECH]# connection disconnect E129 from W132
OK - request added to pending queue (E129-W132)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1AE129]<->W2[1AW132] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E130 from W131",
                    """ROME[TECH]# connection disconnect E130 from W131
OK - request added to pending queue (E130-W131)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1AE130]<->W131[1AW131] OP:disconnect
""",  # noqa: E501
                ),
                Command(
                    "connection disconnect E2 from W3",
                    """ROME[TECH]# connection disconnect E2 from W3
OK - request added to pending queue (E2-W3)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W3[1AW3] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_ports_show),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear_to(src_port, dst_ports)

        emu.check_calls()

    def test_map_clear_to_matrix_q_128(self):
        first_host = "192.168.122.10"
        second_host = "192.168.122.11"
        address = "{}:{}:Q".format(first_host, second_host)
        user = "user"
        password = "password"
        src_port = "{}/1/1".format(address)
        dst_ports = ["{}/1/2".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        ports_show_1 = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q128_1)
        ports_show_1 = set_port_disconnected("E129", ports_show_1)

        ports_show_2 = set_port_disconnected("E1", PORT_SHOW_MATRIX_Q128_2)
        ports_show_2 = set_port_disconnected("E129", ports_show_2)

        emu1 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_1),
                Command(
                    "connection disconnect E1 from W2",
                    """ROME[TECH]# connection disconnect E1 from W2
OK - request added to pending queue (E1-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W2[1AW2] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W130",
                    """ROME[TECH]# connection disconnect E129 from W130
OK - request added to pending queue (E129-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1BE129]<->W130[1BW130] OP:disconnect
""",  # noqa: E501
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", ports_show_1),
            ]
        )
        emu2 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q128_2),
                Command(
                    "connection disconnect E1 from W2",
                    """ROME[TECH]# connection disconnect E1 from W2
OK - request added to pending queue (E1-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W2[1AW2] OP:disconnect
""",
                ),
                Command(
                    "connection disconnect E129 from W130",
                    """ROME[TECH]# connection disconnect E129 from W130
OK - request added to pending queue (E129-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1BE129]<->W130[1BW130] OP:disconnect
""",  # noqa: E501
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", ports_show_2),
            ]
        )

        self.send_line_func_map.update(
            {first_host: emu1.send_line, second_host: emu2.send_line}
        )
        self.receive_all_func_map.update(
            {first_host: emu1.receive_all, second_host: emu2.receive_all}
        )

        with self.patch_sessions():
            self.driver_commands.login(address, user, password)

        self.driver_commands.map_clear_to(src_port, dst_ports)

        emu1.check_calls()

    def test_map_clear_to_matrix_xy(self):
        host = "192.168.122.10"
        address = "{}:XY".format(host)
        user = "user"
        password = "password"
        src_port = "{}/Y/1".format(address)
        dst_ports = ["{}/X/1".format(address)]
        self.driver_commands._mapping_check_delay = 0.1

        disconnected_port_show_xy = set_port_disconnected("E1", PORT_SHOW_MATRIX_XY)
        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_XY),
                Command(
                    "connection disconnect E1 from W1",
                    """ROME[TECH]# connection disconnect E1 from W1
OK - request added to pending queue (E1-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W1[1AW1] OP:disconnect
""",
                ),
                Command("connection show pending", CONNECTION_PENDING_EMPTY),
                Command("port show", disconnected_port_show_xy),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear_to(src_port, dst_ports)

        emu.check_calls()
