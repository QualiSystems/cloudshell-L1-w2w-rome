from __future__ import annotations

import itertools
import random
import re
from copy import copy

from w2w_rome.helpers.cached_property import cached_property
from w2w_rome.helpers.errors import (
    BaseRomeException,
    ConnectedToDifferentPortsError,
    ConnectionPortsError,
)


class SubPort:
    """Sub port that keep fiber port for one direction."""

    PORT_PATTERN = re.compile(
        r"(?P<direction>[EW])(?P<port_id>\d+)"
        r"\[(?P<port_full_name>\w+?)]\s+"
        r"(?P<admin_status>(locked|unlocked))\s+"
        r"(?P<oper_status>(enabled|disabled))\s+"
        r"(?P<port_status>((dis)?connected)|in process)\s+"
        r"\d+\s+"
        r"((?P<conn_to_direction>[EW])(?P<conn_to_port_id>\d+)"
        r"\[\w+])?\s+"
        r"(?P<logical_name>[ABQPXY]\d+)",
        re.IGNORECASE,
    )
    PORT_PATTERN_V2 = re.compile(
        r"(?P<port_full_name>\w+?)\s+"
        r"(?P<admin_status>(locked|unlocked))\s+"
        r"(?P<oper_status>(enabled|disabled))\s+"
        r"(?P<port_status>((dis)?connected)|in process)\s+"
        r"\d+\s+"
        r"((?P<conn_to_direction>[EW])(?P<conn_to_port_id>\d+)"
        r"\[\w+])?\s+"
        r"(?P<direction>[EW])(?P<port_id>\d+)\s*,\s*"
        r"(?P<logical_name>[ABQPXY]\d+)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        direction: str,
        port_id: str,
        port_full_name: str,
        locked: bool,
        enabled: bool,
        connected: bool,
        connected_to_direction: str,
        connected_to_port_id: str,
        logical: str,
        port_resource: str,
    ):
        self.direction = direction
        self.sub_port_id = port_id
        self.sub_port_full_name = port_full_name
        self.blade_letter = logical[0] if logical[0] != "P" else "Q"
        self.sub_port_name = f"{direction}{port_id}"  # E12
        self.locked = locked
        self.enabled = enabled
        self.connected = connected
        self.connected_to_direction = connected_to_direction
        self.connected_to_sub_port_id = connected_to_port_id
        self.logical = logical if logical[0] != "P" else "Q" + logical[1:]
        if self.blade_letter in "XY":
            # XY ports have sub ports from different blades and different port id for
            # the same logical port name, e.g. X1 - E129B, W1A; Y4 - E4A, W132B
            self.port_name = logical
        else:
            # A13, Q1
            self.port_name = f"{self.blade_letter}{self.sub_port_id}"
        self.port_resource = port_resource
        self.original_logical_name = logical

    def __str__(self) -> str:
        return f"<SubPort {self.port_resource}:{self.sub_port_name}>"

    __repr__ = __str__

    def table_view(self) -> str:
        delimiter = ""
        port_width = 17 - 2 - len(self.sub_port_name) - len(self.sub_port_full_name)
        admin_status = "Locked" if self.locked else "Unlocked"
        admin_status_width = 13
        oper_status = "Enabled" if self.enabled else "Disabled"
        oper_status_width = 12
        port_status = "Connected" if self.connected else "Disconnected"
        port_status_width = 14
        counter = random.randrange(0, 99)
        counter_width = 8
        connected_to = (
            "{0}[{1}{0}]".format(
                self.connected_to_sub_port_name, self.sub_port_full_name[:2]
            )
            if self.connected_to_sub_port_name
            else ""
        )
        connected_to_width = 15
        logical_width = 8
        return (
            "{port_direction}[{port_full_name}]{delimiter: <{port_width}}"
            "{admin_status: <{admin_status_width}}"
            "{oper_status: <{oper_status_width}}"
            "{port_status: <{port_status_width}}"
            "{counter: <{counter_width}}"
            "{connected_to: <{connected_to_width}}"
            "{logical: <{logical_width}}".format(
                port_direction=self.sub_port_name,
                port_full_name=self.sub_port_full_name,
                logical=self.original_logical_name,
                **locals(),
            )
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return (
                self.port_resource == other.port_resource
                and self.sub_port_name == other.sub_port_name
            )
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, type(self)):
            if self.direction == other.direction:
                return int(self.sub_port_id) < int(other.sub_port_id)
            return self.direction < other.direction
        raise NotImplementedError

    @property
    def connected_to_sub_port_name(self) -> str:
        return f"{self.connected_to_direction}{self.connected_to_sub_port_id}"

    @classmethod
    def parse_sub_ports(cls, port_table_out: str, port_resource: str) -> list[SubPort]:
        sub_ports = []

        port_info_list = list(cls.PORT_PATTERN.finditer(port_table_out))
        if not port_info_list:
            port_info_list = list(cls.PORT_PATTERN_V2.finditer(port_table_out))

        for port_match in port_info_list:
            # port_info = ('E', '20', '1AE20', 'Unlocked', 'Unlocked', 'Enabled',
            #           'Enabled', 'Connected', 'Connected', '', 'W121[1AW121]', 'W',  # noqa
            #           '121', 'P20')
            port_info = port_match.groupdict()
            sub_port = cls(
                direction=port_info["direction"].upper(),
                port_id=port_info["port_id"],
                port_full_name=port_info["port_full_name"],
                locked=port_info["admin_status"].lower() == "locked",
                enabled=port_info["oper_status"].lower() == "enabled",
                connected=port_info["port_status"].lower() == "connected",
                connected_to_direction=(port_info["conn_to_direction"] or "").upper(),
                connected_to_port_id=port_info["conn_to_port_id"] or "",
                logical=port_info["logical_name"].upper(),
                port_resource=port_resource,
            )
            sub_ports.append(sub_port)
        return sub_ports

    def verify_sub_port_is_not_locked_or_disabled(self) -> None:
        """Check that Sub Ports are not locked or disabled."""
        if self.locked:
            raise BaseRomeException(f"Sub Port {self.sub_port_name} is Locked")
        if not self.enabled:
            raise BaseRomeException(f"Sub Port {self.sub_port_name} is Disabled")


class RomePort:
    """Port keeps east and west ports."""

    def __init__(self, port_resource, port_name: str) -> None:
        self.port_resource = port_resource
        self.port_name = port_name  # A1 or B2
        self.sub_port_id = port_name[1:]
        self.e_port: SubPort | None = None
        self.w_port: SubPort | None = None

    def __str__(self) -> str:
        return f"<RomePort {self.port_resource}:{self.port_name}>"

    __repr__ = __str__

    @property
    def blade_letter(self) -> str:
        return self.e_port.blade_letter

    @property
    def connected_to_sub_port_name(self):
        return self.e_port.connected_to_sub_port_name

    @property
    def connected_from_sub_port_name(self):
        return self.w_port.connected_to_sub_port_name

    def add_sub_port(self, sub_port: SubPort) -> None:
        if sub_port.port_resource != self.port_resource:
            raise ValueError(
                f"Sub port ({sub_port}) located on a different resource from a "
                f"Rome port ({self})"
            )

        attr_name = f"{sub_port.direction.lower()}_port"
        if getattr(self, attr_name) is not None:
            raise BaseRomeException(f"{sub_port.direction} port already set")

        setattr(self, attr_name, sub_port)


class LogicalPort:
    """Rome logical port.

    Can keep a few Logical ports if it's a Q-port.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.blade_letter = name[0].upper()
        self.port_id = name[1:]
        self._rome_ports_map: dict[
            tuple[str, str], RomePort
        ] = {}  # (<port_resource>, <port_name>): <rome_port>
        self.is_q_port: bool = self.blade_letter == "Q"

    @property
    def rome_ports(self) -> list[RomePort]:
        """Rome ports."""
        return list(self._rome_ports_map.values())

    @property
    def e_sub_ports(self) -> list[SubPort]:
        """Return E Sub ports."""
        res = [
            p for rome_port in self.rome_ports if (p := rome_port.e_port) is not None
        ]  # e_port can not be None. Port validation is on PortTable building step.
        return res

    @property
    def w_sub_ports(self) -> list[SubPort]:
        """Return W Sub ports."""
        res = [
            p for rome_port in self.rome_ports if (p := rome_port.w_port) is not None
        ]  # w_port can not be None. Port validation is on PortTable building step.
        return res

    @property
    def original_logical_name(self) -> str:
        return self.rome_ports[0].e_port.original_logical_name

    def __str__(self) -> str:
        return f'<LogicalPort "{self.name}">'

    __repr__ = __str__

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.name == other.name
        return False

    def __iter__(self):
        return iter(self.rome_ports)

    def get_or_create_rome_port(self, port_resource: str, port_name: str) -> RomePort:
        """Get exiting Rome port or create new."""
        try:
            rome_port = self._rome_ports_map[(port_resource, port_name)]
        except KeyError:
            rome_port = RomePort(port_resource, port_name)
            self._rome_ports_map[(port_resource, port_name)] = rome_port

        return rome_port

    def add_sub_port(self, sub_port: SubPort) -> None:
        """Adding sub port."""
        rome_port = self.get_or_create_rome_port(
            sub_port.port_resource, sub_port.port_name
        )
        rome_port.add_sub_port(sub_port)

    @property
    def connected_to_sub_port_names(self):
        return filter(
            None,
            (rome_port.connected_to_sub_port_name for rome_port in self.rome_ports),
        )

    @property
    def connected_from_sub_port_names(self):
        return filter(
            None,
            (rome_port.connected_from_sub_port_name for rome_port in self.rome_ports),
        )

    def verify_connected_ports(self, connected_ports: list) -> None:
        """Verify that the logical port is connected only for one port."""
        if (
            len(connected_ports) != len(self.rome_ports)
            or len(set(connected_ports)) != 1
        ):
            raise ConnectedToDifferentPortsError(
                f"Port {self.name} was already partially mapped to another port. "
                f"Please, update the L1 resource "
                f"using Resource Manage's Sync From option"
            )

    def verify_e_ports_is_not_locked_or_disabled(self) -> None:
        map(SubPort.verify_sub_port_is_not_locked_or_disabled, self.e_sub_ports)

    def verify_w_ports_is_not_locked_or_disabled(self) -> None:
        map(SubPort.verify_sub_port_is_not_locked_or_disabled, self.w_sub_ports)

    def get_connected_sub_ports(
        self, dst_logic_port: LogicalPort
    ) -> set[tuple[SubPort, SubPort]]:
        """Return set with connected sub ports."""
        return {
            (e_port, w_port)
            for e_port in self.e_sub_ports
            for w_port in dst_logic_port.w_sub_ports
            if (
                e_port.connected_to_sub_port_name == w_port.sub_port_name
                and e_port.port_resource == w_port.port_resource
            )
        }


class PortTable:
    """Table with Rome ports."""

    def __init__(self) -> None:
        self._map_ports: dict[str, LogicalPort] = {}

    @classmethod
    def from_output(cls, port_table_output: str, host: str) -> PortTable:
        """Create Port table from CLI port show output."""
        port_table = cls()
        for sub_port in SubPort.parse_sub_ports(port_table_output, host):
            rome_logical_port = port_table.get_or_create(sub_port.logical)
            rome_logical_port.add_sub_port(sub_port)
        port_table.validate(port_table_output)
        return port_table

    @property
    def logical_ports(self) -> list[LogicalPort]:
        """Get logical ports."""
        return list(self._map_ports.values())

    @property
    def is_matrix_q(self) -> bool:
        """Check that matrix is Q or not."""
        return self.logical_ports[0].is_q_port

    @cached_property
    def map_sub_port_name_to_ports(self) -> dict[str, LogicalPort]:
        res = {}
        for lp in self.logical_ports:
            for rp in lp.rome_ports:
                res.update({rp.e_port.sub_port_name: lp, rp.w_port.sub_port_name: lp})
        return res

    def __add__(self, other):
        cls = type(self)
        if not isinstance(other, cls):
            raise ValueError(f"Cannot add {type(other)} to PortTable")

        if set(self._map_ports.keys()) != set(other._map_ports.keys()):
            raise ValueError("Port tables have different logical ports")

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

    def validate(self, output: str) -> None:
        msg = f"Not all sub ports are loaded. Output is:\n{output}"
        for lp in self.logical_ports:
            for rp in lp.rome_ports:
                if rp.e_port is None or rp.w_port is None:
                    raise BaseRomeException(msg)

    def get_or_create(self, logical_name: str) -> LogicalPort:
        try:
            logical_port = self._map_ports[logical_name]
        except KeyError:
            logical_port = LogicalPort(logical_name)
            self._map_ports[logical_name] = logical_port

        return logical_port

    def get(self, logical_name: str, default=None) -> LogicalPort | None:
        return self._map_ports.get(logical_name, default)

    def __getitem__(self, logical_name: str) -> LogicalPort:
        """Return Rome Logical Port."""
        try:
            val = self._map_ports[logical_name]
        except KeyError:
            raise BaseRomeException(
                f"We don't have port '{logical_name}' in Ports table"
            )
        return val

    def get_by_sub_port_name(self, sub_port_name: str) -> LogicalPort:
        """Get Rome Logical Port by sub port name."""
        return self.map_sub_port_name_to_ports[sub_port_name]

    def __iter__(self):
        return iter(self._map_ports.values())

    def get_connected_to_port(self, logical_port: LogicalPort) -> LogicalPort | None:
        """Return a port that connected to given."""
        connected_to_ports = list(
            map(self.get_by_sub_port_name, logical_port.connected_to_sub_port_names)
        )
        if connected_to_ports:
            logical_port.verify_connected_ports(connected_to_ports)
            return connected_to_ports[0]

        return None

    def get_connected_from_port(self, logical_port: LogicalPort) -> LogicalPort | None:
        """Return a port from which the logical port connected."""
        connected_from_ports = list(
            map(self.get_by_sub_port_name, logical_port.connected_from_sub_port_names)
        )
        if connected_from_ports:
            logical_port.verify_connected_ports(connected_from_ports)
            return connected_from_ports[0]

        return None

    def is_connected(
        self,
        src_logic_port: LogicalPort,
        dst_logic_port: LogicalPort,
        bidi: bool = False,
    ) -> bool:
        """Check that ports are connected."""
        src_to_dst = self.get_connected_to_port(src_logic_port) == dst_logic_port
        dst_to_src = True
        if bidi:
            dst_to_src = self.get_connected_to_port(dst_logic_port) == src_logic_port
        return src_to_dst and dst_to_src

    def verify_ports_for_connection(
        self,
        src_logic_port: LogicalPort,
        dst_logic_port: LogicalPort,
        bidi: bool = False,
    ) -> None:
        """Verify that we can use ports for connection."""
        src_logic_port.verify_e_ports_is_not_locked_or_disabled()
        dst_logic_port.verify_w_ports_is_not_locked_or_disabled()

        src_connected_to = self.get_connected_to_port(src_logic_port)
        dst_connected_from = self.get_connected_from_port(dst_logic_port)
        if src_connected_to and src_connected_to != dst_logic_port:
            raise ConnectionPortsError(
                f"Source port connected to another port - {src_connected_to}"
            )
        if dst_connected_from and dst_connected_from != src_logic_port:
            raise ConnectionPortsError(
                f"To destination port connected another port - {dst_connected_from}"
            )

        if bidi:
            src_logic_port.verify_w_ports_is_not_locked_or_disabled()
            dst_logic_port.verify_e_ports_is_not_locked_or_disabled()

            src_connected_from = self.get_connected_from_port(src_logic_port)
            dst_connected_to = self.get_connected_to_port(dst_logic_port)
            if src_connected_from and src_connected_from != dst_logic_port:
                raise ConnectionPortsError(
                    f"To source port connected another port - {src_connected_from}"
                )
            if dst_connected_to and dst_connected_to != src_logic_port:
                raise ConnectionPortsError(
                    f"Destination port connected to another port - {dst_connected_to}"
                )

    def get_connected_port_pairs(
        self, port_names: list[str], bidi: bool = False
    ) -> set[tuple[LogicalPort, LogicalPort]]:
        """Return pairs of logical ports that connected."""
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
