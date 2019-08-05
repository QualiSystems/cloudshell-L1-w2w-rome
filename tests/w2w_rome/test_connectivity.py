from mock import patch, MagicMock

from tests.w2w_rome.base import BaseRomeTestCase, CliEmulator, Command, \
    DEFAULT_PROMPT, PORT_SHOW_MATRIX_A
from w2w_rome.helpers.errors import BaseRomeException, ConnectionPortsError, \
    NotSupportedError


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class RomeTestConnectivity(BaseRomeTestCase):
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
            Command(
                'port show E3',
                '''port show E3
================ ============ =========== ============= ======= ============== ========
Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
E3[1AE3]         Unlocked     Enabled     Connected     0       W4[1BW4]       A3      

ROME[TECH]# 
'''
            ),
            Command(
                'port show W4',
                '''ROME[TECH]# port show W4
================ ============ =========== ============= ======= ============== ========
Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
W4[1AW4]         Unlocked     Enabled     Connected     0       E3[1BE3]       A4      

ROME[TECH]# 
'''
            )
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

        commands_check_ports = [

                              ] * 2

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
                Command(
                    'port show E6',
                    '''port show E6
================ ============ =========== ============= ======= ============== ========
Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
E6[1AE6]         Unlocked     Enabled     Disconnected  0                      A6      

ROME[TECH]# 
'''
                ),
                Command(
                    'port show W4',
                    '''ROME[TECH]# port show W4
================ ============ =========== ============= ======= ============== ========
Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
W4[1AW4]         Unlocked     Enabled     Disconnected  0                      A4      

ROME[TECH]# 
'''
                ),
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
