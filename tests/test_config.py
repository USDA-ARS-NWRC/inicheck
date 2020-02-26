#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_config
----------------------------------

Tests for `inicheck.config` module.
"""

import datetime
import os
import unittest

from inicheck.config import *
from inicheck.tools import cast_all_variables, get_checkers


def compare_config(generated_config, truth_config,
                   master=False, mcfg_attr='default'):
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
        if s not in generated_config:
            print("\nERROR: test data contains section: {} that was not"
                  " contained by the generated config.".format(s))
            return False

        for i, v in truth_config[s].items():

            # Then confirm the item is in the section in the generated config
            if i not in generated_config[s].keys():
                print("\nERROR: test data contains item: {} in section: {} that was not"
                      " contained by the generated config.".format(i, s))
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
                    emsg = "\nERROR: config[{}][{}] = {} not {}.".format(s, i, gv,
                                                                         v)
                # Confirm values are the same
                if gv != v:
                    # print(emsg)
                    return False

    return True


class TestUserConfig(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """
        """
        fname = os.path.abspath(
            os.path.dirname(__file__) +
            '/test_configs/full_config.ini')
        mcfg = MasterConfig(modules='inicheck')
        self.ucfg = UserConfig(fname, mcfg=mcfg)

    def test_ucfg_init(self):
        """
        Simply opens and looks at the base config BEFORE all the recipes and
        stuff has been applied
        """

        # Assert important attributes
        for a in ['mcfg', 'cfg', 'raw_cfg', 'recipes']:
            assert(hasattr(self.ucfg, a))

    def test_apply_recipes(self):
        """
        Tests that the correct recipes were identified to be used for
        interpretation
        """

        truth = {'topo':
                 {'filename': ['None'],
                  'type': 'netcdf'},
                 'cloud_factor':
                 {'distribution': 'idw'}
                 }

        self.ucfg.apply_recipes()
        valid_recipes = ['topo_basic_recipe', 'time_recipe', 'air_temp_recipe',
                         'vp_recipe', 'wind_recipe', 'precip_recipe',
                         'non_winstral_recipe', 'cloud_factor_recipe',
                         'albedo_recipe', 'date_decay_method_recipe',
                         'solar_recipe', 'thermal_recipe', 'soil_recipe',
                         'output_recipe', 'system_recipe', 'csv_recipe',
                         'remove_wind_ninja_recipe', 'non_grid_local_recipe',
                         'dk_recipe', 'idw_recipe']
        for v in valid_recipes:
            assert v in [r.name for r in self.ucfg.recipes]


class TestRecipes(unittest.TestCase):

    def setUp(self):
        self.fname = os.path.abspath(os.path.dirname(__file__) +
                                     '/test_configs/full_config.ini')

        self.mcfg = MasterConfig(modules='inicheck')
        self.ucfg = UserConfig(self.fname, mcfg=self.mcfg)

    def modify_cfg(self, mod_cfg):
        """

        """

        for s, v in mod_cfg.items():
            self.ucfg.raw_cfg[s] = v

        self.ucfg.apply_recipes()

    def check_items(self, section=None, ignore=[]):
        """
        Checks a section for all the items in the master config.

        Args:
            section: Section to exmaine
            ignore: list of items to ignore useful for case when not everything
                    is added for certain values
        """
        checkable = [v for v in self.mcfg.cfg[section].keys()
                     if v not in ignore]

        for v in checkable:
            assert v in self.ucfg.cfg[section].keys()

    def check_defaults(self, section=None, ignore=[]):
        """
        Checks a section for all the items in the master config.
        """
        checkable = [v for v in self.mcfg.cfg[section].keys()
                     if v not in ignore]

        for i in checkable:
            assert self.ucfg.cfg[section][i] == self.mcfg.cfg[section][i].default

    def test_apply_defaults(self):
        """
        Tests the functionality of a recipes ability to add in defaults for
        section when a section is not there.
        """

        del self.ucfg.raw_cfg['csv']

        test = {'csv': {'stations': None}}
        self.modify_cfg(test)

        self.check_items(section='csv')
        self.check_defaults(section='csv')

    def test_remove_section(self):
        """
        Tests the functionality of a recipes ability to a section in defaults for
        section when a section is not there.
        """

        del self.ucfg.raw_cfg['csv']

        # Order matters, since we have conflicting recipes the first one will be
        # applied, in this case CSV will beat out gridded
        test = {'csv': {'stations': None},
                'gridded': {}}

        self.modify_cfg(test)

        self.check_items(section='csv')
        assert 'gridded' not in self.ucfg.cfg.keys()

    def test_remove_item_for_a_section(self):
        """
        Sometimes a recipe will remove an item when a certain section is present
        This tests that scenario occurs, uses thermal_distribution_recipe
        """

        test = {'gridded': {'data_type': 'wrf'}}
        # The order of recipes matters. Del the csv section to avoid recipes on
        # it
        del self.ucfg.raw_cfg['csv']
        self.modify_cfg(test)

        assert 'distribution' not in self.ucfg.cfg['thermal'].keys()

    def test_add_items_for_has_value(self):
        """
        Recipes have the available keyword has_value to trigger on event where
        a section item has a value. This tests that we can trigger on it and
        make edits. Test uses the idw_recipe in which if any section is found
        with the item distribution set to idw, then we add idw_power and remove
        dk_ncores.
        """

        test = {'precip': {'distribution': 'idw', 'dk_ncores': '2'}}
        self.modify_cfg(test)

        assert 'dk_ncores' not in self.ucfg.cfg['precip'].keys()
        assert 'idw_power' in self.ucfg.cfg['precip'].keys()

    def test_apply_defaults_for_has_value(self):
        """
        This recipe applies defaults to items when an item has a certain value
        This test uses the krig_recipe in which any item distribution is set to
        kriging applies several defautls.
        """

        test = {'precip': {'distribution': 'kriging', 'dk_ncores': '2'}}
        self.modify_cfg(test)
        assert 'krig_variogram_model' in self.ucfg.cfg['precip'].keys()
        assert 'dk_ncores' not in self.ucfg.cfg['precip'].keys()


class TestMasterConfig(unittest.TestCase):
    def setUp(self):
        """
        Stage our truthing data here
        """
        self.truth_defaults = {'topo':
                               {'type': 'netcdf',
                                'filename': ['./common_data/topo/topo.nc']},
                               'air_temp':
                               {'distribution': 'idw',
                                'detrend': 'true',
                                'dk_ncores': '1'}}

    def test_grabbing_mcfg(self):
        """
        Builds a master config from the module and paths, check it.
        """
        # Build a master config file using multiple files
        try:
            mcfg = MasterConfig(modules='inicheck')
            assert True
        except BaseException:
            assert False

        base = os.path.dirname(__file__)
        master = os.path.join(base, "./test_configs/CoreConfig.ini")
        recipes = os.path.join(base, "./test_configs/recipes.ini")

        try:
            mcfg = MasterConfig(path=[master, recipes])
            assert True
        except BaseException:
            assert False

    def test_add_files(self):
        """
        Builds a master config from the files, check it.
        """
        # Build a master config file using multiple files
        base = os.path.dirname(__file__)
        master = os.path.join(base, "test_configs/CoreConfig.ini")
        recipes = os.path.join(base, "test_configs/recipes.ini")

        mcfg = MasterConfig(path=master)
        mcfg.cfg = mcfg.add_files([master, recipes])

        valid_sections = ['topo', 'csv', 'air_temp']
        for v in valid_sections:
            assert v in mcfg.cfg.keys()

        assert 'topo_basic_recipe' in [r.name for r in mcfg.recipes]

    def test_check_types(self):
        """
        Checks to make sure we throw the correct error when an unknown data
        type is requested
        """

        # Call out a BS entry type to raise the error
        checkers = get_checkers()
        invalids = ['str', 'filepath', 'criticalfile']
        valids = ['bool', 'criticaldirectory', 'criticalfilename',
                  'discretionarycriticalfilename', 'datetime',
                  'datetimeorderedpair', 'directory', 'filename', 'float',
                  'int', 'string', 'url']

        for z, values in enumerate([invalids, valids]):
            for kw in values:
                line = ["type = {}".format(kw), "description = test"]
                cfg = {"section": {"test": ConfigEntry(name='test',
                                                       parseable_line=line)}}
                # invalids
                if z == 0:
                    self.assertRaises(ValueError, check_types, cfg, checkers)

                # valids
                else:
                    assert check_types(cfg, checkers)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
