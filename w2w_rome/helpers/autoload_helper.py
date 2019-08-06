from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port

from w2w_rome.helpers.errors import BaseRomeException


class AutoloadHelper(object):
    def __init__(
            self, resource_address, board_table, port_table, matrix_letter, logger
    ):
        """Autoload helper.

        :type resource_address: str
        :type board_table: dict
        :type port_table: w2w_rome.helpers.port_entity.PortTable
        :type matrix_letter: str
        :type logger: logging.Logger
        """
        self.board_table = board_table
        self.port_table = port_table
        self.matrix_letter = matrix_letter
        self.resource_address = resource_address
        self.logger = logger

        self._chassis_id = '1'
        self._chassis = None

    @property
    def chassis(self):
        if self._chassis is not None:
            return self._chassis

        serial_number = self.board_table.get('serial_number')
        model_name = self.board_table.get('model_name')
        sw_version = self.board_table.get('sw_version')
        chassis = Chassis(
            self._chassis_id, self.resource_address, model_name, serial_number
        )
        chassis.set_model_name(model_name)
        chassis.set_serial_number(serial_number)
        chassis.set_os_version(sw_version)

        self._chassis = chassis
        return chassis

    def _build_blade(self, blade_name):
        """
        :type blade_name: str
        """
        blade_model = 'Matrix ' + blade_name.upper()
        serial_number = 'NA'
        resource_model = 'Rome Matrix {}'.format(blade_name.upper())
        blade = Blade(blade_name.upper(), resource_model, serial_number)
        blade.set_model_name(blade_model)
        blade.set_serial_number(serial_number)
        blade.set_parent_resource(self.chassis)
        return blade

    def build_ports_and_blades(self):
        blade = self._build_blade(self.matrix_letter)
        ports_dict = {}

        zfill_n = max(
            map(
                len,
                (rome_logical_port.port_id for rome_logical_port in self.port_table),
            )
        )

        for logical_port in self.port_table:
            if self.matrix_letter != logical_port.blade_letter:
                continue

            port = Port(
                logical_port.port_id.zfill(zfill_n),
                'Generic L1 Port',
                'NA',
            )
            port.set_model_name('Port Paired')
            port.set_parent_resource(blade)
            ports_dict[logical_port.name] = port

        for port_name, port in ports_dict.items():
            logical_port = self.port_table[port_name]
            connected_to_port = self.port_table.get_connected_to_port(logical_port)
            if connected_to_port:
                other_port = ports_dict[connected_to_port.name]
                other_port.add_mapping(port)

    def _verify_matrix_letter(self):
        if self.port_table.is_matrix_q and self.matrix_letter.upper() != 'Q':
            raise BaseRomeException(
                'This device has MPO ports. '
                'You should specify MatrixQ in device address.'
            )

    def build_structure(self):
        self._verify_matrix_letter()
        self.build_ports_and_blades()
        return self.chassis
