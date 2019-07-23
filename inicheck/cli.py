# !/usr/bin/env python

import argparse
from . output import print_config_report, generate_config, print_recipe_summary, print_details, print_non_defaults
from . tools import get_user_config, check_config
import os
import sys
from . config import MasterConfig

def main():

    parser = argparse.ArgumentParser(description="Examine and auto populate"
                                                 " ini files with a master file"
                                                 " comparison.")

    parser.add_argument('--config_file','-f', dest='config_file', type=str,
                        help='Path to a config file that needs checking')

    parser.add_argument('--master', '-mf', metavar='MF', type=str, nargs='+',
                        help='Path to a config file that used to check against')

    parser.add_argument('--modules', '-m', metavar='M', type=str, nargs='+',
                    help="Modules name with an attribute __CoreConfig__ that"
                         " is a path to a master config file for checking"
                         " against")

    parser.add_argument('--write','-w', dest='write', action='store_true',
                        help="Determines whether to write out the file with all"
                             " the defaults")

    parser.add_argument('--recipes','-r', dest='recipes', action='store_true',
                        help="Prints out the recipe summary")

    parser.add_argument('--non-defaults','-nd', dest='defaults',
                        action='store_true',
                        help="Prints out a summary of the non-defaults")

    parser.add_argument('--details', '-d', type=str, nargs='+', help="Provide"
                        " section item and value for details regarding them")


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
            f = os.path.abspath(args.config_file)
            ucfg = get_user_config(f, master_files=args.master,
                                      modules=args.modules,
                                      checking_later=True)

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
                                              os.path.basename(f).split('.')[0])

                print("Writing complete config file with all recipes and "
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

        fname = os.path.abspath(f)
        cfgs.append(get_user_config(fname, master_files=args.master,
                                           modules=args.modules,
                                           checking_later=True))

        cfg_rename = "CFG {}".format(i+1)

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

if __name__ == '__main__':
    main()
