import codecs
import json
import os
import re

import yaml


class SourceConfig(object):
    def __init__(self, path = None, index_filename = None):
        self.path           = path           or 'src'
        self.index_filename = index_filename or 'index'


class OutputConfig(object):
    def __init__(self, path = None):
        self.path = path or 'build'


class ThemeConfig(object):
    def __init__(self, path = None, layout = None, contexts = None):
        self.path     = path     or 'build'
        self.layout   = layout   or 'default.html'
        self.contexts = contexts or {}


class PathConfig(object):
    def __init__(self, pattern, theme_path = None, theme_layout = None):
        self.pattern      = re.compile('^{}$'.format(pattern))
        self.theme_path   = theme_path
        self.theme_layout = theme_layout

    def can_handle(self, path):
        return self.pattern.search(path)


class MainConfig(object):
    def __init__(self, source, output, theme, override):
        self.source   = source
        self.output   = output
        self.theme    = theme
        self.override = override

    def get_theme_config(self, path):
        for path_config in self.override:
            if path_config.can_handle(path):
                return ThemeConfig(
                    path     = path_config.theme_path   or self.theme.path,
                    layout   = path_config.theme_layout or self.theme.layout,
                    contexts = self.theme.contexts,
                )

        return self.theme


class Parser(object):
    def __init__(self):
        self._re_json = re.compile('\.json$',  re.I)
        self._re_yaml = re.compile('\.ya?ml$', re.I)

    def parse_from_file(self, path):
        base_path = os.path.dirname(path)
        is_local  = os.path.abspath(base_path) == os.path.abspath(os.getcwd())

        with codecs.open(path, 'r') as f:
            raw_content = f.read()

        parsed_content = {}

        if self._re_json.search(path):
            parsed_content.update(json.loads(raw_content))
        elif self._re_yaml.search(path):
            parsed_content.update(yaml.load(raw_content)['papier'])
        else:
            raise RuntimeError('Not support this type of configuration.')

        source = SourceConfig()
        output = OutputConfig()
        theme  = ThemeConfig()
        paths  = []

        if 'source' in parsed_content:
            source = SourceConfig(**parsed_content['source'])

        if 'output' in parsed_content:
            output = OutputConfig(**parsed_content['output'])

        if 'theme' in parsed_content and parsed_content['theme']:
            theme = ThemeConfig(**parsed_content['theme'])

        if 'override' in parsed_content and parsed_content['override']:
            for pattern, theme_config in parsed_content['override'].items():
                paths.append(PathConfig(pattern, **theme_config))

        if not is_local:
            source.path = self._fix_path(source.path, base_path)
            output.path = self._fix_path(output.path, base_path)
            theme.path  = self._fix_path(theme.path,  base_path)

            for path in paths:
                path.theme_path = self._fix_path(path.theme_path, base_path)

        return MainConfig(source, output, theme, paths)

    def _fix_path(self, path, base_path):
        if not path:
            return None

        return os.path.abspath(path if path[0] == '/' else os.path.join(base_path, path))
