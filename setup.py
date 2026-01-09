#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Guation"

from setuptools import setup, find_packages
import pathlib

VERSION = None

exec(pathlib.Path(__file__).parent.joinpath("edgeone_update/version.py").read_text())

setup(
    name='edgeone_update',
    version=VERSION,
    author="Guation",
    packages=['edgeone_update'],
    entry_points={
        'console_scripts': [
            'edgeone_update = edgeone_update.edgeone_update:main'
        ]
    },
    include_package_data=True,
    install_requires=[
        "urllib3==2.2.3",
    ],
    project_urls={
        "url": "https://github.com/Guation/EdgeOneUpdate",
    }
)