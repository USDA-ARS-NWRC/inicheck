from utilities import cast_variable
from inicheck import __trigger_keywords__, __recipe_keywords__
from iniparse import parse_entry

class RecipeSection:
    """docstring for RecipeEntry."""

    def __init__(self, recipe_section_dict):

        #Conditions to be met
        self.triggers = {}
        #Config file to apply if conditions are met
        self.applied_config = {}

        for item,entry in recipe_section_dict.items():
            # Check item for action keywords
            for word in __trigger_keywords__:
                if word in item:
                    self.triggers[item] = RecipeEntry(entry)
                    break

            # Check for assigned values if any trigger
            if item not in self.triggers.keys():
                item_dict = parse_entry(entry)
                self.applied_config[item] = item_dict

class RecipeEntry:
    """
    RecipeEntry designed to aid in parsing master config file entries under
    a recipe.
    This is meant to parse:

    ------------------------------------------------------------
    item_trigger:
                    has_section_name = <value>,
                    has_value = [<section name> <item name>, <value>],
                    has_item_name = <value>

    -------------------------------------------------------------

    Config entry expects to recieve the above in the following format:

        {item_trigger:
                    ["has_section = <value>",
                     "has_item = [<section> <item>"],
                     "has_value = [<section> <item> <value>]"
                     ]
        }

    Recipe entry then will parse the strings looking for space separated lists,
    values denoted with = and will only accept has_section, has_item, has_item_any
    has_value
    """
    def __init__(self, parseable_line):

        #Acceptable conditions
        self.has_section = None
        self.has_item = []
        self.has_item_any = None
        self.has_value = []

        self.valid_names = ['has_section','has_item','has_item_any',
                            'has_value']

        parsed_dict = parse_entry(parseable_line, valid_names = self.valid_names)
        for name,value in parsed_dict.items():
            setattr(self,name,value)
        #Options should always be a list
        if type(self.has_value) != list or type(self.has_item)!= list:
            raise ValueError("has_value and has_item_name is not type list in"
                             "config ----> {0}".format(parseable_line))

class ConfigEntry:
    """
    ConfigEntry designed to aid in parsing master config file entries.
    This is meant to parse:

    ------------------------------------------------------------
    item:
                    type = <value>,
                    options = [<value> <value>],
                    description = text describing entry
    -------------------------------------------------------------

    Config entry expects to recieve the above in the following format:

        {item:
            ["type = <value>",
             "options = [<value> <value>"],
             "description=text describing entry"]
        }

    Config entry then will parse the strings looking for space separated lists,
    values denoted with =, and will only recieve type,default,options,and
    description
    """

    def __init__(self, name=None, value=None, default = None, entry_type='str',
                 options=[], parseable_line=None):
        self.name = name
        self.value = value
        self.default = default
        self.options = options
        self.description = ''
        self.type = entry_type
        self.valid_names = ['default','type','options','description']

        if parseable_line != None:
            parsed_dict = parse_entry(parseable_line, valid_names = self.valid_names)
            for name,value in parsed_dict.items():
                setattr(self,name,value)

        self.default = self.convert_type(self.default)

        self.options = self.convert_type(self.options)

        #Options should always be a list
        if type(self.options) != list:
            self.options = [self.options]


    def convert_type(self,value):
        if str(value).lower() == 'none':
            value = None

        else:
            if self.type not in str(type(value)):
                value = cast_variable(value,self.type)

        return value
