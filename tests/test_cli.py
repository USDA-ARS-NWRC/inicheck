#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
from os.path import abspath, dirname, join

from inicheck.cli import current_version, inicheck_main, inidiff_main

from .test_output import capture_print
import pytest


class CLITester():
    def __init__(self):
        self.test_base = abspath(join(dirname(__file__), 'test_configs'))
        self.master = [
            join(self.test_base, 'recipes.ini'),
            join(self.test_base, 'CoreConfig.ini')
        ]
        self.full_config = join(self.test_base, 'full_config.ini')

    def capture_with_params(self, **kwargs):
        return str(
            capture_print(
                inicheck_main,
                config_file=self.full_config,
                master=self.master,
                **kwargs
            )
        )


@pytest.fixture
def cli_tester():
    cls = CLITester()

    return cls


def test_basic_inicheck_cli(cli_tester):
    """ Test simplest usage of CLI """

    s = cli_tester.capture_with_params()

    assert s.count("File does not exist") >= 9
    assert s.count("Not a registered option") >= 20


def test_inicheck_recipe_use(cli_tester):
    """ Test recipe output """

    s = cli_tester.capture_with_params(show_recipes=True)

    assert s.count("_recipe") == 20


def test_inicheck_non_defaults_use(cli_tester):
    """ Test non-default output"""

    s = cli_tester.capture_with_params(show_non_defaults=True)

    assert s.count("wind") >= 7
    assert s.count("albedo") >= 3


def test_inicheck_details_use(cli_tester):
    """ Test details output """

    s = cli_tester.capture_with_params(details=['topo'])

    assert s.count("topo") >= 4

    s = cli_tester.capture_with_params(details=['topo', 'basin_lat'])

    assert s.count("topo") >= 1


def test_inicheck_changelog_use(cli_tester):
    """ Test changelog detection output """

    old_cfg = join(cli_tester.test_base, 'old_smrf_config.ini')

    s = str(capture_print(
        inicheck_main,
        config_file=old_cfg,
        master=cli_tester.master,
        changelog_file=join(cli_tester.test_base, 'changelog.ini')
    ))
    assert s.count("topo") == 7
    assert s.count("wind") == 12
    assert s.count("stations") == 5
    assert s.count("solar") == 9
    assert s.count("precip") == 18
    assert s.count("air_temp") == 9
    assert s.count("albedo") == 30


def test_inidiff(cli_tester):
    """
    Tests if the inidiff script is producing the same information
    """

    configs = [
        join(cli_tester.test_base, 'full_config.ini'),
        join(cli_tester.test_base, 'base_cfg.ini')
    ]

    s = capture_print(inidiff_main, configs, master=cli_tester.master)

    mismatches = s.split("config mismatches:")[-1].strip()
    assert '117' in mismatches


def test_version(cli_tester):
    exception_message = re.search(
        '(exception|error)', str(current_version()), re.IGNORECASE
    )
    assert exception_message is None
