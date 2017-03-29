import codecs
import os
import re

from .doctree import DocNode


class Assembler(object):
    def __init__(self, config_parser, file_walker, interpreter, doctree_factory, templates):
        self.config_parser   = config_parser
        self.file_walker     = file_walker
        self.interpreter     = interpreter
        self.doctree_factory = doctree_factory
        self.templates       = templates

    def assemble_by_file(self, configuration_file_path):
        return self.assemble(
            self.config_parser.parse_from_file(configuration_file_path)
        )

    def assemble(self, config):
        nodes = self.file_walker.walk(config.source.path, config.output.path)

        self.interpreter.prepare(nodes)
        self.interpreter.process(nodes)

        doc_tree = self.doctree_factory.make(nodes)

        self.build_many(config, doc_tree)

    def build_many(self, config, doc_tree):
        output_path  = config.output.path
        theme_config = config.theme

        for node in doc_tree.values():
            if not isinstance(node, DocNode):
                self.build_many(config, node)

                continue

            theme_config = config.get_theme_config(node.path)

            self.build_one(node, doc_tree, output_path, theme_config)

    def build_one(self, node, doc_tree, output_path, theme_config):
        if node.is_dir():
            return

        dir_path = os.path.join(output_path, os.path.dirname(node.reference_path))

        if not os.path.exists(dir_path):
            os.makedirs(dir_path, 0o755)

        output = self.templates.get_template('default.html').render(page = node)

        #print(node.output_path)
        with codecs.open(node.output_path, 'w') as f:
            f.write(output)
