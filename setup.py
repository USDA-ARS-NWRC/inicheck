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

setup(
    name='inicheck',
    description="inicheck is an high level configuration file checker "
                "enabling developers tight control over their users "
                "configuration files",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    author="USDA ARS NWRC",
    author_email='snow@ars.usda.gov',
    url='https://github.com/USDA-ARS-NWRC/inicheck',
    project_urls={
        'Documentation': 'https://inicheck.readthedocs.io',
    },
    packages=find_packages(include=['inicheck']),
    entry_points={
        'console_scripts': [
            'inicheck=inicheck.cli:main',
            'inidiff=inicheck.cli:inidiff',
            'inimake=inicheck.cli:inimake',
            'inichangefind=inicheck.cli:detect_file_changes'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    zip_safe=False,
    keywords='inicheck',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
        'Programming Language :: Python :: 3.11'
    ],
    use_scm_version={
        'local_scheme': 'node-and-date',
    },
    setup_requires=[
        'setuptools_scm'
    ],
    test_suite='tests',
)
