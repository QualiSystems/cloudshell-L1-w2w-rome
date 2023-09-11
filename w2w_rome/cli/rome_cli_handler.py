from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from w2w_rome.cli.l1_cli_handler import L1CliHandler
from w2w_rome.cli.rome_command_modes import DefaultCommandMode

if TYPE_CHECKING:
    from cloudshell.cli.service.session_pool_context_manager import (
        SessionPoolContextManager,
    )


class RomeCliHandler(L1CliHandler):
    def __init__(self) -> None:
        super().__init__()
        self.modes = CommandModeHelper.create_command_mode()

    @property
    def _default_mode(self) -> DefaultCommandMode:
        return self.modes[DefaultCommandMode]

    def default_mode_service(self) -> SessionPoolContextManager:
        """Default mode session."""
        return self.get_cli_service(self._default_mode)
