#!/usr/bin/env python

"""Console script for inicheck."""

import click

from inicheck.iniparse import read_config
from inicheck.config import MasterConfig, UserConfig
from inicheck.output import print_config_report,generate_config
from inicheck.utilities import pcfg
import os


@click.command()
@click.argument('config_file',nargs=1,
                              type=click.Path(),
                              metavar='<Users CFG File>')
@click.argument('master_file',nargs=1,
                              type=click.Path(),
                              metavar='<Master CFG File>')
@click.option('-w',is_flag=True,help='Flag to output full config if it passes the checks')

def main(config_file, master_file,w):

    if os.path.isfile(config_file):
        mcfg = MasterConfig(master_file)

        ucfg = UserConfig(config_file, mcfg = mcfg)
        ucfg.apply_recipes()
        warnings, errors = ucfg.check()
        print_config_report(warnings,errors)
    else:
        raise IOError('File does not exist.')

    if w:
        out_f = './{0}_full.ini'.format(os.path.basename(config_file).split('.')[0])
        print("Writing complete config file showing all defaults of values that were not provided...")
        print('{0}'.format(out_f))
        generate_config(ucfg.cfg,mcfg.cfg,out_f, inicheck=True)

if __name__ == '__main__':
    main()
