#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_output
----------------------------------

Tests for `inicheck.output` module.
"""

import unittest
from inicheck.output import *
from collections import OrderedDict
import shutil
from inicheck.tools import get_user_config
import os


class TestOutput(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        base = os.path.dirname(__file__)
        self.ucfg = get_user_config(os.path.join(base,"test_configs/full_config.ini"),
                                                            modules="inicheck")
    @classmethod
    def tearDownClass(self):
        """
        Delete any files
        """
        os.remove('out_config.ini')

    def test_generate_config(self):
        """
        """
        generate_config(self.ucfg, 'out_config.ini', cli=False)

        with open('out_config.ini') as fp:
            lines = fp.readlines()
            fp.close()

        # Assert a header is written
        assert 'Configuration' in lines[1]

        key_count = 0

        # Assert all the sections are written
        for k in self.ucfg.cfg.keys():
            for l in lines:
                if k in l:
                    key_count+=1
                    break

        assert key_count == len(self.ucfg.cfg.keys())


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
