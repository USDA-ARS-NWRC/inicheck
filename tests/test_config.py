#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_config
----------------------------------

Tests for `inicheck.config` module.
"""

import unittest
from inicheck.config import *


class TestUserConfig(unittest.TestCase):
    pass

class TestMasterConfig(unittest.TestCase):
    def setUp(self):
        self.mcfg = MasterConfig(path = './test_configs/CoreConfig.ini')
    def test
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
