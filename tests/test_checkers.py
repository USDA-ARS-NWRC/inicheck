#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_checkers
----------------------------------

Tests for `inicheck.checkers` module.
"""

import unittest
from inicheck.checkers import *


class TestCheckers(unittest.TestCase):

    def test_datetime(self):
        """
        Test we see datetime as datetime
        """

        # Confirm we these values are valid
        for v in ['2018-01-10 10:10','10-10-2018', "October 10 2018"]:
            b = CheckDatetime(value = v, config = None)
            assert b.is_valid()[0]

        # Confirm these are not valid
        for v in ['Not-a-date','Wednesday 5th']:
            b = CheckDatetime(value = v, config = None)
            assert not b.is_valid()[0]

    def test_float(self):
        """
        Test we see floats as floats
        """

        # Confirm we these values are valid
        for v in [-1.5,'2.5']:
            b = CheckFloat(value = v, config = None)
            assert b.is_valid()[0]

        # Confirm these are not valid
        for v in ['tough']:
            b = CheckFloat(value = v, config = None)
            assert not b.is_valid()[0]

    def test_int(self):
        """
        Test we see int as ints and not floats
        """

        # Confirm we these values are valid
        for v in [10, '2',1.0]:
            b = CheckInt(value = v, config = None)
            assert b.is_valid()[0]

        # Confirm these are not valid
        for v in ['tough','1.5','']:
            b = CheckInt(value = v, config = None)
            assert not b.is_valid()[0]

    def test_bool(self):
        """
        Test we see booleans as booleans
        """

        # Confirm we these values are valid
        for v in [True,False,'true','FALSE','yes','y','no','n']:
            b = CheckBool(value = v, config = None)
            assert b.is_valid()[0]

        # Confirm these are not valid
        for v in ['Fasle','treu']:
            b = CheckBool(value = v, config = None)
            assert not b.is_valid()[0]

    def test_string(self):
        """
        Test we see strings as strings
        """

        # Confirm we these values are valid
        for v in ['test']:
            b = CheckString(value = v, config = None)
            assert b.is_valid()[0]


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
