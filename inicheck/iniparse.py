import os
from .utilities import  remove_chars, remove_comment
from collections import OrderedDict


def read_config(fname):
    """
    Opens and reads in the config file in its most raw form.
    Creates a dictionary of dictionaries that contain the string result

    Args:
        fname: Real path to the config file to be opened
    Returns:
        config: dict of dicts containing the info in a config file
    """
    with open(fname, encoding = 'utf-8') as f:
        lines = f.readlines()
        f.close()

    sections = parse_sections(lines)
    sec_and_items = parse_items(sections)
    config = parse_values(sec_and_items)

    return config


def parse_entry(info, item = None, valid_names=None):
    properties = OrderedDict()
    if type(info) != list:
        info = [info]
    last_three = []

    for s in info:
        if '=' in s:
            a = s.split('=')

        else:
            raise ValueError('\n\nMaster Config file missing an equals sign in'
                            ' entry or missing a comma right before the item '
                            '"{0}" in the entry:\n"{1}"'.format(item,info))

        name = (a[0].lower()).strip()
        # Check for constraints on potential names of entries
        if valid_names != None and name not in valid_names:
            raise ValueError("Invalid option set in the master config File"
                            " for entry -----> {0}".format(name))

        value = a[1].strip()

        result = []
        value = value.replace('\n'," ")
        value = value.replace('\t',"")

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
        line = remove_chars(lines[i],'\t')
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

                    section = (remove_chars(line,'[]')).lower()
                    result[section] = []

            else:
                # This protects from funky syntax in a config file and alerts the user
                if section == None:
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

    for k,v in parsed_sections_dict.items():
        item = None
        result[k] = OrderedDict()
        for i,val in enumerate(v):
            val = val.lstrip()
            # Look for item notation

            if ':' in val:
                # Only split on the first colon to avoid collisions with datetime
                parse_loc = val.index(':')
                parseable = [val[0:parse_loc],val[parse_loc + 1:]]
                item = parseable[0].lower()

                result[k][item] = ''

                # Check for a value right after the item name
                potential_value = (parseable[-1].replace('\n', ' ')).lstrip()

                # Avoid stashing properties in line with the item
                if '=' not in potential_value:
                    result[k][item] = potential_value

                # Property value provided in line with item
                else:
                    result[k][item] += " "+potential_value

            # User added line returns likely for readability
            else:
                result[k][item] += " "+val

        # Perform a final cleanup
        if item != None:
            if ',' in result[k][item]:
                result[k][item] = ", ".join([e.strip() for e in result[k][item].split(',')])

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
            for item,val in parsed_items[section].items():
                value = val.strip()
                if ',' in val:
                    result[section][item] = \
                    [v.strip() for v in value.split(',')]

                else:
                    result[section][item] = [value]

        return result
