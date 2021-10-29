import os
from pathlib import Path

import pytest

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope='session', autouse=True)
def test_config_dir():
    return Path(TEST_ROOT).joinpath('test_configs')


@pytest.fixture(scope='session', autouse=True)
def full_config_ini(test_config_dir):
    return Path(test_config_dir).joinpath("full_config.ini")

@pytest.fixture(scope='session', autouse=True)
def base_config_ini(test_config_dir):
    return Path(test_config_dir).joinpath("base_cfg.ini")

@pytest.fixture(scope='session', autouse=True)
def old_smrf_config_ini(test_config_dir):
    return Path(test_config_dir).joinpath("old_smrf_config.ini")


@pytest.fixture(scope='session', autouse=True)
def changelog_ini(test_config_dir):
    return Path(test_config_dir).joinpath("changelog.ini")


@pytest.fixture(scope='session', autouse=True)
def master_ini(test_config_dir):
    return [os.path.join(test_config_dir, "CoreConfig.ini"), os.path.join(test_config_dir, "recipes.ini")]

@pytest.fixture(scope='session', autouse=True)
def recipes_ini(test_config_dir):
    return Path(test_config_dir).joinpath("recipes.ini")
