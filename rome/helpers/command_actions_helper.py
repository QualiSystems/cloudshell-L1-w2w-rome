import re


def parse_ports(ports_data):
    regexp = r'^([\w\[\]]+)\s+((?:locked|unlocked))\s+((?:enabled|disabled))' \
             r'\s+([\w\s]+)\s+\d+\s+([\w\[\]]*)\s+([\w\[\]]+)\s*$'
    return re.findall(regexp, ports_data, flags=re.MULTILINE | re.IGNORECASE)
