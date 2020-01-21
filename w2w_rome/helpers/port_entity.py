import itertools
import random
import re
from copy import copy

from w2w_rome.helpers.errors import BaseRomeException, ConnectedToDifferentPortsError, \
    ConnectionPortsError


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
        r'(?P<logical_name>[ABQP]\d+)\s*$',
        re.IGNORECASE,
    )

    def __init__(self, direction, port_id, port_full_name, locked, enabled, connected,
                 connected_to_direction, connected_to_port_id, logical, port_resource):
        self.direction = direction
        self.sub_port_id = port_id
        self.sub_port_full_name = port_full_name
        self.blade_letter = logical[0] if logical[0] != 'P' else 'Q'
        self.sub_port_name = '{}{}'.format(direction, port_id)  # E12
        self.locked = locked
        self.enabled = enabled
        self.connected = connected
        self.connected_to_direction = connected_to_direction
        self.connected_to_sub_port_id = connected_to_port_id
        self.logical = logical if logical[0] != 'P' else 'Q' + logical[1:]
        self.port_name = '{}{}'.format(self.blade_letter, self.sub_port_id)  # A13, Q1
        self.port_resource = port_resource
        self.original_logical_letter = logical[0]

    def __str__(self):
        return '<SubPort {0.port_resource}:{0.sub_port_name}>'.format(self)

    __repr__ = __str__

    def table_view(self):
        delimiter = ''
        port_width = 17 - 2 - len(self.sub_port_name) - len(self.sub_port_full_name)
        admin_status = 'Locked' if self.locked else 'Unlocked'
        admin_status_width = 13
        oper_status = 'Enabled' if self.enabled else 'Disabled'
        oper_status_width = 12
        port_status = 'Connected' if self.connected else 'Disconnected'
        port_status_width = 14
        counter = random.randrange(0, 99)
        counter_width = 8
        connected_to = '{0}[{1}{0}]'.format(
            self.connected_to_sub_port_name, self.sub_port_full_name[:2]
        ) if self.connected_to_sub_port_name else ''
        connected_to_width = 15
        logical_width = 8
        return (
            '{port_direction}[{port_full_name}]{delimiter: <{port_width}}'
            '{admin_status: <{admin_status_width}}'
            '{oper_status: <{oper_status_width}}'
            '{port_status: <{port_status_width}}'
            '{counter: <{counter_width}}'
            '{connected_to: <{connected_to_width}}'
            '{logical: <{logical_width}}'.format(
                port_direction=self.sub_port_name,
                port_full_name=self.sub_port_full_name,
                logical=self.logical,
                **locals()
            )
        )

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (
                    self.port_resource == other.port_resource
                    and self.sub_port_name == other.sub_port_name
            )
        return False

    def __lt__(self, other):
        if isinstance(other, type(self)):
            if self.direction == other.direction:
                return int(self.sub_port_id) < int(other.sub_port_id)
            return self.direction < other.direction
        raise NotImplementedError

    @property
    def connected_to_sub_port_name(self):
        return '{}{}'.format(self.connected_to_direction, self.connected_to_sub_port_id)

    @classmethod
    def from_line(cls, line, port_resource):
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
            group_dict['logical_name'].upper(),
            port_resource,
        )

    def verify_sub_port_is_not_locked_or_disabled(self):
        """Check that Sub Ports are not locked or disabled.    """
        if self.locked:
            raise BaseRomeException('Sub Port {} is Locked'.format(self.sub_port_name))
        if not self.enabled:
            raise BaseRomeException(
                'Sub Port {} is Disabled'.format(self.sub_port_name)
            )


class RomePort(object):
    """Port keeps east and west ports.

    :param port_name: A1 or B2
    :type port_name: str
    :type e_port: SubPort
    :type w_port: SubPort
    """
    def __init__(self, port_resource, port_name):
        self.port_resource = port_resource
        self.port_name = port_name
        self.sub_port_id = port_name[1:]
        self.e_port = None
        self.w_port = None

    def __str__(self):
        return '<RomePort {0.port_resource}:{0.port_name}>'.format(self)

    __repr__ = __str__

    @property
    def blade_letter(self):
        return self.e_port.blade_letter

    @property
    def connected_to_sub_port_id(self):
        return self.e_port.connected_to_sub_port_id

    @property
    def connected_from_sub_port_id(self):
        return self.w_port.connected_to_sub_port_id

    def add_sub_port(self, sub_port):
        if sub_port.port_resource != self.port_resource:
            raise ValueError(
                'Sub port ({}) located on a different resource from a '
                'Rome port ({})'.format(sub_port, self)
            )

        attr_name = '{}_port'.format(sub_port.direction.lower())
        if getattr(self, attr_name) is not None:
            raise BaseRomeException('{} port already set'.format(sub_port.direction))

        setattr(self, attr_name, sub_port)


class LogicalPort(object):
    """Rome logical port.

    Can keeps a few Logical ports if it's a Q-port.

    :type name: str
    """
    def __init__(self, name):
        self.name = name
        self.blade_letter = name[0].upper()
        self.port_id = name[1:]
        self._rome_ports_map = {}  # (<port_resource>, <port_name>): <rome_port>
        self.is_q_port = self.blade_letter == "Q"

    @property
    def rome_ports(self):
        """:rtype: list[RomePort]"""
        return self._rome_ports_map.values()

    @property
    def e_sub_ports(self):
        """Return E Sub ports.

        :rtype: list[SubPort]
        """
        return [rome_port.e_port for rome_port in self.rome_ports]

    @property
    def w_sub_ports(self):
        """Return W Sub ports.

        :rtype: list[SubPort]
        """
        return [rome_port.w_port for rome_port in self.rome_ports]

    def __str__(self):
        return '<LogicalPort "{}">'.format(self.name)

    __repr__ = __str__

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name
        return False

    def __iter__(self):
        return iter(self.rome_ports)

    def get_or_create_rome_port(self, port_resource, port_name):
        """Get exiting Rome port or create new.

        :type port_resource: str
        :type port_name: str
        :rtype: RomePort
        """
        try:
            rome_port = self._rome_ports_map[(port_resource, port_name)]
        except KeyError:
            rome_port = RomePort(port_resource, port_name)
            self._rome_ports_map[(port_resource, port_name)] = rome_port

        return rome_port

    def add_sub_port(self, sub_port):
        """Adding sub port.

        :type sub_port: SubPort
        """
        rome_port = self.get_or_create_rome_port(
            sub_port.port_resource, sub_port.port_name
        )
        rome_port.add_sub_port(sub_port)

    @property
    def connected_to_sub_port_ids(self):
        return filter(
            None,
            (rome_port.connected_to_sub_port_id for rome_port in self.rome_ports),
        )

    @property
    def connected_from_sub_port_ids(self):
        return filter(
            None,
            (rome_port.connected_from_sub_port_id for rome_port in self.rome_ports),
        )

    def verify_connected_ports(self, connected_ports):
        """Verify that the logical port is connected only for one port."""
        if (len(connected_ports) != len(self.rome_ports)
                or len(set(connected_ports)) != 1):
            raise ConnectedToDifferentPortsError(
                'Logical port {} connected to a few different logical ports: '
                '{}'.format(
                    self.name,
                    ','.join(p.name for p in connected_ports)
                )
            )

    def verify_e_ports_is_not_locked_or_disabled(self):
        map(SubPort.verify_sub_port_is_not_locked_or_disabled, self.e_sub_ports)

    def verify_w_ports_is_not_locked_or_disabled(self):
        map(SubPort.verify_sub_port_is_not_locked_or_disabled, self.w_sub_ports)

    def get_connected_sub_ports(self, dst_logic_port):
        """Return mapping with connected sub ports.

        :type dst_logic_port: LogicalPort
        :rtype: set[tuple[SubPort, SubPort]]
        """
        return {
            (e_port, w_port)
            for e_port in self.e_sub_ports
            for w_port in dst_logic_port.w_sub_ports
            if e_port.connected_to_sub_port_name == w_port.sub_port_name
        }


class PortTable(object):
    """Table with Rome ports.

    :type _map_ports: dict[str, LogicalPort]
    """
    def __init__(self):
        self._map_ports = {}
        self._map_sub_port_id_to_ports = {}

    @property
    def logical_ports(self):
        return self._map_ports.values()

    @property
    def is_matrix_q(self):
        """Check that matrix is Q or not.

        :rtype: bool
        """
        return self.logical_ports[0].is_q_port

    @property
    def map_sub_port_id_to_ports(self):
        if not self._map_sub_port_id_to_ports:
            self._map_sub_port_id_to_ports = {
                rome_port.sub_port_id: logical_port
                for logical_port in self._map_ports.values()
                for rome_port in logical_port.rome_ports
            }
        return self._map_sub_port_id_to_ports

    def __add__(self, other):
        cls = type(self)
        if not isinstance(other, cls):
            raise ValueError('Cannot add {} to PortTable'.format(type(other)))

        if set(self._map_ports.keys()) != set(other._map_ports.keys()):
            raise ValueError('Port tables have different logical ports')

        new_port_table = cls()
        for port_name, first_logical_port in self._map_ports.items():
            second_logical_port = other[port_name]
            new_logical_port = new_port_table.get_or_create(port_name)

            for rome_port in itertools.chain(first_logical_port, second_logical_port):
                new_e_sub_port = copy(rome_port.e_port)
                new_w_sub_port = copy(rome_port.w_port)
                new_logical_port.add_sub_port(new_e_sub_port)
                new_logical_port.add_sub_port(new_w_sub_port)

        return new_port_table

    def get_or_create(self, logical_name):
        try:
            logical_port = self._map_ports[logical_name]
        except KeyError:
            logical_port = LogicalPort(logical_name)
            self._map_ports[logical_name] = logical_port

        return logical_port

    def get(self, logical_name, default=None):
        return self._map_ports.get(logical_name, default)

    def __getitem__(self, logical_name):
        """Return Rome Logical Port.

        :type logical_name: str
        :rtype: LogicalPort
        """
        try:
            val = self._map_ports[logical_name]
        except KeyError:
            raise BaseRomeException(
                'We don\'t have port "{}" in Ports table'.format(logical_name)
            )
        return val

    def get_by_sub_port_id(self, sub_port_id):
        """Get Rome Logical Port by sub port id.

        :type sub_port_id: str
        :rtype: LogicalPort
        """
        if sub_port_id:
            return self.map_sub_port_id_to_ports[sub_port_id]

    def __iter__(self):
        return iter(self._map_ports.values())

    def get_connected_to_port(self, logical_port):
        """Return a port that connected to given.

        :type logical_port: LogicalPort
        :rtype: LogicalPort
        """
        connected_to_ports = map(
            self.get_by_sub_port_id, logical_port.connected_to_sub_port_ids
        )
        if connected_to_ports:
            logical_port.verify_connected_ports(connected_to_ports)
            return connected_to_ports[0]

    def get_connected_from_port(self, logical_port):
        """Return a port from which the logical port connected.

        :type logical_port: LogicalPort
        :rtype: LogicalPort
        """
        connected_from_ports = map(
            self.get_by_sub_port_id, logical_port.connected_from_sub_port_ids
        )
        if connected_from_ports:
            logical_port.verify_connected_ports(connected_from_ports)
            return connected_from_ports[0]

    def is_connected(self, src_logic_port, dst_logic_port, bidi=False):
        """Check that ports are connected.

        :type src_logic_port: LogicalPort
        :type dst_logic_port: LogicalPort
        :type bidi: bool
        :rtype: bool
        """
        src_to_dst = self.get_connected_to_port(src_logic_port) == dst_logic_port
        dst_to_src = True
        if bidi:
            dst_to_src = self.get_connected_to_port(dst_logic_port) == src_logic_port
        return src_to_dst and dst_to_src

    def verify_ports_for_connection(self, src_logic_port, dst_logic_port, bidi=False):
        """Verify that we can use ports for connection.

        :type src_logic_port: LogicalPort
        :type dst_logic_port: LogicalPort
        :type bidi: bool
        """
        src_logic_port.verify_e_ports_is_not_locked_or_disabled()
        dst_logic_port.verify_w_ports_is_not_locked_or_disabled()

        src_connected_to = self.get_connected_to_port(src_logic_port)
        dst_connected_from = self.get_connected_from_port(dst_logic_port)
        if src_connected_to and src_connected_to != dst_logic_port:
            raise ConnectionPortsError(
                "Source port connected to another port - {}".format(src_connected_to)
            )
        if dst_connected_from and dst_connected_from != src_logic_port:
            raise ConnectionPortsError(
                "To destination port connected another port - {}".format(
                    dst_connected_from
                )
            )

        if bidi:
            src_logic_port.verify_w_ports_is_not_locked_or_disabled()
            dst_logic_port.verify_e_ports_is_not_locked_or_disabled()

            src_connected_from = self.get_connected_from_port(src_logic_port)
            dst_connected_to = self.get_connected_to_port(dst_logic_port)
            if src_connected_from and src_connected_from != dst_logic_port:
                raise ConnectionPortsError(
                    "To source port connected another port - {}".format(
                        src_connected_from
                    )
                )
            if dst_connected_to and dst_connected_to != src_logic_port:
                raise ConnectionPortsError(
                    "Destination port connected to another port - {}".format(
                        dst_connected_to
                    )
                )

    def get_connected_port_pairs(self, port_names, bidi=False):
        """Return pairs of logical ports that connected.

        :type port_names: list[str]
        :type bidi: bool
        :rtype: set[tuple[LogicalPort]]
        """
        connected_ports = set()

        for port_name in port_names:
            logic_port = self[port_name]
            connected_to = self.get_connected_to_port(logic_port)
            if connected_to:
                connected_ports.add((logic_port, connected_to))

            if bidi:
                connected_from = self.get_connected_from_port(logic_port)
                if connected_from:
                    connected_ports.add((connected_from, logic_port))

        return connected_ports

    @staticmethod
    def get_connected_sub_ports_pairs(connected_ports, bidi=False):
        """Return pairs of Sub ports that connected.

        :type connected_ports: set[tuple[LogicalPort]]
        :type bidi: bool
        :rtype: set[tuple[SubPort]]
        """
        connected_sub_ports = set()

        for src_logic_port, dst_logic_port in connected_ports:
            connected_sub_ports.update(
                src_logic_port.get_connected_sub_ports(dst_logic_port)
            )
            if bidi:
                connected_sub_ports.update(
                    dst_logic_port.get_connected_sub_ports(src_logic_port)
                )

        return connected_sub_ports
