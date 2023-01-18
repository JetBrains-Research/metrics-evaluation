#!/usr/bin/env python3

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
A setuptools based setup module.

See:
- https://packaging.python.org/en/latest/distributing.html
- https://github.com/pypa/sampleproject

To install:

1. Setup pypi by creating ~/.pypirc

        [distutils]
        index-servers =
          pypi
          pypitest

        [pypi]
        username=
        password=

        [pypitest]
        username=
        password=

2. Create the dist

   python3 setup.py sdist bdist_wheel

3. Push

   twine upload dist/*
"""

import os
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)


def get_version():
    """
    Reads the version from sacrebleu_methods's __init__.py file.
    We can't import the module because required modules may not
    yet be installed.
    """
    VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')
    init = open(os.path.join(ROOT, 'sacrebleu_methods', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


def get_description():
    DESCRIPTION_RE = re.compile(r'''__description__ = ['"](.*)['"]''')
    init = open(os.path.join(ROOT, 'sacrebleu_methods', '__init__.py')).read()
    return DESCRIPTION_RE.search(init).group(1)


def get_long_description():
    with open('README.md') as f:
        long_description = f.read()

    with open('CHANGELOG.md') as f:
        release_notes = f.read()

    # Plug release notes into the long description
    long_description = long_description.replace(
        '# Release Notes\n\nPlease see [CHANGELOG.md](CHANGELOG.md) for release notes.',
        release_notes)

    return long_description


setup(
    name='sacrebleu_methods',
    # Versions should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=get_version(),
    description=get_description(),
    long_description_content_type='text/markdown',
    long_description=get_long_description(),
    url='https://github.com/mjpost/sacrebleu',
    author='Matt Post',
    author_email='post@cs.jhu.edu',
    maintainer_email='post@cs.jhu.edu',
    license='Apache License 2.0',
    # We don't support Python < 3.6 anymore
    python_requires='>=3.6',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # List operating systems
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
    ],

    # What does your project relate to?
    keywords=['machine translation, evaluation, NLP, natural language processing, computational linguistics'],

    # Which packages to deploy (currently sacrebleu_methods, sacrebleu_methods.matrics and sacrebleu_methods.tokenizers)?
    packages=find_packages(),

    # Mark sacrebleu_methods (and recursively all its sub-packages) as supporting mypy type hints (see PEP 561).
    package_data={"sacrebleu_methods": ["py.typed"]},

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['portalocker', 'regex', 'tabulate>=0.8.9', 'numpy>=1.17', 'colorama'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={'ja': ['mecab-python3==1.0.3', 'ipadic>=1.0,<2.0']},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'sacrebleu_methods = sacrebleu_methods.sacrebleu_methods:main',
        ],
    },
)
