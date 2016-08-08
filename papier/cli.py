import codecs
import os
import re
import subprocess
import sys

from gallium import ICommand


class Compile(ICommand):
    """ Compile documents """
    def __init__(self):
        self._re_ext    = re.compile('\.(md|rst)+$', re.IGNORECASE)  # supported extensions
        self._re_config = re.compile('^\..+\.(json|yml)$')  # override config files per file/directory

    def identifier(self):
        return 'compile'

    def define(self, parser):
        parser.add_argument(
            '--src',
            '-s',
            help = 'the directory containing the source of your website',
            required = True
        )

        parser.add_argument(
            '--output',
            '-o',
            help = 'the directory will contain the actual website',
            required = True
        )

    def execute(self, args):
        self.core.get('compiler').compile(
            os.path.abspath(args.src),
            os.path.abspath(args.output)
        )
