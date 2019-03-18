from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict([
    (r'(?i)connection operation',
     lambda session, logger: session.send_line('', logger)),
])
ERROR_MAP = OrderedDict([(r'[Pp]orts\s+are\s+not\s+of\s+the\s+same\s+matrix', 'Ports are not of the same matrix'),
                         (r'[Ee]rror', 'Command error'), (r'ERROR', 'Command error')])

CONNECT = CommandTemplate('connection create {src_port} to {dst_port}', ACTION_MAP, ERROR_MAP)
DISCONNECT = CommandTemplate('connection disconnect {src_port} from {dst_port}', ACTION_MAP, ERROR_MAP)
PORT_INFO = CommandTemplate('port show {port}', ACTION_MAP, ERROR_MAP)
