from iniparse import read_config
from utilities import cast_variable
from entries import ConfigEntry, RecipeSection
from inicheck import __recipe_keywords__
from pandas import to_datetime
import os
import sys

class UserConfig():
    def __init__(self,filename,mcfg=None):
        self.filename = filename
        self.cfg = read_config(filename)
        if mcfg != None:
            self.mcfg = mcfg

    def add_recipes(self):
        """
        Look through the users config file and section by section add in missing
        parameters to add defaults

        Returns:
            user_cfg: User config dictionary with defaults added.
        """
        all_user_sections = self.cfg.keys()

        for r in self.mcfg.recipes:

            for trigger,recipe_entry in r.triggers.items():
                gates = 0
                gates_passed = 0
                #print(trigger)
                for name in recipe_entry.valid_names:
                    condition = getattr(recipe_entry,name)

                    #Checks  if not None or not empty list
                    if bool(condition):
                        #print('\t'+repr(condition))

                        gates+=1

                        #Make sections a list for D-R-Y
                        if 'section' in name:
                            if type(condition) != list:
                                condition = [condition]

                        #Checks for has_section,has_item, or has_value
                        if type(condition) == list and len(condition)>0:
                            #Section check
                            if condition[0] in all_user_sections:
                                #has_section
                                if len(condition) == 1:
                                    print('has_section {0}!'.format(repr(condition)))
                                    gates_passed+=1
                                else:
                                    print(condition[1],self.cfg[condition[0]].keys())

                                    #Check for item name in section
                                    if condition[1] in self.cfg[condition[0]].keys():
                                        # has_item
                                        if len(condition) == 2:
                                            print('has_item {0}!'.format(repr(condition)))
                                            gates_passed+=1

                                        else:
                                            #has_value
                                            if self.mcfg[condition[0]][condition[1]].convert_type(condition[2]) == self.cfg[condition[0]][condition[1]]:
                                                gates_passed+=1
                                                print('has_value {0}!'.format(repr(condition)))


                        else:
                            #look for an item name anywhere (has_item_any)
                            for section in self.cfg.keys():
                                if condition in self.cfg[section]:
                                    gates_passed+=1
                                    break

                #Determine if the condition was met.
                if gates!=0 and gates==gates_passed:
                    print "DEBUG: Trigger: {0} was met!".format(trigger)
                    #Insert the recipe into the users config
                    self.change_cfg(r.applied_config)
                else:
                    print "DEBUG: Trigger: {0} not met. gates = {1} and gates_passed = {2}".format(trigger,gates,gates_passed)


    def change_cfg(self,insert_cfg):
        """
        Uses inserts a partial config to the users config
        """
        for section in insert_cfg.keys():
            if section not in self.cfg.keys():
                self.cfg[section] = {}

            for item, value in insert_cfg[section].items():
                self.cfg[section][item] = value


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

        #Compare user config file to our master config
        for section, configured in self.cfg.items():

            #In the section check the values and options
            for item,value in configured.items():
                litem = item.lower()

                #Is the item known as a configurable item?
                if litem not in self.mcfg[section].keys():
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
                                v = self.mcfg[section][litem].convert_type(v)

                                # Do we have an idea os what to expect (type and options)?
                                options_type = self.mcfg[section][item].type

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

                                if self.mcfg[section][item].options and v not in self.mcfg[section][item].options:
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

        cfg = {}
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
