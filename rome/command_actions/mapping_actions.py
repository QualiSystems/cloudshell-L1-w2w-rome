import re

import rome.command_templates.mapping as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from rome.helpers.command_actions_helper import parse_ports


class MappingActions(object):
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

    def connect(self, src_port, dst_port):
        """
        Connect ports
        :param src_port:
        :param dst_port:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.CONNECT).execute_command(src_port=src_port,
                                                                                                      dst_port=dst_port)
        return output

    def disconnect(self, src_port, dst_port):
        """
        Disconnect ports
        :param src_port:
        :param dst_port:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.DISCONNECT).execute_command(
            src_port=src_port,
            dst_port=dst_port)
        return output

    def port_info(self, port_id):
        self._logger.debug('Getting port info for port {}'.format(port_id))
        port_output = CommandTemplateExecutor(self._cli_service,
                                              command_template.PORT_INFO).execute_command(port=port_id)

        port_info = list(parse_ports(port_output)[0])
        port_info[0] = re.match(r'\w+\[(\w+)\]', port_info[0]).group(1).lower()
        dst_port_match = re.match(r'\w+\[(\w+)\]', port_info[4])
        if dst_port_match:
            port_info[4] = dst_port_match.group(1).lower()
        return port_info
