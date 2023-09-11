from __future__ import annotations

from cloudshell.cli.service.command_mode import CommandMode

CONNECTION_OPERATION_REGEX = (
    r"(\d{1,2}-\d{1,2}-\d{2,4}\s\d{1,2}:\d{1,2}\s"  # date time
    r"("
    r"((dis)?connecting\.{3}\n?)|"
    r"((connection operation \w+:\w+\[\w+\]<->\w+\[\w+\]\sop:\w+\n?)+|"
    r"(connection .+ completed .+\n))*"
    r")"
    r")*"
)


class DefaultCommandMode(CommandMode):
    PROMPT = rf"(?i)\w+\[\w+\]#\s*{CONNECTION_OPERATION_REGEX}$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = "exit"

    def __init__(self) -> None:
        super().__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_error_map={r"[Ee]rror:": "Command error"},
            exit_error_map={r"[Ee]rror:": "Command error"},
        )


CommandMode.RELATIONS_DICT = {DefaultCommandMode: {}}
