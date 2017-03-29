import codecs
import hashlib
import os
import re

class DocBase(object):
    @property
    def ancestors(self):
        """ From leaf to root """
        ancestors = []
        iterator  = self

        while iterator.parent:
            ancestors.append(iterator.parent)

            iterator = iterator.parent

        ancestors.reverse()

        return ancestors

    @property
    def tree_path(self):
        return self.path.split('/') if self.path else []

    def relative_path_to(self, base):
        if self.path == base.path:
            return os.path.basename(self.path)

        self_tree_path = self.path.split('/')
        base_tree_path = base.path.split('/')

        self_level = len(self_tree_path)
        base_level = len(base_tree_path)

        diff_level = self_level - base_level

        prefix = '../' * abs(diff_level) if diff_level < 0 else ''

        return '{}{}#{}'.format(
            prefix,
            '/'.join(self.tree_path[self_level - diff_level - 1:]),
            self_level - diff_level - 1
        )

    def __getattr__(self, name):
        return getattr(self.fs_node, name) if self.fs_node else None

    def __repr__(self):
        return '<{} name="{}">'.format(type(self).__name__, self.name or '(root)')


class DocTree(DocBase, dict):
    """ FSNode Tree """
    def __init__(self, level):
        self.fs_node = None
        self.parent  = None

        super().__init__()

    @property
    def kind(self):
        if 'index' in self:
            return self['index'].kind

        return 'root'

    @property
    def level(self):
        if 'index' in self:
            return self['index'].level

        return 0

    @property
    def path(self):
        if 'index' in self:
            return self['index'].path

        return None

    @property
    def title(self):
        if 'index' in self:
            return self['index'].title

        return None

    def __getattr__(self, name):
        return getattr(self.fs_node, name) if self.fs_node else None


class DocNode(DocBase):
    _re_h1 = re.compile('<h1(?P<extra> [^>]+)?>(?P<title>.*)</h1>', re.M)
    _re_h2 = re.compile('<h2(?P<extra> [^>]+)?>(?P<title>.*)</h2>', re.M)
    _re_h3 = re.compile('<h3(?P<extra> [^>]+)?>(?P<title>.*)</h3>', re.M)
    _re_h4 = re.compile('<h4(?P<extra> [^>]+)?>(?P<title>.*)</h4>', re.M)
    _re_h5 = re.compile('<h5(?P<extra> [^>]+)?>(?P<title>.*)</h5>', re.M)
    _re_h6 = re.compile('<h6(?P<extra> [^>]+)?>(?P<title>.*)</h6>', re.M)

    def __init__(self, level):
        self.level   = level
        self.fs_node = None
        self.parent  = None

    @property
    def title(self):
        compiled = self.fs_node.content

        matches = (
            self._re_h1.match(compiled)
            or self._re_h2.match(compiled)
            or self._re_h3.match(compiled)
            or self._re_h4.match(compiled)
            or self._re_h5.match(compiled)
            or self._re_h6.match(compiled)
        )

        return matches.groupdict()['title'] if matches else None

    @property
    def path(self):
        return self.fs_node.reference_path


class Factory(object):
    def make(self, fs_nodes):
        tree = DocTree(0)

        for fs_node in fs_nodes:
            tree_path     = self._get_tree_path(fs_node)
            parent_node   = None
            tree_iterator = tree # Reset to the root.

            for fs_vertex in tree_path[:-1]:
                if fs_vertex not in tree_iterator:
                    tree_iterator[fs_vertex] = DocTree(tree_iterator.level + 1)

                if tree_iterator:
                    parent_node = tree_iterator

                tree_iterator = tree_iterator[fs_vertex]

                if parent_node:
                    tree_iterator.parent = parent_node

            # Handle the last level.
            doc_name = tree_path[-1]

            if doc_name in tree_iterator and tree_iterator[doc_name].fs_node:
                continue

            depth_level = tree_iterator.level + 1

            doc_node         = DocNode(depth_level) if fs_node.is_file() else DocTree(depth_level)
            doc_node.fs_node = fs_node
            doc_node.parent  = tree_iterator

            tree_iterator[doc_name] = doc_node

        return tree

    def _get_tree_path(self, fs_node):
        return fs_node.name.split('/')
