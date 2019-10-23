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
import inicheck

class TestCheckers(unittest.TestCase):

    def run_a_checker(self, valids, invalids, checker, section='basic',
                                                       item='item',
                                                       extra_config={}):
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
            extra_config: Pass in contextual config info to test more complicated checkers. E.g. ordered datetime pair.
        """

        cfg = self.ucfg.cfg
        cfg.update({section:{item:" "}})

        # Added info for testing e.g. ordered datetime pair
        if extra_config:
            cfg.update(extra_config)

        for z,values in enumerate([valids, invalids]):
            for v in values:

                cfg[section][item] = v
                b = checker(config=self.ucfg, section=section, item=item)
                msgs = b.check()

                if len([True for m in msgs if m==None]) == len(msgs):
                    valid = True
                else:
                    valid = False

                # Expected valid
                if z == 0:
                    assert valid
                else:
                    assert not valid

    @classmethod
    def setUpClass(self):
        """
        Create some key structures for testing
        """
        tests_p = os.path.join(os.path.dirname(inicheck.__file__),'../tests')
        self.mcfg = MasterConfig(path=os.path.join(tests_p,
                                    'test_configs/master.ini'))

        self.ucfg = UserConfig(os.path.join(tests_p,"test_configs/base_cfg.ini"),
                               mcfg=self.mcfg)


    def test_string(self):
        """
        Test we see strings as strings
        """

        # Confirm we these values are valid
        valids = ['test']
        self.run_a_checker(valids, [], CheckString,  item='username')

        # Confirm that casting a string with uppers will auto produce lowers
        self.ucfg.cfg['basic']['username'] = 'Test'

        b = CheckString(config=self.ucfg, section='basic', item='username')
        result = b.cast()
        assert result == 'test'

    def test_bool(self):
        """
        Test we see booleans as booleans
        """

        # Confirm we these values are valid
        valids = [True, False, 'true', 'FALSE', 'yes', 'y', 'no', 'n']
        invalids = ['Fasle', 'treu']
        self.run_a_checker(valids, invalids, CheckBool, item='debug')


    def test_float(self):
        """
        Test we see floats as floats
        """
        valids = [-1.5, '2.5']
        invalids =  ['tough']

        self.run_a_checker(valids, invalids, CheckFloat, item='time_out')


    def test_int(self):
        """
        Test we see int as ints and not floats
        """

        # Confirm we these values are valid
        valids = [10, '2', 1.0]
        invalids = ['tough', '1.5', '']
        self.run_a_checker(valids, invalids, CheckInt, item='num_users')


    def test_datetime(self):
        """
        Test we see datetime as datetime
        """

        valids = ['2018-01-10 10:10','10-10-2018', "October 10 2018"]
        invalids = ['Not-a-date', 'Wednesday 5th']
        self.run_a_checker(valids, invalids, CheckDatetime, item='start_date')

    def test_list(self):
        """
        Test our listing methods using lists of dates.
        """

        valids = ['10-10-2019',['10-10-2019'],['10-10-2019','11-10-2019']]
        self.run_a_checker(valids, [], CheckDatetime, item='epochs')

        # # We have a list in the config when we don't want one
        # self.ucfg.cfg['section']['item'] = ["test", "test2"]
        # invalids = ['test']
        # self.run_a_checker([], invalids, CheckFilename,  is_list=False)

    def test_directory(self):
        """
        Tests the base class for path based checkers
        """

        valids = ["./"]
        invalids = ['./somecrazy_location!/']
        self.run_a_checker(valids, invalids, CheckDirectory, item='tmp')

    def test_filename(self):
        """
        Tests the base class for path based checkers
        """
        # Remember paths are relative to the config
        valids = ["../test_checkers.py"]
        invalids = ['dumbfilename']
        self.run_a_checker(valids, invalids, CheckFilename, item='log')

    def test_url(self):
        """
        Test our url checking.
        """
        valids = ["https://google.com"]
        invalids = ["https://micah_subnaught_is_awesome.com"]
        self.run_a_checker(valids, invalids, CheckURL,
                                                 item='favorite_web_site')

    def test_datetime_ordered_pairs(self):
        """
        Tests the ordered datetime pair checker which looks for <keyword>_start
        <keyword>_end pairs and confirms they occurs in the correct order.

        """
        valids = ["1-02-2019"]
        invalids = ["01-01-2018"]
        acfg = {'basic':{'start_date':'1-1-2019'}}
        self.run_a_checker(valids, invalids, CheckDatetimeOrderedPair,
                                             item="end_date",
                                             extra_config=acfg)
    def test_bounds(self):
        """
        MasterConfig options now have max and min values to constrain continuous
        types. This tests whether that works
        """

        self.run_a_checker([1.0, 0.0, '0.5'], [1.1,-1.0, '10'], CheckFloat,
                                                                item='fraction')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
