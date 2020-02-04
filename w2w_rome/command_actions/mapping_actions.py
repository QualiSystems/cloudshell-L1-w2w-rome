import re
import time
from collections import defaultdict

import w2w_rome.command_templates.mapping as command_template
from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor
)

from w2w_rome.helpers.errors import BaseRomeException, NotSupportedError
from w2w_rome.helpers.run_in_threads import run_in_threads


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
    """Mapping actions."""

    CONNECTION_PENDING_RESET_MAP = {
        '(?i)Multiple Cross Connect Severe Failure': reset_connection_pending,
    }

    def __init__(self, cli_services, logger, mapping_timeout, mapping_check_delay):
        """
        :param cli_services: default mode cli_services
        :type cli_services: list[cloudshell.cli.cli_service_impl.CliServiceImpl]
        :type logger: logging.Logger
        :type mapping_timeout: int
        :type mapping_check_delay: int
        """
        self._mapping_check_delay = mapping_check_delay
        self._mapping_timeout = mapping_timeout
        self._cli_services = cli_services
        self._cli_services_map = {cli.session.host: cli for cli in cli_services}
        self._logger = logger
        self._is_run_in_parallel = len(cli_services) > 1

    def check_full_output(self, cli_service):
        for key, action in self.CONNECTION_PENDING_RESET_MAP.items():
            if re.search(key, cli_service.session.full_buffer):
                action(cli_service.session, self._logger)

        cli_service.session.full_buffer = ''

    def _connect(self, cli_service, src_port_name, dst_port_name):
        """Connect ports by name.

        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :type src_port_name: str
        :type dst_port_name: str
        :return: output
        :rtype: str
        """
        return CommandTemplateExecutor(
            cli_service,
            command_template.CONNECT,
            action_map=self.CONNECTION_PENDING_RESET_MAP,
        ).execute_command(src_port=src_port_name, dst_port=dst_port_name)

    def _connect_and_wait(
            self, cli_service, src_port_name, dst_port_name, num_ports_to_connect
    ):
        """Connect multiple ports.

        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :type src_port_name: str
        :type dst_port_name: str
        :type num_ports_to_connect: int
        """
        self._connect(cli_service, src_port_name, dst_port_name)
        self.wait_ports_not_in_pending_connections(
            cli_service, [(src_port_name, dst_port_name)], num_ports_to_connect,
        )

    def connect(self, src_logic_port, dst_logic_port, bidi=True):
        """Connect logical ports.

        :type src_logic_port: w2w_rome.helpers.port_entity.LogicalPort
        :type dst_logic_port: w2w_rome.helpers.port_entity.LogicalPort
        :type bidi: bool
        """
        if not bidi:
            if src_logic_port.is_q_port:
                raise NotSupportedError("Uni connections not supported for Q ports")
            if self._is_run_in_parallel:
                raise NotSupportedError("Not supported multiple host and map uni")
            e_port = src_logic_port.e_sub_ports[0].sub_port_name
            w_port = dst_logic_port.w_sub_ports[0].sub_port_name
            param_map = {
                cli_service: [[cli_service, e_port, w_port, 2], {}]
                for cli_service in self._cli_services
            }
        else:
            src_logic_name = src_logic_port.original_logical_name
            dst_logic_name = dst_logic_port.original_logical_name
            # connect every E port to W in both directions
            num_ports_to_connect = 2 * len(src_logic_port.rome_ports)
            param_map = {
                cli_service: [
                    [cli_service, src_logic_name, dst_logic_name, num_ports_to_connect],
                    {},
                ]
                for cli_service in self._cli_services
            }

        if not self._is_run_in_parallel:
            params = param_map.values()[0]
            args, kwargs = params
            self._connect_and_wait(*args, **kwargs)
        else:
            run_in_threads(self._connect_and_wait, self._logger, param_map)

    def _disconnect(self, cli_service, src_port, dst_port):
        """Disconnect ports by name.

        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :type src_port: str
        :type dst_port: str
        :return: output
        :rtype: str
        """
        return CommandTemplateExecutor(
            cli_service,
            command_template.DISCONNECT,
            self.CONNECTION_PENDING_RESET_MAP,
        ).execute_command(src_port=src_port, dst_port=dst_port)

    def _disconnect_and_wait(
            self, cli_service, connected_port_names, num_ports_to_disconnect
    ):
        """Disconnect connected port names and wait they are not in pending.

        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :type connected_port_names: list[tuple[str, str]]
        :type num_ports_to_disconnect: int
        """
        for src, dst in connected_port_names:
            self._disconnect(cli_service, src, dst)

        self.wait_ports_not_in_pending_connections(
            cli_service, connected_port_names, num_ports_to_disconnect
        )

    def disconnect(self, connected_logic_ports, bidi=False):
        """Disconnect logical ports.

        :type connected_logic_ports: set[tuple[w2w_rome.helpers.port_entity.LogicalPort]]
        :type bidi: bool
        """
        if bidi:
            connected_port_names = []
            num_ports = 0
            for src_logic_port, dst_logic_port in connected_logic_ports:
                src_logic_name = src_logic_port.original_logical_name
                dst_logic_name = dst_logic_port.original_logical_name
                # connect every E port to W in both directions
                num_ports += 2 * len(src_logic_port.rome_ports)
                connected_port_names.append((src_logic_name, dst_logic_name))
            # for every host disconnect logical ports
            param_map = {
                cli_service: [[cli_service, connected_port_names, num_ports], {}]
                for cli_service in self._cli_services
            }
        else:
            host_connected_ports_map = defaultdict(list)
            for src_logic_port, dst_logic_port in connected_logic_ports:
                for e_port, w_port in src_logic_port.get_connected_sub_ports(
                        dst_logic_port
                ):
                    cli_service = self._cli_services_map[e_port.port_resource]
                    host_connected_ports_map[cli_service].append(
                        (e_port.sub_port_name, w_port.sub_port_name)
                    )

            param_map = {
                cli_service: [
                    [
                        cli_service,
                        sorted(connected_port_names),
                        len(connected_port_names),
                    ],
                    {},
                ]
                for cli_service, connected_port_names in host_connected_ports_map.items()
            }

        if not self._is_run_in_parallel:
            params = param_map.values()[0]
            args, kwargs = params
            self._disconnect_and_wait(*args, **kwargs)
        else:
            run_in_threads(self._disconnect_and_wait, self._logger, param_map)

    def ports_in_pending_connections(self, cli_service, ports):
        """Check ports in process or pending.

        Command in process:
        connect, ports: A3-A4, status: in process with payload

        ======= ========= ========= ================== ======= ===================
        Request Port1     Port2     Command            Source  User
        ======= ========= ========= ================== ======= ===================
        772     A1        A2        connect            CLI     admin
        """
        self.check_full_output(cli_service)

        output = CommandTemplateExecutor(
            cli_service,
            command_template.CONNECTION_SHOW_PENDING,
            action_map=self.CONNECTION_PENDING_RESET_MAP,
        ).execute_command()

        self.check_full_output(cli_service)

        for src, dst in ports:
            match = re.search(r'ports:\s+{}-{}\D'.format(src, dst), output, re.I)
            match = match or re.search(
                r'\w+\s+{}\s+{}\s+\w+'.format(src, dst), output, re.I
            )
            if match:
                return True

        return False

    def wait_ports_not_in_pending_connections(
            self, cli_service, ports, num_ports_to_connect
    ):
        """Wait for ports go away from pending connections.

        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :param ports: src and dst ports that connects
        :type ports: list[tuple[str, str]]
        :param num_ports_to_connect: timeout depends on it
        :type num_ports_to_connect: int
        """
        end_time = time.time() + (self._mapping_timeout * num_ports_to_connect)
        while time.time() < end_time:
            time.sleep(self._mapping_check_delay)
            if not self.ports_in_pending_connections(cli_service, ports):
                break
        else:
            msg = 'There are some pending connections after {}sec'.format(
                self._mapping_timeout
            )
            raise BaseRomeException(msg)
