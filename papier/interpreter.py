import codecs
import os
import re


class Handler(object):
    def can_handle(self, fs_node):
        raise NotImplementedError()


class Interpreter(object):
    def __init__(self, handlers):
        self.handlers = handlers
        self.re_ext   = re.compile('\.[a-z\d]+$', re.I)
        self.html_ext = '.html'

    def prepare(self, fs_nodes):
        for fs_node in fs_nodes:
            for handler in self.handlers:
                if not handler.can_handle(fs_node):
                    continue

                fs_node.output_path    = self.re_ext.sub(self.html_ext, fs_node.output_path)
                fs_node.reference_path = self.re_ext.sub(self.html_ext, fs_node.reference_path)
                fs_node.interpreter    = handler

    def process(self, fs_nodes):
        for fs_node in fs_nodes:
            if not fs_node.interpreter:
                continue

            if not fs_node.is_updated():
                continue

            html = fs_node.interpret()

            dir_path = os.path.dirname(fs_node.cache_path)

            if not os.path.exists(dir_path):
                os.makedirs(dir_path, 0o755)

            with codecs.open(fs_node.cache_path, 'w') as f:
                f.write(html)
