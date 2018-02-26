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

    def connection_table(self):
        connection_table = {}
        ports_output = CommandTemplateExecutor(self._cli_service, command_template.PORT_SHOW).execute_command()
        for record in CommandActionsHelper.parse_ports(ports_output):
            src_record = record[0].lower()
            dst_record = record[4].lower()
            if dst_record and src_record.lower().startswith('e'):
                src_port = re.match(r'\w+\[(\w+)\]', src_record).group(1)
                dst_port = re.match(r'\w+\[(\w+)\]', dst_record).group(1)
                connection_table[src_port] = dst_port
        return connection_table
