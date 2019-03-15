===================
Welcome to inicheck
===================


.. image:: https://img.shields.io/pypi/v/inicheck.svg
        :target: https://pypi.python.org/pypi/inicheck

.. image:: https://readthedocs.org/projects/inicheck/badge/?version=latest
        :target: https://inicheck.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


What is inicheck?
-----------------

inicheck is an advanced configuration file checker/manager enabling developers
high end control over their users configuration files. inicheck is specifcially
aimed at files that adhere to the .ini format. See wiki for more info on the
file standards https://en.wikipedia.org/wiki/INI_file .

Objectives
----------

The goal of inicheck was to reduce endless logic gates and repeat code for
software that required complicated configuration files. We also wanted to
centralize options for an ever changing repo. We have a lot of experience with
codes that required config files that could easily have 1000 different
configurations. So from that need inicheck has been born.

Basic Principles
----------------

inicheck requires a master config file to operate. The master config file is
a gold standard files provided by the developer of a package. The master config
(sometimes called the core config) provides the rules for every configuration
file that is passed to the software. There the developer can set types,
constrain options, documentation strings and defaults. The developer can also
create recipes that can be triggered when a user has a specific combination of
config file entries.

Once a master config file is created, all config files can be passed through
the standards laid out in there. From there the software can provide feedback
to the user about why their file is being rejected. The master file also enables
the user to have really simple config files that have larger meaning. With
recipes and defaults, a user can provide relatively little and the developer can
still move forward without have a ridiculous amount of logic to handle
scenarios.

* Free software: GNU General Public License v3
* Documentation: https://inicheck.readthedocs.io.


Features
--------

* .ini file generating
* Config file checking
* Config file warning and error reporting
* Command line interface
* Apply defaults
* Auto cast items into the correct types.
* Constrain users by designated options
* Create recipes to ensure the right settings are in place
* Use custom types for your config file
* Use multiple master config files for cleaner files
* Auto config file documentation


Credits
---------

inicheck has been developed at the USDA-ARS-NWRC during efforts towards creating
highly configurable, physically based watershed modeling software.

inicheck originally was based on config parser and with time went away from it.
We would not be here with that base and for that were grateful.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
