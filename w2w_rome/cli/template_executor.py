import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)


class RomeTemplateExecutor(CommandTemplateExecutor):
    @staticmethod
    def remove_logs_from_output(output):
        date_pattern = r"\d+-\d+-\d+\s\d+:\d+"
        pattern = re.compile(
            r"\n{}\s"
            r"("
            r"(connection \w+<->\w+\scompleted\s\w+ *)"
            r"|(connection operation [\w( )]+:[\w\[\]]+<->[\w\[\]]+ OP:\w+ *)"
            r")\n+".format(date_pattern),
            flags=re.IGNORECASE,
        )
        return pattern.sub("", output)

    def execute_command(self, remove_logs=True, **command_kwargs):
        output = super(RomeTemplateExecutor, self).execute_command(**command_kwargs)
        if remove_logs:
            output = self.remove_logs_from_output(output)
        return output
