#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_output
----------------------------------

Tests for `inicheck.output` module.
"""

import io
from os.path import isfile
from contextlib import redirect_stdout

from inicheck.output import *
from inicheck.tools import get_user_config
import pytest


@pytest.fixture()
def out_config_ini():
    """
    Fixture for the generated config file path and its clean up
    """
    out_f = 'out_config.ini'
    yield out_f
    if isfile(out_f):
        os.remove(out_f)


def capture_print(function_call, *args, **kwargs):
    """
    Capture the output from a print and return it, designed for functions
    who print as their function and we didn't have a way to check them
    before

    function_call: function to call
    args: arguments to the function

    returns:
        out: string text sent to standard out
    """

    f = io.StringIO()
    with redirect_stdout(f):
        function_call(*args, **kwargs)
    out = f.getvalue()
    return out


class TestOutput:

    @pytest.fixture(scope='function')
    def ucfg(self, full_config_ini):
        """
        Function scoped version of the ucfg fixture so changes can be made to it
        w/o disrupting other tests.
        """
        return get_user_config(full_config_ini, modules="inicheck")

    def test_generate_config_header(self, ucfg, out_config_ini):
        """
        Tests if we generate a config header and dump it to a file
        """
        generate_config(ucfg, out_config_ini, cli=False)

        with open(out_config_ini) as fp:
            lines = fp.readlines()
            fp.close()

        # Assert a header is written
        assert 'Configuration' in lines[1]

    def test_generate_config_sections(self, ucfg, out_config_ini):
        """
            Tests if we generate a config and dump it to a file and all
            the sections are written to the file
            """
        generate_config(ucfg, out_config_ini, cli=False)

        with open(out_config_ini) as fp:
            lines = fp.readlines()
            fp.close()

        key_count = 0

        # Assert all the sections are written
        for k in ucfg.cfg.keys():
            for line in lines:
                if k in line:
                    key_count += 1
                    break

        assert key_count == len(ucfg.cfg.keys())

    @pytest.mark.parametrize('keyword, expected_count', [
        ('\n', 365),  # Test 365 line returns are produced
        ('recipe', 34)  # Test 34 recipes are printed out
    ])
    def test_print_recipe_summary(self, ucfg, keyword, expected_count):
        """
            Checks that the print_summary produces a specific count of a keyword in the output
            """
        lst_recipes = ucfg.mcfg.recipes
        out = capture_print(print_recipe_summary, lst_recipes)
        assert out.count(keyword) == expected_count

    @pytest.mark.parametrize('details_list, keyword, expected_count', [
        (['air_temp'], 'air_temp', 18),  # test details on one section, should match the number of items in the section
        (['precip', 'distribution'], 'distribution', 1),  # test details output on an item
    ])
    def test_print_details(self, ucfg, details_list, keyword, expected_count):
        """
        Tests the function for printting help on the master config
        """
        # Test for a whole section
        out = capture_print(print_details, details_list, ucfg.mcfg.cfg)

        assert out.count(keyword) == expected_count

    def test_non_default_print(self, ucfg):
        """
        Tests if printing the non-defaults is working
        """
        out = capture_print(print_non_defaults, ucfg)

        # Check that we have 27 lines of info for non-defaults
        assert len(out.split('\n')) == 27
