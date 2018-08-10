#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_utilities
----------------------------------

Tests for `inicheck.utilities` module.
"""

import unittest
from inicheck.utilities import *


class TesUtilities(unittest.TestCase):

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


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
