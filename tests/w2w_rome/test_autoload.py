from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port
from mock import patch, MagicMock

from w2w_rome.helpers.errors import BaseRomeException

from tests.w2w_rome.base import BaseRomeTestCase, CliEmulator, Command, DEFAULT_PROMPT, \
    SHOW_BOARD, PORT_SHOW_MATRIX_B, PORT_SHOW_MATRIX_A, PORT_SHOW_MATRIX_Q


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class RomeTestAutoload(BaseRomeTestCase):
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_autoload_without_matrix_letter(self, send_mock, recv_mock):
        address = '192.168.122.10'
        with self.assertRaisesRegexp(
                BaseRomeException,
                r'Resource address should specify MatrixA, MatrixB or Q'
        ):
            self.driver_commands.get_resource_description(address)

        send_mock.assert_not_called()
        recv_mock.assert_not_called()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_autoload_matrix_b(self, send_mock, recv_mock):
        address = '192.168.122.10:B'
        user = 'user'
        password = 'password'

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command(
                'port show',
                PORT_SHOW_MATRIX_B,
            ),
            Command('show board', SHOW_BOARD),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual('9727-4733-2222', chassis.serial_number)
        self.assertEqual('Rome Chassis', chassis.model_name)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual('Rome Matrix B', blade.model_name)
        self.assertEqual('NA', blade.serial_number)
        self.assertEqual('Blade B', blade.name)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            (str(i).zfill(3) for i in range(129, 257)),
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            ('Port B{}'.format(str(i).zfill(3)) for i in range(129, 257)),
            (port.name for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual('Port B{}'.format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(3, len(connected_ports))
        self.assertDictEqual(
            {
                'Port B247': 'Port B246',
                'Port B249': 'Port B253',
                'Port B253': 'Port B249',
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_autoload_matrix_a(self, send_mock, recv_mock):
        address = '192.168.122.10:A'
        user = 'user'
        password = 'password'

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command(
                'port show',
                PORT_SHOW_MATRIX_A,
            ),
            Command('show board', SHOW_BOARD),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual('9727-4733-2222', chassis.serial_number)
        self.assertEqual('Rome Chassis', chassis.model_name)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual('Rome Matrix A', blade.model_name)
        self.assertEqual('NA', blade.serial_number)
        self.assertEqual('Blade A', blade.name)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            (str(i).zfill(3) for i in range(1, 129)),
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            ('Port A{}'.format(str(i).zfill(3)) for i in range(1, 129)),
            (port.name for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual('Port A{}'.format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(len(connected_ports), 1)
        self.assertDictEqual(
            {'Port A002': 'Port A001'},
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_autoload_matrix_q(self, send_mock, recv_mock):
        address = '192.168.122.10:Q'
        user = 'user'
        password = 'password'

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command(
                'port show',
                PORT_SHOW_MATRIX_Q,
            ),
            Command('show board', SHOW_BOARD),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual('9727-4733-2222', chassis.serial_number)
        self.assertEqual('Rome Chassis', chassis.model_name)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual('Rome Matrix Q', blade.model_name)
        self.assertEqual('NA', blade.serial_number)
        self.assertEqual('Blade Q', blade.name)
        self.assertEqual(64, len(blade.child_resources))
        self.assertItemsEqual(
            (str(i).zfill(2) for i in range(1, 65)),
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            ('Port Q{}'.format(str(i).zfill(2)) for i in range(1, 65)),
            (port.name for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual('Port Q{}'.format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(2, len(connected_ports))
        self.assertDictEqual(
            {
                'Port Q01': 'Port Q02',
                'Port Q02': 'Port Q01',
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_autoload_matrix_q_choosed_another_matrix(self, send_mock, recv_mock):
        address = '192.168.122.10:A'
        user = 'user'
        password = 'password'

        emu = CliEmulator([
            Command('', DEFAULT_PROMPT),
            Command(
                'port show',
                PORT_SHOW_MATRIX_Q,
            ),
            Command('show board', SHOW_BOARD),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.driver_commands.login(address, user, password)
        with self.assertRaisesRegexp(BaseRomeException, r'You should specify MatrixQ'):
            self.driver_commands.get_resource_description(address)

        emu.check_calls()
