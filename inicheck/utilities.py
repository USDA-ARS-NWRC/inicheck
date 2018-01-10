
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

def cast_variable(variable,type_value):
    """
    Casts an object to the spectified type value
    Args:
        variable - some variable to be casted
        type_value - string value indicating type to cast.
    Returns:
        value - The original variable now casted in type_value
    """
    if type(variable) != list:
        variable = [variable]
    type_value = str(type_value)
    value = []
    for v in variable:
        if 'datetime' in type_value:
            value.append(pd.to_datetime(v))
        elif 'bool' in type_value:
            if v.lower() in ['yes','y','true']:
                v = True
            elif v.lower() in ['no','n','false']:
                v = False

            value.append(bool(v))
        elif 'int' in type_value:
            value.append(int(v))
        elif 'float' in type_value:
            value.append(float(v))
        elif type_value == 'filename' or type_value == 'directory':
            value.append(v)
        elif v in ['none']:  # None
            value.append(None)
        elif 'str' in type_value:
            value.append(str(v.lower()))
        else:
            raise ValueError("Unknown type_value prescribed. ----> {0}".format(type_value))

    if len(value) == 1:
        value = value[0]
    return value

def pcfg(cfg):
    """
    prints out the config file to the prompt with a nice stagger Look for
    readability
    """

    for sec in cfg.keys():
        print(sec)
        for item in cfg[sec].keys():
            print('\t'+item)
            if type(cfg[sec][item])==list:
                out = ", ".join(cfg[sec][item])
            else:
                out = cfg[sec][item]
            print('\t\t'+out)
