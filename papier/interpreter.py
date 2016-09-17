import re


class Handler(object):
    def can_handle(self, fs_node):
        raise NotImplementedError()


class Interpreter(object):
    def __init__(self, handlers):
        self.handlers     = handlers
        self.re_extension = re.compile('\.[a-z\d]+$', re.I)
        self.html_ext     = '.html'

    def prepare(self, fs_nodes):
        for fs_node in fs_nodes:
            for handler in self.handlers:
                if not handler.can_handle(fs_node):
                    continue

                fs_node.output_path = self.re_extension.sub(self.html_ext, fs_node.output_path)
                fs_node.handler     = handler

    def process(self, fs_nodes):
        for fs_node in fs_nodes:
            if not fs_node.handler:
                continue

            fs_node.handler.process(fs_node)
