class UserConfig():
    def __init__(self,filename):
        pass

class MasterConfig():
    def __init__(self,filename):
        self.cfg = self._read_master_config(filename)

    def _read_master_config(self, master_config_file):
        """
        Reads in the core config file which has special syntax for specifying options

        Args:
            master_config_file: String path to the master config file.

        Returns:
            config: Dictionary of dictionaries representing the defaults and available
                    options in SMRF. Based on the Core Config file.
        """

        cfg = {}
        #Read in will automatically get the configurable key added
        raw_config = read_config(master_config_file)
        for section in raw_config.keys():
            sec = {}
            for item in raw_config[section]:
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
