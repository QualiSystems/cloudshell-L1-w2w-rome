from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.service.cli import CLI
from cloudshell.cli.service.session_pool_manager import SessionPoolManager
from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from w2w_rome.cli.rome_sessions import RomeSSHSession, RomeTelnetSession

if TYPE_CHECKING:
    from cloudshell.cli.service.command_mode import CommandMode
    from cloudshell.cli.service.session_pool_context_manager import (
        SessionPoolContextManager,
    )


class L1CliHandler:
    def __init__(self) -> None:
        self._cli = CLI(session_pool=SessionPoolManager(max_pool_size=1))
        self._defined_session_types = {
            "SSH": RomeSSHSession,
            "TELNET": RomeTelnetSession,
        }

        self._session_types = (
            RuntimeConfiguration().read_key("CLI.TYPE")
            or self._defined_session_types.keys()
        )
        self._ports = RuntimeConfiguration().read_key("CLI.PORTS", {"SSH": "22"})

        self._host: str | None = None
        self._username: str | None = None
        self._password: str | None = None

    def _new_sessions(self) -> list[RomeSSHSession | RomeTelnetSession]:
        """Create sessions based on available types."""
        sessions = []
        for session_type in self._session_types:
            session_class = self._defined_session_types.get(session_type)
            if not session_class:
                raise LayerOneDriverException(
                    f"Session type {session_type} is not defined"
                )
            port = self._ports.get(session_type)
            sessions.append(
                session_class(self._host, self._username, self._password, port)
            )
        return sessions

    def define_session_attributes(
        self, address: str, username: str, password: str
    ) -> None:
        """Define session attributes."""
        address_list = address.split(":")
        if len(address_list) > 1:
            raise LayerOneDriverException("Incorrect resource address")
        self._host = address
        self._username = username
        self._password = password

    def get_cli_service(self, command_mode: CommandMode) -> SessionPoolContextManager:
        """Create new cli service or get it from pool."""
        if not self._host or not self._username or not self._password:
            raise LayerOneDriverException(
                "Cli Attributes is not defined, call Login command first"
            )
        return self._cli.get_session(self._new_sessions(), command_mode)
