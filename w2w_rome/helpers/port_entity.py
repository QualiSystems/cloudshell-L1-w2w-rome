import re

from w2w_rome.helpers.errors import BaseRomeException, ConnectedToDifferentPortsError


class SubPort(object):
    """Sub port that keep fiber port for one direction."""
    PORT_PATTERN = re.compile(
        r'^(?P<direction>[EW])(?P<port_id>\d+)'
        r'\[(?P<port_full_name>\w+?)\]\s+'
        r'(?P<admin_status>(locked|unlocked))\s+'
        r'(?P<oper_status>(enabled|disabled))\s+'
        r'(?P<port_status>((dis)?connected)|in process)\s+'
        r'\d+\s+'
        r'((?P<conn_to_direction>[EW])(?P<conn_to_port_id>\d+)'
        r'\[\w+\])?\s+'
        r'(?P<logical_name>[ABQ]\d+)\s*$',
        re.IGNORECASE,
    )
    PORT_FULL_NAME_PATTERN = re.compile(r'\d+(?P<blade_letter>[AB])[EW]\d+')

    def __init__(self, direction, port_id, port_full_name, locked, enabled, connected,
                 connected_to_direction, connected_to_port_id, logical):
        self.direction = direction
        self.port_id = port_id
        self.port_full_name = port_full_name
        self.blade_letter = logical[0].upper()
        self.name = '{}{}'.format(direction, port_id)
        self.locked = locked
        self.enabled = enabled
        self.connected = connected
        self.connected_to_direction = connected_to_direction
        self.connected_to_port_id = connected_to_port_id
        self.connected_to_port_name = '{}{}'.format(connected_to_direction, connected_to_port_id)
        self.logical = logical
        self.port_name = '{}{}'.format(self.blade_letter, self.port_id)  # A13, B25

    def __str__(self):
        return '<SubPort "{0.direction}{0.port_id}">'.format(self)

    __repr__ = __str__

    @classmethod
    def from_line(cls, line):
        match = cls.PORT_PATTERN.search(line)

        if match is None:
            return

        group_dict = match.groupdict('')
        return cls(
            group_dict['direction'].upper(),
            group_dict['port_id'],
            group_dict['port_full_name'],
            group_dict['admin_status'].lower() == 'locked',
            group_dict['oper_status'].lower() == 'enabled',
            group_dict['port_status'].lower() == 'connected',
            group_dict.get('conn_to_direction', '').upper(),
            group_dict.get('conn_to_port_id'),
            group_dict['logical_name'],
        )


class RomePort(object):
    """Port keeps east and west ports.

    :param port_name: A1 or B2
    :type port_name: str
    :type e_port: SubPort
    :type w_port: SubPort
    """
    def __init__(self, port_name):
        self.port_name = port_name
        self.port_id = port_name[1:]
        self.e_port = None
        self.w_port = None

    def __str__(self):
        return '<RomePort "{}">'.format(self.port_name)

    __repr__ = __str__

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


class RomeLogicalPort(object):
    """Rome logical port.

    Can keeps a few Logical ports if it's a Q-port.

    :type name: str
    :type rome_ports: dict[str, RomePort]
    """
    def __init__(self, name):
        self.name = name
        self.blade_letter = name[0].lower()
        self.port_id = name[1:]
        self.rome_ports = {}

    def __str__(self):
        return '<RomeLogicalPort "{}">'.format(self.name)

    __repr__ = __str__

    def get_or_create_rome_port(self, port_name):
        try:
            rome_port = self.rome_ports[port_name]
        except KeyError:
            rome_port = RomePort(port_name)
            self.rome_ports[port_name] = rome_port

        return rome_port

    def add_sub_port(self, sub_port):
        """Adding sub port.

        :type sub_port: SubPort
        """
        rome_port = self.get_or_create_rome_port(sub_port.port_name)
        rome_port.add_sub_port(sub_port)

    @property
    def connected_to_sub_port_ids(self):
        return [
            rome_port.connected_to_port_id for rome_port in self.rome_ports.values()
        ]


class PortTable(object):
    """Table with Rome ports.

    :type map_ports: dict[str, RomeLogicalPort]
    """
    def __init__(self):
        self.map_ports = {}
        self._map_sub_port_id_to_ports = {}

    @property
    def map_sub_port_id_to_ports(self):
        if not self._map_sub_port_id_to_ports:
            self._map_sub_port_id_to_ports = {
                rome_port.port_id: rome_logical_port
                for rome_logical_port in self.map_ports.values()
                for rome_port in rome_logical_port.rome_ports.values()
            }
        return self._map_sub_port_id_to_ports

    def get_or_create(self, logical_name):
        try:
            rome_logical_port = self.map_ports[logical_name]
        except KeyError:
            rome_logical_port = RomeLogicalPort(logical_name)
            self.map_ports[logical_name] = rome_logical_port

        return rome_logical_port

    def get(self, logical_name, default=None):
        return self.map_ports.get(logical_name, default)

    def __getitem__(self, logical_name):
        """Return Rome Logical Port.

        :type logical_name: str
        :rtype: RomeLogicalPort
        """
        try:
            val = self.map_ports[logical_name]
        except KeyError:
            raise BaseRomeException(
                'We don\'t have port "{}" in Ports table'.format(logical_name)
            )
        return val

    def get_by_sub_port_id(self, sub_port_id):
        if sub_port_id:
            return self.map_sub_port_id_to_ports[sub_port_id]

    def __iter__(self):
        return iter(self.map_ports.values())

    def get_connected_port(self, rome_logical_port):
        """Return a port that connected to given.

        :type rome_logical_port: RomeLogicalPort
        :rtype: RomeLogicalPort
        """
        connected_ports = map(
            self.get_by_sub_port_id, rome_logical_port.connected_to_sub_port_ids
        )
        if any(connected_ports):
            if (len(connected_ports) != len(rome_logical_port.rome_ports)
                    or len(set(connected_ports)) != 1):
                raise ConnectedToDifferentPortsError(
                    'Logical port {} connected to a few different logical ports: '
                    '{}'.format(
                        rome_logical_port.name,
                        ','.join(p.name for p in connected_ports)
                    )
                )

            return connected_ports[0]


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
