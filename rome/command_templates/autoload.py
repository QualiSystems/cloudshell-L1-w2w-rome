#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror', 'Command error'), (r'ERROR', 'Command error')])

SHOW_BOARD = CommandTemplate('show board', ACTION_MAP, ERROR_MAP)
PORT_SHOW = CommandTemplate('port show', ACTION_MAP, ERROR_MAP)
PORT_SHOW_LOGIC_TABLE = CommandTemplate('port show logic table', ACTION_MAP, ERROR_MAP)
PORT_SHOW_LOGIC = CommandTemplate('port show logical', ACTION_MAP, ERROR_MAP)

