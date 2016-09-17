import codecs
import os
import hashlib
import re


class InvalidWalkTargetError(RuntimeError):
    pass


def hash_cache_name(content):
    md5 = hashlib.new('md5')
    md5.update(content.encode('utf-8'))

    return md5.hexdigest()


class FSNode(object):
    def __init__(self, src_path, output_path, reference_path, cache_path, kind):
        self.src_path       = src_path
        self.output_path    = output_path
        self.reference_path = reference_path
        self.cache_path     = cache_path
        self.kind           = kind
        self.handler        = None

    def is_file(self):
        return self.kind == 'file'

    def is_dir(self):
        return self.kind == 'dir'

    def interpret(self):
        return self.handler.process(self)

    def __repr__(self):
        return '<FSNode {}="{}">'.format(self.kind, self.reference_path)


class FileWalker(object):
    def walk(self, src_path, output_path, reference_path = None):
        src_path    = os.path.abspath(src_path)
        output_path = os.path.abspath(output_path)

        reference_path  = reference_path or src_path
        base_cache_path = os.path.join(reference_path, '.papier-cache')
        ref_path_offset = len(reference_path) + 1
        sub_paths       = []

        if os.path.isfile(src_path):
            raise InvalidWalkTargetError('{} must be a directory.'.format(src_path))

        for name in os.listdir(src_path):
            if name[0] == '.':
                continue

            sub_src_path    = os.path.join(src_path, name)
            sub_output_path = os.path.join(output_path, name)
            sub_ref_path    = sub_src_path[ref_path_offset:]
            sub_cache_path  = os.path.join(base_cache_path, hash_cache_name(sub_ref_path))

            sub_paths.append(FSNode(
                sub_src_path,
                sub_output_path,
                sub_ref_path,
                sub_cache_path,
                'dir' if os.path.isdir(sub_src_path) else 'file'
            ))

            if os.path.isdir(sub_src_path):
                sub_paths.extend(self.walk(
                    sub_src_path,
                    output_path,
                    reference_path
                ))

                continue

        sub_paths.sort(key=lambda fs_node: fs_node.reference_path)

        return sub_paths
