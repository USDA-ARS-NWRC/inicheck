import inspect
import os
import sys

import inicheck.checkers

from .changes import ChangeLog
from .config import MasterConfig, UserConfig, check_types
from .utilities import get_inicheck_cmd, mk_lst


def get_checkers(module='inicheck.checkers', keywords="check",
                 ignore=["type", "generic", "path"]):
    """
    Args:
        module: The module to search for the classes
        keyword: Keywords to look for in class names
        ignore: Post parsed keywords to ignore if found in a class name

    Returns:
        dictionary: Dict of the classes available for checking config entries
    """
    keywords = mk_lst(keywords)

    funcs = inspect.getmembers(sys.modules[module], inspect.isclass)
    func_dict = {}

    for name, fn in funcs:
        checker_found = False
        k = name.lower()

        # Remove any keywords
        for w in keywords:
            z = w.lower()

            if z in k:
                k = k.replace(z, '')

                if k not in ignore:
                    checker_found = True
                    break

        if checker_found:
            func_dict[k] = fn

    return func_dict


def get_merged_checkers(ucfg):
    """
    Retrieve the dictionary of checker classes by grabbing all in inicheck and
    any prescribed in the master config through another module

    Args:
        ucfg: User Config object containing modules
    Returns:
        dictionary: all_checks - dictionary of all the checkers from inicheck
                    and any modules assigned to the master config.
    """

    # Grab all the original
    all_checks = get_checkers()

    # Add any checker modules if provided
    if ucfg.mcfg.checker_modules:
        for c in ucfg.mcfg.checker_modules:
            new_checks = get_checkers(module=c)
            all_checks.update(new_checks)

    return all_checks


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

    mcfg = config_obj.mcfg.cfg
    cfg = config_obj.cfg

    # Grab a dictionary of all the checkers
    all_checks = get_merged_checkers(config_obj)

    # Compare user config file to our master config
    for s, configured in cfg.items():

        # Section does not exists in master config
        if s not in mcfg.keys():
            err = "Not a valid section."
            errors.append(msg.format(s, " ", err))

        else:

            for i in configured.keys():
                # lower case item
                li = i.lower()

                # Item does not exist in the Master Config
                if li not in mcfg[s].keys():
                    wrn = "Not a registered option."
                    warnings.append(msg.format(s, i, wrn))

                else:
                    issues = []
                    fn = all_checks[mcfg[s][i].type]

                    b = fn(config=config_obj, item=i, section=s)
                    issues = b.check()

                    # Examine the issues
                    num_issues = len([True for p in issues if p is not None])

                    for ii, issue in enumerate(issues):
                        if issue is not None:
                            pi = i

                            # If we had a list, provide position
                            if num_issues > 1:
                                # Show 1 based lists
                                pi += "[{}]".format(ii + 1)

                            full_msg = msg.format(s, pi, issue)

                            if b.msg_level == 'warning':
                                warnings.append(full_msg)
                            else:
                                errors.append(full_msg)

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

    # Grab a dictionary of all the checkers
    all_checks = get_merged_checkers(config_obj)

    # Confirm checks are valid
    check_types(mcfg, all_checks)

    # Cast all variables
    for s in ucfg.keys():
        if s in mcfg.keys():
            for i in ucfg[s].keys():
                values = []
                # Ensure it is an item we can check
                if i in mcfg[s].keys():
                    fn = all_checks[mcfg[s][i].type]

                    b = fn(config=config_obj, section=s, item=i)
                    values = b.cast()

                # Not recognized items, keep them anyways
                else:
                    values.append(ucfg[s][i])
                    values = mk_lst(values, unlst=True)

                # Reassign the values
                ucfg[s][i] = values

    config_obj.cfg = ucfg
    return config_obj


def get_user_config(config_file, master_files=None, modules=None,
                    mcfg=None, changelog_file=None, cli=False):
    """
    Returns the users config as the object UserConfig.

    Args:
        config_file: real path to existing config file
        master_file: real path to a Core Config file
        modules: a module or list of modules with a string attribute
                __CoreConfig__ which is the path to a CoreConfig
        mcfg: the master config object after it has been read in.
        changelog_file: Path to a changlog showing any changes to the config
                        file the developers have made
        cli: boolean determining whether to attempt to process the changes
            which should be done from the CLI only

    Returns:
        ucfg: Users config as an object
    """

    if modules is None and master_files is None and mcfg is None:
        raise IOError("ERROR: Please provide either a module or a path to a"
                      " master config, or a master config object")
        sys.exit()

    if os.path.isfile(config_file):

        if master_files is not None or modules is not None:
            if master_files is not None:
                master_files = mk_lst(master_files)
            if modules is not None:
                modules = mk_lst(modules)

            mcfg = MasterConfig(path=master_files, modules=modules,
                                changelogs=changelog_file)

    else:
        raise IOError("Config file path {0} doesn't exist."
                      "".format(config_file))

    # Get users config object
    ucfg = UserConfig(config_file, mcfg=mcfg)

    # If were not running the CLI, raise exceptions for issues
    # Check out any change logs for issues
    chlog = ChangeLog(paths=ucfg.mcfg.changelogs, mcfg=ucfg.mcfg)
    potentials, required = chlog.get_active_changes(ucfg)

    # Required Changes that broke things
    if len(required) != 0 and not cli:
        cmd = get_inicheck_cmd(config_file, modules=modules,
                               master_files=master_files)

        raise ValueError("\n\nUser's Config has deprecated information and"
                         " needs adjustment. To see what needs to change:"
                         "\n\n>> {}".format(cmd))

    # Fill in the gaps and make sure they're the right types
    ucfg.apply_recipes()
    ucfg = cast_all_variables(ucfg, mcfg)
    return ucfg


def config_documentation(out_f, paths=None, modules=None,
                         section_link_dict={}):
    """
    Auto documents the core config file. Outputs to a file which is can then be
    used for documentation. Specifically formulated for sphinx

    Args:
        out_f: string path to output location for the auto documentation
        paths: paths to master config files to use for creating docs
        modules: modules with attributes __core_config__ for creating docs
        section_link_dict: dictionary containing special documentation
                 for a section in the config file reference

    """

    if paths is None and modules is None:
        raise ValueError("inicheck function config_documentation args paths or"
                         " module must be specified!")

    master = MasterConfig(path=paths, modules=modules)
    mcfg = master.cfg

    # Beginning
    config_doc = "\nFor configuration file syntax information please visit"
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
        for item, v in sorted(mcfg[section].items()):
            # Check for attributes that are lists
            for att in ['default', 'options']:
                z = getattr(v, att)
                if isinstance(z, list):
                    combo = ' '
                    doc_s = combo.join([str(s) for s in z])
                    setattr(v, att, doc_s)

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
    if not os.path.isdir(os.path.dirname(path)):
        raise IOError("Config Documentation output file does not exist."
                      "\n{0}".format(out_f))

    print("Writing auto documentation for config file to:\n{0}".format(path))

    with open(path, 'w+') as f:
        f.writelines(config_doc)
    f.close()
