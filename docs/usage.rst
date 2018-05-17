=====
Usage
=====

To use inicheck in a project you will need to create a master config file for
all your configuration files to be checked against. To get started with writing
a master configuration file see :ref:`MasterConfig`.

Command Line
============

A First Use Example:
--------------------

Once the Master file is created, create a config file and check it! Consider
the following example. Lets say the Master Configuration file contains
one section and one recipe like:

.. literalinclude:: ../examples/simple/master.ini

To make a simple configuration file we need to create the file and fill out
whatever entries are important to the specific user:

.. literalinclude:: ../examples/simple/config.ini

Now to check what the user just entered into their config:

.. code-block:: console

  inicheck -f config.ini -c master.ini

If you do not get any errors then you have just checked your first config file!

To see how inicheck interpreted your config file add the -w option to the aboved
command. This will output the file the way inicheck sees it. Opening it up will
show all the entries are filled out.

Aiming to be User Proof
^^^^^^^^^^^^^^^^^^^^^^^

For a further demo, let's say the our user think themselves funny and enters the
following into their configuration file:

.. code-block:: console

    age: nunya!
    job_class: king

inicheck will produce errors and report them in the following manner:

.. code-block:: console

      Configuration File Status Report:
      ==========================================================================
      ERRORS:

      Section              Item          Message
      --------------------------------------------------------------------------
      settings             age                Expecting int received str
      settings             job_class          Not a valid option

This takes alot of issues out of the hands of the developer so they can focus
more on functionality rather than the sometimes erratic behavior of users.


For a Project
===========================

Using inicheck for your project is a great way to save on repeated code and
reduce insane amounts of check of types and if something exists etc...

Getting a Config File
---------------------
Once the user has filled out a configuration file, inicheck can bring in the
information via a :class:`~inicheck.config.UserConfig` object by using the
following:

.. code-block:: python

  from inicheck.tools import get_user_config

  ucfg = get_user_config(filename, module = str_module_name, checking_later = True)
  warnings, errors = check_config(ucfg)
  print_config_report(warnings, errors)

**CAUTION**: Using the *checking later* flag will allow inicheck to pass over issues
that would raise exceptions so that the developer can inform the user of the
issues with their config file at the same time. This can be dangerous if the
developer does not follow  up with the functions check_config and
print_config_report.

To learn more see checkout the functions documentation:
  * :func:`~inicheck.tools.get_user_config`
  * :func:`~inicheck.tools.check_config`
  * :func:`~inicheck.output.print_config_report`

Installing a Master Configuration File
--------------------------------------

Once you have made a master configuration file, the easiest way to use it for your own
project is to add its file path as a module attribute. inicheck currently looks
for attributes when a module is requested:

  * __core_config__
  * __recipes__

If both are found inicheck will combine them and create a large master configuration
file. Below is an example of how to add these attributes to your module.

.. code-block:: python

  # Add the following to the packages's __init__.py file
  import os
  __core_config__ = os.path.abspath(os.path.dirname(__file__) + '/master.ini')

  # If you have enough recipes to keep the files separate you can add:
  __recipes__ = os.path.abspath(os.path.dirname(__file__) + '/recipes.ini')

Once this is done make sure you add the file(s) to whateverpackage inclusions you need.
Here is an example of how to include them in your setup.py

.. code-block:: python

  #In a setup.py, under the setup class initializer
  package_data={'mymodule':['./master.ini',
                      './recipes.ini']},
