#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_utilities
----------------------------------

Tests for `inicheck.utilities` module.
"""
import pytest
from os.path import join, dirname
from inicheck.tools import get_user_config
from inicheck.utilities import *

@pytest.mark.parametrize("value, expected", [
('test#comment', 'test'),
("test1;comment", 'test1'),
(";full in line comment", ''),
("testboth; test a comment with both types of # comments ", 'testboth'),
])
def test_remove_comments(value, expected):
    """
    Test our remove comments code
    """
    out = remove_comment(value)
    assert out == expected


@pytest.mark.parametrize("value, unlist, expected",[
# Test we make things into lists
('test', False, True),
(['test'], False, True),
# Test we can take things out of a list
('test', True, False),
(['test'], True, False),
(['test'], True, False),
# Test we don't take lists of len > 1 out of a list
(['test', 'test2'], True, True)
])
def test_mk_lst(value, unlist, expected):
    """
    Test all the ways we use mk_lst
    """
    out = mk_lst(value, unlst=unlist)
    assert isinstance(out, list) == expected


def test_remove_chars():
    """
    Test if we can remove the problematic chars
    """
    out = remove_chars("\t\n my_test\t", "\t\n ")
    assert '\n' not in out
    assert '\t' not in out
    assert ' ' not in out


def test_find_options_in_recipes():
    """
    Tests utilities.find_options_in_recipes which extracts choices being
    made by looking at the recipes and determining which work on each other
    such that they don't exist at the same time. Used in the inimake cli
    """
    base = dirname(__file__)
    ucfg = get_user_config(join(base,"test_configs","full_config.ini"),
                           modules='inicheck')
    mcfg = ucfg.mcfg
    choices = find_options_in_recipes(mcfg.recipes, mcfg.cfg.keys(),
                                      "remove_section")

    # Currently there is 3 sections that are set as optional in the recipes
    for opt in ['gridded', 'mysql', 'csv']:
        assert opt in choices[0]


def test_get_relative_to_cfg():
    """
    Tests that all paths in a config can be made relative to the config
    """
    base = dirname(__file__)
    ucfg = get_user_config(join(base,"test_configs","full_config.ini"),
                            modules='inicheck')
    mcfg = ucfg.mcfg
    choices = find_options_in_recipes(mcfg.recipes, mcfg.cfg.keys(),
                                      "remove_section")
    p = get_relative_to_cfg(__file__, ucfg.filename)
    assert p == '../test_utilities.py'


@pytest.mark.parametrize('value, kw, count, expected',[
# Finds test in string
("tests_my_kw", ['tests'], 1, True),
# Finds all three in the string
("tests_my_kw", ['tests', 'my', 'kw'], 3, True),
# Finds all 2 in the string
("te_my_kw", ['tests', 'my', 'kw'], 2, True),
# No match
("te_ym_k", ['tests', 'my', 'kw'], 1, False),
])
def test_is_kw_matched(value, kw, count, expected):
    """
    Tests utilities.is_kw_matched which is used to match items in
    a config items list
    """
    # Finds test in string
    assert is_kw_matched(value, kw, kw_count=count) == expected

@pytest.mark.parametrize('kw, count, expected',[
(['test'], 1, 'test_my_str'),
(['test', 'float'], 2, 'test_my_float')])
def test_get_kw_match(kw, count, expected):
    """
    Tests utilities.get_kw_match which looks through a list of strings with
    potential matches of the keywords
    """

    test_lst = ['test_my_str', 'test_my_float', 'test_my_flowt']

    # should find the first one only
    t = get_kw_match(test_lst, kw, kw_count=count)
    assert t == expected

@pytest.mark.parametrize('value, dtype, allow_none, expected', [
# Test this is a convertible string
('10.0', float, False, [True, None]),
# Test the allow None kwarg
(None, float, False, [False, "Value cannot be None"]),
(None, float, True, [True, None]),
# Test we report an error
('abc', float, False, [False, 'Expecting float received str']),
])
def test_is_valid(value, dtype, allow_none, expected):
    """
    Tests utilities.is_valid which is grossly used in the checkers that are
    simple enough to pass a function to.
    """
    result = is_valid(value, dtype, dtype.__name__, allow_none=allow_none)
    assert result[0] == expected[0]
    assert result[1] == expected[1]


def test_get_inicheck_cmd():
    """
    Test if the cmd used to generate the str command is working

    """
    base = dirname(__file__)
    fname = join(base,"test_configs","full_config.ini")
    cmd = get_inicheck_cmd(
        fname,
        modules='inicheck',
        master_files=None)
    assert cmd == 'inicheck -f {} -m inicheck'.format(fname)


class TestUtilitiesDateParse():
    def test_string_date_only(self):
        """
        Test the parse_date function which is used in the checks for datetime
        """
        value = parse_date("2019-10-1")
        assert datetime(2019, 10, 1) == value

        # Test for odd issue that came up with casting a value twice
        value = parse_date("2019-10-1 10:00")
        value = parse_date(value)
        assert datetime(2019, 10, 1, 10) == value

    def test_string_with_tz_info_in_utc(self):
        value = parse_date("2019-10-1 10:00 MST")
        assert datetime(2019, 10, 1, 17) == value

    def test_tz_unaware_return(self):
        value = parse_date("2019-10-1 10:00")
        assert value.tzinfo is None

    def test_tz_unaware_return_with_tz_info_given(self):
        value = parse_date("2019-10-1 10:00 MST")
        assert value.tzinfo is None

    def test_parse_date_datetime(self):
        to_convert = datetime(2019, 10, 1)
        value = parse_date(to_convert)
        assert value == to_convert

    def test_parse_date_date(self):
        to_convert = date(2019, 10, 1)
        expected = datetime(2019, 10, 1)
        value = parse_date(to_convert)
        assert value == expected

    def test_parse_date_fails_int(self):
        with pytest.raises(TypeError):
            parse_date(10)

    def test_parse_date_fails_with_unknown_string(self):
        with pytest.raises(TypeError):
            parse_date("10 F")
