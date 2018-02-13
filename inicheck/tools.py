import os
from .config import UserConfig, MasterConfig
from .utilities import mk_lst

def get_user_config(config_file,master_files = None, module= None, mcfg = None):
    """
    Returns the users config as the object UserConfig.

    Args:
        config_file: real path to existing config file
        master_file: real path to a Core Config file
        module: a module with a string attribute __CoreConfig__ which is the path to a CoreConfig
        mcfg: the master config object after it has been read in.

    Returns:
        ucfg: Users config as an object
    """

    if module == None and master_files == None:
        raise IOError("ERROR: Please provide either a module or a path to a master config")
        sys.exit()

    if os.path.isfile(config_file):

        master_files = mk_lst(master_files)

        mcfg = MasterConfig(path = master_files, module = module)


        ucfg = UserConfig(config_file, mcfg = mcfg)

        for s in ucfg.cfg.keys():
            for i in ucfg.cfg[s].keys():
                ucfg.cfg[s][i] = mk_lst(ucfg.cfg[s][i],unlst=True)
    else:
        raise IOError("Config file path {0} doesn't exist.".format(config_file))
    return ucfg
