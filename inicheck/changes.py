import importlib
from collections import OrderedDict
from os.path import abspath
from os.path import join as pjoin

from .entries import ConfigEntry
from .iniparse import parse_changes, parse_items, parse_sections
from .utilities import mk_lst, parse_date


class ChangeLog(object):

    def __init__(self, paths=None, mcfg=None, **kwargs):

        # Paths to changelogs
        self.paths = []

        # We got a direct path
        if paths is not None:
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
        raw_changes = sections['changes'].copy()
        del sections['changes']

        # Parse meta data the same way as everything
        sec_and_items = parse_items(sections)
        self.info = sec_and_items['meta']['info']
        self.date = parse_date(sec_and_items["meta"]['date'])

        # Parse the change list
        changes = parse_changes(raw_changes)

        return changes

    def check_log_validity(self, mcfg):
        """
        Checks the current master config that the items we're moving to
        are valid. Also confirms that removals are aligned with the master.
        """
        action_kw = ["any", 'removed']
        cfe = ConfigEntry()
        invalids = []

        for zz, c in enumerate(self.changes):
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
            msg = ("Changelog states a change that doesn't match the core config."
                   " For a change to be valid the new changes must be in the"
                   " Master Config file. Mismatches are:")

            for n in invalids:
                msg += "\n * "
                msg += "/".join(n[0])
                msg += " -> "
                msg += "/".join(n[1])

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

            # Go through the sections
            for s in cfg.keys():

                # Go through the items
                for i in cfg[s].keys():

                    # Assign original changes to any's
                    assumed = change[0].copy()
                    new = change[1].copy()

                    # Swap out anys with section names
                    if change[0][0] == "any":
                        assumed[0] = s
                        if change[1][0] != "removed":
                            new[0] = s

                    # swap out anys with item names
                    if change[0][1] == "any":
                        assumed[1] = i
                        if change[1][0] != "removed":
                            new[1] = i

                    # If we have a match from the changelog and the ucfg
                    if assumed[0] == s and assumed[1] == i:
                        if "removed" in new:
                            required_changes.append([assumed, "removed"])

                        # Make sure "any" doesn't disagree with master
                        elif new[0] in ucfg.mcfg.cfg.keys():
                            if new[1] in ucfg.mcfg.cfg[new[0]].keys():

                                # Check for an old default match and suggest a
                                # change
                                if assumed[2] == "default":

                                    value = str(mk_lst(cfg[s][i], unlst=True))
                                    if value == assumed[3]:
                                        potential_changes.append(
                                            [assumed, new])

                                else:
                                    required_changes.append([assumed, new])

        return potential_changes, required_changes

    def apply_changes(self, ucfg, potentials, changes):
        """
        Iterate through the list of detectd applicable changes retrieved
        from get_actived_changes to produce a new config file with the
        correct changes.

        Args:
            ucfg: UserConifg Object
            changes: list lists length 4 (section item property value)
                    representing detected changes

        Returns:
            cfg: Config dictionary
        """

        cfg = ucfg.cfg.copy()

        # REVIEW Right now only defaults can be changed so we assume that here
        for p in potentials:
            s_o = p[0][0]
            i_o = p[0][1]

            # assign the new defaults
            cfg[s_o][i_o] = p[1][3]

        for c in changes:
            removal = False
            s_o = c[0][0]
            i_o = c[0][1]

            # Avoid adding removed items
            if c[1] == "removed":
                removal = True

            else:
                s_n = c[1][0]
                i_n = c[1][1]

            #print(s_o, i_o, s_n, i_n)

            # Confirm new section in the config
            if not removal:
                if s_n not in ucfg.cfg.keys():
                    cfg[s_n] = OrderedDict()

            # Its been deprecated
            if removal:
                del cfg[s_o][i_o]

            # Item or section is a name transfer.
            elif s_o in ucfg.cfg.keys():
                if i_o in cfg[s_o].keys():

                    if s_n != "removed":
                        cfg[s_n][i_n] = cfg[s_o][i_o]

                    del cfg[s_o][i_o]

                # look to remove a whole section
                if len(cfg[s_o].keys()
                       ) == 0 and s_o not in ucfg.mcfg.cfg.keys():
                    del(cfg[s_o])

        return cfg
