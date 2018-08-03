#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_recipe
----------------------------------

Tests for `inicheck.entries` module.
"""

import unittest
from inicheck.entries import RecipeSection, TriggerEntry
from collections import OrderedDict

class TestEntries(unittest.TestCase):
    def test_trigger_entry(self):
        """
        Tests to see if we correctly gather a trigger for a recipe
        """
        entryies = [['has_value = [topo type ipw]'],
                    ['has_value = [topo type ipw]']

        t = TriggerEntry(entry1)
        assert(t.conditions[0] == ['topo', 'type', 'ipw'])
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
