import os
import re
from collections import deque
from unittest import TestCase

from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from mock import MagicMock

from w2w_rome.driver_commands import DriverCommands

RUNTIME_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    'test_runtime_config.yaml',
)
DEFAULT_PROMPT = 'ROME[OPER]#'
SHOW_BOARD = '''ROME[OPER]# show board 
CURR SW VERSION  creationDate(Feb 21 2019, 19:51:00)
ROME STATUS      adminStatus(enabled) operStatus(enabled) alarmState(Cleared)
ROME STATE       OPER
ROME NAME        ROME
ACTIVE UNITS     1
ROME TYPE        ROME500
RTOS             VxWorks (6.8) 
BOARD            ver(LCU-100) rev(3) S/N(9727-4733-2222)
MATRIX SIZE:
                 Matrix A: Male/West 1..132, Female/East 1..130
                 Matrix B: Male/West 1..132, Female/East 1..130

IP               IP addr(192.168.1.2) subnet(255.255.255.0/0xffffff00)
                 gateway(192.168.1.1) dns(192.168.1.1)
VERSIONS         nonTffsDbVer(0) nextLoadImage(active)
ACTIVE SW DESC   active image was created at 02-21-2019 19:51
ACTIVE SW BANK   1 
ACTIVE SW VER    1.10.2.10
STANDBY SW DESC  standby image was created at 02-21-2019 19:51
STANDBY SW VER   1.10.2.10
UP TIME          0 days,5 hours,2 minutes and 44 seconds (total 12 seconds)
Recovery         recovery was done
CONNECTIONS      connection execution is enabled
OPERATION COUNT  7766
FPGA VER         proj6_fpga_2019Feb11_a.rbf
TIME SOURCE      MANUAL
AUTHENTICATION   local
CONNECTION TYPE  ssh and telnet
ROME[OPER]#'''


class Command(object):
    def __init__(self, request, response, regexp=False):
        self.request = request
        self.response = response
        self.regexp = regexp

    def is_equal_to_request(self, request):
        return (not self.regexp and self.request == request
                or self.regexp and re.search(self.request, request))

    def __repr__(self):
        return 'Command({!r}, {!r}, {!r})'.format(self.request, self.response, self.regexp)


class CliEmulator(object):
    def __init__(self, commands=None):
        self.request = None

        self.commands = deque([
            Command(None, DEFAULT_PROMPT),
            Command('', DEFAULT_PROMPT),
            Command('show board', SHOW_BOARD),
        ])

        if commands:
            self.commands.extend(commands)

    def _get_response(self):
        try:
            command = self.commands.popleft()
        except IndexError:
            raise IndexError('Not expected request "{}"'.format(self.request))

        if not command.is_equal_to_request(self.request):
            raise KeyError('Unexpected request - "{}"\n'
                           'Expected - "{}"'.format(self.request, command.request))

        if isinstance(command.response, Exception):
            raise command.response
        else:
            return command.response

    def receive_all(self, timeout, logger):
        return self._get_response()

    def send_line(self, command, logger):
        self.request = command

    def check_calls(self):
        if self.commands:
            commands = '\n'.join('\t\t- {}'.format(command.request) for command in self.commands)
            raise ValueError('Not executed commands: \n{}'.format(commands))


class BaseRomeTestCase(TestCase):
    def setUp(self):
        self.runtime_config = RuntimeConfiguration(RUNTIME_CONFIG_PATH)
        self.logger = MagicMock()
        self.driver_commands = DriverCommands(self.logger, self.runtime_config)
        self.cli_handler = self.driver_commands._cli_handler

    def tearDown(self):
        self.driver_commands._cli_handler._cli._session_pool._session_manager._existing_sessions = []
