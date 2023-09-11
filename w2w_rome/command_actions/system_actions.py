from __future__ import annotations

import functools
import re
from typing import TYPE_CHECKING

import w2w_rome.command_templates.system as command_template
from w2w_rome.cli.template_executor import (
    RomeTemplateExecutor as CommandTemplateExecutor,
)
from w2w_rome.helpers.port_entity import PortTable
from w2w_rome.helpers.run_in_threads import run_in_threads

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


class SystemActions:
    def __init__(self, cli_services: list[CliService]) -> None:
        """System actions."""
        self._cli_services = cli_services
        self._is_run_in_parallel: bool = len(cli_services) > 1

    @staticmethod
    def _get_port_table(cli_service: CliService) -> PortTable:
        port_table_output = CommandTemplateExecutor(
            cli_service, command_template.PORT_SHOW
        ).execute_command()
        return PortTable.from_output(port_table_output, cli_service.session.host)

    def get_port_table(self) -> PortTable:
        """Get port table from hosts and concatenating it."""
        if not self._is_run_in_parallel:
            port_table = self._get_port_table(self._cli_services[0])
        else:
            param_map = {
                cli_service: [[cli_service], {}] for cli_service in self._cli_services
            }
            results_map = run_in_threads(self._get_port_table, param_map)
            port_table = functools.reduce(
                PortTable.__add__, results_map.values()
            )  # noqa: F821
        return port_table

    @staticmethod
    def _board_table(cli_service: CliService) -> dict[str, str]:
        """Get board table."""
        board_table = {}
        output = CommandTemplateExecutor(
            cli_service, command_template.SHOW_BOARD
        ).execute_command()
        serial_search = re.search(r"BOARD\s+.*S/N\((.+?)\)", output, re.DOTALL)
        if serial_search:
            board_table["serial_number"] = serial_search.group(1)

        model_search = re.search(
            r"^rome\s+type\s+(.+?)\s*$", output, flags=re.MULTILINE | re.IGNORECASE
        )
        if model_search:
            board_table["model_name"] = model_search.group(1)
        else:
            board_table["model_name"] = "Rome"

        sw_version_search = re.search(
            r"ACTIVE\s+SW\s+VER\s+(\d+\.\d+\.\d+\.\d+)", output, re.DOTALL
        )
        if sw_version_search:
            board_table["sw_version"] = sw_version_search.group(1)

        return board_table

    def get_board_tables_map(self) -> dict[CliService, dict[str, str]]:
        """Get board tables from hosts."""
        if not self._is_run_in_parallel:
            results_map = {
                self._cli_services[0]: self._board_table(self._cli_services[0])
            }
        else:
            param_map = {
                cli_service: [[cli_service], {}] for cli_service in self._cli_services
            }
            results_map = run_in_threads(self._board_table, param_map)
        return results_map
