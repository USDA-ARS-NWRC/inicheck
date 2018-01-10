# -*- coding: utf-8 -*-


def cast_variable(variable,type_value):
    """
    Casts an object to the spectified type value
    Args:
        variable - some variable to be casted
        type_value - string value indicating type to cast.
    Returns:
        value - The original variable now casted in type_value
    """
    if type(variable) != list:
        variable = [variable]
    type_value = str(type_value)
    value = []
    for v in variable:
        if 'datetime' in type_value:
            value.append(pd.to_datetime(v))
        elif 'bool' in type_value:
            if v.lower() in ['yes','y','true']:
                v = True
            elif v.lower() in ['no','n','false']:
                v = False

            value.append(bool(v))
        elif 'int' in type_value:
            value.append(int(v))
        elif 'float' in type_value:
            value.append(float(v))
        elif type_value == 'filename' or type_value == 'directory':
            value.append(v)
        elif v in ['none']:  # None
            value.append(None)
        elif 'str' in type_value:
            value.append(str(v.lower()))
        else:
            raise ValueError("Unknown type_value prescribed. ----> {0}".format(type_value))

    if len(value) == 1:
        value = value[0]
    return value

def parse_config_type(options):
    """
    Parses out the type of a config file available options entry, types are identified
    by < > and type string is the default.
    Types parseable
    datetime
    bool
    integer
    float
    str
    filename
    directory

    Args:
        options - Parsed lines from the master config file.

    Returns:
        tuple:
            Returns the type and the rest of the line in the config file.
            - **option_type** - the string name of the expected type.
            - **option** - the string value of the option parsed.

    """

    type_options = ['datetime','filename','directory','bool','int','float','str']
    if '<' in options and '>' in options:
        start = options.index('<')
        end = options.index('>')
        option_type = options[start+1:end]
        option = options[end+1:]
    else:
        option_type='str'
        option = options

    #Recognize the options.
    if option_type in type_options:
        #print option_type, option
        return option_type, option

    else:
        raise ValueError("Unrecognized type in CoreConfig file ---> '{0}'".format(options))


def parse_str_setting(str_option):
    """
    Parses a single string where options are separated by =
    returns tuple of string
    Require users specfies settings with an equals sign

    Args:
        str_option - the string line that was received from the config file

    Returns:
        tuple:
            Returns the name and values parsed in the config file.
            - **name** - the string name value of the option parsed.
            - **option** - the string value of the option parsed.
    """

    if "=" in str_option:
        name,option = str_option.split("=")
        name = (name.lower()).strip()
        option = (option.lower()).strip()
        option_type, option = parse_config_type(option)
    else:
        msg = "Config file string does not have any options with = to parse."
        msg+= "\nError occurred parsing in config file:\n {0}".format(str_option)
        raise ValueError(msg)

    return name,option_type,option


def parse_lst_options(option_lst_str,types=False):
    """
    Parse options that can be lists form the master config file and returns a dict
    e.g.
    available_options = distribution=[idw,dk,grid],slope=[-1 0 1]...
    returns
    available_options_dict = {"distribution":[dk grid idw],
              "slope":[-1 0 1]}

    Args:
        option_lst_str -  string value of the lined parsed potentiall containing a list.

    Returns:
        available: A dictionary with keys as the names of the entries and values are lists of the options

    """

    available = {}
    #check to see if it is a lists
    if option_lst_str is not None:
        if type(option_lst_str) != list:
            #account for auto lists made by config parser
            options_parseable = [option_lst_str]
        else:
            options_parseable = option_lst_str

        for entry in options_parseable:
            name,option_type,option_lst = parse_str_setting(entry)

            #Account for special syntax for providing a list answer
            options = (''.join(c for c in option_lst if c not in '[]'))
            options = (options.replace('\n'," ")).split(' ')
            if type(options)!=list:
                options = [option_lst]

            #Get correct data type
            for i,o in enumerate(options):
                if o:
                    value = cast_variable(o,option_type)
                else:
                    value = ""
                options[i] = value

            #Change it back from being a list
            if len(options) == 1:
                options = options[0]
            if types:
                available[name] = ConfigEntry(name=name, entry_type = option_type, available_options = options)
            else:
                available[name] = ConfigEntry(name=name, available_options = options)

    return available


def check_config_file(user_cfg, master_config,user_cfg_path=None):
    """
    looks at the users provided config file and checks it to a master config file
    looking at correctness and missing info.

    Args:
        user_cfg - Config file dictionary created by :func:`~smrf.utils.io.read_config'.
        master_config - Config file dictionary created by :func:`~smrf.utils.io.read_master_config'
        user_cfg_path - Path to the config file that is being checked. Useful for relative file paths. If none assumes relative paths from CWD.

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
    user_sections = user_cfg.keys()

    for section in master_config.keys():
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
    for section,configured in user_cfg.items():
        #Are these valid sections?
        if section not in master_config.keys():
            errors.append(msg.format(section,item, "Not a valid section."))

        #In the section check the values and options
        for item,value in configured.items():
            litem = item.lower()
            #Is the item known as a configurable item?
            if litem not in master_config[section].keys():
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
                            v = master_config[section][litem].convert_type(v)

                            # Do we have an idea os what to expect (type and options)?
                            options_type = master_config[section][item].type

                            if options_type == 'datetime':
                                try:
                                    pd.to_datetime(v)
                                except:
                                    errors.append(msg.format(section,item,'Format not datetime'))

                            elif options_type == 'filename':
                                if user_cfg_path != None:
                                    p = os.path.split(user_cfg_path)
                                    v = os.path.join(p[0],v)

                                if not os.path.isfile(os.path.abspath(v)):
                                    errors.append(msg.format(section,item,'Path does not exist'))

                            elif options_type == 'directory':
                                if user_cfg_path != None:
                                    p = os.path.split(user_cfg_path)
                                    v = os.path.join(p[0],v)

                                if not os.path.isdir(os.path.abspath(v)):
                                    warnings.append(msg.format(section,item,'Directory does not exist'))

                            #Check int, bools, float
                            elif options_type not in str(type(v)):
                                errors.append(msg.format(section,item,'Expecting a {0} recieved {1}'.format(options_type,type(v))))

                            if master_config[section][item].options and v not in master_config[section][item].options:
                                err_str = "Invalid option: {0} ".format(v)
                                errors.append(msg.format(section, item, err_str))

    return warnings,errors

def add_defaults(user_config,master_config):
    """
    Look through the users config file and section by section add in missing
    parameters to add defaults

    Args:
        user_cfg - Config file dictionary created by :func:`~smrf.utils.io.read_config'.
        master_config - Config file dictionary created by :func:`~smrf.utils.io.read_master_config'

    Returns:
        user_cfg: User config dictionary with defaults added.
    """
    for section,configured in user_config.items():
            for k,v in master_config[section].items():
                if v.name not in configured.keys():
                    #print(v.name,v.default)
                    user_config[section][k]=v.default
    return user_config


def get_master_config():
    """
    Returns the master config file dictionary
    """
    cfg = MasterConfig(__core_config__).cfg
    return cfg

def update_config_paths(cfg,user_cfg_path, mcfg = None):
    """
    Paths should always be relative to the config file or
    absolute.
    """
    if mcfg == None:
        mcfg = get_master_config()
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
                        path = os.path.abspath(os.path.join(os.path.split(user_cfg_path)[0],cfg[section][item]))
                        cfg[section][item] = path
    return cfg


def get_user_config(fname, mcfg = None):
    """
    Retrieve the user config and apply
    types according to the master config.

    Args:
        fname - filename of the user config file.
        mcfg - master config object
    Returns:
        cfg - A dictionary of dictionaries containing the config file
    """
    if mcfg == None:
        mcfg = get_master_config()

    cfg = read_config(fname)

    #Convert the types
    for section in cfg.keys():
        for item in cfg[section]:
            u = cfg[section][item]
            if item in mcfg[section]:
                m = mcfg[section][item]
                u = mcfg[section][item].convert_type(u)

                #If all is  requested then use all the options
                if u == 'all':
                    u = m.options
                    u.remove('all')

                #Check for stations and passwords
                if m.type == 'str' and u != None:
                    if type(u) == list:
                        if item in ['stations', 'peak']:
                            u = [o.upper() for o in u]
                        else:
                            u = [o.lower() for o in u]

                    else:
                        if item == 'client':
                            u = u.upper()
                        elif item != 'password':
                            u = u.lower()

                #Add the timezone to all date time
                elif mcfg[section][item].type == 'datetime' and u != None:
                    #We tried to apply this to all the datetimes but it was not working if we changed it for the start
                    # and end dates with mySQL.

                    if item not in ['start_date', 'end_date']:
                        u = u.replace(tzinfo = pytz.timezone(cfg['time']['time_zone']))


                cfg[section][item] = u

    return cfg


def config_documentation():
    """
    Auto documents the core config file. Creates a file named auto_config.rst
    in the docs folder which is then used for documentation.
    """

    mcfg = io.get_master_config()

    #RST header
    config_doc ="Config File Reference\n"
    config_doc+="=====================\n"
    config_doc+="""Below are the sections and items that are registered to the
configuration file. If an entry conflicts with these SMRF will end
the run and show the errors with the config file. If an entry is not provided
SMRF will automatical add the default in.
"""

    #Sections
    for section in mcfg.keys():
        #Section header
        config_doc+=" \n"
        config_doc += "{0}\n".format(section)
        config_doc += "-"*len(section)+'\n'
        #If distributed module link api
        dist_modules = ['air_temp','vapor_pressure','precip','wind', 'albedo','thermal','solar','soil_temp']
        if section == 'precip':
            sec = 'precipitation'
        else:
            sec = section
        if section in dist_modules:
            intro = """
The {0} section controls all the available parameters that effect
the distribution of the {0} module, espcially  the associated models.
For more detailed information please see :mod:`smrf.distribute.{0}`.
            """.format(sec)
        else:
            intro = """
The {0} section controls the {0} parameters for an entire SMRF run.
            """.format(sec)

        config_doc+=intro
        config_doc+="\n"

        #Auto document config file according to master config contents
        for item,v in sorted(mcfg[section].items()):
            #Check for attributes that are lists
            for att in ['default','options']:
                z = getattr(v,att)
                if type(z) == list:
                    combo = ' '
                    doc_s = combo.join([str(s) for s in z])
                    setattr(v,att,doc_s)

            #Bold item with definition
            config_doc+="| **{0}**\n".format(item)

            #Add the item description
            config_doc+="| \t{0}\n".format(v.description)

            #Default
            config_doc+="| \t\t*Default: {0}*\n".format(v.default)

            #Add expected type
            config_doc+="| \t\t*Type: {0}*\n".format(v.type)

            #Print options should they be available
            if v.options:
                config_doc+="| \t\t*Options:*\n *{0}*\n".format(v.options)

            config_doc+="| \n"

            config_doc+="\n"

    path = os.path.abspath('./')
    path = os.path.join(path,'auto_config.rst')
    print("Writing auto documentation for config file to:\n{0}".format(path))
    with open(path,'w+') as f:
        f.writelines(config_doc)
    f.close()
