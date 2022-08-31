from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict(
    [
        (
            r"[Pp]orts\s+are\s+not\s+of\s+the\s+same\s+matrix",
            "Ports are not of the same matrix",
        ),
        (r"[Ee]rror", "Command error"),
        (r"ERROR", "Command error"),
    ]
)

SHOW_BOARD = CommandTemplate("show board", error_map=ERROR_MAP)
PORT_SHOW = CommandTemplate("port show", error_map=ERROR_MAP)
