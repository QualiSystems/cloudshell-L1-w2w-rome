from itertools import chain

from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port
from mock import MagicMock, patch

from w2w_rome.helpers.errors import BaseRomeException

from tests.w2w_rome.base import (
    DEFAULT_PROMPT,
    PORT_SHOW_MATRIX_A,
    PORT_SHOW_MATRIX_A_CHANGED_PORT,
    PORT_SHOW_MATRIX_A_Q,
    PORT_SHOW_MATRIX_B,
    PORT_SHOW_MATRIX_Q,
    PORT_SHOW_MATRIX_Q128_1,
    PORT_SHOW_MATRIX_Q128_2,
    PORT_SHOW_MATRIX_Q128_2_CHANGED_PORT,
    PORT_SHOW_MATRIX_Q_B,
    PORT_SHOW_MATRIX_Q_BROKEN_TABLE_OUTPUT,
    PORT_SHOW_MATRIX_XY,
    PORT_SHOW_MATRIX_XY_CHANGED_PORT,
    SHOW_BOARD,
    BaseRomeTestCase,
    CliEmulator,
    Command,
)


@patch("cloudshell.cli.session.ssh_session.paramiko", MagicMock())
@patch(
    "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer",
    MagicMock(return_value=""),
)
class RomeTestAutoload(BaseRomeTestCase):
    def test_autoload_without_matrix_letter(self):
        host = "192.168.122.10"
        address = "{}".format(host)
        with self.assertRaisesRegexp(
            BaseRomeException,
            r"Resource address should specify MatrixA, MatrixB, MatrixQ or MatrixXY",
        ):
            self.driver_commands.get_resource_description(address)

    def test_autoload_matrix_b(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(129, 257)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_B,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix B", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade B", blade.name)
        self.assertEqual(address + "/B", blade.address)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port B{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/B/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port B{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(3, len(connected_ports))
        self.assertDictEqual(
            {
                "Port B247": "Port B246",
                "Port B249": "Port B253",
                "Port B253": "Port B249",
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_a(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_A,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix A", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade A", blade.name)
        self.assertEqual(address + "/A", blade.address)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port A{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/A/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port A{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(len(connected_ports), 1)
        self.assertDictEqual(
            {"Port A002": "Port A001"},
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_a_changed_port(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_A_CHANGED_PORT,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix A", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade A", blade.name)
        self.assertEqual(address + "/A", blade.address)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port A{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/A/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port A{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(len(connected_ports), 2)
        self.assertDictEqual(
            {"Port A002": "Port A001", "Port A003": "Port A005"},
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_q(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(2) for i in range(1, 65)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix Q", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade Q", blade.name)
        self.assertEqual(address + "/Q", blade.address)
        self.assertEqual(64, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Q{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Q/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port Q{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(2, len(connected_ports))
        self.assertDictEqual(
            {"Port Q01": "Port Q02", "Port Q02": "Port Q01"},
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_q_broken_table_output(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(2) for i in range(1, 65)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command("port show", PORT_SHOW_MATRIX_Q_BROKEN_TABLE_OUTPUT),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix Q", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade Q", blade.name)
        self.assertEqual(address + "/Q", blade.address)
        self.assertEqual(64, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Q{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Q/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port Q{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(2, len(connected_ports))
        self.assertDictEqual(
            {"Port Q01": "Port Q02", "Port Q02": "Port Q01"},
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_q128(self):
        first_host = "192.168.122.10"
        second_host = "192.168.122.11"
        address = "{first_host}:{second_host}:q".format(**locals())
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu1 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q128_1,
                ),
                Command("show board", SHOW_BOARD),
            ],
        )
        emu2 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q128_2,
                ),
                Command("show board", SHOW_BOARD),
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

        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix Q", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade Q", blade.name)
        self.assertEqual(address + "/Q", blade.address)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Q{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Q/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port Q{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(2, len(connected_ports))
        self.assertDictEqual(
            {"Port Q001": "Port Q002", "Port Q002": "Port Q001"},
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu1.check_calls()
        emu2.check_calls()

    def test_autoload_matrix_q128_changed_ports(self):
        first_host = "192.168.122.10"
        second_host = "192.168.122.11"
        address = "{first_host}:{second_host}:q".format(**locals())
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu1 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q128_1,
                ),
                Command("show board", SHOW_BOARD),
            ],
        )
        emu2 = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q128_2_CHANGED_PORT,
                ),
                Command("show board", SHOW_BOARD),
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

        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix Q", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade Q", blade.name)
        self.assertEqual(address + "/Q", blade.address)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Q{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Q/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port Q{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(2, len(connected_ports))
        self.assertDictEqual(
            {"Port Q001": "Port Q002", "Port Q002": "Port Q001"},
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu1.check_calls()
        emu2.check_calls()

    def test_autoload_matrix_xy(self):
        host = "192.168.122.10"
        address = "{}:XY".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_XY,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        # One chassis
        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))
        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(2, len(chassis.child_resources))

        # blade X
        blade_x = chassis.child_resources["X"]
        self.assertIsInstance(blade_x, Blade)
        self.assertEqual("Rome Matrix X", blade_x.model_name)
        self.assertEqual("NA", blade_x.serial_number)
        self.assertEqual("Blade X", blade_x.name)
        self.assertEqual(address + "/X", blade_x.address)
        self.assertEqual(128, len(blade_x.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade_x.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port X{}".format, expected_ports_str_range),
            (port.name for port in blade_x.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/X/{}").format, expected_ports_str_range),
            (port.address for port in blade_x.child_resources.values()),
        )

        # blade Y
        blade_y = chassis.child_resources["Y"]
        self.assertIsInstance(blade_y, Blade)
        self.assertEqual("Rome Matrix Y", blade_y.model_name)
        self.assertEqual("NA", blade_y.serial_number)
        self.assertEqual("Blade Y", blade_y.name)
        self.assertEqual(address + "/Y", blade_y.address)
        self.assertEqual(128, len(blade_y.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade_y.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Y{}".format, expected_ports_str_range),
            (port.name for port in blade_y.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Y/{}").format, expected_ports_str_range),
            (port.address for port in blade_y.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in chain(
            blade_x.child_resources.items(), blade_y.child_resources.items()
        ):
            self.assertIsInstance(port, Port)
            blade_letter = port.name.split(" ", 1)[1][0]
            self.assertIn(blade_letter, "XY")
            self.assertEqual(
                "Port {}{}".format(blade_letter, port.resource_id), port.name
            )
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(7, len(connected_ports))
        self.assertDictEqual(
            {
                "Port X001": "Port Y001",
                "Port Y001": "Port X001",
                "Port X002": "Port Y002",
                "Port Y002": "Port X002",
                "Port X004": "Port Y004",
                "Port Y004": "Port X004",
                "Port Y007": "Port X007",
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_xy_changed_port(self):
        host = "192.168.122.10"
        address = "{}:XY".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_XY_CHANGED_PORT,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        # One chassis
        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))
        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(2, len(chassis.child_resources))

        # blade X
        blade_x = chassis.child_resources["X"]
        self.assertIsInstance(blade_x, Blade)
        self.assertEqual("Rome Matrix X", blade_x.model_name)
        self.assertEqual("NA", blade_x.serial_number)
        self.assertEqual("Blade X", blade_x.name)
        self.assertEqual(address + "/X", blade_x.address)
        self.assertEqual(128, len(blade_x.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade_x.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port X{}".format, expected_ports_str_range),
            (port.name for port in blade_x.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/X/{}").format, expected_ports_str_range),
            (port.address for port in blade_x.child_resources.values()),
        )

        # blade Y
        blade_y = chassis.child_resources["Y"]
        self.assertIsInstance(blade_y, Blade)
        self.assertEqual("Rome Matrix Y", blade_y.model_name)
        self.assertEqual("NA", blade_y.serial_number)
        self.assertEqual("Blade Y", blade_y.name)
        self.assertEqual(address + "/Y", blade_y.address)
        self.assertEqual(128, len(blade_y.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade_y.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Y{}".format, expected_ports_str_range),
            (port.name for port in blade_y.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Y/{}").format, expected_ports_str_range),
            (port.address for port in blade_y.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in chain(
            blade_x.child_resources.items(), blade_y.child_resources.items()
        ):
            self.assertIsInstance(port, Port)
            blade_letter = port.name.split(" ", 1)[1][0]
            self.assertIn(blade_letter, "XY")
            self.assertEqual(
                "Port {}{}".format(blade_letter, port.resource_id), port.name
            )
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(7, len(connected_ports))
        self.assertDictEqual(
            {
                "Port X001": "Port Y001",
                "Port Y001": "Port X001",
                "Port X002": "Port Y002",
                "Port Y002": "Port X002",
                "Port X004": "Port Y004",
                "Port Y004": "Port X004",
                "Port Y007": "Port X007",
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_load_a_from_mix_a_and_q(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_A_Q,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix A", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade A", blade.name)
        self.assertEqual(address + "/A", blade.address)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port A{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/A/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port A{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(len(connected_ports), 6)
        self.assertDictEqual(
            {
                "Port A012": "Port A060",
                "Port A015": "Port A057",
                "Port A016": "Port A058",
                "Port A057": "Port A015",
                "Port A058": "Port A016",
                "Port A060": "Port A012",
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_load_q_from_mix_a_and_q(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(2) for i in range(1, 33)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_A_Q,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix Q", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade Q", blade.name)
        self.assertEqual(address + "/Q", blade.address)
        self.assertEqual(32, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Q{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Q/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port Q{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(len(connected_ports), 2)
        self.assertDictEqual(
            {
                "Port Q09": "Port Q28",
                "Port Q28": "Port Q09",
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_load_b_from_mix_q_and_b(self):
        host = "192.168.122.10"
        address = "{}:B".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(3) for i in range(1, 129)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q_B,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix B", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade B", blade.name)
        self.assertEqual(address + "/B", blade.address)
        self.assertEqual(128, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port B{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/B/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port B{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(len(connected_ports), 8)
        self.assertDictEqual(
            {
                "Port B033": "Port B109",
                "Port B034": "Port B110",
                "Port B035": "Port B111",
                "Port B036": "Port B112",
                "Port B109": "Port B033",
                "Port B110": "Port B034",
                "Port B111": "Port B035",
                "Port B112": "Port B036",
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_load_q_from_mix_q_and_b(self):
        host = "192.168.122.10"
        address = "{}:Q".format(host)
        user = "user"
        password = "password"
        expected_ports_str_range = [str(i).zfill(2) for i in range(1, 33)]

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q_B,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        info = self.driver_commands.get_resource_description(address)

        self.assertIsNotNone(info)
        self.assertEqual(1, len(info.resource_info_list))

        chassis = info.resource_info_list[0]
        self.assertIsInstance(chassis, Chassis)
        self.assertEqual("9727-4733-2222", chassis.serial_number)
        self.assertEqual("Rome Chassis", chassis.model_name)
        self.assertEqual(address, chassis.address)
        self.assertEqual(1, len(chassis.child_resources))

        blade = chassis.child_resources.values()[0]
        self.assertIsInstance(blade, Blade)
        self.assertEqual("Rome Matrix Q", blade.model_name)
        self.assertEqual("NA", blade.serial_number)
        self.assertEqual("Blade Q", blade.name)
        self.assertEqual(address + "/Q", blade.address)
        self.assertEqual(32, len(blade.child_resources))
        self.assertItemsEqual(
            expected_ports_str_range,
            blade.child_resources.keys(),
        )
        self.assertItemsEqual(
            map("Port Q{}".format, expected_ports_str_range),
            (port.name for port in blade.child_resources.values()),
        )
        self.assertItemsEqual(
            map((address + "/Q/{}").format, expected_ports_str_range),
            (port.address for port in blade.child_resources.values()),
        )

        connected_ports = []
        for port_id, port in blade.child_resources.items():
            self.assertIsInstance(port, Port)
            self.assertEqual("Port Q{}".format(port.resource_id), port.name)
            if port.mapping:
                connected_ports.append(port)

        self.assertEqual(len(connected_ports), 2)
        self.assertDictEqual(
            {
                "Port Q04": "Port Q11",
                "Port Q11": "Port Q04",
            },
            {p.name: p.mapping.name for p in connected_ports},
        )

        emu.check_calls()

    def test_autoload_matrix_q_choosed_another_matrix(self):
        host = "192.168.122.10"
        address = "{}:A".format(host)
        user = "user"
        password = "password"

        emu = CliEmulator(
            [
                Command("", DEFAULT_PROMPT),
                Command(
                    "port show",
                    PORT_SHOW_MATRIX_Q,
                ),
                Command("show board", SHOW_BOARD),
            ]
        )
        self.send_line_func_map[host] = emu.send_line
        self.receive_all_func_map[host] = emu.receive_all

        self.driver_commands.login(address, user, password)
        with self.assertRaisesRegexp(
            BaseRomeException, r"No 'A' ports found on the device"
        ):
            self.driver_commands.get_resource_description(address)

        emu.check_calls()
