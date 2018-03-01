from pandas import to_datetime
import inspect
import sys

def mk_lst(values, unlst=False):
    """
    while iterating through several type of lists and items it is convenient to
    assume that we recieve a list, use this function to accomplish this. It also
    convenient to be able to return the original type after were done with it.
    """

    if type(values) != list:
        values = [values]
    else:
        if unlst:
            if len(values)==1:
                values = values[0]

    return values

def remove_chars(orig_str,char_str, replace_str=None):
    """
    Removes all character in orig_str that are in char_str

    Args:
        orig_str: Original string needing cleaning
        char_str: String of characters to be removed
        replace_str: replace values with a character if requested

    Returns:
        string: orig_str with out any characters in char_str
    """
    if replace_str == None:
        clean_str = [c for c in orig_str if c not in char_str]
    else:
        clean_str = [c if c not in char_str else replace_str for c in orig_str]

    return "".join(clean_str)


def get_checkers(module = 'inicheck.checkers', keywords = []):
    """
    Args:
        module: The module to search for the classes

    Returns a dictionary of the classes available for checking config entries
    """
    keywords.append('check')

    funcs = inspect.getmembers(sys.modules[module], inspect.isclass)
    func_dict = {}

    for name,fn in funcs:
        checker_found = False
        k = name.lower()
        #Remove any keywords
        for w in keywords:
            if w in k:
                k = k.replace(w,'')
                checker_found = True
        if checker_found:
            func_dict[k] = fn

    return func_dict



def cast_variable(variable,type_value,available_types = None,ucfg = None):
    """
    Casts an object to the spectified type value

    Args:
        variable - some variable to be casted
        type_value - string value indicating type to cast.
        available_types - A dictionary of names and type check functions
        ucfg - users config object from class UserConfig

    Returns:
        value - The original variable now casted in type_value
    """
    variable = mk_lst(variable)
    type_value = str(type_value)
    value = []
    if available_types == None:
        available_types = get_checkers()

    for v in variable:
        option_found = False

        for name,fn in available_types.items():
            if type_value in name:
                b = fn(value = v, config = ucfg)
                value = b.cast()
                option_found = True

        if not option_found:
            raise ValueError("Unknown type_value prescribed. ----> {0}".format(type_value))

    return value


def pcfg(cfg):
    """
    prints out the config file to the prompt with a nice stagger Look for
    readability

    Args:
        cfg: dict of dict in a heirarcy of  {section, {items, values}}
    """

    for sec in cfg.keys():
        print(repr(sec))
        try:
            for item in cfg[sec].keys():
                print('\t'+item)
                if type(cfg[sec][item])==list:
                    out = ", ".join(cfg[sec][item])
                else:
                    out = cfg[sec][item]
                print('\t\t'+repr(out))
        except:
            print('\t recipe')
