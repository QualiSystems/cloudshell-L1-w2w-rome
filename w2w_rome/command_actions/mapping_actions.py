import re

import w2w_rome.command_templates.mapping as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from w2w_rome.helpers.errors import BaseRomeException
from w2w_rome.helpers.port_entity import SubPort


class MappingActions(object):
    """
    Autoload actions
    """
    NO_REQUEST_IN_PROCESS = 'no request in process'
    EMPTY_PENDING_CONNECTION_TABLE = (
        '======= ========= ========= ================== ======= ===================\n'
        'Request Port1     Port2     Command            Source  User               \n'
        '======= ========= ========= ================== ======= ===================\n'
        '\n'
    )

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
        self._empty_connection_table_pattern = re.compile(
            re.escape(self.EMPTY_PENDING_CONNECTION_TABLE)
            + self._cli_service.command_mode.prompt
        )

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

    def is_not_pending_connections(self):
        output = CommandTemplateExecutor(
            self._cli_service,
            command_template.CONNECTION_SHOW_PENDING,
        ).execute_command()

        return (
            self.NO_REQUEST_IN_PROCESS in output
            and self._empty_connection_table_pattern.search(output)
        )

    def get_sub_port(self, port_name):
        self._logger.debug('Getting port info for port {}'.format(port_name))
        port_output = CommandTemplateExecutor(
            self._cli_service,
            command_template.PORT_INFO
        ).execute_command(port=port_name)

        match = re.search(
            r'^{}\[\w+\].+$'.format(port_name),
            port_output,
            re.MULTILINE | re.IGNORECASE,
        )
        if not match:
            raise BaseRomeException('Can\'t get port info')
        return SubPort.from_line(match.group())
