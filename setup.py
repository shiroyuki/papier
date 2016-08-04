#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'papier',
    version = '1.0',
    description = 'Simple Static Site Generator',
    author = 'Juti Noppornpitak',
    author_email = 'jnopporn@shiroyuki.com',
    url = 'https://docs.shiroyuki.com/papier/',
    packages = ['papier'],
    scripts = ['bin/papier'],
    package_dir = {'papier': 'papier'},
    package_data = {'papier': ['cli.json', 'template/*']},
    data_files = [
        #('/usr/local/bin', ['bin/papier_mdc'])
    ]
)
