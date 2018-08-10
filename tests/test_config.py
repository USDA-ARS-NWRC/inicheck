#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_config
----------------------------------

Tests for `inicheck.config` module.
"""

import unittest
import os
from inicheck.config import *
from inicheck.tools import cast_all_variables

def compare_config(generated_config, truth_config, master=False, mcfg_attr='default'):
    """
    Compares config objects for quick tests:

    Args:
        generated_config: the config file the inicheck system produced automatically
        truth_config: a dictionary made up for checking against
        master: boolean for identifying if were checking master config
        mcfg_attr: attribute we want to check when using a master config
    Returns:
        result: boolean describing if cfg are the same.
    """

    # First confirm all keys are available
    for s in truth_config.keys():
        if s  not in generated_config:
            print("\nERROR: test data contains section: {} that was not"
                  " contained by the generated config.".format(s))
            return False

        for i,v in truth_config[s].items():

            # Then confirm the item is in the section in the generated config
            if i not in generated_config[s].keys():
                print("\nERROR: test data contains item: {} in section: {} that was not"
                      " contained by the generated config.".format(i,s))
                return False

            # Check the value
            else:
                # if it is a master config object then use it differently.
                if master:
                    gv = getattr(generated_config[s][i], mcfg_attr)
                    emsg = "\nERROR: config.{} = {} not {}.".format(
                                                    mcfg_attr,
                                                    gv,
                                                    v)

                # Normal config
                else:
                    gv = generated_config[s][i]
                    emsg ="\nERROR: config[{}][{}] = {} not {}.".format(s,i,gv,
                                                                              v)
                # Confirm values are the same
                if gv != v:
                        print(emsg)
                        return False

    return True


class TestUserConfig(unittest.TestCase):
    def setUp(self):
        """
        Stage truth data here, grab the config to pass around
        """

        fname = os.path.abspath(os.path.dirname(__file__)+'/test_configs/base_cfg.ini')

        mcfg = MasterConfig(modules = 'inicheck')
        self.ucfg = UserConfig(fname, mcfg=mcfg)

    def test_base_config(self):
        """
        Simply opens and looks at the base config BEFORE all the recipes and
        stuff has been applied
        """
        truth = {'topo':
                        {},
                 'air_temp':
                        {}
                }

        assert compare_config(self.ucfg.cfg,truth)

    def test_apply_recipes(self):
        """
        Tests that the correct variables are in place after recipes
        """

        truth = {'topo':
                        {'filename':None,
                        'type':'netcdf'},
                 'air_temp':
                        {'distribution': 'idw',
                         'detrend':'true',
                         'slope':'1'}
                }

        self.ucfg.apply_recipes()
        assert compare_config(self.ucfg.cfg,truth)

    def test_apply_casting(self):
        """
        Tests that the correct variables are in place after recipes
        """

        truth = {'topo':
                        {'filename':None,
                        'type':'netcdf'},
                 'air_temp':
                        {'distribution': 'idw',
                         'detrend':True,
                         'slope':1.0}
                }

        self.ucfg.apply_recipes()
        self.ucfg = cast_all_variables(self.ucfg, self.ucfg.mcfg)

        assert compare_config(self.ucfg.cfg,truth)
        

class TestMasterConfig(unittest.TestCase):
    def setUp(self):
        """
        Stage our truthing data here
        """
        self.truth_defaults = {'topo':
                                            {'type': 'netcdf',
                                             'dem': None,
                                             'filename': None},
                                'air_temp':
                                            {'distribution': 'idw',
                                             'detrend': 'true',
                                             'dk_nthreads': '1'}}

    def test_from_module(self):
        """
        Builds a master config from the module, check it.
        """
        # Build a master config file using multiple files
        mcfg = MasterConfig(modules = 'inicheck')
        assert compare_config(mcfg.cfg,self.truth_defaults, master=True,
                                                            mcfg_attr='default')

    def test_from_paths(self):
        """
        Builds a master config from the files, check it.
        """
        # Build a master config file using multiple files
        mcfg = MasterConfig(path = ['./tests/test_configs/CoreConfig.ini',
                                         './tests/test_configs/recipes.ini'])

        assert compare_config(mcfg.cfg,self.truth_defaults, master=True,
                                                            mcfg_attr='default')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
