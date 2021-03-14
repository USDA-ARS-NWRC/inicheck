import os

import pytest

from inicheck import checkers as checkers
from inicheck.config import MasterConfig, UserConfig


def run_a_checker(
    user_config,
    valid_entries,
    invalid_entries,
    checker,
    section='basic',
    item='item',
    extra_config=None
):
    """
    Runs a loop over all the valid entries and applies the checker and asserts
    they are true. Same thing is done for the invalid entries.
    Args:
        user_config:     inicheck.config.UserConfig instance
        valid_entries:   List of valid entries to check
        invalid_entries: List of invalid entries to check
        checker:         Any class in inicheck.checkers
        section:         Section name the item being checked is occurring
        item:            Item name in the config
        extra_config:    Pass in contextual config info to test more
                         complicated checkers. E.g. ordered datetime pair.
    """

    config = user_config.cfg
    config.update({section: {item: " "}})

    # Added info for testing e.g. ordered datetime pair
    if extra_config:
        config.update(extra_config)

    for z, values in enumerate([valid_entries, invalid_entries]):
        for v in values:

            config[section][item] = v
            b = checker(config=user_config, section=section, item=item)
            msgs = b.check()

            if len([True for m in msgs if m is None]) == len(msgs):
                valid = True
            else:
                valid = False

            # Expected valid
            if z == 0:
                assert valid
            else:
                assert not valid


def define_checker(user_config, checker, value, item='item', section='basic'):
    config = user_config.cfg
    config.update({section: {item: " "}})
    config[section][item] = value

    return checker(config=user_config, section=section, item=item)


class TestCheckers:
    @pytest.fixture(scope='class')
    def master_config(self, test_config_dir):
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

    def test_string(self, user_config):
        """
        Test we see strings as strings
        """
        valid_entries = ['test']

        run_a_checker(
            user_config,
            valid_entries,
            [],
            checkers.CheckString,
            item='username'
        )

        # Confirm that casting a string with uppers will auto produce lowers
        user_config.cfg['basic']['username'] = 'Test'

        b = checkers.CheckString(
            config=user_config, section='basic', item='username'
        )
        result = b.cast()
        assert result == 'test'

        # Check we can capture a single item list for strings
        b.is_list = True
        result = b.cast()
        assert result == ['test']

        # Check we capture the when a list is passed and were not expecting one
        b.is_list = False
        result = b.cast()
        assert not isinstance(result, list)

    @pytest.mark.parametrize(
        'value', [True, False, 'true', 'FALSE', 'yes', 'y', 'no', 'n']
    )
    def test_valid_booleans(self, user_config, value):
        """
        Test accepted boolean values
        """
        checker = define_checker(
            user_config,
            checkers.CheckBool,
            value,
            item='debug'
        )

        assert checker.check()[0] is None

    @pytest.mark.parametrize(
        'value', ['Fasle', 'treu', 'F', 'T']
    )
    def test_invalid_booleans(self, user_config, value):
        """
        Test rejected boolean values
        """
        checker = define_checker(
            user_config,
            checkers.CheckBool,
            value,
            item='debug'
        )

        assert checker.check()[0] is not None

    def test_float(self, user_config):
        """
        Test we see floats as floats
        """
        valid_entries = [-1.5, '2.5']
        invalid_entries = ['tough']

        run_a_checker(
            user_config,
            valid_entries,
            invalid_entries,
            checkers.CheckFloat,
            item='time_out'
        )

    def test_int(self, user_config):
        """
        Test we see int as ints and not floats
        """
        valid_entries = [10, '2', 1.0]
        invalid_entries = ['tough', '1.5', '']

        run_a_checker(
            user_config,
            valid_entries,
            invalid_entries,
            checkers.CheckInt,
            item='num_users'
        )

    def test_datetime(self, user_config):
        """
        Test we see datetime as datetime
        """
        valid_entries = ['2018-01-10 10:10', '10-10-2018', "October 10 2018"]
        invalid_entries = ['Not-a-date', 'Wednesday 5th']

        run_a_checker(
            user_config,
            valid_entries,
            invalid_entries,
            checkers.CheckDatetime,
            item='start_date'
        )

    def test_list(self, user_config):
        """
        Test our listing methods using lists of dates.
        """
        valid_entries = [
            '10-10-2019', ['10-10-2019'], ['10-10-2019', '11-10-2019']
        ]

        run_a_checker(
            user_config,
            valid_entries,
            [],
            checkers.CheckDatetime,
            item='epochs'
        )

    def test_directory(self, user_config):
        """
        Tests the base class for path based checkers
        """
        valid_entries = ["./"]
        invalid_entries = ['./somecrazy_location!/']

        run_a_checker(
            user_config,
            valid_entries,
            invalid_entries,
            checkers.CheckDirectory,
            item='tmp'
        )

        # ISSUE #44 check for default when string is empty
        user_config.cfg.update({'basic': {'tmp': ''}})

        value = checkers.CheckDirectory(
            config=user_config, section='basic', item='tmp'
        ).cast()

        assert os.path.split(value)[-1] == 'temp'

    def test_filename(self, user_config):
        """
        Tests the base class for path based checkers
        """
        # Remember paths are relative to the config
        valid_entries = ["../test_checkers.py"]
        invalid_entries = ['dumbfilename']

        run_a_checker(
            user_config,
            valid_entries,
            invalid_entries,
            checkers.CheckFilename,
            item='log'
        )

    def test_filename_empty_string(self, user_config):
        """
        ISSUE #44 check for default when string is empty
        """
        user_config.cfg.update({'basic': {'log': ''}})
        user_config.mcfg.cfg['basic']['log'].default = None

        value = checkers.CheckFilename(
            config=user_config, section='basic', item='log'
        ).cast()

        assert value is None

    def test_filename_empty_string_default_path(self, user_config):
        """
        ISSUE #44 check for default when string is empty but default is a path
        """
        user_config.cfg.update({'basic': {'log': ''}})
        user_config.mcfg.cfg['basic']['log'].default = 'log.txt'

        value = checkers.CheckFilename(
            config=user_config, section='basic', item='log'
        ).cast()

        assert os.path.split(value)[-1] == 'log.txt'

    def test_url(self, user_config):
        """
        Test our url checking.
        """
        valid_entries = ["https://google.com"]
        invalid_entries = ["https://micah_subnaught_is_awesome.com"]

        run_a_checker(
            user_config,
            valid_entries,
            invalid_entries,
            checkers.CheckURL,
            item='favorite_web_site'
        )

    def test_datetime_ordered_pairs(self, user_config):
        """
        Tests the ordered datetime pair checker which looks for <keyword>_start
        <keyword>_end pairs and confirms they occurs in the correct order.
        """
        # Test end dates com after start dates
        starts = ["1-01-2019", "2019-10-01", "1998-01-14 15:00:00"]
        ends = ["1-02-2019", "2019-10-02", "1998-01-14 19:00:00"]

        invalid_entries_starts = [
            "01-01-2020", "2020-06-01", "1998-01-14 20:00:00"
        ]
        invalid_entries_ends = [
            "01-01-2018", "2018-10-01", "1998-01-14 10:00:00"
        ]

        # Check for starts being before the end date
        for start, end, error_start, error_end in zip(starts, ends,
                                                      invalid_entries_starts,
                                                      invalid_entries_ends):
            # Check start values are before end values
            acfg = {'basic': {'end_date': end}}

            run_a_checker(
                user_config,
                [start],
                [error_start],
                checkers.CheckDatetimeOrderedPair,
                item="start_date",
                extra_config=acfg
            )

            # Check start values are before end values
            acfg = {'basic': {'start_date': start}}

            run_a_checker(
                user_config,
                [end],
                [error_end],
                checkers.CheckDatetimeOrderedPair,
                item="end_date",
                extra_config=acfg
            )

        # Check start end values are equal error
        acfg = {'basic': {'start_date': '2020-10-01'}}

        run_a_checker(
            user_config,
            ["2020-10-02"],
            ["2020-10-01"],
            checkers.CheckDatetimeOrderedPair,
            item="end_date",
            extra_config=acfg
        )

    def test_bounds(self, user_config):
        """
        MasterConfig options now have max and min values to constrain
        continuous types. This tests whether that works
        """
        run_a_checker(
            user_config,
            [1.0, 0.0, '0.5'],
            [1.1, -1.0, '10'],
            checkers.CheckFloat,
            item='fraction'
        )
