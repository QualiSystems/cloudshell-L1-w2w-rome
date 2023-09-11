from __future__ import annotations

from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession


class RomeTelnetSession(TelnetSession):
    def __init__(
        self, host: str, username: str, password: str, *args, **kwargs
    ) -> None:
        super().__init__(host, username, password, *args, **kwargs)
        self.full_buffer = ""

    def _receive(self, timeout: float | int) -> str:
        data = super()._receive(timeout)
        self.full_buffer += data
        return data

    def _connect_actions(self, prompt: str) -> None:
        action_map = {
            r"[Ll]ogin:|[Uu]ser:|[Uu]sername:": lambda session: session.send_line(
                session.username
            ),  # noqa: E501
            r"[Pp]assword:": lambda session: session.send_line(session.password),
        }
        error_map = {r"[Ii]nvalid": "Username or Password invalid"}
        self.hardware_expect(
            None,
            expected_string=prompt,
            timeout=self._timeout,
            action_map=action_map,
            error_map=error_map,
        )
        self._on_session_start()


class RomeSSHSession(SSHSession):
    def __init__(
        self, host: str, username: str, password: str, *args, **kwargs
    ) -> None:
        super().__init__(host, username, password, *args, **kwargs)
        self.full_buffer = ""

    def _receive(self, timeout: float | int) -> str:
        data = super()._receive(timeout)
        self.full_buffer += data
        return data
