import re

import w2w_rome.command_templates.mapping as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from w2w_rome.helpers.errors import BaseRomeException


def reset_connection_pending(session, logger):
    """Reset connection pending.

    :type session: cloudshell.cli.session.expect_session.ExpectSession
    :type logger: logging.Logger
    """
    session.hardware_expect('homing run', r'(?i)RECOVERY FINISHED SUCCESSFULLY', logger)
    session.hardware_expect(
        'connection set command-execution enable',
        r'connection execution is enabled',
        logger,
    )
    raise BaseRomeException(
        'Multiple Cross Connect Severe Failure. Problem with a connection. '
        'Reset connection pending.'
    )


class MappingActions(object):
    """
    Autoload actions
    """
    CONNECTION_PENDING_RESET_MAP = {
        '(?i)Multiple Cross Connect Severe Failure': reset_connection_pending,
    }

    def __init__(self, cli_service, logger):
        """
        :param cli_service: default mode cli_service
        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def check_full_output(self):
        for key, action in self.CONNECTION_PENDING_RESET_MAP.items():
            if re.search(key, self._cli_service.session.full_buffer):
                action(self._cli_service.session, self._logger)

        self._cli_service.session.full_buffer = ''

    def connect(self, src_port, dst_port):
        """
        Connect ports
        :param src_port:
        :param dst_port:
        :return:
        """
        return CommandTemplateExecutor(
            self._cli_service, command_template.CONNECT
        ).execute_command(src_port=src_port, dst_port=dst_port)

    def disconnect(self, src_port, dst_port):
        """
        Disconnect ports
        :param src_port:
        :param dst_port:
        :return:
        """
        return CommandTemplateExecutor(
            self._cli_service, command_template.DISCONNECT
        ).execute_command(src_port=src_port, dst_port=dst_port)

    def ports_in_pending_connections(self, ports):
        """Check ports in process or pending.

        Command in process:
        connect, ports: A3-A4, status: in process with payload

        ======= ========= ========= ================== ======= ===================
        Request Port1     Port2     Command            Source  User
        ======= ========= ========= ================== ======= ===================
        772     A1        A2        connect            CLI     admin
        """
        self.check_full_output()

        output = CommandTemplateExecutor(
            self._cli_service,
            command_template.CONNECTION_SHOW_PENDING,
        ).execute_command()

        self.check_full_output()

        for src, dst in ports:
            match = re.search(r'ports:\s+{}-{}\D'.format(src, dst), output, re.I)
            match = match or re.search(
                r'\w+\s+{}\s+{}\s+\w+'.format(src, dst), output, re.I
            )
            if match:
                return True

        return False
