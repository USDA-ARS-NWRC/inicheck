#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_cli
----------------------------------

Tests for `inicheck.cli` functions.
"""

import unittest
from inicheck.cli import *
from subprocess import check_output
import inicheck
from os.path import basename, dirname, join, abspath


class TestCLI(unittest.TestCase):
    base = dirname(inicheck.__file__)
    cfg = abspath(join(base,'../tests','test_configs','full_config.ini'))

    def test_basic_inicheck_cli(self):
        """ Test simplest usage of CLI"""

        cmd = 'inicheck -f {} -m inicheck'.format(self.cfg)
        s = str(check_output(cmd, shell=True))

        # make sure missing file shows up several times
        assert str(s).count("File does not exist") >= 9

        # make sure missing file shows up several times
        assert str(s).count("Not a registered option") >= 20

    def test_inicheck_recipe_use(self):
        """ Test recipe output"""

        cmd = 'inicheck -f {} -m inicheck --recipes'.format(self.cfg)
        s = str(check_output(cmd, shell=True))

        # make sure 19 instances of applied recipes
        assert str(s).count("_recipe") == 20


    def test_inicheck_non_defaults_use(self):
        """ Test non-default output"""

        cmd = 'inicheck -f {} -m inicheck --non-defaults'.format(self.cfg)
        s = str(check_output(cmd, shell=True))

        assert str(s).count("wind") >= 7
        assert str(s).count("albedo") >= 3

    def test_inicheck_details_use(self):
        """ Test details output"""

        cmd = 'inicheck -f {} -m inicheck --details topo'.format(self.cfg)
        s = str(check_output(cmd, shell=True))

        assert str(s).count("topo") >= 4


        cmd = 'inicheck -f {} -m inicheck --details topo basin_lat'.format(self.cfg)
        s = str(check_output(cmd, shell=True))

        assert str(s).count("topo") >= 1

    def test_inicheck_changelog_use(self):
        """ Test changelog detection output"""
        old_cfg = join(self.base,'../tests','test_configs','old_smrf_config.ini')

        cmd = 'inicheck -f {} -m inicheck'.format(old_cfg)
        s = str(check_output(cmd, shell=True))

        assert str(s).count("topo") == 7
        assert str(s).count("wind") == 12
        assert str(s).count("stations") == 5
        assert str(s).count("solar") == 9
        assert str(s).count("precip") == 18
        assert str(s).count("air_temp") == 9
        assert str(s).count("albedo") == 30



if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
