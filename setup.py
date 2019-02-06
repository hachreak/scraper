# -*- coding: utf-8 -*-
#
# This file is part of scraper.
# Copyright 2018-2019 Leonardo Rossi <leonardo.rossi@studenti.unipr.it>.
#
# pysenslog is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pysenslog is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pysenslog.  If not, see <http://www.gnu.org/licenses/>.

"""setuptools."""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scraper',
    version='0.1.0',
    description='Social Scraping!',
    url='https://github.com/hachreak/scraper',
    author='Leonardo Rossi',
    author_email='leonardo.rossi@studenti.unipr.it',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        #  'Programming Language :: Python :: 2',
        #  'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        #  'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='scraper',
    packages=find_packages(),
    install_requires=[
        'selenium>=3.141.0',
        'beautifulsoup4>=4.7.1',
        'requests>=2.21.0',
        'click>=7.0',
        'lxml>=4.3.0',
        'selenium-wire>=1.0.0',
        'pyenchant>=2.0.0',
    ],
    #  extras_require={  # Optional
    #  },
    entry_points='''
        [console_scripts]
        scraper-cli=scraper.cli.main:cli
    ''',
)
