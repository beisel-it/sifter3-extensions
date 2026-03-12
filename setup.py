#!/usr/bin/env python

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sifter3-extensions",
    version="0.0.1",
    author="Manfred Kaiser",
    author_email="python-sifter@logfile.at",
    url="https://github.com/python-sifter/sifter3-extensions",
    license="BSD",
    description='Unofficial extensions for Sifter 3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="sieve email filter parser",
    project_urls={
        'Source': 'https://github.com/python-sifter/sifter3-extensions',
        'Tracker': 'https://github.com/python-sifter/sifter3-extensions/issues',
    },
    python_requires='>= 3.6',
    install_requires=[
        'sifter3'
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email :: Filters",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=("tests",)),
    entry_points={
        'sifter_extensions': [
            # sifter commands
            'pipe = sifter_extensions.commands.pipe:CommandPipe',
            'rewrite = sifter_extensions.commands.rewrite:CommandRewrite',
            'envelope = sifter_extensions.tests.envelope:TestEnvelope',
            'subaddress = sifter_extensions.tests.subaddress:SubaddressExtension',
        ]
    }
)
