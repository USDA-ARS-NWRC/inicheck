from iniparse import read_config
from utilities import cast_variable
from entries import ConfigEntry, RecipeSection
from inicheck import __recipe_keywords__
from pandas import to_datetime
from collections import OrderedDict
import os
import sys
import copy

class UserConfig():

    def __init__(self,filename,mcfg=None):
        self.filename = filename
        self.cfg = read_config(filename)
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

                for condition in recipe_entry.conditions:
                    trigger_section = None
                    trigger_item = None
                    trigger_value = None

                    for section in self.cfg.keys():
                        if (condition[0] == 'any' or
                            condition[0] == section):

                           #checks for a section only
                           if condition[1:2] == ['any','any']:
                               print("has_section triggered! {0}".format(condition))
                               conditions_met+=1
                               break
                           else:
                               for item, value in self.cfg[section].items():
                                   if (condition[1] == 'any' or
                                       condition[1] == item):

                                       # has any items named
                                       if (condition[0]=='any' and
                                           condition[2]=='any'):
                                           conditions_met+=1
                                           print("has_item anywhere triggered! {0}".format(condition))
                                           break

                                       else:
                                           if (condition[2] == 'any' or
                                               [condition[2]] == value):

                                               print("has_value triggered! {0}".format(condition))
                                               conditions_met+=1
                                               break


                #Determine if the condition was met.
                print("NGates: {0} NPassed {1}".format(len(recipe_entry.conditions),conditions_met))
                if (len(recipe_entry.conditions)==conditions_met and
                    len(recipe_entry.conditions) != 0):

                    print "\nDEBUG: Trigger: {0} {1} was met!".format(trigger,condition)
                    #Insert the recipe into the users config
                    self.cfg = self.change_cfg(r,trigger_section=section,
                                                     trigger_item=item,
                                                     trigger_value=value)
                    break
                else:
                    print "\nDEBUG: Trigger: {0} not met. gates = {1} and gates_passed = {2}".format(trigger,condition,conditions_met)
                print('\n\n')

    def change_cfg(self,insert_cfg, trigger_section=None,trigger_item=None,
                    trigger_value=None):
        """
        Uses inserts a partial config to the users config. If the user has
        already defined a value that the inser_cfg has it will do nothing
        """
        result = copy.deepcopy(self.cfg)

        for sections in insert_cfg.keys():
            #Apply cfg to all sections
            if sections =='all':
                sections = result.keys()
                insert_key = 'all'
            #Apply cfg only to section that triggered it
            elif sections == 'any':
                insert_key = 'any'

                if trigger_section == None:
                    raise ValueError('trigger entries cannot be passed as None if keyword any is used')
                else:
                    sections = trigger_section
            else:
                insert_key = None
            if type(sections)!=list:
                sections = [sections]

            for s in sections:

                #Adding a new section
                if s not in result.keys():
                    result[s] = {}

                #Special
                if insert_key not in ['all','any']:
                    insert_key = s

                for item, value in insert_cfg[insert_key].items():
                    applied = value
                    if not item in result[s].keys():
                        #Recipe requests defaults for section
                        print("SECTION: {0} INSERT_KEY: {1} ITEM: {2} VALUE: {3}".format(s,insert_key,item,value))
                        if item == 'apply_defaults' and value.lower() == 'true':
                            for d_item, obj in self.mcfg.cfg[s].items():
                                result[s][d_item] = obj.default

                        #Recipe requests default for item
                        elif value =='default':
                            applied = self.mcfg.cfg[s][item].default

                        #Recipe specifies the entire entry
                        else:
                            print("Added {0} {1} {2}".format(s,item,applied))
                            result[s][item] = applied

                    #Item already in the cfg
                    else:
                        if item == 'remove_section' and value.lower() == 'true':
                            del result[s]
                            print("Removed Section {0}".format(s))
                            #break

                        elif item == 'remove_item':
                            if value in result[s].keys():
                                del result[s][value]
                                print("Removed item {0}, {1}".format(s,item))

            return result

    def add_config(self,add_cfg):
        """
        Adds add_config to self.cfg
        """
        

    def add_defaults(self):
        """
        Look through the users config file and section by section add in missing
        parameters to add defaults

        Returns:
            user_cfg: User config dictionary with defaults added.
        """
        master = self.mcfg.cfg

        for section,configured in self.cfg.items():
                for k,v in master[section].items():
                    if v.name not in configured.keys():
                        self.cfg[section][k]=v.default

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
                                    if self.filename != None:
                                        p = os.path.split(self.filename)
                                        v = os.path.join(p[0],v)

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
    def __init__(self,filename):
        self.recipes = []
        self.cfg = self._read(filename)

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
                    self.recipes.append(RecipeSection(raw_config[section]))
                    break
                else:
                    for item in raw_config[section].keys():
                        sec[item] = ConfigEntry(name = item, parseable_line=raw_config[section][item])

                    cfg[section] = sec


        return cfg
