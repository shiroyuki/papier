import codecs
import hashlib
import os
import re
import shutil
import subprocess
import sys
import pprint


class Compiler(object):
    """ Compile documents """
    def __init__(self, renderer):
        self._re_ext    = re.compile('\.(md|rst)+$', re.IGNORECASE)  # supported extensions
        self._re_config = re.compile('^\..+\.(json|yml)$')  # override config files per file/directory
        self._re_h1     = re.compile('<h1(?P<extra> [^>]+)?>(?P<title>.*)</h1>')
        self._re_h2     = re.compile('<h2(?P<extra> [^>]+)?>(?P<title>.*)</h2>')
        self._renderer  = renderer

    def compile(self, src_path, output_path):
        # Handle the non-existing output directory.
        if not os.path.exists(output_path):
            subprocess.call(['mkdir', '-p', output_path])

        self._traverse(
            src_path,
            output_path,
            self._compile_file_to_html
        )

        self._traverse(
            src_path,
            output_path,
            self._render_file
        )

        # Copy the static files.
        print('Copying static files...')
        self._renderer.copy_static_files(os.path.join(output_path, '_static'))
        print('Done')

    def _traverse(self, src_path, output_path, handle_file_callable, level = -1):
        if not os.path.exists(src_path):
            raise IOError('{} not found'.format(src_path))

        if os.path.isfile(src_path):
            handle_file_callable(src_path, output_path, level)

            return

        # Handle the non-existing output directory.
        if not os.path.exists(output_path):
            subprocess.call(['mkdir', '-p', output_path])

        filenames = self._walk_dir(src_path)

        for filename in filenames:
            next_src_path    = os.path.join(src_path, filename)
            next_output_path = os.path.join(output_path, filename)

            self._traverse(
                next_src_path,
                next_output_path,
                handle_file_callable,
                level + 1
            )

    def _walk_dir(self, path):
        print('{}: Listing'.format(path))
        items = []

        for filename in os.listdir(path):
            if filename[0] in ('.', '_'):
                print('[{}] {}: Skipped (A)'.format(path, filename))
                continue

            # Skip the possible configuration or hidden file.
            if self._re_config.search(filename):
                print('[{}] {}: Skipped (B)'.format(path, filename))
                continue

            items.append(filename)

        return items

    def _get_compiled_path(self, src_path):
        md5 = hashlib.new('md5')
        md5.update(src_path.encode('ascii'))

        if not os.path.exists('.papier-cache'):
            subprocess.call(['mkdir', '-p', '.papier-cache'])

        cache_path = os.path.join('.papier-cache', md5.hexdigest())

        print('{} -> {}'.format(src_path, cache_path))

        return cache_path

    def _get_compiled(self, path):
        compiled = None

        with codecs.open(self._get_compiled_path(path), 'r') as f:
            compiled = f.read()

        return compiled

    def _get_title(self, path):
        compiled = self._get_compiled(path)
        matches  = self._re_h1.match(compiled) or self._re_h2.match(compiled)

        return matches.groupdict()['title'] if matches else None

    def _compile_file_to_html(self, src_path, output_path, level):
        if not self._re_ext.search(src_path):
            return

        tmp_path      = self._get_compiled_path(src_path)
        compiling_cmd = ' '.join(['github-markup', src_path, '>', tmp_path])

        subprocess.call(compiling_cmd, shell = True)

        print('[{}] Compiled'.format(src_path))

    def _render_file(self, src_path, output_path, level):
        # Only copy files that do not require compilation.
        if not self._re_ext.search(src_path):
            shutil.copyfile(src_path, output_path)

            return

        template = self._renderer.template('default.html')

        neighbour_pages = self._get_neighbours(src_path)

        # Compute the base static path
        static_path = '_static'

        if level > 0:
            levels = ['..'] * level
            levels.append(static_path)

            static_path = os.path.join(*levels)

        actual_output_path = self._re_ext.sub('.html', output_path)

        # Render and save the result.
        with codecs.open(actual_output_path, 'w') as f:
            f.write(template.render(
                title       = self._get_title(src_path),
                content     = self._get_compiled(src_path),
                neighbours  = neighbour_pages,
                static_path = static_path,
                level       = level
            ))

        print('[{}] Saved'.format(src_path))

    def _get_neighbours(self, src_path):
        neighbour_pages = []

        src_dir  = os.path.dirname(src_path)
        src_name = os.path.basename(src_path)

        filenames = self._walk_dir(src_dir)

        for filename in filenames:
            neighbour_path = os.path.join(src_dir, filename)

            is_file = os.path.isfile(neighbour_path)
            is_dir  = os.path.isdir(neighbour_path)

            index_dest_path = None
            index_src_path  = None
            neighbour_title = None

            if is_dir:
                index_filename  = 'index.rst'
                index_dest_path = os.path.join(filename, 'index.html')
                index_src_path  = os.path.join(src_dir, filename, index_filename)

                if not os.path.exists(index_src_path):
                    index_filename = 'index.md'

                index_src_path = os.path.join(src_dir, filename, index_filename)

                neighbour_title = self._get_title(index_src_path)
            else:
                if not self._re_ext.search(neighbour_path):
                    print('Skipped: {}'.format(neighbour_path))

                    continue

                neighbour_title = self._get_title(neighbour_path)

            neighbour_pages.append({
                'filename' : index_dest_path or self._re_ext.sub('.html', filename),
                'title'    : neighbour_title,
                'current'  : src_name == filename,
                'is_file'  : is_file,
                'is_dir'   : is_dir,
                'is_index' : bool(index_dest_path),
            })

        return neighbour_pages
