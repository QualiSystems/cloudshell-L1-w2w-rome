#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import time

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.response.response_info import GetStateIdResponseInfo, AttributeValueResponseInfo, \
    ResourceDescriptionResponseInfo
from rome.cli.rome_cli_handler import RomeCliHandler
from rome.command_actions.mapping_actions import MappingActions
from rome.command_actions.system_actions import SystemActions
from rome.helpers.autoload_helper import AutoloadHelper
from rome.helpers.errors import BaseRomeException
from rome.helpers.port_entity import verify_ports_for_connection, SubPort


class DriverCommands(DriverCommandsInterface):
    """
    Driver commands implementation
    """

    ADDRESS_PATTERN = re.compile(r':(matrix)?(?P<letter>[a|b])$', re.IGNORECASE)

    def __init__(self, logger, runtime_config):
        """
        :type logger: logging.Logger
        :type runtime_config: cloudshell.layer_one.core.helper.runtime_configuration.RuntimeConfiguration
        """
        self._logger = logger
        self._runtime_config = runtime_config
        self._cli_handler = RomeCliHandler(logger)
        # self._cli_handler = TestCliHandler(
        #       os.path.join(os.path.dirname(__file__), 'helpers', 'test_fiberzone_data'), logger)

        self._mapping_timeout = runtime_config.read_key('MAPPING.TIMEOUT', 120)
        self._mapping_check_delay = runtime_config.read_key('MAPPING.CHECK_DELAY', 3)
        self.support_multiple_blades = runtime_config.read_key('SUPPORT_MULTIPLE_BLADES', False)

        self.__ports_association_table = None

    def login(self, address, username, password):
        """
        Perform login operation on the device
        :param address: resource address, "192.168.42.240"
        :param username: username to login on the device
        :param password: password
        :return: None
        :raises Exception: if command failed
        Example:
            # Define session attributes
            self._cli_handler.define_session_attributes(address, username, password)

            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Executing simple command
                device_info = session.send_command('show version')
                self._logger.info(device_info)
        """
        self._cli_handler.define_session_attributes(address, username, password)
        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session, self._logger)
            self._logger.info('Connected to ' + system_actions.board_table().get('model_name'))

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
                chassis_name = session.send_command('show chassis name')
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
        self._logger.info('MapBidi, SrcPort: {0}, DstPort: {1}'.format(src_port, dst_port))
        self.map_uni(src_port, [dst_port])
        self.map_uni(dst_port, [src_port])

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
        self._logger.info('MapUni, SrcPort: {0}, DstPort: {1}'.format(src_port, dst_ports[0]))
        if len(dst_ports) != 1:
            raise Exception(self.__class__.__name__, 'MapUni operation is not allowed for multiple Dst ports')
        src_port_e = self._get_port_aliases(self._convert_port(src_port))[0]
        dst_port_w = self._get_port_aliases(self._convert_port(dst_ports[0]))[1]
        self._connect_ports(src_port_e, dst_port_w)

    def get_matrix_letter(self, address):
        letter = None
        if not self.support_multiple_blades:
            try:
                letter = self.ADDRESS_PATTERN.search(address).group('letter')
            except AttributeError:
                msg = ('Resource address should specify MatrixA or MatrixB. '
                       'Format [IP]:[Matrix Letter]')
                self._logger.error(msg)
                raise BaseRomeException(msg)
        return letter

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
        letter = self.get_matrix_letter(address)

        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session, self._logger)
            port_table = system_actions.get_port_table()
            board_table = system_actions.board_table()
        autoload_helper = AutoloadHelper(address, board_table, port_table, letter, self._logger)
        response_info = ResourceDescriptionResponseInfo(autoload_helper.build_structure())
        return response_info

    @staticmethod
    def _convert_port(cs_port):
        port_addr_list = cs_port.split('/')
        return port_addr_list[-2] + port_addr_list[-1]

    def _get_port_aliases(self, port_id):
        aliases = self._ports_association_table.get(port_id.lower())
        if aliases and len(aliases) == 2:
            return aliases
        raise Exception(self.__class__.__name__, 'Could not find correct aliases for port {}'.format(port_id))

    def _get_connected_port(self, port_info):
        """
        Get connected
        :param port_info:
        :type port_info: fiberzone_afm.entities.port_entities.PortInfo
        :return:
        """
        return port_info[4]

    def _check_port_locked_or_disabled(self, port_info):
        """
        Check disabled or locked
        :param port_info:
        :type port_info: fiberzone_afm.entities.port_entities.PortInfo
        :return:
        """
        if port_info[1].lower() != 'unlocked':
            raise Exception(self.__class__.__name__, 'Port {} is Locked'.format(port_info[5]))
        if port_info[2].lower() != 'enabled':
            raise Exception(self.__class__.__name__, 'Port {} is Disabled'.format(port_info[5]))

    def _connect_ports(self, src_port_id, dst_port_id):
        with self._cli_handler.default_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            src_port_info = mapping_actions.port_info(src_port_id)
            dst_port_info = mapping_actions.port_info(dst_port_id)
            self._check_port_locked_or_disabled(src_port_info)
            self._check_port_locked_or_disabled(dst_port_info)
            src_connected_port = self._get_connected_port(src_port_info)
            dst_connected_port = self._get_connected_port(dst_port_info)
            if (src_connected_port and src_connected_port != dst_port_id) or (
                    dst_connected_port and dst_connected_port != src_port_id):
                raise Exception(self.__class__.__name__,
                                'Port {0}, or port {1} connected to a different port'.format(src_port_id, dst_port_id))
            mapping_actions.connect(src_port_id, dst_port_id)
            start_time = time.time()
            while time.time() - start_time < self._mapping_timeout:
                src_port_info = mapping_actions.port_info(src_port_id)
                dst_port_info = mapping_actions.port_info(dst_port_id)
                self._check_port_locked_or_disabled(src_port_info)
                self._check_port_locked_or_disabled(dst_port_info)
                if self._get_connected_port(src_port_info) == dst_port_id and self._get_connected_port(
                        dst_port_info) == src_port_id:
                    return
                else:
                    time.sleep(self._mapping_check_delay)
        raise Exception(self.__class__.__name__,
                        'Cannot connect port {0} to port {1} during {2}sec'.format(src_port_id, dst_port_id,
                                                                                   self._mapping_timeout))

    def _disconnect_ports(self, src_port_id, dst_port_id=None):
        with self._cli_handler.default_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)

            src_port_info = mapping_actions.port_info(src_port_id)
            if not dst_port_id:
                dst_port_id = self._get_connected_port(src_port_info)
                if not dst_port_id:
                    return
            dst_port_info = mapping_actions.port_info(dst_port_id)
            if not self._get_connected_port(src_port_info) and not self._get_connected_port(dst_port_info):
                return
            if self._get_connected_port(src_port_info) != dst_port_id or self._get_connected_port(
                    dst_port_info) != src_port_id:
                raise Exception(self.__class__.__name__,
                                'Port {0} or port {1} connected to a different port'.format(src_port_id, dst_port_id))

            self._check_port_locked_or_disabled(src_port_info)
            self._check_port_locked_or_disabled(dst_port_info)

            mapping_actions.disconnect(src_port_id, dst_port_id)
            start_time = time.time()
            while time.time() - start_time < self._mapping_timeout:
                src_port_info = mapping_actions.port_info(src_port_id)
                dst_port_info = mapping_actions.port_info(dst_port_id)
                self._check_port_locked_or_disabled(src_port_info)
                self._check_port_locked_or_disabled(dst_port_info)
                if not self._get_connected_port(src_port_info) and not self._get_connected_port(dst_port_info):
                    return
                else:
                    time.sleep(self._mapping_check_delay)

            raise Exception(self.__class__.__name__,
                            'Cannot disconnect port {0} from port {1} during {2}sec'.format(src_port_id, dst_port_id,
                                                                                            self._mapping_timeout))

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
        exception_messages = []
        for src_port in ports:
            try:
                src_port_e, src_port_w = self._get_port_aliases(self._convert_port(src_port))
                self._disconnect_ports(src_port_e)
                self._disconnect_ports(src_port_w)
            except Exception as e:
                if len(e.args) > 1:
                    exception_messages.append(e.args[1])
                elif len(e.args) == 1:
                    exception_messages.append(e.args[0])

        if exception_messages:
            raise Exception(self.__class__.__name__, ', '.join(exception_messages))

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
            raise Exception(self.__class__.__name__, 'MapClearTo operation is not allowed for multiple Dst ports')

        self._logger.info('MapClearTo, SrcPort: {0}, DstPort: {1}'.format(src_port, dst_ports[0]))
        src_port_e = self._get_port_aliases(self._convert_port(src_port))[0]
        dst_port_w = self._get_port_aliases(self._convert_port(dst_ports[0]))[1]
        self._disconnect_ports(src_port_e, dst_port_w)

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
        raise NotImplementedError
