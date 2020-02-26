import copy
import importlib
from collections import OrderedDict
from os.path import abspath
from os.path import join as pjoin

from . import __recipe_keywords__
from .entries import ConfigEntry, RecipeSection
from .iniparse import read_config
from .utilities import get_relative_to_cfg, mk_lst

DEBUG = False
FULL_DEBUG = False


class UserConfig():
    """
    Class meant for managing the the users config, here we operate on the
    config repeatedly making it available through the attribute self.cfg

    Attributes:
        raw_cfg: Untouched original OrderedDict that inicheck read from file
        cfg: OrderedDict of the config file that inicheck will check, cast,
            list, etc
        recipes: List of entries.recipes.RecipesSection that apply to this
            config
        sections: List of strings that represent the unique sections for the
            whole config file
        items: List of strings that represent the unique items for the whole
            config file
        values: List of strings that represent the unique values for the whole
            config file
        mcfg: config.MasterConfig object that represents the standard the cfg
            is checked against


    """

    def __init__(self, filename, mcfg=None):
        """
        Args:
            filename: String to path containing config in .ini format
            mcfg: Object of the master config
        """
        self.filename = filename
        self.recipes = []
        self.raw_cfg = OrderedDict()

        # Hang on to the original
        if self.filename is not None:
            self.raw_cfg = read_config(filename)

            # The version  of the config that inicheck will mess with
            self.cfg = copy.deepcopy(self.raw_cfg)

            self.sections, self.items, self.values = \
                self.get_unique_entries(self.cfg)

        if mcfg is not None:
            self.mcfg = mcfg

    def apply_recipes(self):
        """
        Look through the users config file and section by section add in
        missing parameters to add defaults

        Returns:
            user_cfg: User config dictionary with defaults added.
        """

        # Add this in case the user has added anything to the config obj
        self.cfg = copy.deepcopy(self.raw_cfg)

        # Start fresh with recipes to avoid over populating the recipes list
        self.recipes = []

        for r in self.mcfg.recipes:

            for trigger, recipe_entry in r.triggers.items():
                # Full conditions met to handle mulitple triggers
                conditions_met = 0
                triggered = False

                # All conditions must be met if to be applied
                for condition in recipe_entry.conditions:
                    conditions_triggered = []
                    for section in self.cfg.keys():

                        # Is it a valid section
                        if section in self.mcfg.cfg.keys():

                            # Watch out for empty sections
                            if len(self.cfg[section].keys()) == 0:
                                items = [None]
                            else:
                                items = self.cfg[section].keys()

                            for item in items:
                                # Confirm its a registered item
                                if item in self.mcfg.cfg[section].keys():
                                    vals = mk_lst(self.cfg[section][item])

                                # Watch for empties
                                elif item is None:
                                    vals = [None]
                                else:
                                    vals = []

                                for v in vals:
                                    # Sections

                                    if (condition[0] == 'any' or
                                            condition[0] == section):

                                        if FULL_DEBUG:
                                            print("Section Gate {0} == {1}"
                                                  "".format(condition[0],
                                                            section))
                                        # Items
                                        if (condition[1] == 'any' or
                                                condition[1] == item):
                                            if FULL_DEBUG:
                                                print("\t\tItem Gate {0} == {1}"
                                                      "".format(condition[1],
                                                                item))
                                            # Values
                                            if (condition[2] == 'any' or
                                                    condition[2] == v):
                                                if FULL_DEBUG:
                                                    print("\t\t\t\tValue Gate {0}"
                                                          " == {1}"
                                                          "".format(condition[2],
                                                                    v))

                                                # No conditions == [any any
                                                # any]
                                                conditions_triggered.append(
                                                    (section, item, v))
                                                triggered = True

                    # Determine if the condition was met.
                    if triggered:
                        conditions_met += 1
                        triggered = False

                if (conditions_met == len(recipe_entry.conditions) and
                        len(recipe_entry.conditions) != 0):
                    conditions_met = 0
                    self.recipes.append(r)

                    # Check recipes for sections not in the master
                    invalid_r_sections = [s for s in r.adj_config.keys()
                                          if (s not in self.mcfg.cfg.keys()
                                              and s != 'any')]

                    if len(invalid_r_sections) > 0:
                        raise ValueError("The recipe {} attempts to modify"
                                         " section(s) {} not recognized by Master Config."
                                         "".format(r.name, ",".join(invalid_r_sections)))

                    if DEBUG:
                        print("\nDEBUG: Trigger: {0} {1} was met!"
                              "".format(trigger, condition))

                    # Iterate through the conditions found and apply
                    for situation in conditions_triggered:
                        # Insert the recipe into the users config
                        self.cfg = self.interpret_recipes(r.adj_config,
                                                          situation)

                else:
                    if DEBUG:
                        print("\nDEBUG: Trigger: {0} not met. gates = {1}"
                              " and gates_passed = {2}"
                              "".format(trigger, condition,
                                        conditions_met))
                        print('\n\n')

    def interpret_recipes(self, partial_cfg, situation):
        """
        User inserts a partial config by using each situation that
        triggered a recipe. A triggering situation consists of a tuple of
        (section, item, value) that represent the specific settings that
        trigger the recipe. All default references should avoid overwriting the
        users selection.

        Args:
            partial_cfg: dictionary of edits to be applied to the cfg
            situation: List of len=3 describing the trigger mechanism
        Return:
            result: Modified dictionary
        """
        result = copy.deepcopy(self.cfg)

        for section in partial_cfg.keys():
            for item in partial_cfg[section].keys():
                remove = False
                value = partial_cfg[section][item]
                values = mk_lst(value)

                for value in values:

                    # Defaults Keyword
                    if item == 'apply_defaults':
                        if str(value).lower() == 'true':
                            result = self.add_defaults(result,
                                                       sections=section)

                    # Keyword removal
                    elif item == 'remove_section':
                        if value.lower() == 'true':

                            if section in result.keys():
                                if DEBUG:
                                    print("removed section: {0}"
                                          "".format(section))
                                del result[section]

                    # Normal operation
                    else:

                        # Handle the any keyword for sections
                        if section == 'any':
                            s = situation[0]

                        else:
                            s = section

                        # Handle the any keyword for items
                        if item == 'any':
                            i = situation[1]

                        # Enable removing and defaulting
                        elif item in ['remove_item', 'default_item']:
                            i = value

                            if item == "default_item":
                                value = "default"

                            #value = "default"
                        # Nothing special asusme its a valid item name
                        else:
                            i = item

                        # Replace ANYs with values from the situation
                        if value == 'any':
                            v = situation[2]

                        elif value == 'default':
                            # Confirm existence in master
                            if i in self.mcfg.cfg[s].keys():

                                # Prefer user selection over default
                                if i not in self.cfg[s]:
                                    v = self.mcfg.cfg[s][i].default

                            else:
                                raise Exception('{0} is not a valid item for '
                                                'the master config section {1}, check your '
                                                'recipes for a situation triggering on {2}, '
                                                '{3}, {4}'.format(i, s, situation[0],
                                                                  situation[1],
                                                                  situation[2]))
                        # default items were sepcified.
                        else:

                            v = value

                        # Delete items

                        if item == 'remove_item':
                            if s in result.keys():
                                if i in result[s].keys():
                                    if DEBUG:
                                        print("Removed: {0} {1}".format(s, i))
                                    del result[s][i]

                        elif s in result.keys():
                            # Check for empty dictionaries
                            if not bool(result[s]):
                                if DEBUG:
                                    print("Adding section {0}".format(s))
                                result[s] = OrderedDict()

                            # Dictionary exists
                            else:

                                # Handle a item not provided by automatically
                                # adding it
                                if i not in result[s].keys():
                                    if DEBUG:
                                        print("Adding {0} {1} {2}"
                                              "".format(s, i, v))
                                    result[s][i] = v

                                # If the item was provided we don't want to
                                # overide the user with defaults
                                elif value != 'default':
                                    if DEBUG:
                                        print("Changing {0} {1} {2}"
                                              "".format(s, i, v))
                                    result[s][i] = v

        return result

    def get_unique_entries(self, cfg):
        """
        Appends all the values in the user config to respectives lists of
        section names, item names, and values. Afterwards any copy is
        removed so all is left is a unique list of names and values

        Args:
            cfg: OrderedDict of the config file
        Returns:
            tuple: tuple of len=3 of sets of unique sections items and values
        """

        unique_sections = []
        unique_items = []
        unique_values = []

        for section in cfg.keys():
            for item, value in cfg[section].items():
                if not isinstance(value, list):
                    vals = [value]
                else:
                    vals = value

                for v in vals:
                    unique_sections.append(section)
                    unique_items.append(item)
                    unique_values.append(v)

        return set(unique_sections), set(unique_items), set(unique_values)

    def add_defaults(self, cfg, sections=None, items=None):
        """
        Look through the users config file and section by section add in
        missing parameters to add defaults

        Args:
            sections: Single section name or a list of sections to apply
                      (optional) otherwise uses all sections in users
                      config
        Returns:
            user_cfg: User config dictionary with defaults added.

        """
        master = self.mcfg.cfg
        result = copy.deepcopy(cfg)
        # Either go through specified sections or all sections provided by
        # user.
        if sections is None:
            sections = result.keys()
        else:
            # Accounts for single items not entered as a list
            sections = mk_lst(sections)

        for section in sections:
            configured = result[section]
            for k, v in master[section].items():
                if v.name not in configured.keys():
                    result[section][k] = v.default
        return result

    def update_config_paths(self, user_cfg_path=None):
        """
        Sets all paths so that they are always relative to the config
        file or absolute.
        """
        if user_cfg_path is None:
            user_cfg_path = self.filename

        mcfg = self.mcfg.cfg
        cfg = self.cfg

        # Cycle thru users config
        for section in cfg.keys():
            for item in cfg[section].keys():
                d = cfg[section][item]

                # Does master have this and is it not none
                if item in mcfg[section].keys() and d is not None:
                    m = mcfg[section][item]
                    # Any paths
                    if m.type == 'filename' or m.type == 'directory':
                        cfg[section][item] = \
                            get_relative_to_cfg(cfg[section][item],
                                                self.filename)
        return cfg


class MasterConfig():
    def __init__(self, path=None, modules=None, checkers=None, titles=None,
                 header=None, changelogs=None):

        self.paths = []
        self.recipes = []
        self.titles = {}
        self.header = header
        self.checker_modules = []
        self.changelogs = []

        # Paths were manually provided
        if path is not None and modules is None:
            for p in mk_lst(path):
                self.paths.append(abspath(p))

        # If a module was passed
        if modules is not None and self.paths == []:

            for m in mk_lst(modules):
                i = importlib.import_module(m)
                self.paths.append(abspath(pjoin(i.__file__,
                                                i.__core_config__)))

                # Search for possible recipes provided in the module
                if hasattr(i, '__recipes__'):
                    self.paths.append(i.__recipes__)

                # Search for possible section titles provided in the module
                if hasattr(i, '__config_titles__'):
                    self.titles.update(getattr(i, '__config_titles__'))

                # Search for config headers provided in the module
                if hasattr(i, '__config_header__'):
                    self.header = getattr(i, '__config_header__')

                # Search for custom checkers
                if hasattr(i, '__config_checkers__'):
                    self.checker_modules.append(m + '.' +
                                                getattr(i,
                                                        '__config_checkers__'))
                # Grab ayny change logs
                if hasattr(i, "__config_changelog__"):
                    self.changelogs.append(abspath(pjoin(i.__file__,
                                                         i.__config_changelog__)))

        # Add any extra ones provided
        if checkers is not None:
            for c in mk_lst(checkers):
                self.checker_modules.append(c)

        if titles is not None:
            self.titles.update(titles)

        if header is not None:
            self.header = header

        if changelogs is not None:
            self.changelogs.append(changelogs)

        if len(self.paths) == 0 and modules is None:
            raise ValueError("No file was either provided or found when"
                             " initiating a master config file.")

        self.cfg = self.add_files(self.paths)

    def add_files(self, paths):
        """
        Designed to  add to the master config file if the user has split
        up files to reduce the amount of info in a master file. e.g.
        recipes are stored in another file.

        Args:
            paths: list of real path to another cfg.ini
        Returns:
            config: Original config with appended information found in the
                    extra cfg
        """

        result = OrderedDict()

        for f in paths:
            if f is not None:
                extra_cfg = self._read(f)
                result.update(extra_cfg)

        return result

    def merge(self, mcfg):
        """
        Merges the a master config object into the current master config object
        in place
        """

        self.recipes += mcfg.recipes
        self.checker_modules += mcfg.checker_modules
        self.titles.update(mcfg.titles)
        self.cfg.update(mcfg.cfg)

    def _read(self, master_config_file):
        """
        Reads in the core config file which has special syntax for
        specifying options

        Args:
            master_config_file: String path to the master config file.

        Returns:
            config: Dictionary of dictionaries representing the defaults
                    and available options. Based on the Core Config file.
        """

        cfg = OrderedDict()

        # Read in will automatically get the configurable key added
        raw_config = read_config(master_config_file)

        for section in raw_config.keys():
            sec = OrderedDict()

            # Look for keywords in section name e.g. recipe
            for word in __recipe_keywords__:
                if word in section:
                    self.recipes.append(RecipeSection(raw_config[section],
                                                      name=section))
                    break

                # Look for master properties
                else:
                    for item in raw_config[section].keys():
                        sec[item] = ConfigEntry(name=item,
                                                parseable_line=raw_config[section][item])

                    cfg[section] = sec

        return cfg


def check_types(cfg, checkers):
    """
    Iterates through all the master config items and confirm all type are valid

    Args:
        cfg: dict of master config entries listing out properties
        checkers: dict of checker names and class  as Key Value pairs

    Returns:
        Bool: True if no error is raised
    Raises:
        ValueError: raises error if a type is specified not in the lists of
                    checkers
    """

    for s in cfg.keys():
        for i in cfg[s].keys():

            type_value = cfg[s][i].type
            # Is the specified type recognized?
            if type_value not in checkers.keys():
                raise ValueError("\n\nIn master config, SECTION: {0} at ITEM:"
                                 " {1} attempts to use undefined type name "
                                 " '{2}' which has no checker associated."
                                 "\nAvailable checkers are:\n\n{3}"
                                 "".format(s, i, type_value, checkers.keys()))
    return True
