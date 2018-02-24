from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

CONNECT = CommandTemplate('connection create {src_port} to {dst_port}', ACTION_MAP, ERROR_MAP)
DISCONNECT = CommandTemplate('connection disconnect {src_port} from {dst_port}', ACTION_MAP, ERROR_MAP)
CONNECTIONS = CommandTemplate('connection show connected', ACTION_MAP, ERROR_MAP)
