class Port(object):
    def __init__(self, name, paired, connected, locked, disabled):
        self.name = name
        self.paired = paired
        self.connected = connected
        self.locked = locked
        self.disabled = disabled


class PortInfo(object):
    def __init__(self, port_id, east_port, west_port):
        """
        :param east_port:
        :type east_port: Port
        :param west_port:
        :type west_port: Port
        """
        self.port_id = port_id
        self.east_port = east_port
        self.west_port = west_port
