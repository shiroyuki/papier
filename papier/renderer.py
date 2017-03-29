# DEPRECATED

import os
import shutil

from jinja2 import Environment, PackageLoader, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from papier import helper


class NoStaticFilesWarning(RuntimeWarning):
    """ Warning for no static files """


class StaticFileExistWarning(RuntimeWarning):
    """ Warning for no static files """


class Renderer(object):
    def __init__(self):
        self._default_src = helper.path('template')
        self._default_env = Environment(loader = PackageLoader('papier', 'template'))
        self._basepath    = None
        self._environment = None
        print(self._default_src)

    def set_basepath(self, basepath):
        self._basepath    = basepath
        self._environment = Environment(loader = FileSystemLoader(self._basepath))

    def template(self, path):
        if self._environment:
            return self._environment.get_template(path)

        return self._default_env.get_template(path)

    def copy_static_files(self, destination_path):
        src_static_path = os.path.join(self._basepath or self._default_src)

        if not os.path.exists(src_static_path):
            raise NoStaticFilesWarning(src_static_path)

        if os.path.exists(destination_path):
            raise StaticFileExistWarning(destination_path)

        shutil.copytree(src_static_path, destination_path)
