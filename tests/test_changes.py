#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_changes
----------------------------------

Tests for `inicheck.changes` module.
"""

import unittest
from inicheck.changes import *
from inicheck.config import UserConfig, MasterConfig

class TestChanges(unittest.TestCase):

    def test_valid_syntax(self):
        """
        Test we can detect valid syntax
        """
        mcfg = MasterConfig(path = ['./tests/test_configs/CoreConfig.ini',
                                         './tests/test_configs/recipes.ini'])
        try:
            c = ChangeLog(filename='./tests/test_configs/change_log.ini', mcfg=mcfg)
            assert True
        except:
            assert False

        changes=["topo/test/-> nonexistent"]
        self.assertRaises(ValueError, ChangeLog, changes, mcfg)



if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
