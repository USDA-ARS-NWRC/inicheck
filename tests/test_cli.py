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
from . test_output import capture_print


class TestCLI(unittest.TestCase):
    test_base = abspath(join(dirname(__file__),'test_configs'))
    master = [join(test_base, 'recipes.ini'), join(test_base, 'CoreConfig.ini')]
    cfg = join(test_base,'full_config.ini')

    def test_basic_inicheck_cli(self):
        """ Test simplest usage of CLI"""

        s = capture_print(inicheck_main, config_file=self.cfg, master=self.master)

        # make sure missing file shows up several times
        assert str(s).count("File does not exist") >= 9

        # make sure missing file shows up several times
        assert str(s).count("Not a registered option") >= 20

    def test_inicheck_recipe_use(self):
        """ Test recipe output"""

        s = capture_print(inicheck_main, config_file=self.cfg,
                                         master=self.master,
                                         show_recipes=True)

        # make sure 19 instances of applied recipes
        assert str(s).count("_recipe") == 20


    def test_inicheck_non_defaults_use(self):
        """ Test non-default output"""

        # cmd = 'inicheck -f {} -m inicheck --non-defaults'.format(self.cfg)
        s = capture_print(inicheck_main, config_file=self.cfg,
                                         master=self.master,
                                         show_non_defaults=True)

        assert str(s).count("wind") >= 7
        assert str(s).count("albedo") >= 3

    def test_inicheck_details_use(self):
        """ Test details output"""

        # cmd = 'inicheck -f {} -m inicheck --details topo'.format(self.cfg)
        s = capture_print(inicheck_main, config_file=self.cfg,
                                         master=self.master,
                                         details=['topo'])
        assert str(s).count("topo") >= 4


        cmd = 'inicheck -f {} -mf {} --details topo basin_lat'.format(self.cfg,
                                                         ' '.join(self.master))
        s = str(check_output(cmd, shell=True))
        s = capture_print(inicheck_main, config_file=self.cfg,
                                         master=self.master,
                                         details=['topo','basin_lat'])
        assert str(s).count("topo") >= 1

    def test_inicheck_changelog_use(self):
        """ Test changelog detection output"""
        old_cfg = join(self.test_base,'old_smrf_config.ini')

        # cmd = 'inicheck -f {} -m inicheck'.format(old_cfg)
        s = capture_print(inicheck_main, config_file=old_cfg,
                                         master=self.master,
                                         changelog_file=join(self.test_base,
                                                             'changelog.ini'))
        assert str(s).count("topo") == 7
        assert str(s).count("wind") == 12
        assert str(s).count("stations") == 5
        assert str(s).count("solar") == 9
        assert str(s).count("precip") == 18
        assert str(s).count("air_temp") == 9
        assert str(s).count("albedo") == 30

    def test_inidiff(self):
        """
        Tests if the inidiff script is producing the same information
        """

        # cmd = 'inidiff --config_files tests/test_configs/full_config.ini tests/test_configs/base_cfg.ini -m inicheck'
        configs = [join(self.test_base, 'full_config.ini'),
                   join(self.test_base, 'base_cfg.ini')]

        s = capture_print(inidiff_main, configs, master=self.master)
        # s = str(check_output(cmd, shell=True))
        mismatches = s.split("config mismatches:")[-1].strip()
        assert '117' in mismatches


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
