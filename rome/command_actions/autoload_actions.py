#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

import rome.command_templates.autoload as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from rome.helpers.command_actions_helper import CommandActionsHelper


class AutoloadActions(object):
    """
    Autoload actions
    """

    def __init__(self, cli_service, logger):
        """
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def board_table(self):
        """
        :rtype: dict
        """
        board_table = {}
        output = CommandTemplateExecutor(self._cli_service, command_template.SHOW_BOARD).execute_command()
        serial_search = re.search(r'BOARD\s+.*S/N\((.+?)\)', output, re.DOTALL)
        if serial_search:
            board_table['serial_number'] = serial_search.group(1)

        board_table['model_name'] = "Rome"

        sw_version_search = re.search(r'ACTIVE\s+SW\s+VER\s+(\d+\.\d+\.\d+\.\d+)', output, re.DOTALL)
        if sw_version_search:
            board_table['sw_version'] = sw_version_search.group(1)

        return board_table

    def ports_table(self):
        """
        :rtype: dict
        """
        port_table = {}
        ports_output = CommandTemplateExecutor(self._cli_service, command_template.PORT_SHOW).execute_command()

        for record in CommandActionsHelper.parse_ports(ports_output):
            print(record)

            # port_table[]
            # port_table[record[1]] = {'blade': record[2]}

        # port_output = CommandTemplateExecutor(self._cli_service,
        #                                       command_template.PORT_SHOW).execute_command()
        #
        # for record in CommandActionsHelper.parse_table(port_output.strip(), r'^e\d+\s+\d+\s+\d+\s+\d+\s+w\d+\s+.*$'):
        #     record_id = re.sub(r'\D', '', record[0])
        #     if record_id in port_table:
        #         port_table[record_id]['locked'] = record[1]
        #         if len(record) > 7:
        #             port_table[record_id]['connected'] = re.sub(r'\D', '', record[5])
        #         else:
        #             port_table[record_id]['connected'] = None
        return port_table
