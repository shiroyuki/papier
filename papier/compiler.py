import codecs
import os
import re
import shutil
import subprocess
import sys


class Compiler(object):
    """ Compile documents """
    def __init__(self, renderer):
        self._re_ext    = re.compile('\.(md|rst)+$', re.IGNORECASE)  # supported extensions
        self._re_config = re.compile('^\..+\.(json|yml)$')  # override config files per file/directory
        self._re_h1     = re.compile('<h1(?P<extra> [^>]+)?>(?P<title>.*)</h1>')
        self._re_h2     = re.compile('<h2(?P<extra> [^>]+)?>(?P<title>.*)</h2>')
        self._renderer  = renderer

    def compile(self, src_path, output_path, level = -1):
        print('Traversing (LV {}): {} -> {}'.format(level, src_path, output_path))
        if not os.path.exists(src_path):
            raise IOError('{} not found'.format(src_path))

        if os.path.isfile(src_path):
            self._handle_file(src_path, output_path, level)

            return

        # Handle the non-existing output directory.
        if not os.path.exists(output_path):
            subprocess.call(['mkdir', '-p', output_path])

        for filename in os.listdir(src_path):
            if filename[0] in ('.', '_'):
                continue

            # Skip the possible configuration or hidden file.
            if self._re_config.search(filename):
                continue

            next_src_path    = os.path.join(src_path, filename)
            next_output_path = os.path.join(output_path, filename)

            if os.path.isfile(next_src_path):
                next_output_path = self._re_ext.sub('.html', next_output_path)

            self.compile(next_src_path, next_output_path, level + 1)

        if level == -1:
            print('Copying static files...')
            self._renderer.copy_static_files(os.path.join(output_path, '_static'))
            print('Done')

    def _handle_file(self, src_path, output_path, level):
        if not self._re_ext.search(src_path):
            sys.stderr.write('WARNING: {}\n')

            return

        # Only copy files that do not require compilation.
        if not self._re_ext.search(src_path):
            shutil.copyfile(src_path, output_path)

            return

        tmp_path      = '{}.compiled'.format(output_path)
        compiling_cmd = ' '.join(['github-markup', src_path, '>', tmp_path])

        print('[{}] Compiling...'.format(src_path))
        subprocess.call(compiling_cmd, shell = True)

        print('[{}] Rendering...'.format(src_path))
        rendered = None

        with codecs.open(tmp_path, 'r') as f:
            rendered = f.read()

        template = self._renderer.template('default.html')
        matches  = self._re_h1.match(rendered) or self._re_h2.match(rendered)

        static_path = '_static'
        doc_title   = None

        if level > 0:
            levels = ['..'] * level
            levels.append(static_path)

            static_path = os.path.join(*levels)

        if matches:
            doc_title = matches.groupdict()['title']

        with codecs.open(output_path, 'w') as f:
            f.write(template.render(
                title       = doc_title,
                content     = rendered,
                static_path = static_path
            ))

        print('[{}] Saved'.format(src_path))
