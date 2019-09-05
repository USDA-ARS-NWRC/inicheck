from . iniparse import parse_sections, parse_items, parse_changes
from pandas import to_datetime
from . entries import ConfigEntry
from . utilities import mk_lst
import importlib
from os.path import join as pjoin
from os.path import abspath


class ChangeLog(object):

    def __init__(self, paths=None, mcfg=None, **kwargs):

        # Paths to changelogs
        self.paths = []

        # We got a direct path
        if paths != None:
            paths = mk_lst(paths)
            self.paths += paths

            self.changes = self.join_changes(self.paths)

        self.check_log_validity(mcfg)

    def join_changes(self, paths):
        """
        Joins multiple changelogs together

        Args:
            paths: List of paths containing changelogs syntax
        Returns:
            changes: lists of line item changes provided in each line as a
                     list of [old, new]
        """

        changes = []
        for p in paths:
            changes += self.read_change_log(p)

        return changes

    def read_change_log(self, path):
        """
        Opens the file and reads in sections and the items.

        Args:
            path: Path to a changlog file
        """
        with open(path, encoding='utf-8') as f:
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
        Checks the current master config that the items we're moving to
        are valid. Also confirms that removals are aligned with the master.
        """
        action_kw = ["any",'removed']
        cfe = ConfigEntry()
        invalids = []

        for zz,c in enumerate(self.changes):
            # Check the new assignments match the names of current master items
            current = c[1]
            valids = []

            # KW removed or ANY is valid for sections
            if current[0] in action_kw or current[0] in mcfg.cfg.keys():
                valids.append(True)

            # Section is valid, lets check items
            if current[0] != "removed":

                if len(valids) >= 1:

                    # Non-any item and any section provided
                    if current[0] == "any" and current[1] not in action_kw:
                        for s, items in mcfg.cfg.items():
                            if current[1] in items.keys():
                                valids.append(True)
                                break

                    # Valid item check whe valid section provided
                    elif (current[1] in action_kw or
                          current[1] in mcfg.cfg[current[0]].keys()):
                        valids.append(True)

                # Check for valid properties
                if len(valids) >= 2:
                        if current[2] in ["any", "default"]:
                            valids.append(True)

                # TODO Actually check values, ignoring for now.
                if len(valids) == 3:
                    valids.append(True)

                # Final check
                if len(valids) != len(current):
                    invalids.append(c)

        # Form a coherent message about incorrect changlog stuff
        if invalids:
            msg = ("Changelog states a change that doesn match the core config."
                  " For a change to be valid the new changes must be in the"
                  " Master Config file. Mismatches are:")

            for n in invalids:
                msg+="\n * "
                msg+="/".join(n[0])
                msg+=" -> "
                msg+="/".join(n[1])

            raise ValueError(msg)

    def get_active_changes(self, ucfg):
        """
        Goes through the users config looking for matching old configurations,
        then makes recommendations.

        Args:
            ucfg: UserConfig Object
        """
        required_changes = []
        potential_changes = []

        cfe = ConfigEntry()

        cfg = ucfg.cfg

        for change in self.changes:

            # Original config options
            assumed = change[0]

            # New options
            new = change[1]

            # Go through the sections
            for s in cfg.keys():
                if assumed[0] == "any":
                    assumed[0] = s
                    new[0] = s
                # Go through the items
                for i in cfg[s].keys():
                    if assumed[1] == "any":
                        assumed[1] = i
                        new[1] = i
                    # If we have a match from the changelog and the current config
                    if assumed[0] == s and assumed[1] == i:

                        # Check for an old default match and suggest a change
                        if assumed[2] == "default":
                            if str(cfg[s][i]) == assumed[3]:
                                potential_changes.append([assumed, new])

                        else:
                            required_changes.append([assumed, new])

        return potential_changes, required_changes
