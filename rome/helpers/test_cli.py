import os
import re

from cloudshell.cli.cli_service import CliService
from rome.cli.l1_cli_handler import L1CliHandler


class TestCliContextManager(object):
    def __init__(self, test_cli):
        self._test_cli = test_cli

    def __enter__(self):
        return self._test_cli

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestCliService(CliService):
    def __init__(self, data_path, logger):
        self._data_path = data_path
        self._logger = logger

    def reconnect(self, timeout=None):
        pass

    def enter_mode(self, command_mode):
        pass

    def send_command(self, command, expected_string=None, action_map=None, error_map=None, logger=None, *args,
                     **kwargs):
        self._logger.debug(command)
        file_name = re.sub('\s', '_', command) + '.txt'
        try:
            with open(os.path.join(self._data_path, file_name), 'r') as f:
                output = f.read()
            return output
        except IOError:
            pass


class TestCliHandler(L1CliHandler):
    def __init__(self, data_path, logger):
        self._cli_service = TestCliContextManager(TestCliService(data_path, logger))

    def get_cli_service(self, command_mode):
        return self._cli_service

    def define_session_attributes(self, address, username, password):
        pass

    def default_mode_service(self):
        return self._cli_service
