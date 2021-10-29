#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_recipe
----------------------------------

Tests for `inicheck.entries` module.
"""

from inicheck.entries import ConfigEntry, RecipeSection, TriggerEntry
import pytest

class TestEntries():
    @pytest.mark.parametrize('trigger_str_list, expected_conditions_list', [
        (['has_section = test'],  [['test', 'any', 'any']]),
        (['has_item = test'],  [['any', 'test', 'any']]),
        (['has_value = [test test test]'], [['test', 'test', 'test']]),
        (['has_section = test', 'has_item = test2'], [['test', 'any', 'any'], ['any', 'test2', 'any']]),
        (['has_value = [topo type ipw]'], [['topo', 'type', 'ipw']])
    ])
    def test_trigger_entry(self, trigger_str_list, expected_conditions_list):
        """
        Triggers define the condition sets for which a recipe is applied. This tests that those are interepretted
        correctly. A trigger can be defined by multiple triggers.
        """

        # section trigger
        t = TriggerEntry(trigger_str_list)
        assert(t.conditions == expected_conditions_list)

    @pytest.mark.parametrize("entry_str_list, expected_attribute, expected_value", [
        (["default= [swe_z]", "type= string list"], 'default', ['swe_z']),  # Test the list keyword in the type
        (["default= [swe_z]", "type= string listed"], 'default', ['swe_z']), # Test the other list keyword in type
        (["default= 10.5", "type= float"], 'default', '10.5'),
        (["min = 2"], 'min', '2'),
        (["allow_none = true"], 'allow_none', True),
        (["allow_none = false"], 'allow_none', False),
        (["options = [auth guest]"], 'options', ['auth', 'guest']),
        (["description = test"], 'description', 'test'),
    ])
    def test_config_entry(self, entry_str_list, expected_attribute, expected_value):
        """
        This tests defining a master config entry from a string.
        """
        e = ConfigEntry(name=None, parseable_line=entry_str_list)
        assert getattr(e, expected_attribute) == expected_value

    def test_config_entry_allow_none_exception(self):
        """
        Test that an invalid string bool raises an exception
        """
        with pytest.raises(ValueError):
            e = ConfigEntry(name=None, parseable_line=['allow_none = ture'])
