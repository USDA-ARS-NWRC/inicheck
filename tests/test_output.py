#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_output
----------------------------------

Tests for `inicheck.output` module.
"""

import io
import os
from os.path import isfile
import shutil
from collections import OrderedDict
from contextlib import redirect_stdout

from inicheck.output import *
from inicheck.tools import get_user_config
import pytest


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

    out_f = 'out_config.ini'
    if isfile(out_f):
        os.remove(out_f)
    return out


class OutputTester():

    def __init__(self):
        base = os.path.dirname(__file__)
        self.ucfg = get_user_config(os.path.join(base, "test_configs/full_config.ini"),
                                    modules="inicheck")


@pytest.fixture
def output_tester():
    return OutputTester()


def test_generate_config(output_tester):
    """
    Tests if we generate a config to a file
    """
    generate_config(output_tester.ucfg, 'out_config.ini', cli=False)

    with open('out_config.ini') as fp:
        lines = fp.readlines()
        fp.close()

    # Assert a header is written
    assert 'Configuration' in lines[1]

    key_count = 0

    # Assert all the sections are written
    for k in output_tester.ucfg.cfg.keys():
        for l in lines:
            if k in l:
                key_count += 1
                break

    assert key_count == len(output_tester.ucfg.cfg.keys())


def test_print_recipe_summary(output_tester):
    """
    Checks that the output produces 366 lines of recipe info
    """
    lst_recipes = output_tester.ucfg.mcfg.recipes
    out = capture_print(print_recipe_summary, lst_recipes)

    assert len(out.split('\n')) == 366
    assert out.count('recipe') == 34


def test_print_details(output_tester):
    """
    Tests the function for printting help on the master config
    """
    # Test for a whole section
    details = ['air_temp']
    out = capture_print(print_details, details, output_tester.ucfg.mcfg.cfg)

    assert out.count('air_temp') == len(
        output_tester.ucfg.mcfg.cfg[details[0]])

    # test for a section and item
    details = ['precip', 'distribution']
    out = capture_print(print_details, details, output_tester.ucfg.mcfg.cfg)
    assert out.count('precip ') == 1


def test_non_default_print(output_tester):
    """
    Tests if printing the non-defaults is working
    """
    out = capture_print(print_non_defaults, output_tester.ucfg)

    # Check that we have 27 lines of info for non-defaults
    assert len(out.split('\n')) == 27
