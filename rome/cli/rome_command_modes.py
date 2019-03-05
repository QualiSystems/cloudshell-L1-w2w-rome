#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from cloudshell.cli.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r'.+\[.+\]#'
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
