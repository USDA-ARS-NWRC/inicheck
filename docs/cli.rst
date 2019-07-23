.. _CLI:

Command Line tools
===================

inicheck on the command line can greatly speed up debugging of config files
and provide simple ways of getting information. In all inicheck CLI tools
master config arguments are exchangeable with a python module who has inicheck
files installed. For more project related info visit inichecks :ref:`ForAProject`.

1. You can access config options by requesting details using the master file
or a module name (see For a project).

.. code-block:: console

   $ inicheck --details project --master_files examples/master.ini

     Section         Item            Default         Options                   Description
   =======================================================================================================================================
   project         project_path    None            []                        specifies the project directory path
   project         logo_source     None            []                        path to the png for the logo_source
   project         website         None            []                        website domain


2. inicheck can also show which recipes were applied using while checking
the file.

.. code-block:: console

    $ inicheck -f gui_config.ini --master_files examples/master.ini --recipes

    Below are the recipes applied to the config file:
    Recipes Summary:
    ================================================================================

    user_recipe
    --------------------------------------------------------------------------------
    	Conditionals:
    		trigger_1            settings, user_settings, any
    		trigger_2            user_profile, any, any

    	Edits:
    		settings             autosave             True
    		settings             volume               1
    		settings             graphics_quality     medium

3. inicheck can also show which values are non default values.

.. code-block:: console

    $ inicheck -f gui_config.ini --master_files examples/master.ini --non-defaults

    Configuration File Non-Defaults Report:
    The following are all the items that had non-defaults values specified.
    ============================================================================================================================

    Section              Item                 Value                                    Default
    ----------------------------------------------------------------------------------------------------------------------------
    settings             volume               1                                        3
    settings             graphics_quality     medium                                   low
    settings             user_settings        True                                     False


4. inicheck also has a differencing script for checking how a config file is
different from another or different from the master config.

.. code-block:: console

    $ inidiff -f ../examples/gui* -mf ../examples/master.ini

    Checking the differences...

    CFG 1               /home/micahjohnson/projects/inicheck/examples/gui2.ini
    CFG 2               /home/micahjohnson/projects/inicheck/examples/gui_config.ini

    Section             Item                          CFG 1                         CFG 2                         Default
    ============================================================================================================================================
    settings            volume                        1                             1                             3
    settings            graphics_quality              medium                        medium                        low
    settings            user_settings                 True                          True                          False
    settings            end_test                      2016-10-03 00:00:00           2016-10-01 00:00:00           None

    Total items checked: 15
    Total Non-default values: 6
    Total config mismatches: 1
