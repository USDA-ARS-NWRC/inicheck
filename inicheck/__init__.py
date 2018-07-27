# -*- coding: utf-8 -*-
import os
__author__ = """Micah Johnson"""
__email__ = 'micah.johnson150@gmail.com'
__version__ = '0.2.14'

# Keywords for conditional statements in a master config file
__trigger_keywords__ = ['trigger']

# Key words expected in the section name of a recipe
__recipe_keywords__ = ['recipe']

__core_config__ = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                  '../examples/CoreConfig.ini'))
