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
        (['has_section = test'], [['test', 'any', 'any']]),
        (['has_item = test'], [['any', 'test', 'any']]),
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
        assert (t.conditions == expected_conditions_list)

    @pytest.mark.parametrize("entry_str_list, expected_attribute, expected_value", [
        (["default= [swe_z]", "type= string list"], 'default', ['swe_z']),  # Test the list keyword in the type
        (["default= [swe_z]", "type= string listed"], 'default', ['swe_z']),  # Test the other list keyword in type
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

class TestRecipeSection():

    @pytest.fixture(scope='function')
    def recipe(self, recipe_dict):
        return RecipeSection(recipe_section_dict=recipe_dict)

    @pytest.mark.parametrize("recipe_dict, trigger_names", [
        # Test Simple trigger assignment
        ({'test_trigger': 'has_item=username'}, ['test_trigger']),
        # Test on config entry only that has no trigger
        ({'section_adj': 'user_email=user1@internet.org'}, []),
        # Test multiple triggers
        ({'trigger1': 'has_section=test1', 'trigger2': 'has_item=test2'}, ['trigger1', 'trigger2']),
    ])
    def test_recipe_trigger_parse(self, recipe, recipe_dict, trigger_names):
        """
        Test the parsing and assignment of triggers
        """
        assert sorted(recipe.triggers.keys()) == sorted(trigger_names)

    @pytest.mark.parametrize("recipe_dict, expected_adj_config", [
        # Test Simple adjustment config assignment
        ({'trigger': 'has_item=user', 'info': 'age=10'}, {'info': {'age': '10'}}),
        # Test no adjustment config provided
        ({'trigger': 'has_item=user'}, {}),

    ])
    def test_adj_config_parse(self, recipe, recipe_dict, expected_adj_config):
        """
        Test the parsing and assignment of adjustments if the conditions are met
        """
        assert recipe.adj_config == expected_adj_config
