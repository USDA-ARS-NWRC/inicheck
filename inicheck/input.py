import os

def _read_config_file(filename):
    """
    Opens and reads in the config file in its most raw form.
    Creates a dictionary of dictionaries that contain the string result

    Args:
        filename: Real path to the config file to be opened
    Returns:
        dictionary: dict of dict containing the info in a config file
    """


    with open(filename) as f:
        lines = f.readlines()
        f.close()

    sections = parse_sections(lines)
    result = parse_items(sections)
    print result

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
    result = {}
    section = None
    i=0

    while i <len(lines):
        line = _remove_chars(lines[i],'\t\n')
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
                        section = (_remove_chars(line,'[]')).lower()
                        result[section]=[]
                else:
                    raise ValueError("Config file contains an open bracket at"
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
    result = {}
    for k,v in parsed_sections_dict.items():
        for i,val in enumerate(v):

            #Look for item notation
            if ':' in val:
                parseable = val.split(':')
                item = parseable[0].lower()

                #Check for a value right after the item name
                if parseable[-1].strip():
                    result[k]={item:list(parseable[-1])}

                else:
                    properties = ("".join(v[i+1:])).split(',')
                    result[k] = {item:properties}


    return result


def _remove_chars(orig_str,char_str, replace_str=None):
    """
    Removes all charact in orig_str that are in char_str

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
