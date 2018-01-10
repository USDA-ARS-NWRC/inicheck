from iniparse import read_config
from utilities import cast_variable

import os
import sys
class UserConfig():
    def __init__(self,filename,mcfg=None):
        self.filename = filename
        self.cfg = read_config(filename)
        if mcfg != None:
            self.mcfg = mcfg

    def add_defaults(self):
        """
        Look through the users config file and section by section add in missing
        parameters to add defaults

        Returns:
            user_cfg: User config dictionary with defaults added.
        """

        for section,configured in self.cfg.items():
                for k,v in self.mcfg[section].items():
                    if v.name not in configured.keys():
                        #print(v.name,v.default)
                        self.cfg[section][k]=v.default

    def check_config_file(self):
        """
        looks at the users provided config file and checks it to a master config file
        looking at correctness and missing info.

        Returns:
            tuple:
            - **warnings** - Returns a list of string messages that are consider non-critical issues with config file.
            - **errors** - Returns a list of string messages that are consider critical issues with the config file.
        """

        msg = "{: <20} {: <30} {: <60}"
        errors = []
        warnings = []

        #Check for all the required sections
        has_a_data_section = False
        data_sections = ['csv',"mysql","gridded"]
        user_sections = self.cfg.keys()

        for section in self.mcfg.keys():
            if section not in user_sections and section not in data_sections:
                # stations not needed if gridded input data used
                if 'gridded' not in user_sections and section == 'stations':
                    err_str = "Missing required section."
                    errors.append(msg.format(section," ", err_str))

            #Check for a data section
            elif section in user_sections and section in data_sections:
                has_a_data_section = True

        if not has_a_data_section:
            err_str = "Must specify a CSV or MySQL or Gridded section."
            errors.append(msg.format(" "," ", err_str))

        #Compare user config file to our master config
        for section,configured in self.cfg.items():
            #Are these valid sections?
            if section not in self.mcfg.keys():
                errors.append(msg.format(section,item, "Not a valid section."))

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
                                        pd.to_datetime(v)
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
            for item in raw_config[section].keys():
                sec[item] = ConfigEntry(name = item, parseable_line=raw_config[section][item])

            cfg[section] = sec

        return cfg


class ConfigEntry():
    def __init__(self, name=None, value=None, default = None, entry_type='str', options=[], parseable_line=None):
        self.name = name
        self.value = value
        self.default = default
        self.options = options
        self.description = ''
        self.type = entry_type

        if parseable_line != None:
            self.parse_info(parseable_line)

        self.default = self.convert_type(self.default)

        self.options = self.convert_type(self.options)

        #Options should always be a list
        if type(self.options) != list:
            self.options = [self.options]
        if self.name =='client':
            self.options = [v.upper() for v in self.options]

    def parse_info(self,info):
        """
        """
        if type(info) != list:
            info = [info]

        for s in info:
            if '=' in s:
                a = s.split('=')
            else:
                raise ValueError('Master Config file missing an equals sign in entry {0}\n or missing a comma above this entry'.format(info))

            name = (a[0].lower()).strip()
            if not hasattr(self,name):
                raise ValueError("Invalid option set in the Master Config File for item ----->{0}".format(name))

            value = a[1].strip()

            result = []
            value = value.replace('\n'," ")
            value = value.replace('\t',"")

            # Is there a list?
            if '[' in value:
                if ']' not in value:
                    raise ValueError("Missing bracket in Master Config file under {0}".format(name))
                else:
                    value = (''.join(c for c in value if c not in '[]'))
                    value = value.split(' ')
                    #value = [v for v in value if v == ' ' ]

            result = value
            setattr(self,name,result)

    def convert_type(self,value):
        if str(value).lower() == 'none':
            value = None

        else:
            if self.type not in str(type(value)):
                value = cast_variable(value,self.type)

        return value
