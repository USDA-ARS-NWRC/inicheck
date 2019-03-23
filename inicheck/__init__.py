# -*- coding: utf-8 -*-
import os
__author__ = """Micah Johnson"""
__email__ = 'micah.johnson150@gmail.com'
__version__ = '0.3.5'

# Keywords for conditional statements in a master config file
__trigger_keywords__ = ['trigger']

# Key words expected in the section name of a recipe
__recipe_keywords__ = ['recipe']

# Add in core configs for test purposes
__core_config__ = os.path.abspath(os.path.dirname(__file__)+'/../tests/test_configs/CoreConfig.ini')
__recipes__ = os.path.abspath(os.path.dirname(__file__)+'/../tests/test_configs/recipes.ini')
