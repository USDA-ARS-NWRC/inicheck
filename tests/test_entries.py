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
        entries = [ 'has_section = test',
                    'has_item = test',
                    'has_value = [test test test]',
                    ['has_section = test',
                    'has_item = test2']]

        # section trigger
        t = TriggerEntry(entries[0])
        assert(t.conditions[0] == ['test', 'any', 'any'])

        # section item
        t = TriggerEntry(entries[1])
        assert(t.conditions[0] == ['any', 'test', 'any'])

        t = TriggerEntry(entries[2])
        assert(t.conditions[0] == ['test', 'test', 'test'])

        # Confirm we can handle multiple conditions
        t = TriggerEntry(entries[3])
        assert(t.conditions[0] == ['test', 'any', 'any'])
        assert(t.conditions[1] == ['any', 'test2', 'any'])


    def test_config_entry(self):
        """
        Tests to see if we correctly gather a trigger for a recipe
        """
        entries = [['has_value = [topo type ipw]']]

        t = TriggerEntry(entries[0])
        assert(t.conditions[0] == ['topo', 'type', 'ipw'])

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
