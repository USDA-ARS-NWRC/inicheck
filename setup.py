#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('docs/history.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as req_file:
    requirements = req_file.read()


setup_requirements = [
    'pytest-runner',
    # TODO(micahjohnson150): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='inicheck',
    version='0.3.5',
    description="inicheck is an high level configuration file checker enabling developers tight control over their users configuration files",
    long_description=readme + '\n\n' + history,
    author="Micah Johnson",
    author_email='micah.johnson150@gmail.com',
    url='https://github.com/micahjohnson150/inicheck',
    packages=find_packages(include=['inicheck']),
    entry_points={
        'console_scripts': [
            'inicheck=inicheck.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='inicheck',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
