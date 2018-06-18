'''
Functions for checking valus in a config file and producing errors and warnings
'''
import os
from pandas import to_datetime


class GenericCheck(object):
    def __init__(self, **kwargs):

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
            **(boolean, msg)**: True or False whether value valid and
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
        self.type = 'str'
        # Function used for casting to types
        self.type_func = str

    def is_valid(self):
        """
        Checks for type validity
        """
        msg = None
        self.msg_level = 'error'

        try:
            self.value = self.cast()
            valid = True

        except:
            msg = "Expecting {0} received {1}".format(self.type,type(self.value).__name__)
            valid = False

        return valid,msg

    def cast(self):
        """
        Attempts to return the casted value
        """
        return self.type_func(self.value)


class CheckDatetime(CheckType):
    """
    Check values that are declared as type datetime.
    """

    def __init__(self, **kwargs):

        super(CheckDatetime, self).__init__(**kwargs)
        self.type_func = to_datetime
        self.type = 'datetime'


class CheckFloat(CheckType):
    """
    Float checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckFloat, self).__init__(**kwargs)
        self.type_func = float
        self.type = 'float'


class CheckInt(CheckType):
    """
    integer checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckInt, self).__init__(**kwargs)
        self.type_func = self.cast_float_int
        self.type = 'int'


    def cast_float_int(self,value):
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
            raise ValueError("Expecting integer and received float with non-zero decimal")

        return self.value


class CheckBool(CheckType):
    """
    Boolean checking whether a value of the right type.
    """

    def __init__(self, **kwargs):

        super(CheckBool, self).__init__(**kwargs)
        self.type_func = bool
        self.type = 'bool'
        self.affirmatives = ['y', 'yes', 'true']
        self.negatives = ['n', 'no', 'false']

    def cast(self):

        v = str(self.value).lower()
        if v in self.affirmatives:
            self.value = True

        elif v in self.negatives:
            self.value = False
        else:
            raise ValueError("Value {0} not coercable to boolean."
                             "".format(self.value))

        return self.value


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
        self.root_loc = self.config.filename

        self.dir_path = False

        # Path should alsways be absolute or relative to the config file path
        if self.value != None and self.root_loc != None:
            if not os.path.isabs(self.value):
                p = os.path.expanduser(os.path.dirname(self.root_loc))
                self.value = os.path.abspath(os.path.join(p, self.value))

    def is_valid(self):
        """
        Checks for existing filename
        """

        if self.dir_path:
            exists = os.path.isdir(self.value)
        else:
            exists = os.path.isfile(self.value)

        return exists,self.message

    def cast(self):
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
    Checks whether a directory exists.
    """

    def __init__(self, **kwargs):
        super(CheckFilename, self).__init__(**kwargs)
        self.message = "File does not exist."


class CheckCriticalFilename(CheckFilename):
    """
    Checks whether a critical file exists.
    """

    def __init__(self, **kwargs):
        super(CheckCriticalFilename, self).__init__(**kwargs)
        self.msg_level = 'error'


class CheckCriticalDirectory(CheckDirectory):
    """
    Checks whether a critical directory exists.
    """

    def __init__(self, **kwargs):
        super(CheckCriticalDirectory, self).__init__(**kwargs)
        self.msg_level = 'error'
