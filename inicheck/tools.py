import os
from . config import UserConfig, MasterConfig
from . utilities import mk_lst, cast_variable, get_checkers

def check_config(config_obj,checkers = None):
            """
            looks at the users provided config file and checks it to a master config file
            looking at correctness and missing info.

            Returns:
                tuple:
                - **warnings** - Returns a list of string messages that are consider
                                 non-critical issues with config file.
                - **errors** - Returns a list of string messages that are consider
                               critical issues with the config file.
            """

            msg = "{: <20} {: <30} {: <60}"
            errors = []
            warnings = []
            master = config_obj.mcfg.cfg
            cfg = config_obj.cfg
            standard_funcs = get_checkers()

            #Compare user config file to our master config
            for section, configured in cfg.items():

                #In the section check the values and options
                for item,value in configured.items():
                    litem = item.lower()

                    #Is the item known as a configurable item?
                    if litem not in master[section].keys():
                        wrn = "Not a registered option."
                        if section.lower() == 'wind':
                            wrn +=  " Common for station names."
                        warnings.append(msg.format(section,item, wrn))
                    else:
                        if litem != 'stations':
                            #Did the user provide a list value or single value
                            val_lst = mk_lst(value)

                            for v in val_lst:
                                if v != None:
                                    #v = master[section][litem].convert_type(v)

                                    # Do we have an idea os what to expect (type and options)?
                                    options_type = master[section][item].type

                                    for name,fn in standard_funcs.items():

                                        if options_type in name.lower():
                                            b = fn(value = v, config = config_obj)
                                            issue = b.check()
                                            if issue != None:
                                                full_msg = msg.format(section,item,issue)

                                                if b.msg_level == 'error':
                                                    errors.append(full_msg)
                                                if b.msg_level == 'warning':
                                                    warnings.append(full_msg)
                                        else:
                                            issue = None



            return warnings,errors


def cast_all_variables(config_obj,mcfg_obj, other_types = None):
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

    #add in other type casting
    if other_types != None:
        all_checks.update(other_types)

    #Cast all variables
    for s in ucfg.keys():
        for i in ucfg[s].keys():
            values = []
            #Ensure it is something we can check
            if i in mcfg[s].keys():
                type_value = mcfg[s][i].type
                for z,v in enumerate(ucfg[s][i]):
                        #Use all the checks available to cast
                        for name,fn in all_checks.items():
                            if type_value in name:
                                b = fn(value = v, config = config_obj)
                                values.append(b.cast())
                                option_found = True

                        if not option_found:
                            raise ValueError("Unknown type_value prescribed. ----> {0}".format(type_value))

            ucfg[s][i] = mk_lst(values, unlst=True)
    config_obj.cfg = ucfg
    return config_obj


def get_user_config(config_file,master_files = None, module= None, mcfg = None):
    """
    Returns the users config as the object UserConfig.

    Args:
        config_file: real path to existing config file
        master_file: real path to a Core Config file
        module: a module with a string attribute __CoreConfig__ which is the path to a CoreConfig
        mcfg: the master config object after it has been read in.

    Returns:
        ucfg: Users config as an object
    """

    if module == None and master_files == None:
        raise IOError("ERROR: Please provide either a module or a path to a master config")
        sys.exit()

    if os.path.isfile(config_file):

        master_files = mk_lst(master_files)

        mcfg = MasterConfig(path = master_files, module = module)

        ucfg = UserConfig(config_file, mcfg = mcfg)
        ucfg = cast_all_variables(ucfg,mcfg)


    else:
        raise IOError("Config file path {0} doesn't exist.".format(config_file))

    return ucfg
