import os
from . config import UserConfig, MasterConfig
from . utilities import mk_lst, get_checkers

def check_config(config_obj):
            """
            Looks at the users provided config file and checks it to a master
            config file looking at correctness and missing info.

            Args:
                config_obj - UserConfig object produced by
                             :class:`~inicheck.config.UserConfig`
            Returns:
                tuple:
                - **warnings** - Returns a list of string messages that are
                                 consider non-critical issues with config file.
                - **errors** - Returns a list of string messages that are
                               consider critical issues with the config file.
            """

            msg = "{: <20} {: <30} {: <60}"
            errors = []
            warnings = []

            master = config_obj.mcfg.cfg
            cfg = config_obj.cfg

            standard_funcs = get_checkers()

            # Add any checker modules if provided
            if config_obj.mcfg.checker_modules:
                for c in config_obj.mcfg.checker_modules:
                    funcs = standard_funcs.update(
                            get_checkers(module=c))

            # Compare user config file to our master config
            for section, configured in cfg.items():

                # In the section check the values and options
                for item, value in configured.items():
                    litem = item.lower()

                    # Is the item known as a configurable item?
                    if litem not in master[section].keys():
                        wrn = "Not a registered option."
                        warnings.append(msg.format(section, item, wrn))
                    else:
                        # Did the user provide a list value or single value
                        val_lst = mk_lst(value)

                        for v in val_lst:
                            if v != None:
                                # Do we have an idea of what to expect?
                                options_type = master[section][item].type
                                for name, fn in standard_funcs.items():

                                    # Check for type checkers
                                    if options_type == name.lower():
                                        b = fn(value=v, config=config_obj)
                                        issue = b.check()
                                        if issue != None:
                                            full_msg = msg.format(section,
                                                                  item,
                                                                  issue)
                                            if b.msg_level == 'error':
                                                errors.append(full_msg)
                                            elif b.msg_level == 'warning':
                                                warnings.append(full_msg)
                                            break
                                    else:
                                        issue = None
            return warnings, errors


def cast_all_variables(config_obj, mcfg_obj):
    """
    Cast all values into the appropiate type using checkers, other_types
    and the master config.

    Args:
        config_obj: The object of the user config from
        mcfg_obj: The object used for manage the master config from
                  class MasterConfig
        other_types: User provided list to add any custom types

    Returns:
        ucfg: The users config dictionary containing the correct value types

    """

    ucfg = config_obj.cfg
    mcfg = mcfg_obj.cfg
    all_checks = get_checkers()

    # Add any checker modules if provided
    if config_obj.mcfg.checker_modules:
        for c in config_obj.mcfg.checker_modules:
            new_checks = get_checkers(module=c)
            all_checks.update(new_checks)

    # Cast all variables
    for s in ucfg.keys():
        for i in ucfg[s].keys():
            values = []

            # Ensure it is something we can check
            if i in mcfg[s].keys():
                type_value = (mcfg[s][i].type).lower()
                if type_value.lower() not in all_checks.keys():
                    raise ValueError("Type {0} is undefined and has no"
                                    " checker associated"
                                    "".format(type_value))

                for z, v in enumerate(mk_lst(ucfg[s][i])):
                    option_found = False
                    # Use all the checks available to cast
                    for name, fn in all_checks.items():
                        if  type_value == name.lower():
                            b = fn(value=v, config=config_obj)
                            if v in [None, 'none', 'None']:
                                values.append(None)
                            else:
                                values.append(b.cast())
                            option_found = True
                            break

                    if not option_found:
                        raise ValueError("Unknown type_value prescribed."
                                         " ----> {0}".format(type_value))
            else:
                values = ucfg[s][i]

            ucfg[s][i] = mk_lst(values, unlst=True)

    config_obj.cfg = ucfg
    return config_obj


def get_user_config(config_file, master_files=None, modules=None,
                    mcfg=None):
    """
    Returns the users config as the object UserConfig.

    Args:
        config_file: real path to existing config file
        master_file: real path to a Core Config file
        modules: a module or list of modules with a string attribute __CoreConfig__ which is the
                path to a CoreConfig
        mcfg: the master config object after it has been read in.

    Returns:
        ucfg: Users config as an object
    """

    if modules == None and master_files == None and mcfg == None:
        raise IOError("ERROR: Please provide either a module or a path to a"
                      " master config, or a master config object")
        sys.exit()

    if os.path.isfile(config_file):


        if master_files != None or modules != None:
            if master_files != None:
                master_files = mk_lst(master_files)

            mcfg = MasterConfig(path=master_files, modules=modules)

        ucfg = UserConfig(config_file, mcfg=mcfg)

        ucfg.apply_recipes()
        ucfg = cast_all_variables(ucfg, mcfg)


    else:
        raise IOError("Config file path {0} doesn't exist."
                      "".format(config_file))

    return ucfg


def config_documentation(out_f, paths=None, modules=None,
                        section_link_dict=None):
    """
    Auto documents the core config file. Outputs to a file which is can then be
    used for documentation. Specifically formulated for sphinx
    """

    if paths == None and modules == None:
        raise ValueError("inicheck function config_documentation args paths or"
                        " module must be specified!")


    master = MasterConfig(path=paths, modules=modules)
    mcfg = master.cfg

    #RST header
    config_doc = "Configuration File Reference\n"
    config_doc += "============================\n"
    config_doc += "\nFor configuration file syntax information please visit"
    config_doc += " http://inicheck.readthedocs.io/en/latest/\n\n"

    for section in mcfg.keys():
        # Section header
        config_doc += "\n"
        config_doc += "{0}\n".format(section)
        config_doc += "-" * len(section) + '\n'

        # Allow for custom info in a description about the section, useful
        # for linking modules for auto documenting
        if section in section_link_dict.keys():
            intro = section_link_dict[section]
        else:
            intro = ''

        config_doc += intro
        config_doc += "\n"

        # Auto document config file according to master config contents
        for item,v in sorted(mcfg[section].items()):
            # Check for attributes that are lists
            for att in ['default', 'options']:
                z = getattr(v,att)
                if type(z) == list:
                    combo = ' '
                    doc_s = combo.join([str(s) for s in z])
                    setattr(v,att,doc_s)

            # Bold item with definition
            config_doc += "| **{0}**\n".format(item)

            # Add the item description
            config_doc += "| \t{0}\n".format(v.description)

            # Default
            config_doc += "| \t\t*Default: {0}*\n".format(v.default)

            # Add expected type
            config_doc += "| \t\t*Type: {0}*\n".format(v.type)

            # Print options should they be available
            if v.options:
                config_doc += "| \t\t*Options:*\n *{0}*\n".format(v.options)

            config_doc += "| \n"

            config_doc += "\n"

    path = os.path.abspath(out_f)
    if not os.path.isfile(path):
        raise IOError("Config Documentation output file does not exist."
                      "\n{0}".format(out_f))

    print("Writing auto documentation for config file to:\n{0}".format(path))

    with open(path,'w+') as f:
        f.writelines(config_doc)
    f.close()
