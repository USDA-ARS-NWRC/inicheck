import os
from utilities import remove_chars, pcfg
from collections import OrderedDict

def read_config(filename):
    """
    Opens and reads in the config file in its most raw form.
    Creates a dictionary of dictionaries that contain the string result

    Args:
        filename: Real path to the config file to be opened
    Returns:
        config: dict of dicts containing the info in a config file
    """


    with open(filename) as f:
        lines = f.readlines()
        f.close()

    sections = parse_sections(lines)
    config = parse_items(sections)
    pcfg(config)
    print
    print
    return config

def parse_sections(lines):
    """
    Returns a dictionary containing all the sections as keys with a single
    string of the contents after the section
    Args:

        lines: A list of strings that are read in.

    Returns:
        sections: dictionary containing keys that are the section names and
                  values that are strings of the contents between sections

    """
    result = OrderedDict()
    section = None
    i=0

    while i <len(lines):
        line = remove_chars(lines[i],'\t\n')
        line = line.strip()

        #Comment checking
        if '#' in line:
            line = line.split('#')[0]

        elif ';' in line:
            line = line.split(';')[0]

        #check for empty line first
        if line not in os.linesep:
            #Look for section
            if '[' in line:
                #look for open brackets
                if ']' in line:
                    #Ensure this line is not a list provided under an item
                    if ':' not in line and '=' not in line:
                        section = (remove_chars(line,'[]')).lower()
                        result[section]=[]

                    #Catch items that contain lists
                    else:
                        result[section].append(line)
                else:
                    raise ValueError("Config file contains an open bracket at "
                                     "line {0}".format(i))

            else:
                result[section].append(line)

        i+=1
    return result


def parse_items(parsed_sections_dict):
    """
    Takes the output from parse_sections and parses the items in each section

    Args:
        parsed_sections_dict: dictionary containing keys as the sections and
                              values as a continuous string of the
    Returns:
        result: dictionary of dictionaries containing sections,items, and their values
    """
    result = OrderedDict()

    for k,v in parsed_sections_dict.items():
        result[k] = OrderedDict()

        for i,val in enumerate(v):

            #Look for item notation
            if ':' in val:
                parseable = val.split(':')
                item = parseable[0].lower()
                result[k][item] = []

                #Check for a value right after the item name
                potential_value=parseable[-1].strip()
                if potential_value:
                    result[k][item].append(potential_value)
            else:
                result[k][item].append(remove_chars(val,','))
    return result
