import re

from mock import patch, MagicMock

from tests.w2w_rome.base import BaseRomeTestCase, CliEmulator, Command, \
    DEFAULT_PROMPT, PORT_SHOW_MATRIX_A, PORT_SHOW_MATRIX_B, PORT_SHOW_MATRIX_Q
from w2w_rome.helpers.errors import BaseRomeException, ConnectionPortsError, \
    NotSupportedError


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class RomeTestMapUni(BaseRomeTestCase):
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_uni_with_a_few_dst_ports(self, send_mock, recv_mock):
        address = '192.168.122.10:B'
        user = 'user'
        password = 'password'
        src_port = '{}/1/010'.format(address)
        dst_ports = ['{}/1/{}'.format(address, port_num) for port_num in (12, 14, 16)]

        emu = CliEmulator()
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
                BaseRomeException, r'(?i)is not allowed for multiple dst ports'
        ):
            self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_uni_with_connected_ports(self, send_mock, recv_mock):
        address = '192.168.122.10:A'
        user = 'user'
        password = 'password'
        src_port = '{}/1/001'.format(address)
        dst_ports = ['{}/1/002'.format(address)]

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_A),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_uni(self, send_mock, recv_mock):
        address = '192.168.122.10:A'
        user = 'user'
        password = 'password'
        src_port = '{}/1/003'.format(address)
        dst_ports = ['{}/1/004'.format(address)]

        connected_port_show_a = re.sub(
            r"^E3\[.+A3.*$",
            "E3[1AE3]         Unlocked     Enabled     Disconnected  0"
            "       W4[1AW4]       A3",
            PORT_SHOW_MATRIX_A,
            flags=re.MULTILINE,
        )
        connected_port_show_a = re.sub(
            r"W4\[.+A4.*$",
            "W4[1AW4]         Unlocked     Enabled     Disconnected  0"
            "       E3[1AE3]       A4",
            connected_port_show_a,
            flags=re.MULTILINE,
        )

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_A),
            Command(
                'connection create E3 to W4',
                '''ROME[TECH]# connection create E3 to W4
OK - request added to pending queue (E3-W4)
ROME[TECH]# 08-05-2019 09:20 CONNECTING...
08-05-2019 09:20 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect

'''
            ),
            Command('port show', connected_port_show_a),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_uni_failed(self, send_mock, recv_mock):
        address = '192.168.122.10:A'
        user = 'user'
        password = 'password'
        src_port = '{}/1/006'.format(address)
        dst_ports = ['{}/1/004'.format(address)]

        self.driver_commands._mapping_timeout = 0.1
        self.driver_commands._mapping_check_delay = 0.1

        emu = CliEmulator(
            [
                Command('', DEFAULT_PROMPT),
                Command('port show', PORT_SHOW_MATRIX_A),
                Command(
                    'connection create E6 to W4',
                    '''ROME[TECH]# 08-05-2019 09:32 
Ports details:
[E6[1AE6]] [W4[1AW4]]
08-05-2019 09:32 OPERATION VALIDATION FAILED:E6-W4 requestType=connect

ROME[TECH]# 
'''
                ),
                Command('port show', PORT_SHOW_MATRIX_A),
            ]
        )

        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
                ConnectionPortsError, 'Cannot connect port E6 to port W4'
        ):
            self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_uni_for_matrix_q(self, send_mock, recv_mock):
        address = '192.168.122.10:Q'
        user = 'user'
        password = 'password'
        src_port = '{}/1/03'.format(address)
        dst_ports = ['{}/1/04'.format(address)]

        emu = CliEmulator()
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)

        with self.assertRaisesRegexp(
                NotSupportedError, "MapUni for matrix Q doesn't supported"
        ):
            self.driver_commands.map_uni(src_port, dst_ports)

        emu.check_calls()


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class RomeTestMapBidi(BaseRomeTestCase):
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_bidi_with_connected_ports(self, send_mock, recv_mock):
        address = '192.168.122.10:B'
        user = 'user'
        password = 'password'
        src_port = '{}/1/249'.format(address)
        dst_port = '{}/1/253'.format(address)

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_B),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_bidi_one_connection(self, send_mock, recv_mock):
        address = '192.168.122.10:A'
        user = 'user'
        password = 'password'
        src_port = '{}/1/001'.format(address)
        dst_port = '{}/1/002'.format(address)

        connected_port_show_a = re.sub(
            r"^E2\[.+A2.*$",
            "E2[1AE2]         Unlocked     Enabled     Disconnected  0"
            "       W1[1AW1]       A2",
            PORT_SHOW_MATRIX_A,
            flags=re.MULTILINE,
        )
        connected_port_show_a = re.sub(
            r"W1\[.+A1.*$",
            "W1[1AW1]         Unlocked     Enabled     Disconnected  0"
            "       E2[1AE2]       A1",
            connected_port_show_a,
            flags=re.MULTILINE,
        )

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_A),
            Command(
                'connection create A1 to A2',
                '''ROME[TECH]# connection create A1 to A2
OK - request added to pending queue (A1-A2)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SKIPPED(already done):E1[1AE1]<->W2[1AW2] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W1[1AW1] OP:connect
08-06-2019 09:01 Connection A1<->A2 completed successfully
'''
            ),
            Command('port show', connected_port_show_a),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_bidi(self, send_mock, recv_mock):
        address = '192.168.122.10:A'
        user = 'user'
        password = 'password'
        src_port = '{}/1/003'.format(address)
        dst_port = '{}/1/004'.format(address)

        connected_port_show_a = re.sub(
            r"^E3\[.+A3.*$",
            "E3[1AE3]         Unlocked     Enabled     Disconnected  0"
            "       W4[1AW4]       A3",
            PORT_SHOW_MATRIX_A,
            flags=re.MULTILINE,
        )
        connected_port_show_a = re.sub(
            r"^E4\[.+A4.*$",
            "E4[1AE4]         Unlocked     Enabled     Disconnected  0"
            "       W3[1AW3]       A4",
            connected_port_show_a,
            flags=re.MULTILINE,
        )
        connected_port_show_a = re.sub(
            r"W3\[.+A3.*$",
            "W3[1AW3]         Unlocked     Enabled     Disconnected  0"
            "       E4[1AE4]       A3",
            connected_port_show_a,
            flags=re.MULTILINE,
        )
        connected_port_show_a = re.sub(
            r"W4\[.+A4.*$",
            "W4[1AW4]         Unlocked     Enabled     Disconnected  0"
            "       E3[1AE3]       A4",
            connected_port_show_a,
            flags=re.MULTILINE,
        )

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_A),
            Command(
                'connection create A3 to A4',
                '''ROME[TECH]# connection create A3 to A4
OK - request added to pending queue (A3-A4)
ROME[TECH]# 08-06-2019 09:01 CONNECTING...
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W4[1AW4] OP:connect
08-06-2019 09:01 CONNECTION OPERATION SUCCEEDED:E4[1AE2]<->W3[1AW3] OP:connect
08-06-2019 09:01 Connection A3<->A4 completed successfully
'''
            ),
            Command('port show', connected_port_show_a),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_bidi(src_port, dst_port)

        emu.check_calls()


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class RomeTestMapClear(BaseRomeTestCase):
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_clear_matrix_b(self, send_mock, recv_mock):
        address = '192.168.122.10:B'
        user = 'user'
        password = 'password'
        ports = ['{}/1/{}'.format(address, port_id) for port_id in (249, 218, 246)]

        disconnected_port_show_b = re.sub(
            r"^E246\[.+B246.+$",
            "E246[1BE118]     Unlocked     Enabled     Disconnected  0"
            "                      B246",
            PORT_SHOW_MATRIX_B,
            flags=re.MULTILINE,
        )
        disconnected_port_show_b = re.sub(
            r"^E249\[.+B249.+$",
            "E249[1BE121]     Unlocked     Enabled     Connected     13"
            "                     B249",
            disconnected_port_show_b,
            flags=re.MULTILINE,
        )
        disconnected_port_show_b = re.sub(
            r"^E253\[.+B253.+$",
            "E253[1BE125]     Unlocked     Enabled     Connected     13"
            "                     B253",
            disconnected_port_show_b,
            flags=re.MULTILINE,
        )
        disconnected_port_show_b = re.sub(
            r"^W247\[.+B247.+$",
            "W247[1BW119]     Unlocked     Enabled     Disconnected  0"
            "                      B247",
            disconnected_port_show_b,
            flags=re.MULTILINE,
        )
        disconnected_port_show_b = re.sub(
            r"^W249\[.+B249.+$",
            "W249[1BW121]     Unlocked     Enabled     Connected     13"
            "                     B249",
            disconnected_port_show_b,
            flags=re.MULTILINE,
        )
        disconnected_port_show_b = re.sub(
            r"^E253\[.+B253.+$",
            "W253[1BW125]     Unlocked     Enabled     Connected     13"
            "                     B253",
            disconnected_port_show_b,
            flags=re.MULTILINE,
        )

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_B),
            Command(
                'connection disconnect E246 from W247',
                '''ROME[TECH]# connection disconnect E246 from W247
OK - request added to pending queue (E246-W247)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E246[1AE246]<->W247[1AW247] OP:disconnect
'''
            ),
            Command(
                'connection disconnect E249 from W253',
                '''ROME[TECH]# connection disconnect E249 from W253
OK - request added to pending queue (E249-W253)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E249[1AE249]<->W253[1AW253] OP:disconnect
'''
            ),
            Command(
                'connection disconnect E253 from W249',
                '''ROME[TECH]# connection disconnect E253 from W249
OK - request added to pending queue (E253-W249)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E253[1AE253]<->W249[1AW249] OP:disconnect
'''
            ),
            Command('port show', disconnected_port_show_b),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear(ports)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_clear_matrix_q(self, send_mock, recv_mock):
            address = '192.168.122.10:Q'
            user = 'user'
            password = 'password'
            ports = ['{}/1/1'.format(address)]

            disconnected_ports_show = re.sub(
                r"E1\[.+E5\[",
                """E1[1AE1]         Unlocked     Enabled     Connected     5                      Q1      
E2[1AE2]         Unlocked     Enabled     Connected     5                      Q1      
E3[1AE3]         Unlocked     Enabled     Connected     3                      Q2      
E4[1AE4]         Unlocked     Enabled     Connected     3                      Q2      
E5[""",
                PORT_SHOW_MATRIX_Q,
                flags=re.DOTALL,
            )
            disconnected_ports_show = re.sub(
                r"W1\[.+W5\[",
                """W1[1AW1]         Unlocked     Enabled     Connected     5                      Q1      
W2[1AW2]         Unlocked     Enabled     Connected     5                      Q1      
W3[1AW3]         Unlocked     Enabled     Connected     3                      Q2      
W4[1AW4]         Unlocked     Enabled     Connected     3                      Q2      
W5[""",
                disconnected_ports_show,
                flags=re.DOTALL,
            )
            disconnected_ports_show = re.sub(
                r"E129\[.+E133\[",
                """E129[1BE1]       Unlocked     Enabled     Connected     5                      Q1      
E130[1BE2]       Unlocked     Enabled     Connected     5                      Q1      
E131[1BE3]       Unlocked     Enabled     Connected     3                      Q2      
E132[1BE4]       Unlocked     Enabled     Connected     3                      Q2      
E133[""",
                disconnected_ports_show,
                flags=re.DOTALL,
            )
            disconnected_ports_show = re.sub(
                r"W129\[.+W133\[",
                """W129[1BW1]       Unlocked     Enabled     Connected     5                      Q1      
W130[1BW2]       Unlocked     Enabled     Connected     5                      Q1      
W131[1BW3]       Unlocked     Enabled     Connected     3                      Q2      
W132[1BW4]       Unlocked     Enabled     Connected     3                      Q2      
W133[""",
                disconnected_ports_show,
                flags=re.DOTALL,
            )

            emu = CliEmulator([
                Command('', DEFAULT_PROMPT),
                Command('port show', PORT_SHOW_MATRIX_Q),
                Command(
                    'connection disconnect E1 from W4',
                    '''ROME[TECH]# connection disconnect E1 from W4
OK - request added to pending queue (E1-W4)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W4[1AW4] OP:disconnect
'''
                ),
                Command(
                    'connection disconnect E2 from W3',
                    '''ROME[TECH]# connection disconnect E2 from W3
OK - request added to pending queue (E2-W3)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W3[1AW3] OP:disconnect
'''
                ),
                Command(
                    'connection disconnect E3 from W2',
                    '''ROME[TECH]# connection disconnect E3 from W2
OK - request added to pending queue (E3-W2)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E3[1AE3]<->W2[1AW2] OP:disconnect
'''
                ),
                Command(
                    'connection disconnect E4 from W1',
                    '''ROME[TECH]# connection disconnect E4 from W1
OK - request added to pending queue (E4-W1)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E4[1AE4]<->W1[1AW1] OP:disconnect
'''
                ),
                Command(
                    'connection disconnect E129 from W132',
                    '''ROME[TECH]# connection disconnect E129 from W132
OK - request added to pending queue (E129-W132)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1AE129]<->W2[1AW132] OP:disconnect
'''
                ),
                Command(
                    'connection disconnect E130 from W131',
                    '''ROME[TECH]# connection disconnect E130 from W131
OK - request added to pending queue (E130-W131)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1AE130]<->W131[1AW131] OP:disconnect
'''
                ),
                Command(
                    'connection disconnect E131 from W130',
                    '''ROME[TECH]# connection disconnect E131 from W130
OK - request added to pending queue (E131-W130)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E131[1AE131]<->W130[1AW130] OP:disconnect
'''
                ),
                Command(
                    'connection disconnect E132 from W129',
                    '''ROME[TECH]# connection disconnect E132 from W129
OK - request added to pending queue (E132-W129)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E132[1AE132]<->W129[1AW129] OP:disconnect
'''
                ),
                Command('port show', disconnected_ports_show),
            ])
            send_mock.side_effect = emu.send_line
            recv_mock.side_effect = emu.receive_all

            self.driver_commands.login(address, user, password)
            self.driver_commands.map_clear(ports)

            emu.check_calls()


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class RomeTestMapClearTo(BaseRomeTestCase):
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_clear_to_matrix_b(self, send_mock, recv_mock):
        address = '192.168.122.10:B'
        user = 'user'
        password = 'password'
        src_port = '{}/1/249'.format(address)
        dst_ports = ['{}/1/253'.format(address)]

        disconnected_port_show_b = re.sub(
            r"^E249\[.+B249.+$",
            "E249[1BE121]     Unlocked     Enabled     Connected     13"
            "                     B249",
            PORT_SHOW_MATRIX_B,
            flags=re.MULTILINE,
        )
        disconnected_port_show_b = re.sub(
            r"^W249\[.+B249.+$",
            "W249[1BW121]     Unlocked     Enabled     Connected     13"
            "                     B249",
            disconnected_port_show_b,
            flags=re.MULTILINE,
        )

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_B),
            Command(
                'connection disconnect E249 from W253',
                '''ROME[TECH]# connection disconnect E249 from W253
OK - request added to pending queue (E249-W253)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E249[1AE249]<->W253[1AW253] OP:disconnect
'''
            ),
            Command('port show', disconnected_port_show_b),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear_to(src_port, dst_ports)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_map_clear_to_matrix_q(self, send_mock, recv_mock):
        address = '192.168.122.10:Q'
        user = 'user'
        password = 'password'
        src_port = '{}/1/1'.format(address)
        dst_ports = ['{}/1/2'.format(address)]

        disconnected_ports_show = re.sub(
            r"(?<=\n)E1\[.+?E3\[",
            """E1[1AE1]         Unlocked     Enabled     Connected     5                      Q1      
E2[1AE2]         Unlocked     Enabled     Connected     5                      Q1      
E3[""",
            PORT_SHOW_MATRIX_Q,
            flags=re.DOTALL,
        )
        disconnected_ports_show = re.sub(
            r"(?<=\n)W1\[.+?W3\[",
            """W1[1AW1]         Unlocked     Enabled     Connected     5                      Q1      
W2[1AW2]         Unlocked     Enabled     Connected     5                      Q1      
W3[""",
            disconnected_ports_show,
            flags=re.DOTALL,
        )
        disconnected_ports_show = re.sub(
            r"(?<=\n)E129\[.+?E131\[",
            """E129[1BE1]       Unlocked     Enabled     Connected     5                      Q1      
E130[1BE2]       Unlocked     Enabled     Connected     5                      Q1      
E131[""",
            disconnected_ports_show,
            flags=re.DOTALL,
        )
        disconnected_ports_show = re.sub(
            r"(?<=\n)W129\[.+?W131\[",
            """W129[1BW1]       Unlocked     Enabled     Connected     5                      Q1      
W130[1BW2]       Unlocked     Enabled     Connected     5                      Q1      
W131[""",
            disconnected_ports_show,
            flags=re.DOTALL,
        )

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command('port show', PORT_SHOW_MATRIX_Q),
            Command(
                'connection disconnect E1 from W4',
                '''ROME[TECH]# connection disconnect E1 from W4
OK - request added to pending queue (E1-W4)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E1[1AE1]<->W4[1AW4] OP:disconnect
'''
            ),
            Command(
                'connection disconnect E2 from W3',
                '''ROME[TECH]# connection disconnect E2 from W3
OK - request added to pending queue (E2-W3)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E2[1AE2]<->W3[1AW3] OP:disconnect
'''
            ),
            Command(
                'connection disconnect E129 from W132',
                '''ROME[TECH]# connection disconnect E129 from W132
OK - request added to pending queue (E129-W132)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E129[1AE129]<->W2[1AW132] OP:disconnect
'''
            ),
            Command(
                'connection disconnect E130 from W131',
                '''ROME[TECH]# connection disconnect E130 from W131
OK - request added to pending queue (E130-W131)
ROME[TECH]# 08-05-2019 12:19 DISCONNECTING...
08-05-2019 12:19 CONNECTION OPERATION SUCCEEDED:E130[1AE130]<->W131[1AW131] OP:disconnect
'''
            ),
            Command('port show', disconnected_ports_show),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        self.driver_commands.map_clear_to(src_port, dst_ports)

        emu.check_calls()
