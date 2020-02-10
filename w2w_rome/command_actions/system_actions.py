import re

import w2w_rome.command_templates.system as command_template
from w2w_rome.cli.template_executor import (
    RomeTemplateExecutor as CommandTemplateExecutor
)
from w2w_rome.helpers.port_entity import PortTable
from w2w_rome.helpers.run_in_threads import run_in_threads


class SystemActions(object):
    """Autoload actions."""

    def __init__(self, cli_services, logger):
        """
        :param cli_services: default mode cli_services
        :type cli_services: list[cloudshell.cli.cli_service_impl.CliServiceImpl]
        :type logger: logging.Logger
        """
        self._cli_services = cli_services
        self._logger = logger
        self._is_run_in_parallel = len(cli_services) > 1

    @staticmethod
    def _get_port_table(cli_service):
        port_table_output = CommandTemplateExecutor(
            cli_service, command_template.PORT_SHOW
        ).execute_command()
        return PortTable.from_output(port_table_output, cli_service.session.host)

    def get_port_table(self):
        """Get port table from hosts and concatenating it.

        :rtype: PortTable
        """
        if not self._is_run_in_parallel:
            port_table = self._get_port_table(self._cli_services[0])
        else:
            param_map = {
                cli_service: [[cli_service], {}] for cli_service in self._cli_services
            }
            results_map = run_in_threads(self._get_port_table, self._logger, param_map)
            port_table = reduce(PortTable.__add__, results_map.values())
        return port_table

    @staticmethod
    def _board_table(cli_service):
        """
        :rtype: dict
        """
        board_table = {}
        output = CommandTemplateExecutor(
            cli_service, command_template.SHOW_BOARD
        ).execute_command()
        serial_search = re.search(r'BOARD\s+.*S/N\((.+?)\)', output, re.DOTALL)
        if serial_search:
            board_table['serial_number'] = serial_search.group(1)

        model_search = re.search(
            r'^rome\s+type\s+(.+?)\s*$', output, flags=re.MULTILINE | re.IGNORECASE
        )
        if model_search:
            board_table['model_name'] = model_search.group(1)
        else:
            board_table['model_name'] = "Rome"

        sw_version_search = re.search(
            r'ACTIVE\s+SW\s+VER\s+(\d+\.\d+\.\d+\.\d+)', output, re.DOTALL
        )
        if sw_version_search:
            board_table['sw_version'] = sw_version_search.group(1)

        return board_table

    def get_board_tables_map(self):
        """Get board tables from hosts.

        :return: dict[cli_service, dict with board table info[
        :rtype: dict[cloudshell.cli.cli_service_impl.CliServiceImpl, dict]
        """
        if not self._is_run_in_parallel:
            results_map = {
                self._cli_services[0]: self._board_table(self._cli_services[0])
            }
        else:
            param_map = {
                cli_service: [[cli_service], {}] for cli_service in self._cli_services
            }
            results_map = run_in_threads(self._board_table, self._logger, param_map)
        return results_map
