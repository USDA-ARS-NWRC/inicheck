from collections import OrderedDict
from . iniparse import parse_entry
from . import __trigger_keywords__

class RecipeSection:
    """
    The RecipeSection enables the master config file to parses a section
    that is actually a recipe. Operates using keywords provided n the name
    of the section. It collects triggers and adjustments to the config file
    and assigns them to this class. Trigger represent the conditional
    statements to apply the adjustments listed  below. If an item in the
    section doesn't contain any trigger keyword then it is assumed to be
    an adjustment to be made.

    """

    def __init__(self, recipe_section_dict, name=None):
        """
            Args:
                recipe_section_dict: a dictionary containing the triggers
                                     and config file adjustments.
        """
        self.name = name

        # Conditions to be met
        self.triggers = OrderedDict()

        # Config file to apply if conditions are met
        self.adj_config = OrderedDict()

        for item, entry in recipe_section_dict.items():

            # Check item for action keywords
            for word in __trigger_keywords__:
                if word in item:
                    self.triggers[item] = TriggerEntry(entry)
                    break

            # Check for assigned values if any trigger
            if item not in self.triggers.keys():
                item_dict = parse_entry(entry, item = item)

                self.adj_config[item] = item_dict

class TriggerEntry:
    """
    RecipeEntry designed to aid in parsing master config file entries under
    a recipe.
    This is meant to parse:

    Example::

        ------------------------------------------------------------
        item_trigger:
                        has_section_name = <value>,
                        has_value = [<section name> <item name>, <value>],
                        has_item_name = <value>

        -------------------------------------------------------------

    Config entry expects to recieve the above in the following format:

    .. code-block:: python

        {item_trigger:
                    ["has_section = <value>",
                     "has_item = [<section> <item>"],
                     "has_value = [<section> <item> <value>]"
                     ]
        }

    Recipe entry then will parse the strings looking for space separated lists,
    values denoted with = and will only accept keyword

        * has_section
        * has_item
        * has_value

    """

    def __init__(self, parseable_line, name=None):

        self.conditions = []
        self.valid_names = ['has_section', 'has_item', 'has_value']
        heirarcy = ['section', 'item', 'value']

        parsed_dict = parse_entry(parseable_line,
                                  valid_names=self.valid_names)
        # There can be multiple conditions returned
        for name,value in parsed_dict.items():
            result = ['any', 'any', 'any']
            if type(value) == list:
                # Easy assignment to result using [section  item value syntax]
                for i,v in enumerate(value):
                    result[i] = v

            # If single item provided
            else:
                for i,keyword in enumerate(heirarcy):
                    if keyword in name:
                        result[i] = value

            # If result is all any, then clear it
            if len([True for i in result if i == 'any']) != len(result):
                self.conditions.append(result)


class ConfigEntry:
    """
    ConfigEntry designed to aid in parsing master config file entries.
    This is meant to parse:

    Example::

        ------------------------------------------------------------
        item:
                        type = <value>,
                        options = [<value> <value>],
                        description = text describing entry
        -------------------------------------------------------------

    Config entry expects to recieve the above in the following format:

    .. code-block:: python

        {item:
            ["type = <value>",
             "options = [<value> <value>"],
             "description=text describing entry"]
        }

    Config entry then will parse the strings looking for space separated
    lists, values denoted with =, and will only receive:

        * type
        * default
        * options
        * description

    """

    def __init__(self, name=None, value=None, default=None,
                 entry_type='string', options=[], parseable_line=None):

        self.name = name
        self.value = value
        self.default = default
        self.options = options
        self.description = ''
        self.listed = False
        self.type = entry_type
        self.valid_names = ['default', 'type', 'options', 'description']

        if parseable_line != None:
            parsed_dict = parse_entry(parseable_line, item = name,
                                        valid_names=self.valid_names)
            for name,value in parsed_dict.items():
                setattr(self,name,value)

        # Options should always be a list
        if type(self.options) != list:
            self.options = [self.options]

        # types should always be lower case
        self.type = self.type.lower()

        # Handle the list types
        if 'list' in self.type:
            self.listed = True
            self.type = self.type.replace('list','')
            self.type = self.type.strip()
