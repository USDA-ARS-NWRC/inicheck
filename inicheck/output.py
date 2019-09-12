from datetime import date
import os
import sys
from . utilities import mk_lst

def generate_config(config_obj, fname, cli=False):
    """
    Generates a list of strings using the config data then its written to an
    .ini file

    Args:
        config_obj: config object containing data to be outputted
        fname: String path to the output location for the new config file
        cli : Boolean value that adds the line "file generated using
            inicheck.cli", Default = False
    """

    header_len = 80
    pg_sep = '#' * header_len

    # Header surround each commented titles in the ini file
    section_header = pg_sep + '\n' + ('# {0}\n') + pg_sep

    # Construct the section strings
    config_str = ""
    config_str += pg_sep

    # File header with specific package option
    if config_obj.mcfg.header != None:
        header = config_obj.mcfg.header.split('\n')
        for line in header:
            config_str += ('\n# ' + line)
    else:
        config_str += "\n# Configuration File "

    # Add in the date generated
    config_str += "\n#\n# Date generated: {0}".format(date.today())

    # Generated with inicheck
    if cli:
        config_str += "\n#\n# Generated using: inicheck <filename> -w"

    config_str += "\n#\n# For more inicheck help see:" + \
                  "\n# http://inicheck.readthedocs.io/en/latest/\n"

    config = config_obj.cfg
    mcfg = config_obj.mcfg.cfg

    # Check to see if section titles were provided
    has_section_titles = hasattr(config_obj.mcfg,'titles')

    # Generate the string for the file, creating them in order.
    for section in mcfg.keys():
        if section in config.keys():
            config_str += '\n' * 2

            # Add a section header
            s_hdr = pg_sep
            if has_section_titles:
                if section in config_obj.mcfg.titles.keys():
                    # Add the header
                    s_hdr = section_header.format(config_obj.mcfg.titles[section])

            else:
                config_str += s_hdr

            config_str += s_hdr
            config_str += '\n'
            config_str += '\n[{0}]\n'.format(section)

            # Add section items and values
            for k in config[section].keys():
                v = config[section][k]
                if type(v) == list:
                    astr = ", ".join(str(c).strip() for c in v)
                else:
                    astr = str(v)
                config_str += "{0:<30} {1:<10}\n".format((k+':'), astr)

    # Write out the string generated
    with open(os.path.abspath(fname), 'w') as f:
        f.writelines(config_str)
        f.close()


def print_config_report(warnings, errors, logger=None):
    """
    Pass in the list of string messages generated by check_config file.
    print out in a pretty format the issues

    Args:
        warnings: List of non-critical messages returned from
                :func:`~utilities.check_config`.
        errors: List of critical messages returned from
              :func:`~utilities.check_config`.
        logger: pass in the logger function being used. If no logger is
                provided, print is used. Default = None
    """

    msg = "{: <20} {: <25} {: <60}"

    # Check to see if user wants the logger or stdout
    if logger != None:
        out = logger.info
    else:
        out = print


    msg_len = 90
    out(" ")
    out(" ")
    out("Configuration File Status Report:")
    header = "="*msg_len
    out(header)
    any_warnings = False
    any_errors = False

    # Output warnings
    if len(warnings) > 0:
        any_warnings = True
        out("WARNINGS:")
        out(" ")
        out(msg.format(" Section", "Item", "Message"))
        out("-"*msg_len)
        for w in warnings:
            out(w)
        out(" ")
        out(" ")

    # Output errors
    if len(errors) > 0:
        any_errors = True
        out("ERRORS:")
        out(" ")
        out(msg.format("Section", "Item", "Message"))
        out("-"*msg_len)
        for e in errors:
            out(e)
        out(" ")
        out(" ")

    if not any_errors and not any_warnings:
        out("No errors or warnings were reported with the config file.\n")


def print_recipe_summary(lst_recipes):
    """
    Prints out the recipes found and how they are interpretted

    Args:
        lst_recipes: list of the recipe entry objects

    """
    # len of recipe separators
    msg_len = 80
    header = "=" * msg_len
    recipe_hdr = "-" * msg_len
    r_msg = "\n{0: <20}\n"+recipe_hdr
    cfg_msg = "\t\t{0: <20} {1: <20} {2: <20}"

    msg = "\t\t{0: <20} {1: <25}"

    print('\n\n')
    print("Below are the recipes applied to the config file:")
    print("Recipes Summary:")
    print(header)

    for r in lst_recipes:
        print(r_msg.format(r.name))
        print("\tConditionals:")
        for n, t in r.triggers.items():
            for i, c in enumerate(t.conditions):
                if type(c) == list:
                    c = ", ".join(c)
                if i == 0:
                    print(msg.format(n, c))
                else:
                    print(msg.format("", c))

        print_cfg_for_recipe(r.adj_config, cfg_msg, hdr="\n\tEdits:")
        #print('\n')
    print('\n')


def print_cfg_for_recipe(cfg, fmt, hdr=None):
    if hdr != None:
        print(hdr)

    for section in cfg.keys():
        for item, value in cfg[section].items():
            if type(value) != list:
                v = [value]
            else:
                v = value

            for qq in v:
                print(fmt.format(section, item, qq))


def print_details(details, mcfg):
    """
    Prints out the details for a list of provided options designed for use
    with the CLI. Details about a section, or an item can be requested by
    passing in a list of in the section,item order. If a section is only passed
    then we the details provided are for the entire section

    Args:
        details: a list in [section item value] requesting details.
        mcfg: master config object to gather the details from


    """

    msg = "{: <15} {: <15} {: <15} {: <25} {: <60}"
    hdr  = '\n' + msg.format('Section', 'Item', 'Default', 'Options',
                           'Description')
    print(hdr)
    print('='*len(hdr))
    nopts = len(details)
    # At least a section was provided
    if nopts >= 1:
        if details[0] in mcfg.keys():
            # A section and item was provided
            if nopts == 2:
                if details[1] in mcfg[details[0]].keys():
                    print(msg.format(details[0], details[1],
                                    str(mcfg[details[0]][details[1]].default),
                                    str(mcfg[details[0]][details[1]].options),
                                    str(mcfg[details[0]][details[1]].description)))
                else:
                    print("Item {0} in not a registered item."
                          "".format(details[1]))
                    sys.exit()

            # Print the whole section
            else:
                for k, v in mcfg[details[0]].items():

                    print(msg.format(details[0],
                                     k,
                                     str(v.default),
                                     str(v.options),
                                     str(v.description)))

        # Section does not exist
        else:
            print("Section {0} in not a valid section.".format(details[0]))
            sys.exit()

    else:
        print("Please provide at least a section for information")
        sys.exit()


def print_non_defaults(ucfg):
    """
    Prints out the options used that were not default option values.

    Args:
        ucfg: config object containing options that are not default
    """

    mcfg = ucfg.mcfg.cfg
    cfg = ucfg.cfg

    msg = "{: <20} {: <20} {: <40} {: <40}"
    hdr = '\n'+msg.format("Section","Item","Value","Default")

    print("\n\nConfiguration File Non-Defaults Report:")
    print("The following are all the items that had non-defaults values specified.")
    print("="*len(hdr))
    print(hdr)
    print('-'*len(hdr))

    # Cycle through option/items checking defaults, print em if they don't match
    for s in mcfg.keys():
        if s in cfg.keys():
            for i in mcfg[s].keys():
                if i in cfg[s].keys():
                    default_lst = mk_lst(mcfg[s][i].default)
                    str_default_lst =  [str(kk).lower() for kk in default_lst]
                    user_lst = mk_lst(cfg[s][i])
                    str_lst = [str(kk).lower() for kk in user_lst]

                    for vi, v in enumerate(str_default_lst):
                        # Single entries
                        if v != 'none':
                            if len(str_lst) == 1:
                                if str_lst[vi] != v:
                                    print(msg.format(s, i,str(user_lst[vi]),
                                                          str(default_lst[vi])))

                            # Handle awkward list comparisons
                            elif v not in str_lst:
                                print(msg.format(s, i,"all values",
                                                       str(default_lst[vi])))

    print("")


def print_change_report(potential_changes, required_changes, ucfg, logger=None):
    """
    Pass in the list of changes generated by check_config file.
    print out in a pretty format the changes required

    Args:
        potential_changes: List of warnings about config property changes
                           especialy about defaults retruned from
                           :func:`~changes.ChangeLog.get_active_changes`.
        potential_required: List of critical changes returned from
                            :func:`~changes.ChangeLog.get_active_changes`.
    """

    msg = "{: <20} {: <25} {: <25} {: <25}"

    # Check to see if user wants the logger or stdout
    if logger != None:
        out = logger.info
    else:
        out = print


    msg_len = 90
    out(" ")
    out(" ")
    title = "Configuration File Change Log Report:"
    out(title)
    header = "=" * len(title)
    out(header)

    # Output warnings
    if len(potential_changes) > 0:

        out("Default changes - Warnings issued only when old default values are "
        "detected in file.\n")

        out("Default Changes:")
        out("No. of default changes: {:0.0f}".format(len(potential_changes)))

        any_warnings = True
        out(" ")
        out(msg.format(" Section", "Item", "Old Default", "New Default"))
        out("-"*msg_len)

        for w in potential_changes:
            out(msg.format(w[0][0], w[0][1], w[0][3], w[1][3]))

        out(" ")
        out(" ")

    # Output errors
    msg = "{: <50} {: <50}"

    if len(required_changes) > 0:
        any_errors = True
        out("Required Changes:")
        out("No. of necessary changes: {:0.0f}".format(len(required_changes)))
        out(" ")
        out(msg.format("From", "To"))
        out("-"*msg_len)
        for e in required_changes:
            orig = "{}/{}".format(e[0][0], e[0][1])
            if e[1] != "removed":
                to = "{}/{}".format(e[1][0], e[1][1])
            else:
                to = e[1]

            out(msg.format(orig,to))
        out(" ")
        out(" ")

    if not any_errors and not any_warnings:
        out("No required changes or old defaults were reported with the config"
            " file.\n")
