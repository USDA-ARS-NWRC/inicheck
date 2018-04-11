=========================
Master Configuration File
=========================

Basic Entry
-----------
To accurately check files, every entry and section must be provided in the
master configuration file. Every entry must belong to a section. However, if an
option is not registered (in the master config), inicheck will simply produce a
warning to alert the user.

Example::

  [time]

  time_step:
            default = 60,
            type = int,
            description = Time interval that SMRF distributes data at in minutes

The example above specifies that the section **time** has an entry **time_step**
with a default of 60 and should always be an integer. The end outcome is
that inicheck requires all provided options for time_step are integers. If the
user didn't provide it, inicheck will add the default.

Available Types
---------------
Each entry in the master config file can provide a type. If no type is provided,
then the default is type string.

**Note**: Any path options with critical prepended just means that inicheck will
throw an error instead of a warning.

Available types:

* bool
* string
* float
* integer
* datetime
* filename
* CriticalFilename
* directory
* CriticalDirectory

**lists**: can be provided but are not checked, they are not specified as a type
though. To provide a list you must use space separated bracketed lists in the entry
in the config file.

The following example required the users input to be a string, and must match
nearest,linear, or cubic.

Example::

  [interpolation]
    method:
          default = linear,
					options = [nearest linear cubic],
					description = interpolation method to use for this variable


Recipes
--------
The master config can have recipes to generate certain adding or removing of
entries. This can really help with config file bloat.
Recipes are entered like sections **but** they must have the word recipe in
the section name. Each recipe has triggers. A trigger is the scenario for which
all the entries not labeled as a trigger are applied. Every trigger must have
the word trigger or condition in it's entry name.

The following example shows a recipe that is triggered when a user provides a
csv section, when this happens sections mysql and gridded (if provided) are
removed and csv is added with all available entries not provided will have a
default applied

Example::

  [csv_recipe]
  trigger:      has_section = csv
  csv:          apply_defaults= true
  mysql:        remove_section = true
  gridded:      remove_section = true


Recipe triggers have a few key words available:

* **has_section** - if the config file has this section
* **has_value** - This is the most flexible trigger provided. It is provded using
                  a bracketed, space delimited list in section, item, value order.
                  The user can use an any keyword to snag more ambiguous scenarios
                  e.g. has_value = [any intensity 25] will trigger if any
                  section has an item named intensity set to 25.

Recipe edits are simply anything in the recipe not listed with trigger or
condition in the item name. They are interpretted literally if there are no
keywords used.

Edits are prescribed by section and item names under a recipe:

Example::
  [my_recipe]
    my_trigger:   has_value=[test_section  test_item test_value]

    section:
      item_name (or keyword) = value


Available keywords for entries are:

* **apply_defaults** - apply the defaults set in the sectio
* **remove_item** - remove an item in this section

If a keyword is not used then values are treated like section > item > value

Example::

  [topo_ipw_recipe]
  trigger_type:       has_value = [topo type ipw]

  topo:               type = ipw,
                      apply_defaults = dem,
                      apply_defaults = mask,
                      remove_item = filename
