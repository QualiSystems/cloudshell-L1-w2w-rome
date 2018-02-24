import re


class CommandActionsHelper(object):
    @staticmethod
    def parse_table(data, pattern):
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        table = []
        for record in data.split('\n'):
            matched = re.search(compiled_pattern, record.strip())
            if matched:
                table.append(re.split(r'\s+', matched.group(0)))
        return table

    @staticmethod
    def parse_ports(ports_data):
        regexp = r'^([\w\[\]]+)\s+((?:locked|unlocked))\s+((?:enabled|disabled))' \
                 r'\s+((?:connected|disconnected))\s+\d+\s+([\w\[\]]*)\s+([\w\[\]]+)\s*$'
        return re.findall(regexp, ports_data, flags=re.MULTILINE | re.IGNORECASE)