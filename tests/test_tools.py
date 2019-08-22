#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_recipe
----------------------------------

Tests for `inicheck.Tools` module.
"""

import unittest
from inicheck.tools import *
from collections import OrderedDict

class TestTools(unittest.TestCase):
    def test_get_checkers(self):
        """
        Tests the get_checkers func in tools
        """
        checkers = get_checkers().keys()

        valids = ['bool', 'criticaldirectory', 'criticalfilename', 'datetime',
                  'datetimeorderedpair', 'directory', 'filename', 'float',
                  'int', 'path', 'string', 'url']

        for v in valids:
            assert v in checkers

        valids = ["type", "generic"]
        checkers = get_checkers(ignore=[]).keys()
        for v in valids:
                assert v in checkers

    def test_check_config(self):
        """
        Tests the check_config func in tools
        """
        ucfg = get_user_config("./tests/test_configs/base_cfg.ini",
                                                            modules="inicheck")

        warnings, errors = check_config(ucfg)
        assert not warnings
        assert not errors

    def test_cast_all_variables(self):
        """
        Tests the cast_all_variables func in tools
        """
        ucfg = get_user_config("./tests/test_configs/base_cfg.ini",
                                                            modules="inicheck")
        ucfg.cfg['topo']['test_start'] = "10-1-2019"
        ucfg.cfg['air_temp']['dk_nthreads'] = "1.0"
        ucfg.cfg['air_temp']['detrend'] = "true"

        ucfg = cast_all_variables(ucfg, ucfg.mcfg, checking_later=False)
        results = ['timestamp','int','bool']
        valids = [ucfg.cfg['topo']['test_start'],
                  ucfg.cfg['air_temp']['dk_nthreads'],
                  ucfg.cfg['air_temp']['detrend']]

        for i,v in enumerate(valids):
            assert results[i] in type(v).__name__.lower()


    def test_get_user_config(self):
        """
        Tests the get_user_config func in tools
        """

        # Check that we raise an error when they don't provide everything
        with self.assertRaises(IOError):
            ucfg = get_user_config("./tests/test_configs/base_cfg.ini")

        # Check that we can handle multiple files
        ucfg = get_user_config("./tests/test_configs/base_cfg.ini",
                            master_files=['./tests/test_configs/CoreConfig.ini',
                                          './tests/test_configs/recipes.ini'])
        assert ucfg.cfg['air_temp']['slope'] == 1


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
