import os
from collections import OrderedDict

from .utilities import remove_chars, remove_comment


def read_config(fname):
    """
    Opens and reads in the config file in its most raw form.
    Creates a dictionary of dictionaries that contain the string result

    Args:
        fname: Real path to the config file to be opened
    Returns:
        config: dict of dicts containing the info in a config file
    """
    with open(fname, encoding='utf-8') as f:
        lines = f.readlines()
        f.close()

    sections = parse_sections(lines)
    sec_and_items = parse_items(sections)
    config = parse_values(sec_and_items)

    return config


def parse_entry(info, item=None, valid_names=None):
    """
    Parse the values found in the master config where the entries are a little
    more complicated. Specifically this deals with syntax issues and whether
    a entry option is valid or not.

    This should be used only after knowning the section and item.

    Args:
        info: a single line or a List of lines to parse containing master
             config options
        item: Item name were parsing. Only for reporting errors purposes
        valid_names: valid property names to be parsing.

    Returns:
        properties: dictionary containing the properties as keys
    """

    properties = OrderedDict()
    if not isinstance(info, list):
        info = [info]

    last_three = []

    for s in info:

        if '=' in s:
            a = s.split('=')

        else:
            raise ValueError('\n\nMaster Config file missing an equals sign in'
                             ' entry or missing a comma right before the item '
                             '"{0}" in the entry:\n"{1}"\nIssue generated from:'
                             ' \n>> "{2}"'.format(item, info, s))

        name = (a[0].lower()).strip()

        # Check for constraints on potential names of entries
        if valid_names is not None and name not in valid_names or len(a) > 2:
            raise ValueError("\nInvalid property set in the master config file,"
                             " available options are: \n * {0}\n"
                             "\nIf this is supposed to be a recipe, you may have"
                             " forgotten to add keyword 'recipe' to the section"
                             " name.\nIssue generated from: \n>> '{1}'"
                             "".format("\n * ".join(valid_names), s))

        value = a[1].strip()

        result = []
        value = value.replace('\n', " ")
        value = value.replace('\t', "")

        # Is there a list of values provided?
        if '[' in value:
            if ']' not in value:
                raise ValueError('Missing bracket or commas used in a list'
                                 ' instead of spaces in config file under'
                                 ' {0} in the entry:\n"{1}"'.format(name, info))
            else:
                value = (''.join(c for c in value if c not in '[]'))
                value = value.split(' ')

        properties[name] = value
    return properties


def parse_sections(lines):
    """
    Returns a dictionary containing all the sections as keys with a single
    string of the contents after the section

    Args:

        lines: a list of string lines containing all the raw info of a cfg file

    Returns:
        sections: dictionary containing keys that are the section names and
                  values that are strings of the contents between sections

    """

    result = OrderedDict()
    section = None
    i = 0

    for i in range(len(lines)):
        line = remove_chars(lines[i], '\t')
        # Comment checking
        line = remove_comment(line)

        # Watch out for extraneous chars at the beginning an end
        line = line.strip()

        # Check for empty line first
        if line and line not in os.linesep:
            # Look for section
            if line.startswith('['):
                # Look for open brackets
                if ']' in line:
                    # Isolate the section and anything else in the same line
                    data = line.split("]")
                    section = data[0]

                    # join the rest bask together
                    data = "]".join(data[1:])

                    # Clean up the section name
                    section = (remove_chars(section, '[]')).lower().strip()

                    # If the section already exists then we have seen it twice
                    if section in result.keys():
                        raise ValueError("Section name {} already used in "
                                         "config, consider renaming it to "
                                         "something unique.".format(section))
                    result[section] = []

                    # If the data is not empty append it
                    if data:
                        result[section].append(data)

            else:
                # This protects from funky syntax in a config file and alerts
                # the user
                if section is None:
                    raise Exception("Non-section like syntax before any "
                                    "sections were identified at line {0} in "
                                    "config file. Please use bracketed sections"
                                    " or use # or ; to write comments."
                                    "".format(i))
                else:
                    result[section].append(line)

    return result


def parse_items(parsed_sections_dict, mcfg=None):
    """
    Takes the output from parse_sections and parses the items in each
    section

    Args:
        parsed_sections_dict: dictionary containing keys as the sections
                              and values as a continuous string of the
    Returns:
        result: dictionary of dictionaries containing sections,items, and
                their values
    """
    result = OrderedDict()

    for k, v in parsed_sections_dict.items():
        item = None
        result[k] = OrderedDict()
        for i, val in enumerate(v):
            val = val.lstrip()
            # Look for item notation

            if ':' in val:
                # Only split on the first colon to avoid collisions with
                # datetime
                parse_loc = val.index(':')
                parseable = [val[0:parse_loc], val[parse_loc + 1:]]
                item = parseable[0].lower().strip()

                result[k][item] = ''

                # Check for a value right after the item name
                potential_value = (parseable[-1].replace('\n', ' ')).lstrip()

                # Avoid stashing properties in line with the item
                if '=' not in potential_value:
                    result[k][item] = potential_value

                # Property value provided in line with item
                else:
                    result[k][item] += " " + potential_value

            # User added line returns likely for readability
            else:
                result[k][item] += " " + val

        # Perform a final cleanup
        if item is not None:
            if ',' in result[k][item]:
                final = [e.strip() for e in result[k][item].split(',')]
                result[k][item] = ", ".join(final)

            result[k][item] = result[k][item].strip()

    return result


def parse_values(parsed_items):
    """
    Takes the output from parse_items and parses any values or
    properties provided in each item placing the strings into a list.
    If no properties are defined then it will clean up values provided
    and put them in a list of len one.

    Args:
        parsed_sections_dict: dict of dicts containing joined strings
                              found under each item
    Returns:
        result: dictionary of dictionaries containing sections, items,
                and the values provided as a list
    """
    result = OrderedDict()

    for section in parsed_items.keys():
        result[section] = OrderedDict()

        for item, val in parsed_items[section].items():
            value = val.strip()

            # list was provided
            if ',' in val:
                final = [v.strip() for v in value.split(',') if v != '']

            # For use later always make it a list
            else:
                # watch out for items that have commented out values
                if value != '':
                    final = [value]
                else:
                    final = []

            # If there are values provided add them
            if final:
                result[section][item] = final

    return result


def parse_changes(change_list):
    """
    Takes in a section and item parsed dictionary and parses on > forming a
    list. It works as the following:

    To move an item to another section or item name
    section/item -> new_section/new_item

    section/item -> Removed

    Args:
        change_list: List of modifcations that occured to the config
    Returns:
        result: a list of a list length 2 containing of list length 4
                representing section item property value which are all any
                by default.
    """
    results = []

    for i, s in enumerate(change_list):
        if "->" in s:
            changes = [c.lower().strip() for c in s.split("->")]
        else:
            raise ValueError("Invalid changelog syntax at line "
                             " {}. A changelog entry must follow"
                             " <section>/<item>/<property>/<value> ->"
                             " <section>/<item>/<property>/<value>  or REMOVED"
                             "".format(i))

        # build out an any list and populate it
        final_changes = []

        for ii, c in enumerate(changes):
            mods = ["any" for i in range(4)]
            mod_lst = []
            if "/" in c:
                mod_lst = c.split("/")

            # Catch singular sections referenced
            else:
                mod_lst.append(c)

            mods[0:len(mod_lst)] = mod_lst
            final_changes.append(mods)

        results.append(final_changes)

    return results
