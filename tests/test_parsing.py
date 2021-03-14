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


class IniparseTester():

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


@pytest.fixture
def iniparse_tester():
    return IniparseTester()


@pytest.mark.parametrize('info, expected', [
    # Test a simple parsing
    (['[s]', 'i:v'], {'s': ['i:v']}),
    # Test a section only without items
    (['[s]'], {'s': []}),
    # Test every section is made lower case
    (['[CASE]'], {'case': []}),
    # Test space remove before and after section
    (['[ spaces ]'], {'spaces': []}),
    # Test a single line section/value is parsed
    (['[single_line]i:v'], {'single_line': ['i:v']}),
    # Test some comment removal
    (['#comment', '[s]', 'i:v'], {'s': ['i:v']}),
    ([';[commented]'], {}),
    (['[s]', 'i:v ;comment'], {'s': ['i:v']}), ])
def test_parse_sections(iniparse_tester, info, expected):
    '''
    Tests our base function used to parse sections before we do any
    processing

    Ensures:

    * we can handle comments around sections.
    * caps issues

    '''
    iniparse_tester.run_parsing_test(parse_sections, info, expected, None)


@pytest.mark.parametrize("info, expected", [
    # Test exception with repeat sections
    (['[test]', '#', '[test]'], {}),
    # Test non-comment chars before the first section
    (['a#', '#', '[test]'], {}),
])
def test_parse_sections_exception(iniparse_tester, info, expected):
    '''
    Tests our base function used to parse sections before we do any
    processing

    Ensures:

    * we can handle comments around sections.
    * caps issues

    '''
    iniparse_tester.run_parsing_test(parse_sections, info, expected, Exception)


@pytest.mark.parametrize('info, expected', [
    # Test simple config item parsing
    (['a:10'], {'a': '10'}),
    # Test a value thats a list parse with a line return which should
    # simply merge them
    (['a:10,', '15,20'], {'a': '10, 15, 20'}),
    # Test interpreting master file properties that span multiple lines
    (['a: default=10', 'options=[10 15 20]'], {
     'a': 'default=10 options=[10 15 20]'}),
])
def test_parse_items(iniparse_tester, info, expected):
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
    iniparse_tester.run_parsing_test(parse_items, info, expected, None)


@pytest.mark.parametrize('info, expected', [
    # Test parse values that might have excess chars
    ('test1,\ttest2, test3', ['test1', 'test2', 'test3']),
    # Test parsing master properties parsing
    ('\tdefault=10,\toptions=[10 15 20]', [
     'default=10', 'options=[10 15 20]']),
])
def test_parse_values(iniparse_tester, info, expected):
    '''
    test parse values

    Ensures:
    * Cleans up values with list entries
    * Cleans up properties we recieve including non-comma sep lists
    '''
    # Assign info to a place in a dict of dict which are all ordered
    info = OrderedDict({'s': OrderedDict({'i': info})})
    expected = OrderedDict({'s': OrderedDict({'i': expected})})
    iniparse_tester.run_parsing_test(parse_values, info, expected, None)


@pytest.mark.parametrize('info, expected', [
    # Test interpreting renaming a section
    (['section/item -> new_section/item'], [['section', 'item',
                                             'any', 'any'], ['new_section', 'item', 'any', 'any']]),
    # Test interpreting renaming an item
    (['section/item -> section/new_item'], [['section', 'item',
                                             'any', 'any'], ['section', 'new_item', 'any', 'any']]),
    # test syntax error@pytest.mark.parametrize('info, expected', [
    # Test interpreting renaming a section
    (['section/item -> new_section/item'], [['section', 'item',
                                             'any', 'any'], ['new_section', 'item', 'any', 'any']]),
    # Test interpreting renaming an item
    (['section/item -> section/new_item'], [['section', 'item',
                                             'any', 'any'], ['section', 'new_item', 'any', 'any']]),
])
def test_parse_changes(iniparse_tester, info, expected):
    '''
    Tests tha change lof parsing. Ensures we raise a value error for invalid
    syntax and that valid syntax is parsed correctly
    '''
    iniparse_tester.run_parsing_test(parse_changes, info, [expected], None)


@pytest.mark.parametrize('info, expected', [
    # Test syntax error
    (['section/item > REMOVED'], []),
])
def test_parse_changes_exception(iniparse_tester, info, expected):
    '''
    Tests tha change lof parsing. Ensures we raise a value error for invalid
    syntax and that valid syntax is parsed correctly
    '''
    iniparse_tester.run_parsing_test(
        parse_changes, info, [expected], ValueError)
