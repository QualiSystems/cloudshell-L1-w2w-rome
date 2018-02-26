from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port


class AutoloadHelper(object):
    def __init__(self, resource_address, board_table, ports_association_table, connections_table, logger):
        self._logger = logger
        self._board_table = board_table
        self._ports_association_table = ports_association_table
        self._connection_table = connections_table
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
        """
        :type blade_name: str
        """
        blade_model = 'Panel'
        serial_number = 'NA'
        blade = Blade(blade_name.upper(), 'Generic L1 Module', serial_number)
        blade.set_model_name(blade_model)
        blade.set_serial_number(serial_number)
        return blade

    def _build_ports_and_blades(self, chassis_dict):
        blades_dict = {}
        ports_dict = {}
        for record_id, port_aliases in self._ports_association_table.iteritems():
            blade_id = record_id[0]
            port_id = record_id[1:]
            if blade_id not in blades_dict:
                blade = self._build_blade(blade_id)
                blades_dict[blade_id] = blade
                blade.set_parent_resource(chassis_dict.get(self._chassis_id))
            else:
                blade = blades_dict.get(blade_id)

            port = Port(port_id, 'Generic L1 Port', 'NA')
            port.set_model_name('Port Paired')
            port.set_parent_resource(blade)
            ports_dict[port_aliases[0]] = port
            ports_dict[port_aliases[1]] = port
        return ports_dict

    def _build_mappings(self, ports_dict):
        for src_alias, dst_alias in self._connection_table.iteritems():
            src_port = ports_dict.get(src_alias)
            dst_port = ports_dict.get(dst_alias)
            if src_port and dst_port:
                src_port.add_mapping(dst_port)

    def build_structure(self):
        chassis_dict = self._build_chassis()
        ports_dict = self._build_ports_and_blades(chassis_dict)
        self._build_mappings(ports_dict)
        return chassis_dict.values()
