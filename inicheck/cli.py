# !/usr/bin/env python

import argparse
from . output import *
from . tools import get_user_config, check_config
from . changes import ChangeLog
from os.path import basename, abspath
import sys
from . config import MasterConfig, UserConfig
from . import __version__
from .utilities import *
from collections import OrderedDict
from . import __version__

def main():

    parser = argparse.ArgumentParser(description="Examine and auto populate"
                                                 " ini files with a master"
                                                 " file comparison.")

    parser.add_argument('--config_file','-f', dest='config_file', type=str,
                        help='Path to a config file that needs checking')

    parser.add_argument('--master', '-mf', metavar='MF', type=str, nargs='+',
                        help='Path to a config file that used to check '
                        ' against')

    parser.add_argument('--modules', '-m', metavar='M', type=str, nargs='+',
                    help="Modules name with an attribute __CoreConfig__ that"
                         " is a path to a master config file for checking"
                         " against")

    parser.add_argument('--write','-w', dest='write', action='store_true',
                        help="Determines whether to write out the file with"
                        " all the defaults")

    parser.add_argument('--recipes','-r', dest='recipes', action='store_true',
                        help="Prints out the recipe summary")

    parser.add_argument('--non-defaults','-nd', dest='defaults',
                        action='store_true',
                        help="Prints out a summary of the non-defaults")

    parser.add_argument('--details', '-d', type=str, nargs='+', help="Provide"
                        " section item and value for details regarding them")

    parser.add_argument('--change', '-c', action='store_true',
                        help="Automatically apply changes to the config"
                        " according to a packages changelog. Including"
                        " recommended default changes.")

    parser.add_argument('--version', action='version',
                                     version=('%(prog)s {version}'
                                     '').format(version=__version__))

    args = parser.parse_args()

    # Module not provided, or master config
    if args.modules == None and args.master == None:
        print("ERROR: Please provide either a module or a path to a master"
             " config, or ask for details on config entries")
        sys.exit()


    # Normal operation
    else:
        # Requesting details for a section and item
        if args.details != None:
            if len(args.details) == 1:
                print("Providing details for section {0}..."
                "".format(args.details[0]))

            elif len(args.details) == 2:
                print("Providing details for section {0} and item {1}..."
                      "".format(args.details[0], args.details[1]))

            else:
                print("Details option can at most recieve section and item ")
                sys.exit()

            mcfg = MasterConfig(path=args.master, modules=args.modules)
            print_details(args.details, mcfg.cfg)

        # Requesting a check on a config file
        else:
            f = abspath(args.config_file)
            ucfg = get_user_config(f, master_files=args.master,
                                      modules=args.modules, cli=True)

            # Check out any change logs for issues
            chlog = ChangeLog(paths = ucfg.mcfg.changelogs, mcfg=ucfg.mcfg)
            potentials, required = chlog.get_active_changes(ucfg)

            # Request to apply changes
            if args.change:
                    print("Applying {} changes due to deprecation..."
                          "".format(len(required) + len(potentials)))
                    ucfg.cfg = chlog.apply_changes(ucfg, potentials, required)
                    required = []

            # report issues if there are recommended changes
            if len(required) > 0:
                cmd = get_inicheck_cmd(args.config_file,
                                       master_files=args.master,
                                       modules=args.modules)
                cmd += " --change -w"
                print_change_report(potentials, required, ucfg)
                print("Please make the above changes before continuing."
                      " To apply the name and default changes automatically "
                      "use:\n{}".format(cmd))

            else:
                warnings, errors = check_config(ucfg)
                print_config_report(warnings, errors)

                # Print out the recipes summary
                if args.recipes:
                    print_recipe_summary(ucfg.recipes)

                # Print out the summary of non-defaults values
                if args.defaults:
                    print_non_defaults(ucfg)

            # Output the config file as inicheck interprets it.
            if args.write:
                out_f = './{0}_full.ini'.format(
                                              basename(f).split('.')[0])

                print("Writing complete config file with all recipes and"
                      " necessary defaults...")
                print('{0}'.format(out_f))

                generate_config(ucfg, out_f, cli=True)

def inidiff():
    """
    Creates a report showing the difference in files
    """
    parser = argparse.ArgumentParser(description="Examine and compare"
                                                 " ini files with a master file"
                                                 "")

    parser.add_argument('--config_files','-f', dest='config_files', type=str,
                        nargs='+', required=True,
                        help='Path to two config file that needs comparing')

    parser.add_argument('--master', '-mf', metavar='MF', type=str, nargs='+',
                        help='Path to a config file that used to check against')

    parser.add_argument('--modules', '-m', metavar='M', type=str, nargs='+',
                    help="Modules name with an attribute __CoreConfig__ that"
                         " is a path to a master config file for checking"
                         " against")
    parser.add_argument('--version', action='version',
                                     version=('%(prog)s {version}'
                                     '').format(version=__version__))
    args = parser.parse_args()

    # handle multiple files
    cfgs = []

    # Keep track of non-default and mismatches
    non_default_count = 0
    mismatch_count = 0
    total_count = 0

    # Legend print out
    msg = "{0:<20}{1:<20}"

    # header formatable
    msg = "{0:<20}{1:<20}"

    # We need to start with Section, Item, and a Default
    tmsg = "{:<20}{:<30}{:<30}"
    header = ["Section","Item"]

    print("\nChecking the differences...\n")

    # Instatiates CFGs and prints out legend
    for i,f in enumerate(args.config_files):

        fname = abspath(f)
        cfgs.append(get_user_config(fname, master_files=args.master,
                                           modules=args.modules))

        cfg_rename = "CFG {}".format(i + 1)

        # Print out the Config rename legend at the top
        print(msg.format(cfg_rename, fname))

        # Start building the table header
        header.append(cfg_rename)
        tmsg+="{:<30}"

    # Print out a nice table header
    header.append("Default")
    column_header = tmsg.format(*header)
    msg_len = len(column_header)

    banner = "=" * msg_len

    print("\n" + column_header)
    print(banner)

    # Use the master config to look at everything
    mcfg = cfgs[0].mcfg.cfg

    for s in mcfg.keys():

        for i in mcfg[s].keys():
            showit = False
            values = ["Not Found" for c in cfgs]
            total_count +=1
            # Iterate through all the configs, find a value
            for zz, ucfg in enumerate(cfgs):
                cfg = ucfg.cfg

                # Is the section in the CFG
                if s in cfg.keys():
                    # is the item in there
                    if i in cfg[s].keys():
                        values[zz] = str(cfg[s][i])

            # Always grab the default
            m = str(mcfg[s][i].default)

            # Check one value against all to see if theyre mistmatched
            mismatched = [True for cv in values if values[0] != cv ]

            # Non Default check
            non_default = [True for v in values if v != m]

            # Show if any values are mismatched
            if len(mismatched) > 0:
                showit = True
                mismatch_count += len(mismatched)

            elif m.lower() != "none" and len(non_default) > 0:
                    showit = True
                    non_default_count += len(non_default)

            if showit:
                table = [s,i]
                table += values
                table.append(m)
                print(tmsg.format(*table))

    # # Print out some final details regarding the differences
    print("\nTotal items checked: {:0.0f}".format(total_count))
    print("Total Non-default values: {}".format(non_default_count))
    print("Total config mismatches: {:0.0f}\n".format(mismatch_count))


def inimake():
    """
    Attempts to walk through making a brand new ini file based on developers
    master config and recipes.

    Currently config files can have different configurations based on recipes.
    This script will ask the user for a decision by looking for:

    * Triggers built on sections and if that section is removed in another
      conditional
    * Triggers built on any_section item trigger which is also removed in
      another conditional

    """

    parser = argparse.ArgumentParser(description=" Walk through creating a "
                                                 " brand new config file "
                                                 " guided by the master "
                                                 " config and recipes!")

    parser.add_argument('--master', '-mf', metavar='MF', type=str, nargs='+',
                        help='Path to a config file that used to check '
                        'against')

    parser.add_argument('--modules', '-m', metavar='M', type=str, nargs='+',
                    help="Modules name with an attribute __CoreConfig__ that"
                         " is a path to a master config file for checking"
                         " against")

    parser.add_argument('--version', action='version',
                                     version=('%(prog)s {version}'
                                     '').format(version=__version__))

    args = parser.parse_args()

    hdr = " Welcome to inimake V{}".format(__version__)
    print("="*(len(hdr) + 1))
    print(hdr)
    print("="*(len(hdr) + 1))

    mcfg = MasterConfig(path=args.master, modules=args.modules)
    ucfg = UserConfig(None, mcfg=mcfg)

    # Start with a blank Config
    ucfg.raw_cfg = {}

    print("Building a new config file from scratch, if I have any questions"
          " I will ask!")

    ################################# SECTIONS ################################
    print("Looking through {:0.0f} config recipes that could be potential "
          " decisions...".format(len(mcfg.recipes)))

    # Look at all the sections
    choices = find_options_in_recipes(mcfg.recipes, mcfg.cfg.keys(),
                                                    "remove_section")

    print("There are {} sectional choices to be made...\n"
          "".format(len(choices)))

    selections = ask_config_setup(choices)

    # Add sections that don't end being in a choice which assumes its default
    for s in mcfg.cfg.keys():
        section_a_choice = [True for c in choices if s in c]

        if not section_a_choice or s in selections:
            ucfg.raw_cfg[s] = {}


    # Apply recipes to clean up stuff that was added and populate ucfg.cfg
    ucfg.apply_recipes()


    ################################# ITEMS ###################################
    # # Look at all the items in all the sections
    # print("Great! Let's go through items inside each section...")
    # decisions = {}
    # questions = 0
    # for s in ucfg.cfg.keys():
    #     decisions[s] = find_options_in_recipes(mcfg.recipes,
    #                                            mcfg.cfg.keys(),
    #                                            "remove_items",
    #                                            condition_position=1)
    #     if decisions[s]:
    #         questions += len(decisions[s])
    #
    # print("There are {} items related choices to be made...\n"
    #       "".format(questions))
    #
    # for s, choices in decisions.items():
    #     selections = ask_config_setup(choices, section=s,
    #                                            num_questions=questions)
    #     for i in selections:
    #         ucfg.raw_cfg[s][i] = mcfg.cfg[s][i].default
    #
    # # Apply recipes to clean up stuff that was added and populate ucfg.cfg
    # ucfg.apply_recipes()
    #
    # ################################ Values #################################
    # # Look at all the values in all the items
    # print("Great! Let's go through the values that might need choosing...")
    # decisions = {}
    # questions = 0
    # for s in ucfg.cfg.keys():
    #     decisions[s] = {}
    #
    #     for i in mcfg.cfg[s].keys():
    #         opts = mcfg.cfg[s][i].options
    #         default = mcfg.cfg[s][i].default
    #         if opts != None and type(default) != list :
    #
    #             decisions[s][i] = find_options_in_recipes(mcfg.recipes,
    #                                                   opts,
    #                                                   default,
    #                                                   condition_position=2)
    #             if decisions[s][i]:
    #                 questions += len(decisions[s])
    #
    # print("There are {} value related choices to be made...\n"
    #       "".format(questions))
    #
    # for s, choices in decisions.items():
    #     selections = ask_config_setup(choices, section=s,
    #                                            num_questions=questions)
    #     for i in selections:
    #         ucfg.raw_cfg[s][i] = mcfg.cfg[s][i].default

    ################################# END ####################################
    # Clean up and report to the user
    print("Excellent! All finished with questions...")
    out_f = "generated_config.ini"
    print("Outputting to {}".format(out_f))
    generate_config(ucfg, out_f, cli=True)

    msg = ("Your config still need some populating, use the command below to "
          "see:\n\n inicheck -f {}").format(out_f)
    if args.modules != None:
        msg += " -m {}".format(args.module)
    else:
        msg += " -mf {}".format(" ".join(mcfg.paths))

    print(msg)
if __name__ == '__main__':
    main()
