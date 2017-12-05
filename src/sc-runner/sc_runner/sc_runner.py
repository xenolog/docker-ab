import argparse
# import json
import yaml
import sys
import os
from io import StringIO


def dict_merger(*args):
    if len(args) < 2:
        return {}
    for i in args:
        if not isinstance(i, dict):
            raise TypeError("all argiments should be a dict")
    rv = {}
    # rv.update(args[0])
    for d in args:
        keys2 = set()
        keys2.update(rv.keys())
        keys2.update(d.keys())
        for k in sorted(keys2):
            if d.get(k) is None:
                continue
            if isinstance(d[k], dict) and isinstance(rv.get(k), dict):
                rv[k] = dict_merger(rv[k], d[k])
            else:
                rv[k] = d[k]
    return rv


def DefaultizeConfig(h):
    defaults = h.get('defaults', {})
    if not defaults:
        return {}
    rv = {}
    for t in sorted(h.keys() - ["defaults"]):
            rv[t] = dict_merger(defaults, h[t])
    return rv


class ScRunner(object):
    override = {}
    settings = {}
    config = {}

    def __init__(self, setfname='', overrfname=''):
        if setfname:
            self._load('settings', setfname)
        if overrfname:
            self._load('override', overrfname)

    def _prepare(self):
        self.config = DefaultizeConfig(self.settings)
        # self.config = hash_override(self.settings, self.override)

    def _loader(self, target, infile):
        setattr(self, target, yaml.load(infile))

    def _load(self, target, filename):
        with open(filename, 'r') as datafile:
            self._loader(target, datafile)

    def _loads(self, target, string):
        strio = StringIO(string)
        self._loader(target, strio)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generic", help="print JSON in generic format",
                        action="store_true")
    args = parser.parse_args()

    # ab_output_to_json(generic=args.generic)


if __name__ == "__main__":
    main()