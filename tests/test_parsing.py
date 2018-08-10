#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_iniparse
----------------------------------

Tests for `inicheck.iniparse` module.
"""

import unittest
from inicheck.iniparse import parse_sections, parse_items, parse_entry, parse_values


class TestIniparse(unittest.TestCase):

    def test_parse_sections(self):
        """
        Tests our base function used to parse sections before we do any
        processing

        Ensures:

        * we can handle comments around sections.
        * caps issues

        """

        info = ["# Test our line comments",
                "[unit]",
                "a:10; in line comment",
                "[test CASe] # another inline comment test",
                "b:5"]
        sections = parse_sections(info)

        # Confirm we see a normal section
        assert(sections['unit'][0] == "a:10")

        # Confirm we see a section with space caps issues
        assert(sections['test case'][0] == "b:5")

        # Confirm we catch dumb errors before we find a section name
        self.assertRaises(Exception, parse_sections,['a#','#','[test]'])


    def test_parse_items(self):
        """
        Tests our base function used to parse items after we read sections but
        before processing values.

        * tests for wrapped lists
        * tests to remove bracketed lists with comments
        * tests for properties being added in master files
        """

        info = {"unit":["a:10"],
                "test case":["a:10,","15,20"],
                'recipe':['a: default=10,',
                          'options=[10 15 20]']} # Handle wrapped lines with tabs

        items = parse_items(info)

        # Check for a normal single entry parse
        #print(items['test case']['a'])
        assert(items['unit']['a'] == '10')

        # Check for correct interpretation of a wrapped list
        assert(items['test case']['a'] == "10, 15, 20")

        # Check for a correct interpretation of item properties for master files
        assert(items['recipe']['a'] == "default=10, options=[10 15 20]")

    def test_parse_values(parsed_items):
        """
        test parse values

        Ensures:
        * we can clean up values with list entries
        * we can clean up properties we recieve including non-comma sep lists
        """
        info = {'unit':{'a': 'test1,\ttest2, test3'},
                'recipe':{'a':'\tdefault=10,\toptions=[10 15 20]'}
                }

        values = parse_values(info)

        # Check we parse a comma list correctly
        assert(values['unit']['a'][1] == 'test2')

        # Check we parse a properties list with no commas correctly
        assert(values['recipe']['a'][1]=='options=[10 15 20]')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
