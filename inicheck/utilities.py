import sys
import os

def remove_comment(string_entry):
    """
    Takes a single line and removes and .ini type comments.
    Also remove any spaces at the begining or end of a commented line
    """
    # Comment checking
    if '#' in string_entry:
        result = string_entry.split('#')[0]
    elif ';' in string_entry:
        result = string_entry.split(';')[0]
    else:
        result = string_entry

    return result


def mk_lst(values, unlst=False):
    """
    while iterating through several type of lists and items it is convenient to
    assume that we recieve a list, use this function to accomplish this. It also
    convenient to be able to return the original type after were done with it.
    """
    # Not a list, were not looking to unlist it. make it a list
    if type(values) != list and not unlst:
            values = [values]
    else:
        # We want to unlist a list we get
        if unlst:
            # single item provided so we don't want it a list
            if len(values) == 1:
                values = values[0]

    return values


def remove_chars(orig_str, char_str, replace_str=None):
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


def get_relative_to_cfg(path, user_cfg_path):
    """
    Converts a path so that all paths are relative to the config file

    Args:
        path: relative str path to be converted
        user_cfg_path: path to the users config file
    Returns:
        path: absolute path of the input considering it was relative to the cfg
    """
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.join(os.path.dirname(user_cfg_path),
                                                            path))
    return path


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
                print('\t' + item)
                values = cfg[sec][item]

                if type(cfg[sec][item]) == list:
                    out = ", ".join(cfg[sec][item])
                else:
                    out = cfg[sec][item]
                print('\t\t' + repr(out))
        except:
            print('\t recipe')


def pmcfg(cfg):
    """
    prints out the core config file to the prompt with a nice stagger Look for
    readability

    Args:
        cfg: dict of dict in a heirarcy of  {section, {items, values}}
    """

    for sec in cfg.keys():
        print(repr(sec))
        for item in cfg[sec].keys():
            print('\t' + item)
            obj = cfg[sec][item]
            for att in ['type', 'options', 'default', 'description']:
                value = getattr(obj, att)
                print('\t\t' + att)

                if type(value) == list:
                    out = ", ".join(value)
                else:
                    out = value
                print('\t\t\t' + repr(out))
