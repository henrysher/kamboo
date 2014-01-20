#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

import kamboo


requires = ['kotocore']

if sys.version_info[:2] == (2, 6):
    # For python2.6 we have to require argparse since it
    # was not in stdlib until 2.7.
    requires.append('argparse>=1.1')


setup_options = dict(
    name='kamboo',
    version=kamboo.__version__,
    description='To build and distribute AMI images' +
    ' or EC2 snapshots across accounts and regions',
    long_description=open('README.rst').read(),
    author='Henry Huang',
    author_email='henry.s.huang@gmail.com',
    url='https://github.com/henrysher/kamboo',
    scripts=[],
    packages=find_packages('.', exclude=['tests*']),
    package_dir={'kamboo': 'kamboo'},
    package_data={'kamboo': []},
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ),
)

setup(**setup_options)
