#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
from os.path import dirname, abspath, join

from inicheck.cli import inicheck_main, inidiff_main

from .test_output import capture_print


class TestCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_base = abspath(join(dirname(__file__), 'test_configs'))
        cls.master = [
            join(cls.test_base, 'recipes.ini'),
            join(cls.test_base, 'CoreConfig.ini')
        ]
        cls.full_config = join(cls.test_base, 'full_config.ini')

    @classmethod
    def capture_with_params(cls, **kwargs):
        return str(
            capture_print(
                inicheck_main,
                config_file=cls.full_config,
                master=cls.master,
                **kwargs
            )
        )

    def test_basic_inicheck_cli(self):
        """ Test simplest usage of CLI """

        s = self.capture_with_params()

        assert s.count("File does not exist") >= 9
        assert s.count("Not a registered option") >= 20

    def test_inicheck_recipe_use(self):
        """ Test recipe output """

        s = self.capture_with_params(show_recipes=True)

        assert s.count("_recipe") == 20

    def test_inicheck_non_defaults_use(self):
        """ Test non-default output"""

        s = self.capture_with_params(show_non_defaults=True)

        assert s.count("wind") >= 7
        assert s.count("albedo") >= 3

    def test_inicheck_details_use(self):
        """ Test details output """

        s = self.capture_with_params(details=['topo'])

        assert s.count("topo") >= 4

        s = self.capture_with_params(details=['topo', 'basin_lat'])

        assert s.count("topo") >= 1

    def test_inicheck_changelog_use(self):
        """ Test changelog detection output """

        old_cfg = join(self.test_base, 'old_smrf_config.ini')

        s = str(capture_print(
            inicheck_main,
            config_file=old_cfg,
            master=self.master,
            changelog_file=join(self.test_base, 'changelog.ini')
        ))
        assert s.count("topo") == 7
        assert s.count("wind") == 12
        assert s.count("stations") == 5
        assert s.count("solar") == 9
        assert s.count("precip") == 18
        assert s.count("air_temp") == 9
        assert s.count("albedo") == 30

    def test_inidiff(self):
        """
        Tests if the inidiff script is producing the same information
        """

        configs = [
            join(self.test_base, 'full_config.ini'),
            join(self.test_base, 'base_cfg.ini')
        ]

        s = capture_print(inidiff_main, configs, master=self.master)

        mismatches = s.split("config mismatches:")[-1].strip()
        assert '117' in mismatches


if __name__ == '__main__':
    sys.exit(unittest.main())
