import os
from pathlib import Path

import pytest

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope='session', autouse=True)
def test_config_dir():
    return Path(TEST_ROOT).joinpath('test_configs')
