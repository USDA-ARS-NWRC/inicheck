from .iniparse import read_config
from .utilities import cast_variable, mk_lst, pcfg
from .entries import ConfigEntry, RecipeSection
from . import __recipe_keywords__
from pandas import to_datetime
from collections import OrderedDict
import os
import sys
import copy
import importlib

DEBUG = True
FULL_DEBUG = False

class UserConfig():

    def __init__(self,filename,mcfg=None):
        self.filename = filename
        self.recipes = []
        self.cfg = read_config(filename)
        self.sections,self.items,self.values = self.get_unique_entries(self.cfg)
        if mcfg != None:
            self.mcfg = mcfg

    def apply_recipes(self):
        """
        Look through the users config file and section by section add in missing
        parameters to add defaults

        Returns:
            user_cfg: User config dictionary with defaults added.
        """

        for r in self.mcfg.recipes:

            for trigger,recipe_entry in r.triggers.items():
                conditions_met = 0
                triggered = False
                #All conditions must be met if to be applied
                for condition in recipe_entry.conditions:
                    conditions_triggered = []
                    for section in self.cfg.keys():

                        #Watch out for empty sections
                        if len(self.cfg[section].keys()) == 0:
                            items = [None]
                        else:
                            items = self.cfg[section].keys()

                        for item in items:
                            #Watch for empties
                            if item == None:
                                vals = [None]
                            else:
                                vals = mk_lst(self.cfg[section][item])
                            for v in vals:

                                if (condition[0] == 'any' or
                                    condition[0] == section):
                                   if FULL_DEBUG:
                                       print("Section Gate {0} == {1}".format(condition[0],section))

                                   if (condition[1] == 'any' or
                                       condition[1] == item):
                                      if FULL_DEBUG:
                                          print("\t\tItem Gate {0} == {1}".format(condition[1],item))

                                      if (condition[2] == 'any' or
                                          condition[2] == v):
                                          if FULL_DEBUG:
                                             print("\t\t\t\tValue Gate {0} == {1}".format(condition[2],v))

                                          #Note conditions cannot be [any any any]
                                          conditions_triggered.append((section,item,v))
                                          triggered = True

                    #Determine if the condition was met.
                    #print("NGates: {0} NPassed {1}".format(len(recipe_entry.conditions),conditions_met))
                    if triggered:
                        conditions_met +=1
                        triggered = False

                if (conditions_met==len(recipe_entry.conditions) and
                    len(recipe_entry.conditions) != 0):
                    conditions_met = 0
                    self.recipes.append(r)

                    if DEBUG:
                        print "\nDEBUG: Trigger: {0} {1} was met!".format(trigger,condition)

                    #Iterate through the conditions found and apply changes
                    for situation in conditions_triggered:
                        #Insert the recipe into the users config for each situation
                        self.cfg = self.interpret_recipes(r.adj_config, situation)
                else:
                    if DEBUG:
                        print "\nDEBUG: Trigger: {0} not met. gates = {1} and gates_passed = {2}".format(trigger,condition,conditions_met)
                        print('\n\n')


    def interpret_recipes(self,partial_cfg, situation):
        """
        User inserts a partial config by using each situation that triggered a
        recipe. A situation consists of a tuple of (section,item,value).
        """
        result = copy.deepcopy(self.cfg)

        for section in partial_cfg.keys():
            for item in partial_cfg[section].keys():
                remove = False
                value = partial_cfg[section][item]

                if item =='apply_defaults':
                    result = self.add_defaults(result,sections = section)

                elif item == 'remove_section':
                    if value.lower()=='true':

                        if section in result.keys():
                            print("removed section: {0}".format(section))
                            del result[section]

                else:

                    #Normal operation
                    if section =='any':
                        s = situation[0]

                    else:
                        s = section

                    if item == 'any':
                        i = situation[1]

                    elif item == 'remove_item':
                        i = value

                    else:
                        i = item

                    if value == 'any':
                        v = situation[2]

                    elif value == 'default' and i in self.mcfg.cfg[s].keys():
                        v = self.mcfg.cfg[s][i].default

                    else:
                        v = value

                    if item == 'remove_item':
                        if s in result.keys():
                            if i in result[s].keys():
                                print("Removed: {0} {1}".format(s,i))
                                del result[s][i]

                    elif s in result.keys():
                        #Check for empty dictionaries, add them if not removing
                        if not bool(result[s]):
                            print("Adding section {0}".format(s))
                            result[s] = {}
                        else:
                            if i not in result[s].keys():
                                print("Adding {0} {1} {2}".format(s,i,v))
                                result[s][i]=v

        return result


    def get_unique_entries(self,cfg):
        """
        Appends all the values in the user config to respectives lists of
        section names, item names, and values. Afterwards any copy is removed
        so all is left is a unique list of names and values
        """

        unique_sections = []
        unique_items = []
        unique_values = []

        for section in cfg.keys():
            for item,value in cfg[section].items():
                if type(value) != list:
                    vals = [value]
                else:
                    vals = value

                for v in vals:
                    unique_sections.append(section)
                    unique_items.append(item)
                    unique_values.append(v)

        return set(unique_sections),set(unique_items), set(unique_values)


    def add_defaults(self, cfg, sections = None):
        """
        Look through the users config file and section by section add in missing
        parameters to add defaults

        Args:
            sections: Single section name or a list of sections to apply (optional)
                      otherwise uses all sections in users config
        Returns:
            user_cfg: User config dictionary with defaults added.

        """
        master = self.mcfg.cfg
        result = copy.deepcopy(cfg)
        #Either go through specified sections or all sections provided by the user.
        if sections == None:
            sections = result.keys()
        else:
            #Accounts for single items not entered as a list
            sections = mk_lst(sections)

        for section in sections:
            configured = result[section]
            for k,v in master[section].items():
                if v.name not in configured.keys():
                    result[section][k]=v.default
        return result

    def update_config_paths(self,user_cfg_path = None):
            """
            Sets all paths so that they are always relative to the config file or
            absolute.
            """
            if user_cfg_path == None:
                user_cfg_path = self.filename

            mcfg = self.mcfg.cfg
            cfg = self.cfg

            #Cycle thru users config
            for section in cfg.keys():
                for item in cfg[section].keys():
                    d = cfg[section][item]
                    #Does master have this and is it not none
                    if item in mcfg[section].keys() and d != None:
                        m = mcfg[section][item]
                        #Any paths
                        if m.type == 'filename' or  m.type == 'directory':
                            if not os.path.isabs(cfg[section][item]):
                                path = os.path.abspath(os.path.join(os.path.dirname(user_cfg_path),cfg[section][item]))
                                cfg[section][item] = path
            return cfg

    def check(self):
        """
        looks at the users provided config file and checks it to a master config file
        looking at correctness and missing info.

        Returns:
            tuple:
            - **warnings** - Returns a list of string messages that are consider
                             non-critical issues with config file.
            - **errors** - Returns a list of string messages that are consider
                           critical issues with the config file.
        """

        msg = "{: <20} {: <30} {: <60}"
        errors = []
        warnings = []
        master = self.mcfg.cfg

        #Compare user config file to our master config
        for section, configured in self.cfg.items():

            #In the section check the values and options
            for item,value in configured.items():
                litem = item.lower()

                #Is the item known as a configurable item?
                if litem not in master[section].keys():
                    wrn = "Not a registered option."
                    if section.lower() == 'wind':
                        wrn +=  " Common for station names."
                    warnings.append(msg.format(section,item, wrn))
                else:
                    if litem != 'stations':
                        #Did the user provide a list value or single value
                        if type(value) != list:
                            val_lst = [value]
                        else:
                            val_lst = value

                        for v in val_lst:
                            if v != None:
                                v = master[section][litem].convert_type(v)

                                # Do we have an idea os what to expect (type and options)?
                                options_type = master[section][item].type

                                if options_type == 'datetime':
                                    try:
                                        to_datetime(v)
                                    except:
                                        errors.append(msg.format(section,item,'Format not datetime'))

                                elif options_type == 'filename':
                                    if self.filename != None and v != None:
                                        p = os.path.dirname(self.filename)
                                        v = os.path.join(p,v)

                                        if not os.path.isfile(os.path.abspath(v)):
                                            errors.append(msg.format(section,item,'Path does not exist'))

                                elif options_type == 'directory':
                                    if self.filename != None:
                                        p = os.path.split(self.filename)
                                        v = os.path.join(p[0],v)

                                    if not os.path.isdir(os.path.abspath(v)):
                                        warnings.append(msg.format(section,item,'Directory does not exist'))

                                #Check int, bools, float
                                elif options_type not in str(type(v)):
                                    errors.append(msg.format(section,item,'Expecting a {0} recieved {1}'.format(options_type,type(v))))

                                if master[section][item].options and v not in master[section][item].options:
                                    err_str = "Invalid option: {0} ".format(v)
                                    errors.append(msg.format(section, item, err_str))

        return warnings,errors

class MasterConfig():
    def __init__(self, path=None, module=None):

        if path == None:
            path == []

        if type(path) != list:

            path = [path]

        self.recipes = []

        if module != None:
            i = importlib.import_module(module)
            path.append(os.path.abspath(os.path.join(i.__file__, i.__core_config__)))

            if hasattr(i,'__recipes__'):
                path.append(i.__recipes__)

        if len(path)==0:
            raise ValueError("No file was either provided or found when initiating a master config file")

        self.cfg = self.add_files(path)

    def add_files(self,paths):
        """
        Designed to  add to the master config file if the user has split up files
        to reduce the amount of info in a master file. e.g. recipes are stored in a
        other file

        Args:
            paths: list of real path to another cfg.ini
        Returns:
            config: Original config with appended information found in the extra cfg
        """

        result = OrderedDict()

        for f in paths:
            if f != None:
                extra_cfg = self._read(f)
                result.update(extra_cfg)

        return result

    def _read(self, master_config_file):
        """
        Reads in the core config file which has special syntax for specifying options

        Args:
            master_config_file: String path to the master config file.

        Returns:
            config: Dictionary of dictionaries representing the defaults and available
                    options. Based on the Core Config file.
        """

        cfg = OrderedDict()
        #Read in will automatically get the configurable key added
        raw_config = read_config(master_config_file)
        for section in raw_config.keys():
            sec = {}
            for word in __recipe_keywords__:
                if word in section:
                    self.recipes.append(RecipeSection(raw_config[section], name = section))
                    break
                else:
                    for item in raw_config[section].keys():
                        sec[item] = ConfigEntry(name = item, parseable_line=raw_config[section][item])

                    cfg[section] = sec


        return cfg
