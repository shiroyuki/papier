import codecs
import os
import re
import subprocess

from gallium import ICommand


class Compile(ICommand):
    """ Compile documents """
    def __init__(self):
        self._re_ext = re.compile('\.[^\.]+$')

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
        self._compile(os.path.abspath(args.src), os.path.abspath(args.output))

    def _compile(self, src_path, output_path):
        print('Traversing:', src_path, ' ->', output_path)
        if not os.path.exists(src_path):
            raise IOError('{} not found'.format(src_path))

        if os.path.isfile(src_path):
            tmp_path      = '{}.compiled'.format(output_path)
            compiling_cmd = ' '.join(['github-markup', src_path, '>', tmp_path])

            subprocess.call(compiling_cmd, shell = True)

            print('[{}]'.format(src_path))
            with codecs.open(tmp_path, 'r') as f:
                print(f.read())
            print('')

            return

        # Handle the non-existing output directory.
        if not os.path.exists(output_path):
            subprocess.call(['mkdir', '-p', output_path])

        for filename in os.listdir(src_path):
            if filename[0] in ('.', '_'):
                continue

            next_src_path    = os.path.join(src_path, filename)
            next_output_path = os.path.join(output_path, filename)

            if os.path.isfile(next_src_path):
                next_output_path = self._re_ext.sub('.html', next_output_path)

            self._compile(next_src_path, next_output_path)
