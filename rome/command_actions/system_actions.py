import re
from collections import defaultdict

import rome.command_templates.system as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from rome.helpers.command_actions_helper import CommandActionsHelper


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

    def ports_association_table(self):
        """
        :rtype: dict
        """
        ports_table = defaultdict(lambda: ['', ''])
        ports_output = CommandTemplateExecutor(self._cli_service, command_template.PORT_SHOW).execute_command()

        for record in CommandActionsHelper.parse_ports(ports_output):
            alias_record = record[0]
            match_alias = re.match(r'\w+\[(\w+)\]', alias_record)
            logic_id = record[5]
            if logic_id and match_alias:
                alias = match_alias.group(1)
                if alias_record.lower().startswith('e'):
                    ports_table[logic_id][0] = alias
                else:
                    ports_table[logic_id][1] = alias
        return ports_table
