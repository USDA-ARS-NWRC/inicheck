from os.path import join, dirname, abspath
from pathlib import Path
from inicheck.tools import get_user_config, get_checkers
from inicheck.config import MasterConfig

import pytest

TEST_ROOT = dirname(abspath(__file__))


@pytest.fixture(scope='session', autouse=True)
def test_config_dir():
    return Path(TEST_ROOT).joinpath('test_configs')


@pytest.fixture(scope='session', autouse=True)
def full_config_ini(test_config_dir):
    return join(test_config_dir, "full_config.ini")


@pytest.fixture(scope='session', autouse=True)
def base_config_ini(test_config_dir):
    return join(test_config_dir, "base_cfg.ini")


@pytest.fixture(scope='session', autouse=True)
def old_smrf_config_ini(test_config_dir):
    return join(test_config_dir, "old_smrf_config.ini")


@pytest.fixture(scope='session', autouse=True)
def changelog_ini(test_config_dir):
    return join(test_config_dir, "changelog.ini")


@pytest.fixture(scope='session', autouse=True)
def core_ini(test_config_dir):
    return join(test_config_dir, "CoreConfig.ini")


@pytest.fixture(scope='session', autouse=True)
def recipes_ini(test_config_dir):
    return join(test_config_dir, "recipes.ini")


@pytest.fixture(scope='session', autouse=True)
def master_ini(core_ini, recipes_ini):
    return [core_ini, recipes_ini]

@pytest.fixture(scope='session', autouse=True)
def basic_mcfg(test_config_dir,):
    """
    Master config fixture to be used with the basic config fixture
    """
    return MasterConfig(path=join(test_config_dir, 'master.ini'))

@pytest.fixture(scope='session', autouse=True)
def full_mcfg(master_ini):
    return MasterConfig(path=master_ini)

@pytest.fixture(scope='session', autouse=True)
def full_ucfg(full_config_ini, master_ini):
    return get_user_config(full_config_ini, master_files=master_ini)


@pytest.fixture(scope='session', autouse=True)
def checkers_dict():
    """
    Get a dictionary of checkers to use.
    """
    return get_checkers()
