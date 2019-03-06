import re
from collections import defaultdict

import rome.command_templates.system as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from rome.helpers.command_actions_helper import parse_ports
from rome.helpers.port_entity import PortTable, SubPort


class SystemActions(object):
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

    def get_port_table(self):
        port_table = PortTable()

        port_table_output = CommandTemplateExecutor(
            self._cli_service, command_template.PORT_SHOW).execute_command()

        for line in port_table_output.splitlines():
            sub_port = SubPort.from_line(line)
            if sub_port:
                port = port_table.get_or_create(sub_port.port_id)
                port.add_sub_port(sub_port)

        return port_table

    def board_table(self):
        """
        :rtype: dict
        """
        board_table = {}
        output = CommandTemplateExecutor(self._cli_service, command_template.SHOW_BOARD).execute_command()
        serial_search = re.search(r'BOARD\s+.*S/N\((.+?)\)', output, re.DOTALL)
        if serial_search:
            board_table['serial_number'] = serial_search.group(1)

        model_search = re.search(r'^rome\s+type\s+(.+?)\s*$', output, flags=re.MULTILINE | re.IGNORECASE)
        if model_search:
            board_table['model_name'] = model_search.group(1)
        else:
            board_table['model_name'] = "Rome"

        sw_version_search = re.search(r'ACTIVE\s+SW\s+VER\s+(\d+\.\d+\.\d+\.\d+)', output, re.DOTALL)
        if sw_version_search:
            board_table['sw_version'] = sw_version_search.group(1)

        return board_table

    def ports_association_table(self):
        """
        :rtype: dict
        """
        ports_table = defaultdict(lambda: ['', ''])
        ports_output = CommandTemplateExecutor(self._cli_service, command_template.PORT_SHOW).execute_command()

        for record in parse_ports(ports_output):
            alias_record = record[0].lower()
            match_alias = re.match(r'\w+\[(\w+)\]', alias_record)
            logic_id = record[5].lower()
            if logic_id and match_alias:
                alias = match_alias.group(1)
                if alias_record.startswith('e'):
                    ports_table[logic_id][0] = alias
                else:
                    ports_table[logic_id][1] = alias
        return ports_table
