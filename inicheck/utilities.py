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


def is_kw_matched(single_word, kw_list, kw_count=1):
    """
    Checks to see if there are any keywords in the single word and returns
    a boolean

    Args:
        single_word: String to be examined for keywords
        kw_list: List of strings to look for inside the single word
        kw_count: Minimum Number of keywords to be found for it to be True

    Returns:
        boolean: Whether a keyword match was found
    """
    truths = [True for kw in kw_list if kw in single_word]

    if len(truths) >= kw_count:
        return True
    else:
        return False


def get_kw_match(potential_matches, kw_list, kw_count=1):
    """
    Loops through a list of potential matches looking for keywords in the
    list of strings being presented. When a match is found return its value.

    Args:
        potential_matches: List of strings to check
        kw_list: List of strings to look for inside the single word
        kw_count: Minimum Number of keywords to be found for it to be True

    Returns:
        result: The first potential found with the keyword match
    """
    result = False
    for potential in potential_matches:
        match = is_kw_matched(potential, kw_list, kw_count=kw_count)
        result = potential
        if match:
            break
    return result


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

def is_valid(value, cast_fn, expected_data_type):
    """
    Checks whether a value can be converted using the cast_fn function.

    Args:
        value: Value to be considered
        cast_fn: Function used to determine the validity, should throw an
                 excpetion if it cannot
        expected_data_type: string name of the expected data
    Returns:
        tuple:
            **valid (boolean)**: whether it could be casted
            **msg (string)**: Msg reporting what happen
    """

    try:
        value = cast_fn(value)
        valid = True
        msg = None

    except Exception as e:
        valid = False
        msg = "Expecting {0} received {1}".format(expected_data_type,
                                                  type(value).__name__)
    return valid, msg
