#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from cloudshell.cli.command_mode import CommandMode


CONNECTION_OPERATION_REGEX = (
    r'(\d{1,2}-\d{1,2}-\d{2,4}\s\d{1,2}:\d{1,2}\s'  # date time
    r'('
    r'((dis)?connecting\.{3}\n?)|'
    r'(connection operation \w+:\w+\[\w+\]<->\w+\[\w+\]\sop:\w+\n?)'
    r')'
    r')*'
)


class DefaultCommandMode(CommandMode):
    PROMPT = r'(?i)\w+\[\w+\]#\s*{}$'.format(CONNECTION_OPERATION_REGEX)
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self):
        super(DefaultCommandMode, self).__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_error_map=OrderedDict([(r'[Ee]rror:', 'Command error')]),
            exit_error_map=OrderedDict([(r'[Ee]rror:', 'Command error')]),
        )


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {}
}
