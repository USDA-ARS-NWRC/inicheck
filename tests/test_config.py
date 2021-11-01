#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_config
----------------------------------

Tests for `inicheck.config` module.
"""
import pytest
from inicheck.config import *
from tests.conftest import TEST_ROOT
from os.path import join


class TestUserConfig:
    @pytest.fixture(scope='class')
    def ucfg(self, full_config_ini):
        mcfg = MasterConfig(modules='inicheck')
        return UserConfig(full_config_ini, mcfg=mcfg)

    @pytest.fixture(scope='class')
    def ucfg_w_recipes(self, full_config_ini):
        mcfg = MasterConfig(modules='inicheck')

        ucfg = UserConfig(full_config_ini, mcfg=mcfg)
        ucfg.apply_recipes()
        return ucfg

    @pytest.mark.parametrize('important_att', ['mcfg', 'cfg', 'raw_cfg', 'recipes'])
    def test_userconfig_attributes(self, ucfg, important_att):
        """
        Simply confirms the user config has the important attributes that inicheck relies on
        """
        assert (hasattr(ucfg, important_att))

    @pytest.mark.parametrize("expected_recipe_name", [
        'topo_basic_recipe', 'time_recipe', 'air_temp_recipe', 'vp_recipe', 'wind_recipe', 'precip_recipe',
        'non_winstral_recipe', 'cloud_factor_recipe', 'albedo_recipe', 'date_decay_method_recipe', 'solar_recipe',
        'thermal_recipe', 'soil_recipe', 'output_recipe', 'system_recipe', 'csv_recipe', 'remove_wind_ninja_recipe',
        'non_grid_local_recipe', 'dk_recipe', 'idw_recipe'
    ])
    def test_apply_recipes(self, ucfg_w_recipes, expected_recipe_name):
        """
        Tests that the correct recipes were identified to be used for
        interpretation
        """
        assert expected_recipe_name in [r.name for r in ucfg_w_recipes.recipes]


class TestRecipeActions:
    """
    This tests the interpretation/actions of the recipes on the config.
    """

    @pytest.fixture(scope='function')
    def ucfg(self, full_config_ini, del_sections, mod_cfg):
        mcfg = MasterConfig(modules='inicheck')
        ucfg = UserConfig(full_config_ini, mcfg=mcfg)

        # Delete and section
        for s in del_sections:
            del ucfg.raw_cfg[s]

        # Modify the config
        for s, v in mod_cfg.items():
            ucfg.raw_cfg[s] = v

        ucfg.apply_recipes()
        return ucfg

    def check_items(self, ucfg, section=None, ignore=[]):
        """
        Checks a section for all the items in the master config.

        Args:
            ucfg: instantiated UserConfig
            section: Section to exmaine
            ignore: list of items to ignore useful for case when not everything
                    is added for certain values
        """
        checkable = [v for v in ucfg.mcfg.cfg[section].keys()
                     if v not in ignore]

        for v in checkable:
            assert v in ucfg.cfg[section].keys()

    def check_defaults(self, ucfg, section=None, ignore=[]):
        """
        Checks a section for all the items in the master config.
        """
        checkable = [v for v in ucfg.mcfg.cfg[section].keys()
                     if v not in ignore]

        for i in checkable:
            assert ucfg.cfg[section][i] == ucfg.mcfg.cfg[section][i].default

    @pytest.mark.parametrize("del_sections, mod_cfg, section_to_check", [
        (['csv'], {'csv': {'stations': None}}, 'csv')
    ])
    def test_apply_defaults(self, ucfg, del_sections, mod_cfg, section_to_check):
        """
        Tests the functionality of a recipes ability to ADD in defaults for
        section when a section is not there.
        """
        self.check_items(ucfg, section=section_to_check)
        self.check_defaults(ucfg, section=section_to_check)

    @pytest.mark.parametrize("del_sections, mod_cfg, expected_removed_section", [
        # Order matters, since we have conflicting recipes the first one will be
        # applied, in this case CSV will beat out gridded
        (['csv'], {'csv': {'stations': None}, 'gridded': {}}, 'gridded')
    ])
    def test_remove_section(self, ucfg, del_sections, mod_cfg, expected_removed_section):
        """
        Tests the functionality of a recipes ability to REMOVE a section in defaults
        """
        assert expected_removed_section not in ucfg.cfg.keys()

    @pytest.mark.parametrize("del_sections, mod_cfg, expected_section, expected_item_removed", [
        # Test removing an item when a section is present
        (['csv'], {'gridded': {'data_type': 'wrf'}}, 'thermal', 'distribution'),
        # Test removing an item when an item has a value
        ([], {'precip': {'distribution': 'idw', 'dk_ncores': '2'}}, 'precip', 'dk_ncore')
    ])
    def test_remove_item_recipe(self, ucfg, del_sections, mod_cfg, expected_section, expected_item_removed):
        """
        Recipes can be triggered to remove items under certain events. The triggers can be the presence of a section
        or an item has a specific value
        """
        assert expected_item_removed not in ucfg.cfg[expected_section].keys()

    @pytest.mark.parametrize("del_sections, mod_cfg, expected_section, expected_item_added", [
        # Test krig_recipe which added the variogram when the distribution is kriging
        (['precip'], {'precip': {'distribution': 'kriging'}}, 'precip', 'krig_variogram_model')
    ])
    def test_adding_item_recipe(self, ucfg, del_sections, mod_cfg, expected_section, expected_item_added):
        """
        This recipe applies defaults to items when an item has a certain value
        """
        assert expected_item_added in ucfg.cfg[expected_section].keys()


class TestMasterConfig():
    @pytest.fixture
    def mcfg(self):
        return MasterConfig(modules='inicheck')

    @pytest.mark.parametrize("mcfg_kwargs", [
        ({"modules": 'inicheck'}),  # Master config from module
        ({"path": join(TEST_ROOT, 'test_configs', 'CoreConfig.ini')}),  # Master config from file path
    ])
    def test_mcfg_instantiate(self, mcfg_kwargs):
        """
        Attempt to instantiate a master config with different kwargs
        """
        try:
            MasterConfig(**mcfg_kwargs)
            assert True
        except BaseException:
            assert False

    def test_exception_on_no_files(self):
        """
        This tests that a master config when attempted to instantiate without a module or a path throws an exception
        """
        with pytest.raises(ValueError):
            MasterConfig()

    def test_add_recipe_file(self, core_ini, recipes_ini):
        """
        Builds a master config from the files, add a recipe file, check that the recipe name is in the list
        """
        # Build a master config file using multiple files
        mcfg = MasterConfig(path=core_ini)
        mcfg.cfg = mcfg.add_files([recipes_ini])
        assert 'topo_basic_recipe' in [r.name for r in mcfg.recipes]


@pytest.fixture
def cfg_type(type_name):
    """
    Simple config dictionary to test check_types from config.py
    """
    line = ["type = {}".format(type_name)]
    cfg = {"section": {"test": ConfigEntry(name='test',
                                           parseable_line=line)}}
    return cfg


@pytest.mark.parametrize("type_name", ['bool', 'criticaldirectory', 'criticalfilename',
                                       'discretionarycriticalfilename', 'datetime',
                                       'datetimeorderedpair', 'directory', 'filename', 'float',
                                       'int', 'string', 'url'])
def test_check_types_valid(checkers_dict, cfg_type, type_name):
    """
    Check the valid set of item types that the master config will accept
    """
    assert check_types(cfg_type, checkers_dict)


@pytest.mark.parametrize("type_name", ['str', 'filepath', 'criticalfile'])
def test_check_types_exception(checkers_dict, cfg_type, type_name):
    """
    Check an invalid item type in the master config will raise an exception
    """
    with pytest.raises(ValueError):
        check_types(cfg_type, checkers_dict)

