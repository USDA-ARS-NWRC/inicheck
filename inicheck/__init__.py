# -*- coding: utf-8 -*-

"""Top-level package for inicheck."""
import os
__author__ = """Micah Johnson"""
__email__ = 'micah.johnson150@gmail.com'
__version__ = '0.1.0'

#Keywords for conditional statements in a master config file
__trigger_keywords__ = ['trigger','triggers','condition']

# Key words expected in the section name of a recipe
__recipe_keywords__ = ['recipe']

__CoreConfig__ = os.path.abspath(os.path.join(os.path.dirname(__file__),'../examples/CoreConfig.ini'))
