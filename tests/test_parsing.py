#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
test_iniparse
----------------------------------

Tests for `inicheck.iniparse` module.
'''
from collections import OrderedDict

import pytest
from inicheck.iniparse import *


class TestIniparse():

    def run_parsing_test(self, fn, info, expected, exception):
        '''
        Manages testing exceptions and testing dict output
        '''
        if isinstance(info, OrderedDict):
            expected = OrderedDict(expected)

        if exception is None:
            received = fn(info)

            # Test the dictionaries recieved match the expected
            assert received == expected

        else:
            with pytest.raises(exception):
                received = fn(info)

    @pytest.mark.parametrize('info, expected, exception', [
        # Test a simple parsing
        (['[s]', 'i:v'], {'s': ['i:v']}, None),
        # Test a section only without items
        (['[s]'], {'s': []}, None),
        # Test every section is made lower case
        (['[CASE]'], {'case': []}, None),
        # Test space remove before and after section
        (['[ spaces ]'], {'spaces': []}, None),
        # Test a single line section/value is parsed
        (['[single_line]i:v'], {'single_line': ['i:v']}, None),
        # Test some comment removal
        (['#comment', '[s]', 'i:v'], {'s': ['i:v']}, None),
        ([';[commented]'], {}, None),
        (['[s]', 'i:v ;comment'], {'s': ['i:v']}, None),
        # Test exception with repeat sections
        (['[test]', '#', '[test]'], {}, Exception),
        # Test non-comment chars before the first section
        (['a#', '#', '[test]'], {}, Exception),

    ])
    def test_parse_sections(self, info, expected, exception):
        '''
        Tests our base function used to parse sections before we do any
        processing

        Ensures:

        * we can handle comments around sections.
        * caps issues

        '''
        self.run_parsing_test(parse_sections, info, expected, exception)

    @pytest.mark.parametrize('info, expected, exception', [
        # Test simple config item parsing
        (['a:10'], {'a': '10'}, None),
        # Test a value thats a list parse with a line return which should
        # simply merge them
        (['a:10,', '15,20'], {'a': '10, 15, 20'}, None),
        # Test interpreting master file properties that span multiple lines
        (['a: default=10', 'options=[10 15 20]'], {
         'a': 'default=10 options=[10 15 20]'}, None),
    ])
    def test_parse_items(self, info, expected, exception):
        '''
        Tests our base function used to parse items after reading sections but
        before processing values.

        * tests for wrapped lists
        * tests to remove bracketed lists with comments
        * tests for properties being added in master files
        '''
        # Assign a section to the info which are always OrderedDict
        info = OrderedDict({'s': info})
        expected = {'s': OrderedDict(expected)}
        self.run_parsing_test(parse_items, info, expected, exception)

    @pytest.mark.parametrize('info, expected, exception', [
        # Test parse values that might have excess chars
        ('test1,\ttest2, test3', ['test1', 'test2', 'test3'], None),
        # Test parsing master properties parsing
        ('\tdefault=10,\toptions=[10 15 20]', [
         'default=10', 'options=[10 15 20]'], None),
    ])
    def test_parse_values(self, info, expected, exception):
        '''
        test parse values

        Ensures:
        * Cleans up values with list entries
        * Cleans up properties we recieve including non-comma sep lists
        '''
        # Assign info to a place in a dict of dict which are all ordered
        info = OrderedDict({'s': OrderedDict({'i': info})})
        expected = OrderedDict({'s': OrderedDict({'i': expected})})
        self.run_parsing_test(parse_values, info, expected, exception)

    @pytest.mark.parametrize('info, expected, exception', [
        # Test interpreting renaming a section
        (['section/item -> new_section/item'], [['section', 'item',
                                                 'any', 'any'], ['new_section', 'item', 'any', 'any']], None),
        # Test interpreting renaming an item
        (['section/item -> section/new_item'], [['section', 'item',
                                                 'any', 'any'], ['section', 'new_item', 'any', 'any']], None),
        # Tet syntax error
        (['section/item > REMOVED'], [], ValueError),

    ])
    def test_parse_changes(self, info, expected, exception):
        '''
        Tests tha change lof parsing. Ensures we raise a value error for invalid
        syntax and that valid syntax is parsed correctly
        '''
        # d = ['section/item -> new_section/item', 'section/item -> REMOVED']
        self.run_parsing_test(parse_changes, info, [expected], exception)
