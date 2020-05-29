# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join

__author__ = """Micah Johnson"""
__email__ = 'micah.johnson150@gmail.com'

# Keywords for conditional statements in a master config file
__trigger_keywords__ = ['trigger']

# Key words expected in the section name of a recipe
__recipe_keywords__ = ['recipe']

# Add in core configs for test purposes
test_dir = abspath(join(dirname(__file__), '../', 'tests', 'test_configs'))
__core_config__ = join(test_dir, 'CoreConfig.ini')
__recipes__ = join(test_dir, 'recipes.ini')
__config_changelog__ = join(test_dir, 'changelog.ini')
