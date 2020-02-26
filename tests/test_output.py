#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_output
----------------------------------

Tests for `inicheck.output` module.
"""

import io
import os
import shutil
import unittest
from collections import OrderedDict
from contextlib import redirect_stdout

from inicheck.output import *
from inicheck.tools import get_user_config


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


class TestOutput(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        base = os.path.dirname(__file__)
        self.ucfg = get_user_config(os.path.join(base, "test_configs/full_config.ini"),
                                    modules="inicheck")

    @classmethod
    def tearDownClass(self):
        """
        Delete any files
        """
        os.remove('out_config.ini')

    def test_generate_config(self):
        """
        Tests if we generate a config to a file
        """
        generate_config(self.ucfg, 'out_config.ini', cli=False)

        with open('out_config.ini') as fp:
            lines = fp.readlines()
            fp.close()

        # Assert a header is written
        assert 'Configuration' in lines[1]

        key_count = 0

        # Assert all the sections are written
        for k in self.ucfg.cfg.keys():
            for l in lines:
                if k in l:
                    key_count += 1
                    break

        assert key_count == len(self.ucfg.cfg.keys())

    def test_print_recipe_summary(self):
        """
        Checks that the output produces 366 lines of recipe info
        """
        lst_recipes = self.ucfg.mcfg.recipes
        out = capture_print(print_recipe_summary, lst_recipes)
        assert len(out.split('\n')) == 366
        assert out.count('recipe') == 34

    def test_print_details(self):
        """
        Tests the function for printting help on the master config
        """
        # Test for a whole section
        details = ['air_temp']
        out = capture_print(print_details, details, self.ucfg.mcfg.cfg)

        assert out.count('air_temp') == len(self.ucfg.mcfg.cfg[details[0]])

        # test for a section and item
        details = ['precip', 'distribution']
        out = capture_print(print_details, details, self.ucfg.mcfg.cfg)
        assert out.count('precip ') == 1

    def test_non_default_print(self):
        """
        Tests if printing the non-defaults is working
        """
        out = capture_print(print_non_defaults, self.ucfg)

        # Check that we have 27 lines of info for non-defaults
        assert len(out.split('\n')) == 27


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
