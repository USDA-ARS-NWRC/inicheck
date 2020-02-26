'''
Functions for checking values in a config file and producing errors and warnings
'''

import os
from functools import partial

import requests

from .utilities import (get_kw_match, is_kw_matched, is_valid, mk_lst,
                        parse_date)


class GenericCheck(object):
    """
    Generic Checking class. Every class thats a checker should inherit from this
    class. This class is used like:

    Every check will run the check().

    Attributes:
        message: String message to report if the value passed is not valid
        msg_level: Urgency of the message which can be either a warning or error
        values: value to be checked, casted, and reported on
        config: UserConfig object that the item/value being check resides
        type: string name representing the datatype which is based off the class
              name
        is_list: Boolean specifying the resulting values as a list or not
        allow_none: Boolean specifying the values can contain a value

        E.G.
            b = GenericCheck(section='test', item= 'tiem1', config=ucfg)
            issue = b.check()
            if issue != None:
                log.info(b.message)
    """

    def __init__(self, **kwargs):
        """
        Instatiates the check and setups the message, value and msg_level.

        Args:
            section: Name of the section contain the value being evaluated
            item: Name of the item in section which has a value being evaluated
            config: UserConfig object containing

        Raises:
            ValueError: Raises an error if Kwargs section, item, config is not
                        provided.
        """

        # Keywords are more convenient to use, make these ones required
        required = ["section", "item", "config"]
        for req in required:
            if req not in kwargs.keys():
                raise ValueError("Must provided at least keywords {} to "
                                 "Checkers.".format(", ".join(required)))
            else:
                setattr(self, req, kwargs[req])

        # initial error messgae is nothing
        self.message = None

        # Initial level of concern is just a warning (can also be error)
        self.msg_level = 'warning'

        if not self.msg_level.lower() in ['warning', 'error']:
            raise ValueError("msg_level = {0} not allowed."
                             "".format(self.msg_level))

        # Initial values are set from the config directly, can be a list
        self.values = self.config.cfg[self.section][self.item]

        # Are the values received supposed to be a list?
        self.is_list = self.config.mcfg.cfg[self.section][self.item].listed

        # Allow None as a value?
        self.allow_none = self.config.mcfg.cfg[self.section][self.item].allow_none

        # Auto retrieve the type name from the class name which is always
        # Check<type name>
        self.type = type(self).__name__.lower().replace('check', '')

    def is_it_a_lst(self, values):
        """
        This checks to see if the original entry was a list or not.
        So instead of evaluating self.values  which is always a single item,
        we evaluate self.config[self.section][self.item]

        Args:
            values: The uncasted entry from a config file section and item,
                    can be a list or a single item

        Returns:
            boolean: True if its a list false if it is not.
        """
        # Grab the original values and see if theyre in a list
        if isinstance(values, list):
            return True

        # not a list, its good
        else:
            return False

    def is_valid(self, value):
        """
        Abstract function for defining how a value is checked for validity.
        It should always be used in check(). Is valid should always return
        a boolean whether the result is valid, and the issue as a string stating
        the problem. If no issue it should still return None.

        Args:
            value: Single value to be evaluated

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """
        pass

    def check(self):
        """
        Function that is ran by the checking function of the user config to
        return useful message to instruct user.

        Returns:
            msgs: None if the entry is valid, else returns self.message
        """
        valids = []
        issues = []

        for v in mk_lst(self.values):
            valid, issue = self.is_valid(v)
            issues.append(issue)

        return issues


class CheckType(GenericCheck):
    """
    Base class for type checking whether a value of the right type. Here extra
    Attributes are added such as maximum and minimum.

    Attributes:
            minimum: Minimum value for bounded entries.
            maximum: Maximum value for bounded entries.
            type_func: Function used to cast the data to the desired type.
                      Default - str()
            bounded: Boolean indicating if a value can be limited by a min or max.
    """

    def __init__(self, **kwargs):
        super(CheckType, self).__init__(**kwargs)

        req = ['maximum', 'minimum']
        for kw in req:
            if kw in kwargs.keys():
                value = kwargs[kw]
            else:
                value = None

            setattr(self, kw, value)

        # Default Function used for casting to types
        self.type_func = str

        # Allow developers to specify bounds for certain types
        self.bounded = False

        # Default issue for type check is error
        self.msg_level = 'error'

    def check_bounds(self, value):
        """
        Checks the users values to see if its in the bounds specified by the
        developer.

        If self.max or self.min == None then it is assumed no bounds on either
        end.

        Function only runs when bounded = True in the master config.

        Args:
            value: Single value being evaluated against the bounds.

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """

        valid = True
        msg = None

        if self.bounded:
            msg = "Value must be"

            # Grab it from the config
            if self.config is not None:
                max_value = self.config.mcfg.cfg[self.section][self.item].max
                min_value = self.config.mcfg.cfg[self.section][self.item].min

            # Check upper and lower bounds
            if value is not None:
                value = self.type_func(value)

                if min_value is not None:
                    min_value = self.type_func(min_value)
                    msg += " greater than {}".format(min_value)

                    if value < min_value:
                        valid = False

                if max_value is not None:
                    if min_value is not None:
                        msg += " and"

                    max_value = self.type_func(max_value)
                    msg += " less than {}".format(max_value)

                    if value > max_value:
                        valid = False

            # Throw error if max or min is set and value is none.
            elif value is None and (max_value is not None or min_value is not None):
                valid == False
                msg = "Value cannot be None"

            if valid:
                msg = None

        return valid, msg

    def check_list(self):
        """
        Checks to see if self.values provided are in a list and if they should be.

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable in terms of being a list
                **msg** - string to print if value is not valid.
        """

        # Is it currently a list
        currently_a_list = self.is_it_a_lst(self.values)

        valid = True
        msg = None

        # NOTE This is for checking single items but we can cast these no matter what so its viable.
        # # Is it supposed to be a list and isn't?
        # if self.is_list and not currently_a_list:
        #     valid = False
        #     msg = "Expected list recieved single item"

        # Not supposed to be a list and is one?
        if not self.is_list and currently_a_list:
            msg = "Expected single value received list."
            valid = False

        return valid, msg

    def check_options(self, value):
        """
        Check to see if the current value being evaluated is also in the list of
        provided options in the master config. Only runs if options were
        provided.

        Args:
            value: A single value which is checked against the list of options
                   in the master config

        Returns:
            tuple:
                **valid** - Boolean whether the value was in the options list
                **msg** - string to print if value is not in the options.

        """
        valid = True
        msg = None

        if self.config.mcfg.cfg[self.section][self.item].options:

            # If it is not in the options its invalid
            options = self.config.mcfg.cfg[self.section][self.item].options

            if str(value).lower() not in options:
                msg = "Not a valid option"
                valid = False

        return valid, msg

    def is_valid(self, value):
        """
        Checks  a single value using the specified type function.
        All checkers should have a version of this function.

        Args:
            value: Single value to be evaluated

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """
        valid, msg = is_valid(value, self.type_func, self.type,
                              allow_none=self.allow_none)
        return valid, msg

    def check_none(self, value):
        """
        Check a single value if it is None and whether that is accecptable.

        Args:
            value: single value to be assessed whether none is valid

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """
        # You got nones and you can't have them
        if not self.allow_none and str(value).lower() == 'none':
            valid = False
            msg = "Value cannot be None"
        else:
            valid = True
            msg = None

        return valid, msg

    def check(self):
        """
        Types are checked differently than some general checker.
        The checking goes through 5 steps and if anyone of them is invalid
        it will not check the rest. The process is as follows:

        1. Check if self.values should be a list or not.

        2. Check if a value in self.values should be None or not.

        3. Check for options and if a single value from self.values is among them.

        4. Check is a single value is valid according to self.valid.

        5. Check if a single value is inside any defined bounds.


        Returns:
            list: A list equal to the len(self.values) of either None or
                  strings relaying the issues found
        """
        msgs = []
        valids = []

        # 1. Check for lists
        valid, msg = self.check_list()
        msgs.append(msg)
        valids.append(valid)

        if valid:
            # We clear the nones since check_list is only checking the whole
            # entry
            msgs = []
            valids = []

            for v in mk_lst(self.values):

                # 2. Check if none is allowed.
                valid, msg = self.check_none(v)

                if str(v).lower() != "none":
                    # 3. Check for option constraints
                    if valid:
                        valid, msg = self.check_options(v)

                    # 4. Check for type constraints
                    if valid:
                        valid, msg = self.is_valid(v)

                    # 5. Check for bounding constraints
                    if valid:
                        valid, msg = self.check_bounds(v)

                msgs.append(msg)
                valids.append(valid)

        return msgs

    def cast(self):
        """
        Attempts to return the casted values of the each value in self.values.

        This is performed with self.type_func unless the value is none in which
        we return None (NoneType)

        Returns:
            list: All values from self.values casted correctly
        """

        result = []

        for v in mk_lst(self.values):

            # 1. Manage nones:
            if str(v).lower() == "none":
                result.append(None)

            # 2. Manage the value types
            else:
                result.append(self.type_func(v))

        # 3. Manage the list
        if not self.is_list or (len(result) == 1 and result[0] is None):
            result = mk_lst(result, unlst=True)

        return result


class CheckDatetime(CheckType):
    """
    Check values that are declared as type datetime. Parses anything that dateparser can parse.
    """

    def __init__(self, **kwargs):

        super(CheckDatetime, self).__init__(**kwargs)
        self.type_func = parse_date


class CheckDatetimeOrderedPair(CheckDatetime):
    """
    Checks to see if start and stop based items are infact in fact ordered
    in the same section.

    Requires keywords section and item to ba passed as keyword args.
    Looks for keywords start/begin or stop/end in an item name. Then looks for a
    corresponding match with the opposite name.

    .. code-block:: ini

        start_simulation: 10-01-2019
        stop_simulation: 10-01-2017

    Would return an issue.

    This when checking the start will look for "simulation" with a
    temporal keyword reference in an item name like end/stop etc.
    Then it will attempt to determine them to be before.
    """

    def __init__(self, **kwargs):
        super(CheckDatetimeOrderedPair, self).__init__(**kwargs)

        self.cfg_dict = kwargs['config'].cfg[self.section]
        self.msg_level = "error"

    def is_corresponding_valid(self, value):
        """
        Looks in the config section for an opposite match for the item.

        e.g.
             if we are checking start_simulation, then we look for
             end_simulation

        Returns:
            corresponding: item name in the config section corresponding with
                           item being checked
        Raises:
            ValueError: raises an error if the name contains both sets or None
                        of keywords
        """
        init_kw = ["start", 'begin']
        final_kw = ['stop', 'end']

        # First check whether our item has a kw
        is_start = is_kw_matched(self.item, init_kw)
        is_end = is_kw_matched(self.item, final_kw)

        # The current item is the beginning of an ordered datetime pair
        if is_start and not is_end:
            # Look for a corresponding end
            corresponding = get_kw_match(self.cfg_dict.keys(), final_kw)

        # The current item is the end of an ordered datetime pair
        elif is_end and not is_start:
            # Look for the corresponding start
            corresponding = get_kw_match(self.cfg_dict.keys(), init_kw)

        else:
            raise ValueError("Ordered Datetime pairs must be distinguishable "
                             " by item name. {} was either found to have both "
                             " sets of keywords or none of them."
                             " ".format(self.item))

        # Is corresponding castable?
        corresponding_val = self.cfg_dict[corresponding]
        valid, msg = is_valid(corresponding_val, self.type_func, self.type)

        if valid:
            corresponding_val = self.type_func(corresponding_val)
            value = self.type_func(value)

            # Check for equal value entries
            if value == corresponding_val:
                # Message context stating start value is euqla to end value
                incorrect_context = 'equal to'
                order_valid = False

            # Check start value is before end value
            elif is_start:
                order_valid = value < corresponding_val
                # Message context stating start value is after end value
                incorrect_context = "after"

            # Check end value is after start value
            elif is_end:
                order_valid = value > corresponding_val
                # Message context stating end value is before start value
                incorrect_context = "before"

            msg = "Date is {} {} value".format(
                incorrect_context, corresponding)

        valid = valid and order_valid

        return valid, msg

    def is_valid(self, value):
        """
        Checks whether it convertable to datetime, then checks for order.

        Args:
            value: Single value to be evaluated

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """
        valid, msg = is_valid(value, parse_date, self.type)

        if valid:
            valid, msg = self.is_corresponding_valid(value)

        return valid, msg


class CheckFloat(CheckType):
    """
    Float checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckFloat, self).__init__(**kwargs)
        self.type_func = float

        # Can be bounded but not required
        self.bounded = True


class CheckInt(CheckType):
    """
    Integer checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckInt, self).__init__(**kwargs)
        self.type_func = self.convert_to_int

        # Can be bounded but not requried
        self.bounded = True

    def convert_to_int(self, value):
        """
        When expecting an integer, it is convenient to automatically convert
        floats to integers (e.g. 6.0 --> 6) but its pertinent to catch when the
        input has a non-zero decimal and warn user (e.g. avoid 6.5 --> 6)

        Args:
            value: The value to be casted to integer
        Returns:
            value : the value converted
        """

        value = float(value)

        if value.is_integer():
            value = int(value)

        else:
            raise ValueError("Expecting integer and received float with "
                             " non-zero decimal")
        return value


class CheckBool(CheckType):
    """
    Boolean checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckBool, self).__init__(**kwargs)
        self.type_func = self.convert_bool

        self.affirmatives = ['y', 'yes', 'true']
        self.negatives = ['n', 'no', 'false']

    def convert_bool(self, value):
        """
        Function used to cast values to boolean

        Args:
            value:  value(s) to be casted

        Returns:
            value: Value returned as a boolean
        """

        v = str(value).lower()

        if v in self.affirmatives:
            result = True

        elif v in self.negatives:
            result = False

        else:
            raise ValueError("Value {0} not coercable to boolean."
                             "".format(value))

        return result


class CheckString(CheckType):
    """
    String checking non paths and passwords. These types of strings are always
    lower case.
    """

    def __init__(self, **kwargs):

        super(CheckString, self).__init__(**kwargs)

        # Most strings types that are not paths or passowrds should be lower
        # case
        self.type_func = lambda x: str(x).lower()


class CheckPassword(CheckType):
    """
    No checking of any kind here other than avoids alterring it.
    """

    def __init__(self, **kwargs):

        super(CheckPassword, self).__init__(**kwargs)
        self.type_func = str


class CheckPath(CheckType):
    """
    Checks whether a Path exists. Base for checking if paths exist.
    """

    def __init__(self, **kwargs):

        super(CheckPath, self).__init__(**kwargs)

        # Allow None as a value?
        self.allow_none = False

        self.root_loc = os.path.dirname(os.path.abspath(self.config.filename))
        self.dir_path = False
        self.type_func = self.make_abs_from_cfg

    def is_valid(self, value):
        """
        Checks for existing filename

        Args:
            value: Single value to be evaluated

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """
        v = self.make_abs_from_cfg(value)

        if self.dir_path:
            valid = os.path.isdir(v)

        else:
            valid = os.path.isfile(v)

        if valid:
            msg = None
        else:
            msg = self.message

        return valid, msg

    def make_abs_from_cfg(self, value):
        """
        Looks at a path and determines its absolute path. All paths should be
        either absolute or relative to the config file in which they will be
        converted to absolute paths

        Args:
            value: single path or filename
        Returns:
            str: absolute path or filename
        """
        # Watch out for empty strings, assume default
        if value == '':
            value = self.config.mcfg.cfg[self.section][self.item].default
        if str(value).lower() != 'none':
            if not os.path.isabs(value):
                value = os.path.abspath(os.path.join(self.root_loc, value))

        return value


class CheckDirectory(CheckPath):
    """
    Checks whether a directory exists. These directories are allowed to be none
    and only warn when they do not exist. E.g. Output folders
    """

    def __init__(self, **kwargs):
        super(CheckDirectory, self).__init__(**kwargs)
        self.dir_path = True
        self.allow_none = True
        self.message = "Directory does not exist."
        self.msg_level = "warning"


class CheckFilename(CheckPath):
    """
    Checks whether a directory exists. These are files that the may be created
    or not necessary to run. E.g. Log files
    """

    def __init__(self, **kwargs):
        super(CheckFilename, self).__init__(**kwargs)
        self.message = "File does not exist."
        self.allow_none = True
        self.msg_level = "warning"


class CheckCriticalFilename(CheckFilename):
    """
    Checks whether a critical file exists. This would be any files that
    absolutely have to exist to avoid crashing the software. These are static
    files.
    """

    def __init__(self, **kwargs):
        super(CheckCriticalFilename, self).__init__(**kwargs)
        self.msg_level = 'error'
        self.allow_none = False


class CheckDiscretionaryCriticalFilename(CheckCriticalFilename):
    """
    Checks whether a an optional file exists that may change software behavior
    by being present. In other words, this can be none and still valid. If the
    not then it registers an error if the string doesn't exist as path.
    """

    def __init__(self, **kwargs):
        super(CheckDiscretionaryCriticalFilename, self).__init__(**kwargs)
        self.allow_none = True


class CheckCriticalDirectory(CheckDirectory):
    """
    Checks whether a critical directory exists. This is for any directories
    that have to exist prior to launching some piece of software.
    """

    def __init__(self, **kwargs):
        super(CheckCriticalDirectory, self).__init__(**kwargs)
        self.msg_level = 'error'
        self.allow_none = True


class CheckURL(CheckType):
    """
    Check URLs to see if it can be connected to.
    """

    def __init__(self, **kwargs):

        super(CheckURL, self).__init__(**kwargs)
        self.msg_level = 'error'

    def is_valid(self, value):
        """
        Makes a request to the URL to determine the validity.

        Args:
            value: Single value to be evaluated

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.

        """
        # Attempt to establish a connection
        try:
            r = requests.get(value, timeout=5)

        except Exception as e:
            msg = "Invalid connection or URL"
            r = None

        valid = False
        msg = "Webpage does not exist"

        if r is not None:
            if r.status_code == 200:
                valid = True
                msg = None

        return valid, msg
