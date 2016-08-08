#!/usr/bin/env python
from distutils.core import setup
import os

base_path = 'papier'

def _list_files(path):
    subpaths    = []
    actual_path = os.path.join(base_path, path)

    for filename in os.listdir(actual_path):
        next_path        = os.path.join(path, filename)
        actual_next_path = os.path.join(actual_path, filename)

        subpaths.append(next_path)

        if os.path.isfile(actual_next_path):
            continue

        subpaths.extend(_list_files(next_path))

    return subpaths

static_files = ['cli.json', 'containers.xml', ]
static_files.extend(_list_files('template'))
static_files.sort()

print('\n'.join(static_files))

setup(
    name         = 'papier',
    version      = '1.0',
    description  = 'Simple Static Site Generator',
    author       = 'Juti Noppornpitak',
    author_email = 'jnopporn@shiroyuki.com',
    url          = 'https://docs.shiroyuki.com/papier/',
    packages     = ['papier'],
    scripts      = ['bin/papier'],
    package_dir  = {'papier': 'papier'},
    package_data = {'papier': static_files},
    data_files   = [
        #('/usr/local/bin', ['bin/papier_mdc'])
    ]
)
