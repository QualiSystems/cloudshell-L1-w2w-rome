from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port


class AutoloadHelper(object):
    def __init__(self, resource_address, board_table, ports_table, logger):
        self._logger = logger
        self._board_table = board_table
        self._ports_table = ports_table
        self._resource_address = resource_address

        self._chassis_id = '1'

    def _build_chassis(self):
        chassis_dict = {}

        serial_number = self._board_table.get('serial_number')
        model_name = self._board_table.get('model_name')
        sw_version = self._board_table.get('sw_version')
        chassis = Chassis(self._chassis_id, self._resource_address, 'Rome Chassis', serial_number)
        chassis.set_model_name(model_name)
        chassis.set_serial_number(serial_number)
        chassis.set_os_version(sw_version)
        chassis_dict[self._chassis_id] = chassis
        return chassis_dict

    def _build_blade(self, blade_name):
        blade_model = 'Panel'
        serial_number = 'NA'
        blade = Blade(blade_name, 'Generic L1 Module', serial_number)
        blade.set_model_name(blade_model)
        blade.set_serial_number(serial_number)
        return blade

    def _build_ports_and_blades(self, chassis_dict):
        blades_dict = {}
        ports_dict = {}
        for port_id, port_record in self._ports_table.iteritems():
            blade_id = port_record.get('blade')
            if blade_id not in blades_dict:
                blade = self._build_blade(blade_id)
                blades_dict[blade_id] = blade
                blade.set_parent_resource(chassis_dict.get(self._chassis_id))
            else:
                blade = blades_dict.get(blade_id)

            port = Port(port_id, 'Generic L1 Port', 'NA')
            port.set_model_name('Port Paired')
            port.set_parent_resource(blade)
            ports_dict[port_id] = port
        return ports_dict

    def _build_mappings(self, ports_dict):
        for port_id, port_record in self._ports_table.iteritems():
            connected_to = port_record.get('connected')
            if connected_to:
                src_port = ports_dict.get(port_id)
                dst_port = ports_dict.get(connected_to)
                if src_port and dst_port:
                    src_port.add_mapping(dst_port)

    def build_structure(self):
        chassis_dict = self._build_chassis()
        ports_dict = self._build_ports_and_blades(chassis_dict)
        self._build_mappings(ports_dict)
        return chassis_dict.values()
