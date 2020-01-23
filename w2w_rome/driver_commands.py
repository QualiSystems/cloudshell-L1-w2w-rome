#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys

import time
from collections import defaultdict
from contextlib import contextmanager

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.response.response_info import GetStateIdResponseInfo, AttributeValueResponseInfo, \
    ResourceDescriptionResponseInfo
from w2w_rome.cli.rome_cli_handler import RomeCliHandler
from w2w_rome.command_actions.mapping_actions import MappingActions
from w2w_rome.command_actions.system_actions import SystemActions
from w2w_rome.helpers.autoload_helper import AutoloadHelper
from w2w_rome.helpers.errors import BaseRomeException, ConnectionPortsError, \
    NotSupportedError
from w2w_rome.helpers.port_entity import PortTable


class DriverCommands(DriverCommandsInterface):
    """Driver commands implementation."""

    ADDRESS_PATTERN = re.compile(
        (
            r'^(?P<host>[^:]+?):'
            r'((?P<second_host>[^:]+?):)?'
            r'(matrix)?(?P<letter>(a|b|q))(/.+)?$'
        ),
        re.IGNORECASE,
    )

    def __init__(self, logger, runtime_config):
        """
        :type logger: logging.Logger
        :type runtime_config: cloudshell.layer_one.core.helper.runtime_configuration.RuntimeConfiguration
        """
        self._logger = logger
        self._runtime_config = runtime_config
        self._cli_handler = RomeCliHandler(logger)
        self._second_cli_handler = None

        self._mapping_timeout = runtime_config.read_key('MAPPING.TIMEOUT', 120)
        self._mapping_check_delay = runtime_config.read_key('MAPPING.CHECK_DELAY', 3)
        self.support_multiple_blades = runtime_config.read_key('SUPPORT_MULTIPLE_BLADES', False)

        self.__ports_association_table = None

    def _initialize_second_cli_handler(self):
        if self._second_cli_handler is None:
            self._second_cli_handler = RomeCliHandler(self._logger)
            self._cli_handler._cli._session_pool._pool.maxsize = 2
            self._second_cli_handler._cli._session_pool._pool.maxsize = 2

    def login(self, address, username, password):
        """Perform login operation on the device.

        :param address: resource address specified in CloudShell, "192.168.42.240:A"
        :param username: username to login on the device
        :param password: password
        :return: None
        :raises Exception: if command failed
        """
        hosts, _ = self.split_addresses_and_letter(address)
        first_host = hosts[0]

        self._cli_handler.define_session_attributes(first_host, username, password)
        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session, self._logger)
            self._logger.info('Connected to ' + system_actions.board_table().get('model_name'))

        if len(hosts) == 2:
            second_host = hosts[1]
            self._initialize_second_cli_handler()
            self._second_cli_handler.define_session_attributes(
                second_host, username, password
            )
            with self._second_cli_handler.default_mode_service() as session:
                system_actions = SystemActions(session, self._logger)
                self._logger.info(
                    'Connected to ' + system_actions.board_table().get('model_name')
                )

    def get_state_id(self):
        """
        Check if CS synchronized with the device.
        :return: Synchronization ID, GetStateIdResponseInfo(-1) if not used
        :rtype: cloudshell.layer_one.core.response.response_info.GetStateIdResponseInfo
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Execute command
                chassis_name = session.send_command('show chassis sub_port_name')
                return chassis_name
        """
        return GetStateIdResponseInfo('-1')

    def set_state_id(self, state_id):
        """
        Set synchronization state id to the device, called after Autoload or SyncFomDevice commands
        :param state_id: synchronization ID
        :type state_id: str
        :return: None
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.config_mode_service() as session:
                # Execute command
                session.send_command('set chassis name {}'.format(state_id))
        """
        pass

    def convert_cs_port_to_port_name(self, cs_port):
        _, matrix_letter = self.split_addresses_and_letter(cs_port)
        return '{}{}'.format(
            matrix_letter, cs_port.rsplit('/', 1)[-1].lstrip('0')
        )

    def _bidi_connect_ports(self, src_logic_port, dst_logic_port, cli_services):
        ports_names = [
            src_logic_port.original_logical_name, dst_logic_port.original_logical_name
        ]

        for cli_service in cli_services:
            mapping_actions = MappingActions(cli_service, self._logger)
            mapping_actions.connect(*ports_names)
            self._wait_ports_not_in_pending_connections(
                mapping_actions,
                [ports_names],
                2 * len(src_logic_port.rome_ports),
            )

    def _disconnect_logical_ports(self, src_logic_port, dst_logic_port, cli_services):
        for cli_service in cli_services:
            mapping_actions = MappingActions(cli_service, self._logger)
            mapping_actions.disconnect(
                src_logic_port.original_logical_name,
                dst_logic_port.original_logical_name,
            )

    def map_bidi(self, src_port, dst_port):
        """
        Create a bidirectional connection between source and destination ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_port: dst port address, '192.168.42.240/1/22'
        :type dst_port: str
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                session.send_command('map bidir {0} {1}'.format(convert_port(src_port), convert_port(dst_port)))

        """
        self._logger.info(
            'MapBidi, SrcPort: {0}, DstPort: {1}'.format(src_port, dst_port)
        )

        src_port_name = self.convert_cs_port_to_port_name(src_port)
        dst_port_name = self.convert_cs_port_to_port_name(dst_port)

        with self._get_cli_services() as cli_services:
            port_table = self._get_port_table(cli_services)
            src_logic_port = port_table[src_port_name]
            dst_logic_port = port_table[dst_port_name]

            if port_table.is_connected(src_logic_port, dst_logic_port, bidi=True):
                self._logger.debug(
                    'Ports {} and {} already connected'.format(
                        src_port_name, dst_port_name
                    )
                )
                return

            port_table.verify_ports_for_connection(
                src_logic_port, dst_logic_port, bidi=True
            )
            self._bidi_connect_ports(src_logic_port, dst_logic_port, cli_services)

            port_table = self._get_port_table(cli_services)
            src_logic_port = port_table[src_port_name]
            dst_logic_port = port_table[dst_port_name]

            if not port_table.is_connected(src_logic_port, dst_logic_port, bidi=True):
                self._disconnect_logical_ports(
                    src_logic_port, dst_logic_port, cli_services
                )
                raise ConnectionPortsError(
                    'Cannot connect port {} to port {} during {}sec'.format(
                        src_logic_port.name, dst_logic_port.name, self._mapping_timeout
                    )
                )

    def _wait_ports_not_in_pending_connections(
            self, mapping_actions, ports, amount_ports_to_connect
    ):
        """Wait for ports go away from pending connections.

        :type mapping_actions: MappingActions
        :param ports: src and dst ports that connects
        :type ports: list[tuple[str, str]]
        :type amount_ports_to_connect: int
        """
        end_time = time.time() + (self._mapping_timeout * amount_ports_to_connect)
        while time.time() < end_time:
            time.sleep(self._mapping_check_delay)
            if not mapping_actions.ports_in_pending_connections(ports):
                break
        else:
            msg = 'There are some pending connections after {}sec'.format(
                self._mapping_timeout
            )
            raise BaseRomeException(msg)

    def map_uni(self, src_port, dst_ports):
        """
        Unidirectional mapping of two ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/22', '192.168.42.240/1/23']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                for dst_port in dst_ports:
                    session.send_command('map {0} also-to {1}'.format(convert_port(src_port), convert_port(dst_port)))
        """
        if len(dst_ports) != 1:
            raise BaseRomeException(
                'MapUni operation is not allowed for multiple Dst ports'
            )
        _, letter = self.split_addresses_and_letter(src_port)
        if letter.startswith('Q'):
            raise NotSupportedError(
                "MapUni for matrix Q doesn't supported"
            )
        self._logger.info('MapUni, SrcPort: {0}, DstPort: {1}'.format(
            src_port, dst_ports[0])
        )

        src_port_name = self.convert_cs_port_to_port_name(src_port)
        dst_port_name = self.convert_cs_port_to_port_name(dst_ports[0])

        with self._cli_handler.default_mode_service() as cli_service:
            system_actions = SystemActions(cli_service, self._logger)
            mapping_actions = MappingActions(cli_service, self._logger)
            port_table = system_actions.get_port_table()
            src_logic_port = port_table[src_port_name]
            dst_logic_port = port_table[dst_port_name]

            if port_table.is_connected(src_logic_port, dst_logic_port):
                self._logger.debug(
                    'Ports {} and {} already connected'.format(
                        src_port_name, dst_port_name
                    )
                )
                return

            port_table.verify_ports_for_connection(src_logic_port, dst_logic_port)
            src = src_logic_port.e_sub_ports[0].sub_port_name
            dst = dst_logic_port.w_sub_ports[0].sub_port_name
            mapping_actions.connect(src, dst)
            self._wait_ports_not_in_pending_connections(
                mapping_actions, [(src, dst)], 1
            )

            port_table = system_actions.get_port_table()
            src_logic_port = port_table[src_port_name]
            dst_logic_port = port_table[dst_port_name]

            if not port_table.is_connected(src_logic_port, dst_logic_port):
                raise ConnectionPortsError(
                    'Cannot connect port {} to port {} during {}sec'.format(
                        src, dst, self._mapping_timeout
                    )
                )

    def split_addresses_and_letter(self, address):
        """Extract resources addresses and matrix letter.

        :param address: <host>:<MatrixA> or <host>:<host>:<Q>
        :type address: str
        :return: list of hosts and matrix letter (upper)
        :rtype: tuple[tuple[str], str]
        """
        letter = None
        if not self.support_multiple_blades:
            try:
                match = self.ADDRESS_PATTERN.search(address)
                first_host = match.group('host')
                second_host = match.group('second_host')
                letter = match.group('letter').upper()
            except AttributeError:
                msg = (
                    'Incorrect address. Resource address should specify '
                    'MatrixA, MatrixB or Q. '
                    'Format <host>:[<second_host>:]<matrix_letter>'
                )
                self._logger.error(msg)
                raise BaseRomeException(msg)

            if second_host and letter != 'Q':
                raise BaseRomeException('')

            hosts = tuple(filter(None, (first_host, second_host)))
        else:
            hosts = (address, )
        return hosts, letter

    @contextmanager
    def _get_cli_services(self):
        stacks = [self._cli_handler.default_mode_service()]
        if self._second_cli_handler:
            stacks.append(self._second_cli_handler.default_mode_service())

        services = []
        for stack in stacks:
            services.append(stack.__enter__())

        try:
            yield services
        finally:
            exc_info = sys.exc_info()
            for stack in stacks:
                not_raise = stack.__exit__(*exc_info)

            if not not_raise and exc_info[0]:
                raise exc_info

    def _get_port_table(self, cli_services):
        port_tables = []
        for cli_service in cli_services:
            system_actions = SystemActions(cli_service, self._logger)
            port_tables.append(system_actions.get_port_table())

        return reduce(PortTable.__add__, port_tables)

    def get_resource_description(self, address):
        """
        Auto-load function to retrieve all information from the device
        :param address: resource address, '192.168.42.240' if Shell run without support multiple
            blades address should be IP:[Matrix]A|B, '192.168.42.240:MatrixB'
        :type address: str
        :return: resource description
        :rtype: cloudshell.layer_one.core.response.response_info.ResourceDescriptionResponseInfo
        :raises cloudshell.layer_one.core.layer_one_driver_exception.LayerOneDriverException: Layer one exception.

        Example:

            from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
            from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
            from cloudshell.layer_one.core.response.resource_info.entities.port import Port

            chassis_resource_id = chassis_info.get_id()
            chassis_address = chassis_info.get_address()
            chassis_model_name = "Fiberzone Afm Chassis"
            chassis_serial_number = chassis_info.get_serial_number()
            chassis = Chassis(resource_id, address, model_name, serial_number)

            blade_resource_id = blade_info.get_id()
            blade_model_name = 'Generic L1 Module'
            blade_serial_number = blade_info.get_serial_number()
            blade.set_parent_resource(chassis)

            port_id = port_info.get_id()
            port_serial_number = port_info.get_serial_number()
            port = Port(port_id, 'Generic L1 Port', port_serial_number)
            port.set_parent_resource(blade)

            return ResourceDescriptionResponseInfo([chassis])
        """
        hosts, letter = self.split_addresses_and_letter(address)
        first_host = hosts[0]

        with self._get_cli_services() as cli_services:
            cli_service1 = cli_services[0]
            system_actions = SystemActions(cli_service1, self._logger)
            port_table = self._get_port_table(cli_services)
            board_table = system_actions.board_table()

        autoload_helper = AutoloadHelper(
            first_host, board_table, port_table, letter, self._logger
        )
        response_info = ResourceDescriptionResponseInfo(
            autoload_helper.build_structure()
        )
        return response_info

    def _disconnect_sub_ports(self, sub_ports_pairs, cli_services):
        mapping_actions_map = {
            cli_service.session.host: MappingActions(cli_service, self._logger)
            for cli_service in cli_services
        }
        sub_ports_pairs_host_map = defaultdict(list)
        for e_port, w_port in sub_ports_pairs:
            sub_ports_pairs_host_map[e_port.port_resource].append((e_port, w_port))

        for host, sub_ports_pairs in sub_ports_pairs_host_map.items():
            sub_ports_pairs_names = [
                (e_port.sub_port_name, w_port.sub_port_name)
                for e_port, w_port in sorted(sub_ports_pairs)
            ]
            mapping_action = mapping_actions_map[host]

            for e_port_name, w_port_name in sub_ports_pairs_names:
                mapping_action.disconnect(e_port_name, w_port_name)

            self._wait_ports_not_in_pending_connections(
                mapping_action, sub_ports_pairs_names, len(sub_ports_pairs_names)
            )

    def map_clear(self, ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param ports: ports, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
            for port in ports:
                session.send_command('map clear {}'.format(convert_port(port)))
        """
        self._logger.info('MapClear, Ports: {}'.format(', '.join(ports)))
        port_names = map(self.convert_cs_port_to_port_name, ports)

        with self._get_cli_services() as cli_services:
            port_table = self._get_port_table(cli_services)
            connected_ports = port_table.get_connected_port_pairs(port_names, bidi=True)
            connected_sub_ports = port_table.get_connected_sub_ports_pairs(
                connected_ports, bidi=True
            )
            self._disconnect_sub_ports(connected_sub_ports, cli_services)

            port_table = self._get_port_table(cli_services)
            connected_ports = port_table.get_connected_port_pairs(
                port_names, bidi=True
            )
            if connected_ports:
                connected_port_names = [
                    (src.name, dst.name) for src, dst in connected_ports
                ]
                raise BaseRomeException(
                    "Cannot disconnect all ports. Ports: {} left connected".format(
                        ', '.join(map(' - '.join, connected_port_names))
                    )
                )

    def map_clear_to(self, src_port, dst_ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                _src_port = convert_port(src_port)
                for port in dst_ports:
                    _dst_port = convert_port(port)
                    session.send_command('map clear-to {0} {1}'.format(_src_port, _dst_port))
        """
        if len(dst_ports) != 1:
            raise BaseRomeException(
                'MapClearTo operation is not allowed for multiple Dst ports'
            )

        self._logger.info(
            'MapClearTo, SrcPort: {0}, DstPort: {1}'.format(src_port, dst_ports[0])
        )

        src_port_name = self.convert_cs_port_to_port_name(src_port)
        dst_port_name = self.convert_cs_port_to_port_name(dst_ports[0])

        with self._get_cli_services() as cli_services:
            port_table = self._get_port_table(cli_services)
            connected_ports = port_table.get_connected_port_pairs([src_port_name])

            if not connected_ports:
                self._logger.debug("Ports already disconnected.")
                return

            src_logic_port, dst_logic_port = next(iter(connected_ports))
            if dst_logic_port.name != dst_port_name:
                raise BaseRomeException(
                    "Source port connected to another port - {}".format(
                        dst_logic_port.name
                    )
                )

            connected_sub_ports = port_table.get_connected_sub_ports_pairs(
                connected_ports
            )
            self._disconnect_sub_ports(connected_sub_ports, cli_services)

            port_table = self._get_port_table(cli_services)
            connected_ports = port_table.get_connected_port_pairs([src_port_name])
            if connected_ports:
                raise BaseRomeException(
                    "Cannot disconnect ports: {}".format(
                        ' - '.join((src_logic_port.name, dst_logic_port.name))
                    )
                )

    def get_attribute_value(self, cs_address, attribute_name):
        """
        Retrieve attribute value from the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.get_attribute_command(cs_address, attribute_name)
                value = session.send_command(command)
                return AttributeValueResponseInfo(value)
        """
        serial_number = 'Serial Number'
        if len(cs_address.split('/')) == 1 and attribute_name == serial_number:
            with self._cli_handler.default_mode_service() as session:
                autoload_actions = SystemActions(session, self._logger)
                board_table = autoload_actions.board_table()
            return AttributeValueResponseInfo(board_table.get('serial_number'))
        else:
            raise Exception(self.__class__.__name__,
                            'Attribute {0} for {1} is not available'.format(attribute_name, cs_address))

    def set_attribute_value(self, cs_address, attribute_name, attribute_value):
        """
        Set attribute value to the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :param attribute_value: value, "10000"
        :type attribute_value: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.set_attribute_command(cs_address, attribute_name, attribute_value)
                session.send_command(command)
                return AttributeValueResponseInfo(attribute_value)
        """
        if attribute_name == 'Serial Number':
            return
        else:
            raise Exception(self.__class__.__name__, 'SetAttribute {} is not supported'.format(attribute_name))

    def map_tap(self, src_port, dst_ports):
        return self.map_uni(src_port, dst_ports)

    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        """
        Set connection speed. Is not used with the new standard
        :param src_port:
        :param dst_port:
        :param speed:
        :param duplex:
        :return:
        """
        self._logger.debug(
            'Command "set_speed_manual" was called with args: src_port - {}, '
            'dst_port - {}, speed - {}, duplex - {}'.format(
                src_port, dst_port, speed, duplex
            )
        )
