#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='brandelion',
    version='0.1.7',
    description='Social media brand analytics',
    long_description=readme + '\n\n' + history,
    author='Aron Culotta',
    author_email='aronwc@gmail.com',
    url='https://github.com/tapilab/brandelion',
    packages=[
        'brandelion',
        'brandelion/cli',
    ],
    package_dir={'brandelion':
                 'brandelion'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='brandelion',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'brandelion = brandelion.cli.brandelion:main',
            'brandelion-collect = brandelion.cli.collect:main',
            'brandelion-analyze = brandelion.cli.analyze:main',
            'brandelion-diagnose = brandelion.cli.diagnose:main',
            'brandelion-report = brandelion.cli.report:main',
        ],
    },
    test_suite='tests',
    tests_require=test_requirements
)
