from jinja2 import Environment, PackageLoader

class Renderer(object):
    def __init__(self):
        self._default_env = Environment(loader=PackageLoader('papier', 'templates'))
