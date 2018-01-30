#!/usr/bin/env python

"""Console script for inicheck."""

import importlib
import argparse
from inicheck.iniparse import read_config
from inicheck.config import MasterConfig, UserConfig
from inicheck.output import print_config_report,generate_config, print_recipe_summary
from inicheck.utilities import pcfg
import os

def main():

    parser = argparse.ArgumentParser(description="Examine and auto populate"
                                                 " ini files with a master file"
                                                 " comparison.")
    parser.add_argument('config_file', metavar='CF', type=str,
                        help='Path to a config file that needs checking')

    parser.add_argument('--master','-c', metavar='MF', type=str,
                        help='Path to a config file that used to check gaainst')

    parser.add_argument('--module','-m', metavar='M', type=str,
                        help="Module name with an attribute __CoreConfig__ that"
                             " is a path to a master config file for checking"
                             " against")

    parser.add_argument('-w', dest='write', action='store_true',
                        help="Determines whether to write out the file with all"
                             " the defaults")
    args = parser.parse_args()

    #Prefer module use
    if args.module != None:
        i = importlib.import_module(args.module)
        master_file = os.path.abspath(os.path.join(i.__file__, i.__core_config__))

    #Alternatively use a path for the master file
    elif args.master != None:
        master_file = args.master_file

    else:
        print("ERROR: Please provide either a module or a path to a master config")
        sys.exit()

    if os.path.isfile(args.config_file):
        config_file = args.config_file
        mcfg = MasterConfig(master_file)

        #pcfg(mcfg.cfg)
        ucfg = UserConfig(config_file, mcfg = mcfg)
        ucfg.apply_recipes()
        warnings, errors = ucfg.check()
        print_config_report(warnings,errors)

        print_recipe_summary(mcfg.recipes)
    else:
        raise IOError('File does not exist.')

    if args.write:
        out_f = './{0}_full.ini'.format(os.path.basename(config_file).split('.')[0])
        print("Writing complete config file showing all defaults of values that were not provided...")
        print('{0}'.format(out_f))
        generate_config(ucfg.cfg,mcfg.cfg,out_f, inicheck=True)

if __name__ == '__main__':
    main()
