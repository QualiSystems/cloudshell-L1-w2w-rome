import rome.command_templates.mapping as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from rome.helpers.port_entity import SubPort


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

    def get_sub_port(self, port_id):
        self._logger.debug('Getting port info for port {}'.format(port_id))
        port_output = CommandTemplateExecutor(
            self._cli_service,
            command_template.PORT_INFO
        ).execute_command(port=port_id)
        return SubPort.from_line(port_output)
