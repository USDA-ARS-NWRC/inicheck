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
                        nargs=2, required=True,
                        help='Path to two config file that needs comparing')

    parser.add_argument('--master', '-mf', metavar='MF', type=str, nargs='+',
                        help='Path to a config file that used to check against')

    parser.add_argument('--modules', '-m', metavar='M', type=str, nargs='+',
                    help="Modules name with an attribute __CoreConfig__ that"
                         " is a path to a master config file for checking"
                         " against")
    args = parser.parse_args()

    cfg1 = os.path.abspath(args.config_files[0])
    ucfg1 = get_user_config(cfg1, master_files=args.master,
                              modules=args.modules,
                              checking_later=True)

    cfg2 = os.path.abspath(args.config_files[1])
    ucfg2 = get_user_config(cfg2, master_files=args.master,
                              modules=args.modules,
                              checking_later=True)

    msg = "{0:<20}{1:<20}"
    header = ["\n"+msg.format("Base File:", cfg1),
              msg.format("Compare File:", cfg2),
              "",""]

    msg = "{:<20}{:<30}{:<30}{:<30}{:<30}"
    column_header = msg.format("Section","Item","CFG 1","CFG 2","Default")


    msg_len = len(column_header)

    banner = "=" * msg_len

    print("\nChecking the differences...")

    print("\n".join(header))
    print(column_header)
    print(banner)

    for s in ucfg1.mcfg.cfg.keys():

        for i in ucfg1.mcfg.cfg[s].keys():
            showit = False
            v1 = "Not Found"
            v2 = "Not Found"

            if s in ucfg1.cfg.keys():
                if i in ucfg1.cfg[s].keys():
                    v1 = str(ucfg1.cfg[s][i])

            if s in ucfg2.cfg.keys():
                if i in ucfg2.cfg[s].keys():
                    v2 = str(ucfg2.cfg[s][i])

            m = ucfg1.mcfg.cfg[s][i].default

            if v1 != v2:
                showit = True

            elif str(m).lower() != "none":
                if v1 != m or v2 != m:
                    showit = True

            if showit:
                print(msg.format(s, i, v1, v2, str(m)))

if __name__ == '__main__':
    main()
