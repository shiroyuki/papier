import re
import subprocess

from .interpreter import Handler


class MarkDownHandler(Handler):
    def __init__(self):
        self._re_supported_ext = re.compile('\.(md|markdown)$', re.I)
        self._cli_cmd          = 'github-markup {input}'

    def can_handle(self, fs_node):
        return (
            fs_node.is_file() and
            bool(self._re_supported_ext.search(fs_node.reference_path))
        )

    def process(self, fs_node):
        actual_cmd = self._cli_cmd.format(input = fs_node.src_path)

        return subprocess.check_output(actual_cmd, shell = True).decode('utf-8')
