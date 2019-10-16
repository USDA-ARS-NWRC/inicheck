'''
Functions for checking values in a config file and producing errors and warnings
'''

import os
from pandas import to_datetime
from .utilities import mk_lst, is_valid, is_kw_matched, get_kw_match
import requests


class GenericCheck(object):
    """
    Generic Checking class. Every class thats a checker should inherit from this
    class. This class is used like:

    Every check will run the check().


    Attributes:
        message: String message to report if the value passed is not valid
        msg_level: Urgency of the message which can be either a warning or error
        value: value to be checked, casted, and reported on
        config: UserConfig object that the item/value being check resides

        e.g.
            b = GenericCheck(value=v, config=ucfg)
            issue = b.check()
            if issue != None:
                log.info(b.message)
    """

    def __init__(self, **kwargs):
        """
        Instatiates the check and setups the message, value and msg_level.

        Args:
            value: Value to be checked
            config: UserConfig object
            is_listed: Boolean determining whether to expect a list or not

        Raises:
            ValueError: Raises an error if Kwargs config or value is not
                        provided.
        """

        if 'value' not in kwargs.keys():
            raise ValueError("Must provided at least keyword value to "
                             "Checkers.")
        if 'config' not in kwargs.keys():
            raise ValueError("Must provided at least keyword config to"
                             " Checkers.")

        self.message = None
        self.msg_level = 'warning'
        self.value = kwargs["value"]

        self.config = kwargs["config"]

        if not self.msg_level.lower() in ['warning', 'error']:
            raise ValueError("msg_level = {0} not allowed."
                             "".format(self.msg_level))

    def is_valid(self):
        """
        Abstract function for defining how a value is checked for validity

        Args:
            value: Value that is going to be check for validity

        Returns:
            **(boolean, msg)**: Boolean result whether value valid and
                              correspond error message if it is not
        """
        pass

    def check(self):
        """
        Function that is ran by the checking function of the user config to
        return useful message to instruct user

        Args:
            value: value to be check for validity
        Returns:
            msg: None is the entry is valid, else returns self.message
        """

        valid, issue = self.is_valid()

        if valid:
            msg = None
        else:
            msg = issue
        return msg


class CheckType(GenericCheck):
    """
    Base class for type checking whether a value of the right type.
    """

    def __init__(self, **kwargs):
        super(CheckType, self).__init__(**kwargs)

        self.type = 'string'
        kwargs_requires = ["item","section", "config", "is_list", 'maximum',
                                                                  'minimum']

        # Allow None as a value?
        self.allow_none = False

        for kw in kwargs_requires:
            if kw in kwargs.keys():
                value = kwargs[kw]
            else:
                value = None

            setattr(self, kw, value)

        # Function used for casting to types
        self.type_func = str

        # Allow users to specify an option to be a list
        if self.is_list == None:
            self.is_list = False

        # Allow developers to specify bounds for certain types
        self.bounded = False

    def check_bounds(self):
        """
        Checks the developers values for bounded checks on the config file.

        If self.max or self.min == None then it is assumed no bounds on either
        end.

        Function only runs when requested.
        """

        valid = True

        msg = "Value must be"

        if self.bounded:
            # Grab it from the config
            if self.config != None:
                max_value = self.config.mcfg.cfg[self.section][self.item].max
                min_value = self.config.mcfg.cfg[self.section][self.item].min

            # grab the args
            else:
                max_value = self.maximum
                min_value = self.minimum

            # Check upper and lower bounds
            if self.value != None:
                value = self.type_func(self.value)

                if min_value != None:
                    min_value = self.type_func(min_value)
                    msg += " greater than {}".format(min_value)

                    if value < min_value:
                        valid = False

                if max_value != None:
                    if min_value != None:
                        msg += " and"

                    max_value = self.type_func(max_value)
                    msg += " less than {}".format(max_value)

                    if value > max_value:
                        valid = False

            # Throw error if max or min is set and value is none.
            elif value == None and (max_value != None or min_value != None):
                valid == False
                msg = "Value cannot be None"

            if valid:
                msg = None

        return valid, msg

    def is_it_a_lst(self):
        """
        Check to see if an option should be a list of not and convert it if
        necessary.
        * If it is a list, check for single value lists and convert it,
          return false.
        * If it is a list and not single item, return True
        * If its not a list return false

        """
        if type(self.value) == list:
            # Its list but its a single item
            if len(self.value) == 1:

                self.value = mk_lst(self.value, unlst=True)
                return False

            # Its a list and not a single item
            else:
                return True

        # not a list, its good
        else:
            return False

    def is_valid(self):
        """
        Checks for type validity

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """
        msg = None
        self.msg_level = 'error'

        # Provide a list check
        currently_a_list = self.is_it_a_lst()

        if currently_a_list and not self.is_list:
            msg = "Expected single value received list"
            valid = False

        else:
            valid, msg = is_valid(self.value, self.type_func, self.type,
                                              allow_none=self.allow_none)

        # Check for bounds
        if valid:
            valid, msg = self.check_bounds()

        return valid, msg

    def cast(self):
        """
        Attempts to return the casted value
        """
        if type(self.value) == str:
            if self.value.lower() == "none":
                return None
            else:
                return  self.type_func(self.value)

        elif self.value != None:
            return  self.type_func(self.value)

        else:
            return None

class CheckDatetime(CheckType):
    """
    Check values that are declared as type datetime. Parses anything that pandas
    to_datetime can parse.
    """

    def __init__(self, **kwargs):

        super(CheckDatetime, self).__init__(**kwargs)
        self.type_func = to_datetime
        self.type = 'datetime'

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

    def is_corresponding_valid(self):
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
        init_kw = ["start",'begin']
        final_kw = ['stop','end']

        # First check whether our item has a kw
        is_start = is_kw_matched(self.item, init_kw)
        is_end = is_kw_matched(self.item, final_kw)

        if is_start and not is_end:
            # Look for a corresponding end
            corresponding = get_kw_match(self.cfg_dict.keys(), final_kw)

        elif is_end and not is_start:
            # Look for the start
            corresponding = get_kw_match(self.cfg_dict.keys(), init_kw)

        else:
            raise ValueError("Ordered Date time pairs must be distinguishable "
                             " by item name. {} was either found to have both "
                             " sets of keywords or none of them."
                             "".format(self.item))

        # Is corresponding castable?
        corresponding_val = self.cfg_dict[corresponding]

        valid, msg = is_valid(corresponding_val, self.type_func, self.type)
        if valid:
            corresponding_val = self.type_func(corresponding_val)
            value = self.type_func(self.value)

            if is_start:
                # validity check
                order_valid = value < corresponding_val
                incorrect_context = "after"

            elif is_end:
                # validity check
                order_valid = value > corresponding_val
                incorrect_context = "before"

            msg = "Date is {} {} value".format(incorrect_context, corresponding)

        valid = valid and order_valid

        return valid, msg

    def is_valid(self):
        """
        Checks whether it convertable to datetime, then checks for order.

        Returns:
            valid: boolean representing whether the valid
            msg: issue report string if there is an issue, otherwise returns
                 None
        """
        # Check for the datetime first
        valid, msg = is_valid(self.value, self.type_func, self.type)

        if valid:
            valid, msg = self.is_corresponding_valid()

        return valid, msg


class CheckFloat(CheckType):
    """
    Float checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckFloat, self).__init__(**kwargs)
        self.type_func = float
        self.type = 'float'

        # Can be bounded but not required
        self.bounded = True

class CheckInt(CheckType):
    """
    Integer checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckInt, self).__init__(**kwargs)
        self.type = 'int'
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
            self.value: the value converted
        """

        self.value = float(value)

        if self.value.is_integer():
            self.value = int(self.value)

        else:
            raise ValueError("Expecting integer and received float with "
                            " non-zero decimal")
        return self.value


class CheckBool(CheckType):
    """
    Boolean checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckBool, self).__init__(**kwargs)
        self.type = 'bool'
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
    Float checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckString, self).__init__(**kwargs)
        self.type_func = str
        self.type = 'string'


class CheckPath(CheckType):
    """
    Checks whether a Path exists.
    """

    def __init__(self, **kwargs):

        super(CheckPath, self).__init__(**kwargs)

        # Allow None as a value?
        self.allow_none = False

        self.root_loc = self.config.filename

        self.dir_path = False

        # Path should alsways be absolute or relative to the config file path
        if type(self.value) == str:
            if self.value.lower() == "none":
                self.value = None

        if self.value != None and self.root_loc != None:
            if not os.path.isabs(self.value):
                p = os.path.expanduser(os.path.dirname(self.root_loc))
                self.value = os.path.abspath(os.path.join(p, self.value))

    def is_valid(self):
        """
        Checks for existing filename
        """
        # This avoids crashing on os.posix on none type
        if self.value == None:
            if self.allow_none:
                exists = True
            else:
                exists = False

        elif self.dir_path:
            exists = os.path.isdir(self.value)

        else:
            exists = os.path.isfile(self.value)

        return exists, self.message

    def cast(self):
        """
        Special casting function to just pass the path through
        """

        return self.value


class CheckDirectory(CheckPath):
    """
    Checks whether a directory exists.
    """

    def __init__(self, **kwargs):
        super(CheckDirectory, self).__init__(**kwargs)
        self.dir_path = True
        self.message = "Directory does not exist."


class CheckFilename(CheckPath):
    """
    Checks whether a directory exists. These are files that the may be created
    or not necessary to run.
    """

    def __init__(self, **kwargs):
        super(CheckFilename, self).__init__(**kwargs)
        self.message = "File does not exist."



class CheckCriticalFilename(CheckFilename):
    """
    Checks whether a critical file exists. This would be any files that absolutely
    have to exist to avoid crashing the software. These are static files.
    """

    def __init__(self, **kwargs):
        super(CheckCriticalFilename, self).__init__(**kwargs)
        self.msg_level = 'error'

class CheckDiscretionaryCriticalFilename(CheckCriticalFilename):
    """
    Checks whether a an optional file exists that may change software behavior
    by being present. In otherwords, this can be none and still valid. If the not
    then it registers an error if the string doesn't exist.
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

class CheckURL(CheckType):
    """
    Check URLs to see if it can be connected to.
    """

    def __init__(self, **kwargs):

        super(CheckURL, self).__init__(**kwargs)
        self.type = 'url'
        self.msg_level = 'error'

    def is_valid(self):
        """
        Makes a request to the URL to determine the validity
        """
        # Attempt to establish a connection
        try:
            r = requests.get(self.value)

        except Exception as e:
            self.message = "Invalid connection or URL"
            r = None

        exists = False
        if r != None:
            if r.status_code == 200:
                exists = True
            else:
                self.message = "Webpage does not exist"

        return exists, self.message
