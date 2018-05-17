=====
Usage
=====

To use inicheck in a project you will need to create a master config file for
all your configuration files to be checked against. To get started with writing
a master configuration file see master-config_.


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

Knuckle Head Proof
^^^^^^^^^^^^^^^^^^
For a further demo lets say the our user think themselves funny and enters the
following:

.. code-block::

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
