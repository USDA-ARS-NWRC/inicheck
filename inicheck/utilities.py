import os
from datetime import date, datetime

import dateparser


def parse_date(value):
    """
    Function used to cast value to datetime from String or date objects.
    Uses the `dateparser` library for String objects.

    All strings will be parsed in UTC timezone, but returned value will be
    timezone unaware. Hardcoded timezone setting to UTC for dateparser enables
    parsing of dates independent of the timezone set with the operating system.

    Args:
        value: string or date object
    Returns:
        converted: Datetime object of given value
    """

    if isinstance(value, datetime):
        return value

    elif isinstance(value, date):
        return datetime(value.year, value.month, value.day)

    else:
        converted = dateparser.parse(
            value, settings={
                'STRICT_PARSING': True,
                'TIMEZONE': 'UTC',
                'RETURN_AS_TIMEZONE_AWARE': False
            }
        )
        if converted is None:
            raise TypeError("{} is not a date".format(value))

        return converted


def find_options_in_recipes(recipes, choice_search,
                            action_kw, condition_position=0):
    """
    Looks through the master config at recipes and entries to determine if
    there are place the developer made distince choices, this is used in the
    inimake script to walk users through making their own config file from
    scratch.

    This function looks through and finds sections or items that match the
    conditional. Then it looks through the adj_config to determine if any
    sections/items are being removed as a result, then it finds those.
    If a section/item appears in a recipe condition and a removed by
    another trigger it is extremely likely these are choices.

    Args:
        mcfg: Recipes object from master config
        conditional: list of 3 focusing on what were looking for
        action_kw: action keyword is a string of what to look for in matching
                   choices where ever true is used will popoulate with every
                   item/section

    Returns:
        final_choices:

    """
    decisions = {}
    conditional = ["any" for i in range(3)]
    final_choices = []
    pos = condition_position

    # Gather which recipes might represent a decision point
    for r in recipes:
        choices = []

        for t_name, trigger in r.triggers.items():

            for condition in trigger.conditions:
                # if the position of interest is not a generic place holder
                if condition[pos] != "any":
                    # Look at how it adjusts the config
                    for k, v in r.adj_config.items():
                        # If our action word shows up then we know its a choice
                        if action_kw in v.keys():
                            choices.append(condition[pos])
                            # Look inside the adjustment for more choices
                            for kk, vv in v.items():
                                actions = [k, kk, vv]

                                if kk == action_kw:
                                    choices.append(actions[pos])

        # if the list is not empty add it

        if choices:
            final_choices.append(tuple(set(sorted(choices))))

    # Because there will be redundent sets of choices, we perform a set to
    # clean up
    return list(set(final_choices))


def ask_user(question, choices=None):
    """
    Asks the user which choice to make and handles incorrect choices.
    """
    valid = False
    if choices is None:
        choices = ["yes", "no"]

    if choices is not None:
        choice_str = "(" + ", ".join(choices) + ")\n"

    while not valid:
        msg = question + choice_str
        s = input(msg)
        if s not in choices:
            print("Invalid Choice: Try again.")
            valid = False
        else:
            valid = True
    return s


def ask_config_setup(choices_series, section=None, item=None,
                     num_questions=None):
    """
    Ask repeating questions for setting up a config
    """
    if section is None and item is None:
        msg = "Which of these sections do you want to use? "

    elif section is not None and item is None:
        msg = ("In section {}, Which of these items do you want to use? "
               "".format(section))

    else:
        msg = ("In section {} item {},  Which of these values do you want to "
               "use? ".format(section, item))

    if num_questions is None:
        num_questions = len(choices_series)

    # Add sections that we choose
    selections = []

    for i, c in enumerate(choices_series):
        count = "{}/{}: ".format(i + 1, num_questions)
        q = count + msg

        selections.append(ask_user(q, c))

    return selections


def remove_comment(string_entry):
    """
    Takes a single line and removes and .ini type comments.
    Also remove any spaces at the begining or end of a commented line
    """
    result = string_entry

    # Comment checking
    for c in '#;':
        if c in result:
            result = result.split(c)[0]

    return result


def mk_lst(values, unlst=False):
    """
    while iterating through several type of lists and items it is convenient to
    assume that we recieve a list, use this function to accomplish this. It also
    convenient to be able to return the original type after were done with it.
    """
    # Not a list, were not looking to unlist it. make it a list
    if not isinstance(values, list) and not unlst:
        values = [values]

    # We want to unlist a list we get
    if unlst:
        # single item provided so we don't want it a list
        if isinstance(values, list):
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
    if replace_str is None:
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
    if os.path.isabs(path):
        path = os.path.relpath(path, os.path.dirname(user_cfg_path))
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

        if match:
            result = potential
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

                if isinstance(cfg[sec][item], list):
                    out = ", ".join(cfg[sec][item])
                else:
                    out = cfg[sec][item]
                print('\t\t' + repr(out))
        except BaseException:
            print('\t recipe')


def pmcfg(cfg):
    """
    prints out the core config file to the prompt with a nice stagger Look for
    readability

    Args:
        cfg: dict of dict in a hierarchy of  {section, {items, values}}
    """

    for sec in cfg.keys():
        print(repr(sec))
        for item in cfg[sec].keys():
            print('\t' + item)
            obj = cfg[sec][item]
            for att in ['type', 'options', 'default', 'description']:
                value = getattr(obj, att)
                print('\t\t' + att)

                if isinstance(value, list):
                    out = ", ".join(value)
                else:
                    out = value
                print('\t\t\t' + repr(out))


def is_valid(value, cast_fn, expected_data_type, allow_none=False):
    """
    Checks whether a value can be converted using the cast_fn function.

    Args:
        value: Value to be considered
        cast_fn: Function used to determine the validity, should throw an
                 exception if it cannot
        expected_data_type: string name of the expected data
        allow_none: Boolean determining if none is valid
    Returns:
        tuple:
            **valid (boolean)**: whether it could be casted
            **msg (string)**: Msg reporting what happen
    """
    try:

        # Check for a non-none value
        if str(value).lower() != 'none':
            value = cast_fn(value)
            valid = True
            msg = None

        # Handle the error for none when not allowed
        elif not allow_none and str(value).lower() == 'none':
            valid = False
            msg = 'Value cannot be None'

        # Report all good for nones when they are allowed
        else:
            valid = True
            msg = None

    # Report an exception when the casting goes bad.
    except Exception as e:
        valid = False
        msg = "Expecting {0} received {1}".format(expected_data_type,
                                                  type(value).__name__)
    return valid, msg


def get_inicheck_cmd(config_file, modules=None, master_files=None):
    """
    Strings together an inicheck cli command based on modules and files

    """

    cmd = "inicheck -f {}".format(config_file)

    if master_files is not None:
        master_files = mk_lst(master_files)
        cmd += " -mf {}".format(" ".join(master_files))

    if modules is not None:
        modules = mk_lst(modules)
        cmd += " -m {}".format(" ".join(modules))

    return cmd
