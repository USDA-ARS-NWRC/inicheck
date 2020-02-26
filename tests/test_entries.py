#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_recipe
----------------------------------

Tests for `inicheck.entries` module.
"""

import unittest
from collections import OrderedDict

from inicheck.entries import ConfigEntry, RecipeSection, TriggerEntry


class TestEntries(unittest.TestCase):
    def test_trigger_entry(self):
        """
        Tests to see if we correctly gather a trigger for a recipe
        """
        entries = ['has_section = test',
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

    def test_config_tigger_entry(self):
        """
        Tests to see if we correctly gather a trigger for a recipe
        """
        entries = [['has_value = [topo type ipw]']]

        t = TriggerEntry(entries[0])
        assert(t.conditions[0] == ['topo', 'type', 'ipw'])

    def test_config(self):
        """
        User should be able to make a single item a list by requesting it by
        with a master config entry like the following
        ```
            points_values_property:
             default= [swe_z],
             type= string list,
             description = stuff
         ```
        Issue #20
        """
        s = ["default= [swe_z]",
             "type= string list",
             "description = stuff"]

        e = ConfigEntry(name="points_values_property", parseable_line=s)

        # Assert the defaults a signle item list
        assert e.default == ['swe_z']
        assert e.type == 'string'
        assert e.listed == True


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
