#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_changes
----------------------------------

Tests for `inicheck.changes` module.
"""

from inicheck.changes import ChangeLog


class TestChanges:

    def test_valid_syntax(self, full_mcfg, changelog_ini):
        """
        Test we can detect valid syntax
        """
        try:
            c = ChangeLog(paths=changelog_ini, mcfg=full_mcfg)
            assert True
        except Exception:
            assert False
