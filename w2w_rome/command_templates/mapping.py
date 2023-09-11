from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = {
    r"[Pp]orts\s+are\s+not\s+of\s+the\s+same\s+matrix": "Ports are not of the same matrix",  # noqa: E501
    r"[Ee]rror": "Command error",
    r"ERROR": "Command error",
}

CONNECT = CommandTemplate(
    "connection create {src_port} to {dst_port}", error_map=ERROR_MAP
)
DISCONNECT = CommandTemplate(
    "connection disconnect {src_port} from {dst_port}", error_map=ERROR_MAP
)
PORT_INFO = CommandTemplate("port show {port}", error_map=ERROR_MAP)
CONNECTION_SHOW_PENDING = CommandTemplate("connection show pending")
