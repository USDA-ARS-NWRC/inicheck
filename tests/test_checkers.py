import pytest

from inicheck import checkers
from inicheck.config import MasterConfig, UserConfig
from .conftest import TEST_ROOT
from os.path import join


class CheckerTestBase:
    checker_cls = None

    @pytest.fixture(scope='function')
    def master_config(self, test_config_dir, section, item):
        """
        Master config from test data
        """
        return MasterConfig(
            path=test_config_dir.joinpath('master.ini').as_posix()
        )

    @pytest.fixture
    def user_config(self, test_config_dir, master_config):
        return UserConfig(
            test_config_dir.joinpath('base_cfg.ini').as_posix(),
            mcfg=master_config
        )

    @pytest.fixture
    def checker(self, user_config, section, item, value, extra_config):
        user_config.cfg.update({section: {item: value}})

        # Added info for testing e.g. ordered datetime pair
        if extra_config is not None:
            user_config.cfg[section].update(extra_config)
        return self.checker_cls(config=user_config, section=section, item=item)

    def check_value(self, checker_obj):
        """
        Returns whether the value result in any errors or warnings
        Args:
            checker_obj:
        Returns:
            Bool: indicating whether an error was returned
        """
        result = checker_obj.check()
        return result[0] is None


class TestCheckString(CheckerTestBase):
    checker_cls = checkers.CheckString

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'username', 'test', None, True),
        ('basic', 'username', 'Test', None, True),
    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid


class TestCheckBool(CheckerTestBase):
    checker_cls = checkers.CheckBool

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'debug', True, None, True),
        ('basic', 'debug', True, None, True),
        ('basic', 'debug', 'True', None, True),
        ('basic', 'debug', 'False', None, True),
        ('basic', 'debug', 'yes', None, True),
        ('basic', 'debug', 'y', None, True),
        ('basic', 'debug', 'no', None, True),
        ('basic', 'debug', 'n', None, True),
        ('basic', 'debug', 'Fasle', None, False),
        ('basic', 'debug', 'treu', None, False),
        ('basic', 'debug', 'F', None, False),
        ('basic', 'debug', 'T', None, False),
    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid


class TestCheckFloat(CheckerTestBase):
    checker_cls = checkers.CheckFloat

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'time_out', -1.5, None, True),
        ('basic', 'time_out', '2.5', None, True),
        ('basic', 'time_out', '2.5', None, True),
        ('basic', 'time_out', 2, None, True),
        ('basic', 'time_out', 'tough', None, False),
        ('basic', 'time_out', '2.a', None, False),
    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'fraction', 0.0, None, True),
        ('basic', 'fraction', 1.0, None, True),
        ('basic', 'fraction', '0.5', None, True),
        ('basic', 'fraction', 1.5, None, False),
    ])
    def test_bounds_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid


class TestCheckInt(CheckerTestBase):
    checker_cls = checkers.CheckInt

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'num_users', 10, None, True),
        ('basic', 'num_users', 1.0, None, True),
        ('basic', 'num_users', '2', None, True),
        ('basic', 'num_users', 'tough', None, False),
        ('basic', 'num_users', '1.5', None, False),
        ('basic', 'num_users', '', None, False),

    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid


class TestCheckDatetime(CheckerTestBase):
    checker_cls = checkers.CheckDatetime

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'start_date', '2018-01-10 10:10', None, True),
        ('basic', 'start_date', '10-10-2018', None, True),
        ('basic', 'start_date', 'October 10 2018', None, True),
        ('basic', 'start_date', 'Not-A-date', None, False),
        ('basic', 'start_date', 'Wednesday 5th', None, False),
        ('basic', 'start_date', '02-31-20', None, False),
    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'epochs', ['January 1st 1970'], None, True),
        ('basic', 'epochs', ['May 5th 2021', '2-31-2020'], None, True),
    ])
    def test_listed_datetime_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid


class TestCheckDirectory(CheckerTestBase):
    checker_cls = checkers.CheckDirectory

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'tmp', './', None, True),
        ('basic', 'tmp', './some_nonexistent_location', None, False),
        ('basic', 'tmp', '', None, False),  # ISSUE #44 check for invalid dir (default) when string is empty
    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid


class TestCheckFilename(CheckerTestBase):
    checker_cls = checkers.CheckFilename

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'log', join(TEST_ROOT, 'test_checkers.py'), None, True),
        ('basic', 'log', './non_existent_file.z', None, False),
    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid

    @pytest.mark.parametrize('section, item, default', [
        ('basic', 'log', '/var/log/log.txt'),
    ])
    def test_filename_default_on_empty_string(self, user_config, section, item, default):
        """
        Check noncritical path in the event an empty string is passed that a default is not None.
            * ISSUE #44 check for default when string is empty
        """
        # Assign empty string for file path
        user_config.cfg.update({section: {item: ''}})
        user_config.mcfg.cfg[section][item].default = default

        value = checkers.CheckFilename(
            config=user_config, section=section, item=item
        ).cast()

        assert value is default


class TestCheckURL(CheckerTestBase):
    checker_cls = checkers.CheckURL

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        ('basic', 'favorite_web_site', 'https://google.com', None, True),
        ('basic', 'favorite_web_site', 'https://micah_subnaught_is_awesome.com"', None, False),
    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid


class TestCheckDatetimeOrderedPair(CheckerTestBase):
    checker_cls = checkers.CheckDatetimeOrderedPair

    @pytest.mark.parametrize('section, item, value, extra_config, valid', [
        # Test Starts with Ends as extra config
        ('basic', 'start_date', '1-01-2019', {'end_date': '1-02-2019'}, True),
        ('basic', 'start_date', '2019-10-01', {'end_date': '2019-10-02'}, True),
        ('basic', 'start_date', '1998-01-14 15:00:00', {'end_date': '1998-01-14 19:00:00'}, True),
        ('basic', 'start_date', '2020-06-01', {'end_date': '2018-10-01'}, False),
        ('basic', 'start_date', '1998-01-14 20:00:00', {'end_date': '1998-01-14 10:00:00'}, False),
        # Test Ends with Starts as extra config
        ('basic', 'end_date', '2005-10-1 20:00:00', {'start_date': '2004-10-01 10:00:00'}, True),
        ('basic', 'end_date', '2016-04-01', {'start_date': '2016-05-01'}, False),
        # Equal dates is invalid
        ('basic', 'end_date', '2010-11-02', {'start_date': '2010-11-02'}, False),

    ])
    def test_check(self, checker, section, item, value, extra_config, valid):
        assert self.check_value(checker) == valid
