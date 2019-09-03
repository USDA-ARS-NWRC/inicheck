from . iniparse import parse_sections, parse_items, parse_changes
from pandas import to_datetime
from . entries import ConfigEntry
from . utilities import mk_lst
import importlib
from os.path import join as pjoin

class ChangeLog(object):

    def __init__(self, paths=None, modules=None, mcfg=None,**kwargs):
        self.paths =[]

        # We got a direct path
        if path != None:
            paths = mk_lst(paths)
            self.paths += paths

        # Paths were manually provided
        if modules != None:
            modules = mk_lst(modules)
            for m in modules:
                i = importlib.import_module(m)
                if hasattr(i,"__config_changelog__"):
                    self.paths.append(os.path.abspath(pjoin(i.__file__,
                                                      i.__config_changelog__)))

        else:
            # For testing only
            self.changes = kwargs["changes"]

        self.check_log_validity(mcfg)

    def read_change_log(self, changelog):
        """
        Opens the file and reads in sections and the items.
        """

        with open(changelog, encoding='utf-8') as f:
            lines = f.readlines()
            f.close()

        sections = parse_sections(lines)
        raw_changes = sections['changes']
        del sections['changes']

        # Parse meta data the same way as everything
        sec_and_items = parse_items(sections)
        self.info = sec_and_items['meta']['info']
        self.date = to_datetime(sec_and_items["meta"]['date'])

        # Parse the change list
        changes = parse_changes(raw_changes)

        return changes

    def check_log_validity(self, mcfg):
        """
        Checks the current master config that the items were moving to
        are valid. Also confirms that removals are aligned with the master.
        """

        cfe = ConfigEntry()
        invalids = []

        for zz,c in enumerate(self.changes):

            # Check the new assignments match the names of current master items
            current = c[1]
            valids = []

            # KW removed is valid
            if current[0] == "removed":
                valids = [True]

            # Valid Sections check
            elif current[0] == "any" or current[0] in mcfg.cfg.keys():
                valids.append(True)

            # Valid items when section is any
            if current[1] == "any":
                valids.append(True)

            # Non-any item and any section provided
            elif current[0] == "any":
                for s,items in mcfg.cfg.items():
                    if current[1] in items.keys():
                        valids.append(True)
                        break
            # Valid item check whe valid section provided
            elif current[1] in mcfg.cfg[current[0]].keys():
                valids.append(True)


            # Check for valid properties
            if current[3] == "any" or current[3] in cfe.valid_names:
                valids.append(True)

            # Final check
            if len(valids) != len(current[0:-1]):
                invalids.append(current)

        # Form a coherent message
        if invalids:
            msg = ("Changelog states a change that doesn match the core config."
                  " For a change to be valid the new changes must be in the"
                  " Master Config file. Mismatches are:")

            for n in invalids:
                msg+="\n"
                msg+="/".join(n)
            raise ValueError(msg)


    def detect_changes(ucfg, changelog):
        """
        As config files evolve over time it is important to be able to detect
        changes. This is accomplished by a changelog file which follows the syntax
        is the changes in the changelog are found in the current config
        file
        """
