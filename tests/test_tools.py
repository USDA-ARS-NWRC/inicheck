#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_recipe
----------------------------------

Tests for `inicheck.Tools` module.
"""

from collections import OrderedDict

import pytest
from inicheck.tools import *
from datetime import datetime
from os.path import join
from .conftest import TEST_ROOT

@pytest.mark.parametrize('fn_kwargs, expected_types', [
    ({}, ['bool', 'criticaldirectory', 'criticalfilename', 'datetime', 'datetimeorderedpair',
          'directory', 'filename', 'float', 'int', 'string', 'url']),
    ({'ignore': []}, ["type", "generic", "path"]),
    # Check the keyword is removed from the name
    ({'keywords': 'checkdate'}, ["time"]),
    # Confirm get_checkers can grab any class from any module using keywords and modules
    ({'module': 'inicheck.config', 'keywords': 'config'}, ["user", 'master']),

])
def test_get_checkers(fn_kwargs, expected_types):
    """
    Tests the get_checkers func in tools
    """
    checkers = get_checkers(**fn_kwargs).keys()
    for v in expected_types:
        assert v in checkers


def test_check_config(full_ucfg):
    """
    Tests the check_config func in tools
    """
    warnings, errors = check_config(full_ucfg)
    assert len(errors) == 11

@pytest.mark.parametrize("section, item, str_value, expected_type", [
    ('time', 'start_date', "10-1-2019", datetime),
    ('air_temp', 'dk_ncores', "1.0", int),
    ('air_temp', 'detrend', "true", bool),
    ('wind', 'reduction_factor', "0.2", float),
    ('precip', 'distribution', "dk", str),
    ('output', 'variables', "dk", list),
])
def test_cast_all_variables(full_config_ini, core_ini, section, item, str_value, expected_type):
    """
    Tests the cast_all_variables func in tools
    """
    ucfg = get_user_config(full_config_ini, master_files=core_ini)
    ucfg.cfg = {section: {item: str_value}}
    ucfg = cast_all_variables(ucfg, ucfg.mcfg)
    assert type(ucfg.cfg[section][item]) == expected_type


def test_get_user_config_exception():
    """
    Tests getting the user config
    """
    # check for the Exception
    with pytest.raises(IOError):
        get_user_config('not_a_file.ini')


def test_config_documentation_error():
    """
    Confirms that we still make config documentation
    """
    # Confirm exception when file doesnt exist
    with pytest.raises(IOError):
        f = '/no/folder/exists/f.rst'
        config_documentation(f, modules='inicheck')

@pytest.fixture()
def documentation_f():
    f = 'test.rst'
    yield f
    os.remove(f)
@pytest.mark.parametrize("fn_kwargs", [
     {"modules": 'inicheck'},
     {"paths": [join(TEST_ROOT, 'test_configs', 'CoreConfig.ini')]}
])
def test_config_documentation(documentation_f, fn_kwargs):
    """
    Test the auto documentation function for the config file using different methods of
    supplying a master config
    """
    config_documentation(documentation_f, **fn_kwargs)

    with open(documentation_f) as fp:
        lines = fp.readlines()
    assert len(lines) == 1483

