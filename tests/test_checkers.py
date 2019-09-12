#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_checkers
----------------------------------

Tests for `inicheck.checkers` module.
"""

import unittest
from inicheck.checkers import *
from inicheck.config import UserConfig, MasterConfig

class TestCheckers(unittest.TestCase):

    def run_a_checker(self, valids, invalids, checker, ucfg=None, is_list=False,
                                                                  section=None,
                                                                  item=None):
        """
        Runs a loop over all the valids and applies the checker and asserts
        theyre true. Same thing is done for the invalids
        Args:
            valids: List of valid entries to check
            invalids: List of invalid entries to check
            checker: any class in inicheck.checkers
            ucfg: inicheck.config.UserConfig instance (optional)
            is_list: is it expected to be a list?
            section: section name the item being checked is occurring
            item: Item name in the config
        """
        for v in valids:
            b = checker(value=v, config=ucfg, is_list=is_list, section=section,
                                                               item=item)
            valid, msg = b.is_valid()
            if not valid:
                print(msg)
            assert valid

        for v in invalids:
            b = checker(value=v, config=ucfg, is_list=is_list, section=section,
                                                               item=item)
            valid, msg = b.is_valid()
            if valid:
                print(msg)

            assert not valid

    def test_datetime(self):
        """
        Test we see datetime as datetime
        """
        valids = ['2018-01-10 10:10','10-10-2018', "October 10 2018"]
        invalids = ['Not-a-date', 'Wednesday 5th']
        self.run_a_checker(valids, invalids, CheckDatetime)

    def test_float(self):
        """
        Test we see floats as floats
        """

        valids = [-1.5, '2.5']
        invalids =  ['tough']
        self.run_a_checker(valids, invalids, CheckFloat)

    def test_int(self):
        """
        Test we see int as ints and not floats
        """

        # Confirm we these values are valid
        valids = [10, '2', 1.0]
        invalids = ['tough', '1.5', '']
        self.run_a_checker(valids, invalids, CheckInt, ucfg=None)


    def test_bool(self):
        """
        Test we see booleans as booleans
        """

        # Confirm we these values are valid
        valids = [True, False, 'true', 'FALSE', 'yes', 'y', 'no', 'n']
        invalids = ['Fasle', 'treu']
        self.run_a_checker(valids, invalids, CheckBool)


    def test_string(self):
        """
        Test we see strings as strings
        """

        # Confirm we these values are valid
        valids = ['test']
        self.run_a_checker(valids, [], CheckString)

    def test_list(self):
        """
        Test our listing methods.

        Case a. The user wants a list and recieves a single item. The result
        should be a list of length one.

        Case B. The user enters a list of lenght > 1 and requests it not to be
        as list, the result should be the value is invalid

        Case C. The user enters a single value and requests it not to be
        as list, the result should be the value is valid and not type list
        """

        valids = ["test"]
        invalids = [["test", "test2"]]
        self.run_a_checker(valids, [], CheckString,  is_list=True)
        self.run_a_checker([], invalids, CheckString,  is_list=False)

    def test_directory(self):
        """
        Tests the base class for path based checkers
        """

        ucfg = UserConfig("./tests/test_configs/base_cfg.ini")
        valids = ["../"]
        invalids = ['./somecrazy_location!/']
        self.run_a_checker(valids, invalids, CheckDirectory, ucfg=ucfg)

    def test_filename(self):
        """
        Tests the base class for path based checkers
        """

        ucfg = UserConfig("./tests/test_configs/base_cfg.ini")
        valids = ["../test_entries.py"]
        self.run_a_checker(valids, [], CheckFilename, ucfg=ucfg)

    def test_url(self):
        """
        Test our url checking.
        """
        valids = ["https://google.com"]
        invalids = ["https://micah_subnaught_is_awesome.com"]
        self.run_a_checker(valids, [], CheckURL, is_list=True)

    def test_datetime_ordered_pairs(self):
        """
        Tests the ordered datetime pair checker which looks for <keyword>_start
        <keyword>_end pairs and confirms they occurs in the correct order.

        """
        mcfg = MasterConfig(path='./tests/test_configs/CoreConfig.ini')
        ucfg = UserConfig(None, mcfg=mcfg)

        ucfg.raw_cfg = {"topo":{"test_end":"10-01-2019"}}
        ucfg.apply_recipes()
        valids = ["9-01-2019"]
        invalids = ["10-02-2019"]
        self.run_a_checker(valids, invalids, CheckDatetimeOrderedPair,
                                             section="topo",
                                             item="test_start",
                                             ucfg=ucfg)
    def test_bounds_checking(self):
        """
        MasterConfig options now have max and min values to constrain continuous
        types. This tests whether that works
        """
        mcfg = MasterConfig(path='./tests/test_configs/CoreConfig.ini')
        ucfg = UserConfig(None, mcfg=mcfg)
        s = "air_temp"
        i = "dk_nthreads"

        ucfg.raw_cfg = {s:{i:None}}

        ucfg.apply_recipes()
        valids = [0, 5, 10]
        invalids = [-1,11]
        for v in valids:
            ucfg.cfg[s][i] = v
            self.run_a_checker([v], [], CheckInt, ucfg=ucfg, section=s, item=i)

        for v in invalids:
            ucfg.cfg[s][i] = v
            self.run_a_checker([], [v], CheckInt, ucfg=ucfg, section=s, item=i)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
