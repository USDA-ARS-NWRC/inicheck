#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_changes
----------------------------------

Tests for `inicheck.changes` module.
"""

import os

from inicheck.changes import ChangeLog
from inicheck.config import MasterConfig


class TestChanges():

    def test_valid_syntax(self, master_ini, changelog_ini):
        """
        Test we can detect valid syntax
        """
        mcfg = MasterConfig(path=master_ini)
        try:
            c = ChangeLog(paths=changelog_ini, mcfg=mcfg)
            assert True
        except Exception:
            assert False
