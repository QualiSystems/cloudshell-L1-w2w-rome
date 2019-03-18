from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port


class AutoloadHelper(object):
    def __init__(self, resource_address, board_table, port_table, matrix_letter, logger):
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
        chassis = Chassis(self._chassis_id, self.resource_address, 'Rome Chassis', serial_number)
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
        blades_dict = {}
        ports_dict = {}
        for rome_port in self.port_table:
            if self.matrix_letter and self.matrix_letter != rome_port.blade_letter:
                continue

            try:
                blade = blades_dict[rome_port.blade_letter]
            except KeyError:
                blade = self._build_blade(rome_port.blade_letter)
                blades_dict[rome_port.blade_letter] = blade

            port = Port(rome_port.port_id.zfill(3), 'Generic L1 Port', 'NA')
            port.set_model_name('Port Paired')
            port.set_parent_resource(blade)
            ports_dict[rome_port.port_id] = port

        for port_id, port in ports_dict.items():
            rome_port = self.port_table[port_id]
            if rome_port.connected_to_port_id:
                other_port = ports_dict[rome_port.connected_to_port_id]
                other_port.add_mapping(port)

    def build_structure(self):
        self.build_ports_and_blades()
        return self.chassis
