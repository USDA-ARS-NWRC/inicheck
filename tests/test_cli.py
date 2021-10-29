#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

from os.path import join

from inicheck.cli import current_version, inicheck_main, inidiff_main
from .test_output import capture_print
import pytest


class TestInicheckCLI:

    def capture_with_params(self, config_ini, master_ini, **kwargs):
        return str(
            capture_print(
                inicheck_main,
                config_file=config_ini,
                master=master_ini,
                **kwargs
            )
        )

    @pytest.mark.parametrize('flags_dict, countable_str, expected_str_count', [
        ({}, "File does not exist", 9),
        ({}, "Not a registered option", 23),
        ({"show_recipes": True}, "_recipe", 20),
        ({"show_non_defaults": True}, "wind", 35),
        ({"show_non_defaults": True}, "albedo", 3),
        ({"details": ['topo']}, "topo", 6),
        ({"details": ['topo', 'basin_lat']}, "basin", 3),
    ])
    def test_cli_output(self, full_config_ini, master_ini, flags_dict, countable_str, expected_str_count):
        """
        Collec the console output from the cli and count certain keywords to check if the result is as expected.
        Args:
            flags_dict: Kwargs to pass to the cli
            countable_str: String to search for in the output and count its occurances
            expected_str_count: Integer of expected occurances of the countable_str
        """
        s = self.capture_with_params(full_config_ini, master_ini, **flags_dict)
        assert s.count(countable_str) == expected_str_count

    @pytest.mark.parametrize("countable_str, expected_str_count", [
        ("topo", 7),
        ('wind', 12),
        ('solar', 9),
        ('precip', 18),
        ('air_temp', 9),
        ('albedo', 30)
    ])
    def test_inicheck_changelog_use(self, old_smrf_config_ini, master_ini, changelog_ini, countable_str,
                                    expected_str_count):
        """ Test changelog detection output """
        s = str(capture_print(
            inicheck_main,
            config_file=old_smrf_config_ini,
            master=master_ini,
            changelog_file=changelog_ini
        ))
        assert s.count(countable_str) == expected_str_count


class TestInidiffCLI():

    def test_inidiff(self, full_config_ini, base_config_ini, master_ini):
        """
        Tests if the inidiff script is producing the same information
        """
        s = capture_print(inidiff_main, [full_config_ini, base_config_ini], master=master_ini)

        mismatches = s.split("config mismatches:")[-1].strip()
        assert '117' in mismatches


def test_version():
    exception_message = re.search(
        '(exception|error)', str(current_version()), re.IGNORECASE
    )
    assert exception_message is None
