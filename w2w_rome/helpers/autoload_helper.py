from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port
from w2w_rome.helpers.errors import BaseRomeException

if TYPE_CHECKING:
    from w2w_rome.helpers.port_entity import PortTable


class AutoloadHelper:
    def __init__(
        self,
        resource_address: str,
        board_table: dict,
        port_table: PortTable,
        matrix_letter: str,
    ) -> None:
        """Autoload helper."""
        self.board_table = board_table
        self.port_table = port_table
        self.matrix_letter = matrix_letter
        self.resource_address = resource_address

        self._chassis_id: str = "1"
        self._chassis: Chassis | None = None

    @property
    def chassis(self) -> Chassis:
        if self._chassis is not None:
            return self._chassis

        serial_number = self.board_table.get("serial_number")
        model_name = self.board_table.get("model_name")
        sw_version = self.board_table.get("sw_version")
        chassis = Chassis(
            self._chassis_id, self.resource_address, "Rome Chassis", serial_number
        )
        chassis.set_model_name(model_name)
        chassis.set_serial_number(serial_number)
        chassis.set_os_version(sw_version)

        self._chassis = chassis
        return chassis

    def _build_blades(self, blade_name: str) -> Generator:
        """Build blades."""
        for name in tuple(blade_name):  # ('A',) or ('Q',) or ('X', 'Y')
            blade_model = f"Matrix {name}"
            serial_number = "NA"
            resource_model = f"Rome Matrix {name}"
            blade = Blade(name.upper(), resource_model, serial_number)
            blade.set_model_name(blade_model)
            blade.set_serial_number(serial_number)
            blade.set_parent_resource(self.chassis)
            yield blade

    def build_ports_and_blades(self) -> None:
        ports_dict = {}
        zfill_n = max(
            len(rlp.port_id)
            for rlp in self.port_table
            if rlp.blade_letter in self.matrix_letter
        )

        for blade in self._build_blades(self.matrix_letter):
            for logical_port in self.port_table:
                if blade.name[-1] != logical_port.blade_letter:
                    continue

                str_port_id = logical_port.port_id.zfill(zfill_n)
                port = Port(str_port_id, "Generic L1 Port", "NA")
                port.name = f"Port {logical_port.blade_letter}{str_port_id}"
                port.set_model_name("Port Paired")
                port.set_parent_resource(blade)
                ports_dict[logical_port.name] = port

        for port_name, port in ports_dict.items():
            logical_port = self.port_table[port_name]
            connected_to_port = self.port_table.get_connected_to_port(logical_port)
            if connected_to_port:
                other_port = ports_dict[connected_to_port.name]
                other_port.add_mapping(port)

    def build_structure(self) -> Chassis:
        self._validate_port_table()
        self.build_ports_and_blades()
        return self.chassis

    def _validate_port_table(self) -> None:
        for logical_port in self.port_table:
            if logical_port.blade_letter in self.matrix_letter:
                break
        else:
            raise BaseRomeException(
                f"No '{self.matrix_letter}' ports found on the device"
            )
