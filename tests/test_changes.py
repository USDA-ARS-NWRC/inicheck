#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_changes
----------------------------------

Tests for `inicheck.changes` module.
"""

import os

from inicheck.changes import ChangeLog
from inicheck.config import MasterConfig, UserConfig


class TestChanges():

    def test_valid_syntax(self):
        """
        Test we can detect valid syntax
        """
        base = os.path.dirname(__file__)
        master = os.path.join(base, 'test_configs/CoreConfig.ini')
        recipes = os.path.join(base, 'test_configs/recipes.ini')
        mcfg = MasterConfig(path=[master, recipes])
        cf = os.path.join(base, 'test_configs/changelog.ini')
        try:
            c = ChangeLog(paths=cf, mcfg=mcfg)
            assert True
        except Exception:
            assert False
