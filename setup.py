#!/usr/bin/env python3
# More info: https://github.com/navdeep-G/setup.py
import os

from setuptools import setup
from sys import version_info

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'launcher', '__version__.py'), 'r') as f:
    exec(f.read(), about)

with open('README.md', 'r') as f:
    readme = f.read()

ver_spec_install = []
if version_info.minor >= 12:
    ver_spec_install = ['setuptools']

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    install_requires=["bs4", "platformdirs", "py7zr", "unrar", "requests", 'tenacity', 'tqdm'] + ver_spec_install,
    packages=['launcher', 'launcher.commands', 'launcher.mods', 'launcher.mods.downloader', 'launcher.mods.installer'],
    entry_points={
        'console_scripts': [
            'gamma-launcher = launcher.cli:main',
        ],
    },
    python_requires='>=3.10.0',
    license=about['__license__'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10'
        'Programming Language :: Python :: 3.11'
        'Programming Language :: Python :: 3.12'
    ]
)
