from __future__ import annotations

import re
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.helper.logger import get_l1_logger
from cloudshell.layer_one.core.response.response_info import (
    AttributeValueResponseInfo,
    GetStateIdResponseInfo,
    ResourceDescriptionResponseInfo,
)
from w2w_rome.cli.rome_cli_handler import RomeCliHandler
from w2w_rome.command_actions.mapping_actions import MappingActions
from w2w_rome.command_actions.system_actions import SystemActions
from w2w_rome.helpers.autoload_helper import AutoloadHelper
from w2w_rome.helpers.errors import (
    BaseRomeException,
    ConnectionPortsError,
    NotSupportedError,
)

if TYPE_CHECKING:
    from cloudshell.layer_one.core.helper.runtime_configuration import (
        RuntimeConfiguration,
    )

logger = get_l1_logger(name=__name__)


class DriverCommands(DriverCommandsInterface):
    """Driver commands implementation."""

    ADDRESS_PATTERN = re.compile(
        (
            r"^(?P<host>[^:]+?):"
            r"((?P<second_host>[^:]+?):)?"
            r"(matrix)?(?P<letter>(a|b|q|xy))(/.+)?$"
        ),
        re.IGNORECASE,
    )

    def __init__(self, runtime_config: RuntimeConfiguration) -> None:
        self._runtime_config = runtime_config
        self._cli_handler = RomeCliHandler()
        self._second_cli_handler: RomeCliHandler | None = None

        self._mapping_timeout = runtime_config.read_key("MAPPING.TIMEOUT", 120)
        self._mapping_check_delay = runtime_config.read_key("MAPPING.CHECK_DELAY", 3)
        self.support_multiple_blades = runtime_config.read_key(
            "SUPPORT_MULTIPLE_BLADES", False
        )

        self.__ports_association_table = None

    def _initialize_second_cli_handler(self) -> None:
        if self._second_cli_handler is None:
            self._second_cli_handler = RomeCliHandler()
            self._cli_handler._cli._session_pool._pool.maxsize = 2
            self._second_cli_handler._cli._session_pool._pool.maxsize = 2

    def login(self, address: str, username: str, password: str) -> None:
        """Perform login operation on the device.

        address - "192.168.42.240:A"
        """
        hosts, _ = self._split_addresses_and_letter(address)
        first_host = hosts[0]

        self._cli_handler.define_session_attributes(first_host, username, password)
        if len(hosts) == 2:
            second_host = hosts[1]
            self._initialize_second_cli_handler()
            if self._second_cli_handler:
                self._second_cli_handler.define_session_attributes(
                    second_host, username, password
                )

        with self._get_cli_services_lst() as cli_services_lst:
            system_actions = SystemActions(cli_services_lst)
            board_tables_map = system_actions.get_board_tables_map()
            for cli_service, board_table in board_tables_map.items():
                model_name = board_table["model_name"]
                logger.info(f"Connected to {model_name}")

    def get_state_id(self) -> GetStateIdResponseInfo:
        """Check if CS synchronized with the device."""
        return GetStateIdResponseInfo("-1")

    def set_state_id(self, state_id: str) -> None:
        """Set synchronization state id to the device.

        Called after Autoload or SyncFomDevice commands
        """
        pass

    def _convert_cs_port_to_port_name(self, cs_port: str) -> str:
        _, matrix_letter = self._split_addresses_and_letter(cs_port)
        port_num = cs_port.rsplit("/", 1)[-1].lstrip("0")
        if matrix_letter == "XY":
            blade_letter = cs_port.split("/")[1]
            port_name = f"{blade_letter}{port_num}"
        else:
            port_name = f"{matrix_letter}{port_num}"
        return port_name

    def map_bidi(self, src_port: str, dst_port: str) -> None:
        """Create a bidirectional connection between source and destination ports.

        src port - "192.168.42.240:A/A/21"
        dst port - "192.168.42.240:A/A/22"
        """
        logger.info(f"MapBidi: SrcPort: {src_port}, DstPort: {dst_port}")
        src_port_name = self._convert_cs_port_to_port_name(src_port)
        dst_port_name = self._convert_cs_port_to_port_name(dst_port)

        with self._get_cli_services_lst() as cli_services_lst:
            mapping_actions = MappingActions(
                cli_services_lst,
                self._mapping_timeout,
                self._mapping_check_delay,
            )
            system_actions = SystemActions(cli_services_lst)
            port_table = system_actions.get_port_table()
            src_logic_port = port_table[src_port_name]
            dst_logic_port = port_table[dst_port_name]

            if port_table.is_connected(src_logic_port, dst_logic_port, bidi=True):
                logger.debug(
                    f"Ports {src_port_name} and {dst_port_name} already connected"
                )
                return

            port_table.verify_ports_for_connection(
                src_logic_port, dst_logic_port, bidi=True
            )

            try:
                mapping_actions.connect(src_logic_port, dst_logic_port, bidi=True)

                port_table = system_actions.get_port_table()
                src_logic_port = port_table[src_port_name]
                dst_logic_port = port_table[dst_port_name]

                is_connected = port_table.is_connected(
                    src_logic_port, dst_logic_port, bidi=True
                )
            except Exception:
                is_connected = False

            if not is_connected:
                mapping_actions.disconnect(
                    {(src_logic_port, dst_logic_port)}, bidi=True
                )
                raise ConnectionPortsError(
                    f"Cannot connect port {src_logic_port.original_logical_name} "
                    f"to port {dst_logic_port.original_logical_name} "
                    f"during {self._mapping_timeout}sec"
                )

    def map_uni(self, src_port: str, dst_ports: list[str]) -> None:
        """Unidirectional mapping of two ports.

        src port  - "192.168.42.240:B/B/21"
        dst ports - ["192.168.42.240:B/B/22", "192.168.42.240:B/B/23"]
        """
        if len(dst_ports) != 1:
            raise BaseRomeException(
                "MapUni operation is not allowed for multiple Dst ports"
            )
        _, letter = self._split_addresses_and_letter(src_port)
        if letter and letter.startswith("Q"):
            raise NotSupportedError("MapUni for matrix Q doesn't supported")
        logger.info(f"MapUni: SrcPort: {src_port}, DstPort: {dst_ports[0]}")

        src_port_name = self._convert_cs_port_to_port_name(src_port)
        dst_port_name = self._convert_cs_port_to_port_name(dst_ports[0])

        with self._get_cli_services_lst() as cli_services_lst:
            system_actions = SystemActions(cli_services_lst)
            mapping_actions = MappingActions(
                cli_services_lst,
                self._mapping_timeout,
                self._mapping_check_delay,
            )
            port_table = system_actions.get_port_table()
            src_logic_port = port_table[src_port_name]
            dst_logic_port = port_table[dst_port_name]

            if port_table.is_connected(src_logic_port, dst_logic_port):
                logger.debug(
                    f"Ports {src_port_name} and {dst_port_name} already connected"
                )
                return

            port_table.verify_ports_for_connection(src_logic_port, dst_logic_port)
            mapping_actions.connect(src_logic_port, dst_logic_port, bidi=False)

            port_table = system_actions.get_port_table()
            src_logic_port = port_table[src_port_name]
            dst_logic_port = port_table[dst_port_name]

            if not port_table.is_connected(src_logic_port, dst_logic_port):
                raise ConnectionPortsError(
                    f"Cannot connect port {src_port_name} "
                    f"to port {dst_port_name} "
                    f"during {self._mapping_timeout}sec"
                )

    def _split_addresses_and_letter(
        self, address: str
    ) -> tuple[tuple[str, ...], str | None]:
        """Extract resources addresses and matrix letter.

        address - <host>:<MatrixA> or <host>:<host>:<Q>
        """
        letter = None
        err_msg = (
            "Incorrect address. Resource address should specify MatrixA, MatrixB, "
            "MatrixQ or MatrixXY. Format <host>:[<second_host>:]<matrix_letter>. "
            "Second host is used in Q128 devices."
        )
        if not self.support_multiple_blades:
            try:
                match = self.ADDRESS_PATTERN.search(address)
                if match:
                    first_host = match.group("host")
                    second_host = match.group("second_host")
                    letter = match.group("letter").upper()
                else:
                    logger.error(err_msg)
                    raise BaseRomeException(err_msg)
            except AttributeError:
                logger.error(err_msg)
                raise BaseRomeException(err_msg)
            if second_host and letter != "Q":
                raise BaseRomeException(err_msg)

            hosts = tuple(filter(None, (first_host, second_host)))
        else:
            hosts = (address,)
        return hosts, letter

    @contextmanager
    def _get_cli_services_lst(self):
        stacks = [self._cli_handler.default_mode_service()]
        if self._second_cli_handler:
            stacks.append(self._second_cli_handler.default_mode_service())

        services = []
        for stack in stacks:
            services.append(stack.__enter__())

        try:
            yield services
        finally:
            not_raise = False
            exc_info = sys.exc_info()
            for stack in stacks:
                not_raise = stack.__exit__(*exc_info)

            if not not_raise and exc_info[0]:
                raise exc_info[1]

    def get_resource_description(self, address: str) -> ResourceDescriptionResponseInfo:
        """Auto-load function to retrieve all information from the device.

        resource address, "192.168.42.240" if Shell run without support
        multiple blades address should be IP:[Matrix]A|B, "192.168.42.240:MatrixB"
        """
        _, letter = self._split_addresses_and_letter(address)

        with self._get_cli_services_lst() as cli_services_lst:
            system_actions = SystemActions(cli_services_lst)
            port_table = system_actions.get_port_table()
            board_tables_map = system_actions.get_board_tables_map()

        autoload_helper = AutoloadHelper(
            address, list(board_tables_map.values())[0], port_table, letter
        )
        response_info = ResourceDescriptionResponseInfo(
            autoload_helper.build_structure()
        )
        return response_info

    def map_clear(self, ports: list[str]) -> None:
        """Remove simplex/multi-cast/duplex connection ending on the destination port.

        ports - ["192.168.42.240:A/A/21", "192.168.42.240:A/A/22"]
        """
        logger.info(f"MapClear: Ports: {', '.join(ports)}")
        port_names = list(map(self._convert_cs_port_to_port_name, ports))

        with self._get_cli_services_lst() as cli_services_lst:
            mapping_actions = MappingActions(
                cli_services_lst,
                self._mapping_timeout,
                self._mapping_check_delay,
            )
            system_actions = SystemActions(cli_services_lst)
            port_table = system_actions.get_port_table()
            connected_ports = port_table.get_connected_port_pairs(port_names, bidi=True)
            mapping_actions.disconnect(connected_ports)

            port_table = system_actions.get_port_table()
            connected_ports = port_table.get_connected_port_pairs(port_names, bidi=True)
            if connected_ports:
                connected_port_names = [
                    (src.name, dst.name) for src, dst in connected_ports
                ]
                raise BaseRomeException(
                    f"Cannot disconnect all ports. "
                    f"Ports: {', '.join(map(' - '.join, connected_port_names))} left connected"  # noqa: E501
                )

    def map_clear_to(self, src_port: str, dst_ports: list[str]) -> None:
        """Remove simplex/multi-cast/duplex connection ending on the destination port.

        src port  - "192.168.42.240:A/A/21"
        dst ports - ["192.168.42.240:A/A/21", "192.168.42.240:A/A/22"]
        """
        if len(dst_ports) != 1:
            raise BaseRomeException(
                "MapClearTo operation is not allowed for multiple Dst ports"
            )

        logger.info(f"MapClearTo: SrcPort: {src_port}, DstPort: {dst_ports[0]}")

        src_port_name = self._convert_cs_port_to_port_name(src_port)
        dst_port_name = self._convert_cs_port_to_port_name(dst_ports[0])

        with self._get_cli_services_lst() as cli_services_lst:
            mapping_actions = MappingActions(
                cli_services_lst,
                self._mapping_timeout,
                self._mapping_check_delay,
            )
            system_actions = SystemActions(cli_services_lst)
            port_table = system_actions.get_port_table()
            connected_ports = port_table.get_connected_port_pairs([src_port_name])

            if not connected_ports:
                logger.debug("Ports already disconnected.")
                return

            src_logic_port, dst_logic_port = next(iter(connected_ports))
            if dst_logic_port.name != dst_port_name:
                raise BaseRomeException(
                    f"Source port connected to another port - {dst_logic_port.name}"
                )
            mapping_actions.disconnect(connected_ports)

            port_table = system_actions.get_port_table()
            connected_ports = port_table.get_connected_port_pairs([src_port_name])
            if connected_ports:
                raise BaseRomeException(
                    f"Cannot disconnect ports: "
                    f"{' - '.join((src_logic_port.name, dst_logic_port.name))}"
                )

    def get_attribute_value(
        self, cs_address: str, attribute_name: str
    ) -> AttributeValueResponseInfo:
        """Retrieve attribute value from the device.

        address        - "192.168.42.240:A/A/21"
        attribute name - "Port Speed"
        """
        serial_number = "Serial Number"
        if len(cs_address.split("/")) == 1 and attribute_name == serial_number:
            with self._get_cli_services_lst() as cli_services_lst:
                system_actions = SystemActions(cli_services_lst)
                board_tables_map = system_actions.get_board_tables_map()
            return AttributeValueResponseInfo(
                list(board_tables_map.values())[0].get("serial_number")
            )
        else:
            raise BaseRomeException(
                f"Attribute {attribute_name} for {cs_address} is not available"
            )

    def set_attribute_value(
        self, cs_address: str, attribute_name: str, attribute_value: str
    ) -> None:
        """Set attribute value to the device.

        address        - "192.168.42.240:A/A/21"
        attribute name - "Port Speed"
        value          - "10000"
        """
        if attribute_name == "Serial Number":
            return
        else:
            raise BaseRomeException(f"SetAttribute {attribute_name} is not supported")

    def map_tap(self, src_port, dst_ports):
        return self.map_uni(src_port, dst_ports)

    def set_speed_manual(self, src_port: str, dst_port: str, speed: str, duplex: str):
        """Set connection speed.

        DEPRECATED. Is not used with the new standard
        """
        logger.debug(
            f"Command 'set_speed_manual' was called with args: src_port - {src_port}, "
            f"dst_port - {dst_port}, speed - {speed}, duplex - {duplex}"
        )
