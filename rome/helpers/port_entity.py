import re

from rome.helpers.errors import BaseRomeException


class SubPort(object):
    PORT_PATTERN = re.compile(
        r'^(?P<direction>[EW])(?P<port_id>\d+)'
        r'\[(?P<port_name>\w+)\]\s+'
        r'(?P<admin_status>(locked|unlocked))\s+'
        r'(?P<oper_status>(enabled|disabled))\s+'
        r'(?P<port_status>(dis)?connected)\s+'
        r'\d+\s+'
        r'((?P<conn_to_direction>[EW])(?P<conn_to_port_id>\d+)'
        r'\[(?P<conn_to_port_name>\w+)\])?\s+'
        r'(?P<logical_name>[AB]\d+)\s*$',
        re.IGNORECASE,
    )

    def __init__(self, direction, port_id, name, locked, enabled, connected,
                 connected_to_direction, connected_to_port_id, connected_to_port_name, logical):
        self.direction = direction
        self.port_id = port_id
        self.name = name
        self.locked = locked
        self.enabled = enabled
        self.connected = connected
        self.connected_to_direction = connected_to_direction
        self.connected_to_port_id = connected_to_port_id
        self.connected_to_port_name = connected_to_port_name
        self.logical = logical

    def __str__(self):
        return '<SubPort "{0.direction}{0.port_id}">'.format(self)

    @property
    def blade_letter(self):
        return self.logical[0].upper()

    @classmethod
    def from_line(cls, line):
        match = cls.PORT_PATTERN.search(line)

        if match is None:
            return

        group_dict = match.groupdict('')
        return cls(
            group_dict['direction'].upper(),
            group_dict['port_id'].zfill(3),  # Port 001
            group_dict['port_name'],
            group_dict['admin_status'].lower() == 'locked',
            group_dict['oper_status'].lower() == 'enabled',
            group_dict['port_status'].lower() == 'connected',
            group_dict.get('conn_to_direction', '').upper(),
            group_dict.get('conn_to_port_id'),
            group_dict.get('conn_to_port_name'),
            group_dict['logical_name'],
        )


class RomePort(object):
    def __init__(self, port_id):
        self.port_id = port_id
        self.e_port = None  # type: SubPort
        self.w_port = None  # type: SubPort

    def __str__(self):
        return '<RomePort "{}">'.format(self.port_id)

    @property
    def blade_letter(self):
        return self.e_port.blade_letter

    @property
    def connected_to_port_id(self):
        return self.e_port.connected_to_port_id

    def add_sub_port(self, sub_port):
        attr_name = '{}_port'.format(sub_port.direction.lower())
        if getattr(self, attr_name) is not None:
            raise BaseRomeException('{} port already set'.format(sub_port.direction))

        setattr(self, attr_name, sub_port)


class PortTable(object):
    def __init__(self):
        self.map_ports_num = {}

    def get_or_create(self, port_id):
        try:
            port_obj = self.map_ports_num[port_id]
        except KeyError:
            port_obj = RomePort(port_id)
            self.map_ports_num[port_id] = port_obj

        return port_obj

    def __getitem__(self, port_id):
        """Return Port with port id
        :type port_id: str
        :rtype: RomePort
        """
        try:
            val = self.map_ports_num[port_id]
        except KeyError:
            raise BaseRomeException('Ups we don\'t have port id "{}" in Ports table'.format(port_id))
        return val

    def __iter__(self):
        return iter(self.map_ports_num.values())


def verify_port_is_not_locked_or_disabled(sub_port):
    """Check disabled or locked."""
    if sub_port.locked:
        raise BaseRomeException('Port {} is Locked'.format(sub_port.port_id))
    if not sub_port.enabled:
        raise BaseRomeException('Port {} is Disabled'.format(sub_port.port_id))


def verify_ports_for_connection(e_port, w_port):
    verify_port_is_not_locked_or_disabled(e_port)
    verify_port_is_not_locked_or_disabled(w_port)

    if (e_port.connected_to_port_id and e_port.connected_to_port_id != w_port.port_id or
            w_port.connected_to_port_id and w_port.connected_to_port_id != e_port.port_id):
        raise BaseRomeException('Port {}, or port {} connected to a different port'.format(
            e_port.port_id, w_port.port_id))
