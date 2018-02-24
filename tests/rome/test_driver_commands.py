from unittest import TestCase

from mock import Mock

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from rome.driver_commands import DriverCommands




class TestDriverCommands(TestCase):
    def setUp(self):
        self._logger = Mock()
        self._instance = DriverCommands(self._logger)

    def test_implementing_interface(self):
        self.assertIsInstance(self._instance, DriverCommandsInterface)
