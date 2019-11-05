#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_utilities
----------------------------------

Tests for `inicheck.utilities` module.
"""

import unittest
from inicheck.utilities import *
from inicheck.tools import get_user_config

class TestUtilities(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        base = os.path.dirname(__file__)
        self.ucfg = get_user_config(os.path.join(base,
                                    "test_configs/full_config.ini"),
                                    modules="inicheck")

    def test_remove_comments(self):
        """
        Test our remove comments code
        """
        values = {"test":"test#comment",
                  "test":"test;comment"}
        for k,v in values.items():
            out = remove_comment(v)

            assert k==out

    def test_mk_lst(self):
        """
        Test all the ways we use mk_lst

        Case A: Convert non-list to list and keep lists as lists
        Case B: Convert lists to single value and keep singles as single
        Case C: Don't undo lists that are acutal lists

        """

        # Case A
        for v in ['test',['test']]:
            out = mk_lst(v,unlst=False)
            assert type(out) == list

        # Case B
        for v in ['test',['test']]:
            out = mk_lst(v,unlst=True)
            assert type(out) != list

        # Case C
        for v in [['test','test2']]:
            out = mk_lst(v,unlst=True)
            assert type(out) == list

    def test_remove_chars(self):
        """
        Test if we can remove the problematic chars
        """
        out = remove_chars("\t\n my_test\t","\t\n ")
        assert '\n' not in out
        assert '\t' not in out
        assert ' ' not in out

    def test_find_options_in_recipes(self):
        """
        Tests utilites.find_options_in_recipes which extracts choices being
        nade by looking at the recipes and determining which work on each other
        such that they don't exist at the same time. Used in the inimake cli
        """
        mcfg = self.ucfg.mcfg
        choices = find_options_in_recipes(mcfg.recipes, mcfg.cfg.keys(),
                                                    "remove_section")

        # Currently there is 3 sections that are set as optional in the recipes
        for opt in ['gridded','mysql','csv']:
            self.assertTrue(opt in choices[0])

    def test_get_relative_to_cfg(self):
        """
        Tests that all paths in a config can be made relative to the config
        """
        p = get_relative_to_cfg(__file__, self.ucfg.filename)
        assert p == '../test_utilities.py'

    def test_is_kw_matched(self):
        """
        Tests utilities.is_kw_matched which is used to match items in
        a config items list
        """

        # Finds test in string
        assert is_kw_matched("tests_my_kw", ['tests'])

        # Finds all three in the string
        assert is_kw_matched("tests_my_kw", ['tests','my','kw'], kw_count=3)

        # Finds all three in the string
        assert is_kw_matched("te_my_kw", ['tests','my','kw'], kw_count=1)

        # No match at all
        assert not is_kw_matched("te_ym_k", ['tests','my','kw'])

    def test_get_kw_match(self):
        """
        Tests utilities.get_kw_match which looks through a list of strings with
        potential matches of the keywords
        """

        test_lst = ['test_my_str','test_my_float','test_my_flowt']

        # should find the first one only
        t = get_kw_match(test_lst, ['test'], kw_count=1)
        assert t == 'test_my_str'

        t = get_kw_match(test_lst, ['test','float'], kw_count=2)
        assert t == 'test_my_float'

    def test_is_valid(self):
        """
        Tests utilities.is_valid which is grossly used in the checkers that are
        simple enough to pass a function to.
        """

        # Check to can handle a normal scenario
        result = is_valid('10.0', float, 'float', allow_none=False)
        assert result[1] == None
        assert result[0] == True

        # Test the handling of Nones
        for b in [False, True]:
            result = is_valid(None, float, 'float', allow_none=b)[0]
            print(result)
            assert b == result

        # Check to see that we return an error message
        result = is_valid(None, float, 'float', allow_none=False)[1]
        assert 'Value' in result
        assert 'None' in result

        # Check to see that we return an error message
        result = is_valid('abc', float, 'float', allow_none=False)[1]
        assert 'float' in result
        assert 'str' in result


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
