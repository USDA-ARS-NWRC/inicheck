=========================
Change Logs
=========================

If a package is around long enough and is sufficiently configurable, it will
almost undergo a refactoring of the configuration file.

To cope with this inicheck allows developers to add a changelog.ini to warn
users and remap old config files if need be.

If a changelog is provided, then the inicheck will stop a program if there is a
any matches in the changelog that are in the users configuration file.

Usage
-----

If your configuration file contains deprecated information as determined by the
changelog, then inicheck will exit the program and report the possible issues.

To use inicheck's CLI to apply the changes simply use

.. code-block:: console

    inicheck -f my_config.ini -m my_module --changes -w

This says apply the changes and output the result.


Writing your own change log
---------------------------

Syntax
^^^^^^
Every changelog must have two sections, a meta section and a changes section.
The meta section should have an info item with a description of what happened
and why. And it should have a date  in which indicates the date at which this
went into effect.

*Future Feature* - Currently inicheck will only handle a single changelog but
in the future will use the dates to map the changes to each changelog.

A changelog can track the following type of changes:

1. Removal of a section or item.
2. The rename of a section or item.
3. The migrating of an item to another section
4. Default changes.


An entry in the change log is done with the following format:

.. code-block:: ini

    <OLD SECTION>/<OLD ITEM> -> <NEW SECTION>/<NEW ITEM>

*If declaring a default has changed* then the syntax is the same plus the
property and value appended.

.. code-block:: ini

    <OLD SECTION>/<OLD ITEM>/default/<OLD VALUE> -> <NEW SECTION>/<NEW ITEM>/default/<NEW VALUE>

*WARNING:* If an old default value is identified, auto changing will update any
older default values to the new ones.

Look at the following example change log to see various implementations.

Example Changelog

.. code-block:: ini

    [meta]
    info: Major config file changes occurred leading to cleaner files
    date: 09-04-2019

    [changes]

    # Rename an item with in a section
    topo/threading -> topo/topo_threading

    # Removing an item from a section
    topo/dem -> REMOVED

    # Removing a section entirely
    stations -> REMOVED

    # Migrating an item to a new section
    solar/distribution -> cloud_factor/distribution

    # Migrating an item to a new section and renamed.
    solar/slope -> cloud_factor/detrend_slope

    # A default value has changed from 0.7 to 1.0
    wind/reduction_factor/default/0.7 -> wind/reduction_factor/default/1.0

Where do I keep my change log
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change logs can only be associated to a module. Its association is done by creating a module attribute
called __config_changelog__.

Example in your <my_module>/__init__.py:

.. code-block:: python

  import os
  __config_changelog__ = os.path.abspath(os.path.dirname(__file__) + '/path/to/changelog.ini')
