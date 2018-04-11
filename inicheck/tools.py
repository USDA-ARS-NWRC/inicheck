import os
from . config import UserConfig, MasterConfig
from . utilities import mk_lst, get_checkers

def check_config(config_obj):
            """
            looks at the users provided config file and checks it to a master
            config file looking at correctness and missing info.

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
            if config_obj.mcfg.checker_module != None:
                funcs = standard_funcs.update(
                        get_checkers(module=config_obj.mcfg.checker_module))

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
        config_obj: The object of the user config from class UserConfig
        mcfg_obj: The object used for manage the master config from
                  class MasterConfig
        other_types: User provided list to add any custom types

    Returns:
        ucfg: The users config dictionary containing the correct value types

    """

    ucfg = config_obj.cfg
    mcfg = mcfg_obj.cfg
    all_checks = get_checkers()

    # add in other type casting
    if mcfg_obj.checker_module != None:
        all_checks.update(get_checkers(module=mcfg_obj.checker_module))

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


def get_user_config(config_file, master_files=None, module=None,
                    mcfg=None):
    """
    Returns the users config as the object UserConfig.

    Args:
        config_file: real path to existing config file
        master_file: real path to a Core Config file
        module: a module with a string attribute __CoreConfig__ which is the
                path to a CoreConfig
        mcfg: the master config object after it has been read in.

    Returns:
        ucfg: Users config as an object
    """

    if module == None and master_files == None:
        raise IOError("ERROR: Please provide either a module or a path to a"
                      "master config")
        sys.exit()

    if os.path.isfile(config_file):

        master_files = mk_lst(master_files)

        mcfg = MasterConfig(path=master_files, module=module)

        ucfg = UserConfig(config_file, mcfg=mcfg)
        ucfg.apply_recipes()
        ucfg = cast_all_variables(ucfg, mcfg)


    else:
        raise IOError("Config file path {0} doesn't exist."
                      "".format(config_file))

    return ucfg
