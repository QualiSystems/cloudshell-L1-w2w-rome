from collections import OrderedDict

from cloudshell.cli.session.telnet_session import TelnetSession


class RomeTelnetSession(TelnetSession):
    def _connect_actions(self, prompt, logger):
        action_map = OrderedDict()
        action_map['[Ll]ogin:|[Uu]ser:|[Uu]sername:'] = lambda session, logger: session.send_line(session.username,
                                                                                                  logger)
        action_map['[Pp]assword:'] = lambda session, logger: session.send_line(session.password, logger)
        error_map = OrderedDict([(r'[Ii]nvalid', 'Username or Password invalid')])
        self.hardware_expect(None, expected_string=prompt, timeout=self._timeout, logger=logger,
                             action_map=action_map, error_map=error_map)
        self._on_session_start(logger)
