import argparse
# import json
import yaml
import sys
import os
from io import StringIO


def dict_merger(*args):
    for i in args:
        if not isinstance(i, dict):
            raise TypeError("all argiments should be a dict, not {}".format(type(i)))
    rv = {}
    # rv.update(args[0])
    for d in args:
        keys2 = set()
        keys2.update(rv.keys())
        keys2.update(d.keys())
        for k in keys2:
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
    settings = []  # incoming settings will be merged hierarchicaly
    config = {}    # result config
    _scenario = None

    def __init__(self, scenario_id, configpaths=[]):
        self.settings.append({
            # defaults for tasks
            'tasks': {
              'defaults': {
                'implementation': 'sh'
              }
            }
        })
        self._scenario = scenario_id
        for cfg in configpaths:
            self._load(cfg)

    def _prepare(self):
        overrided_config = dict_merger(*self.settings)
        self.config = DefaultizeConfig(overrided_config.get('tasks', {}))

    def _loader(self, infile):
        self.settings.append(yaml.load(infile))

    def _load(self, filename):
        with open(filename, 'r') as datafile:
            self._loader(datafile)

    def _loads(self, string):
        strio = StringIO(string)
        self._loader(strio)


def main():
    parser = argparse.ArgumentParser(
        prog='sc-runner',
        description='Scenario runner'
    )
    parser.add_argument("--scenario-id", help="Pre-defined scenario ID",
                        action="store", dest='scenario_id', required=True)
    parser.add_argument("--config", help="Config file",
                        action="append", dest='configs', required=True)
    args = parser.parse_args()

    tt = ScRunner(args.scenario_id, *args.configs)


if __name__ == "__main__":
    main()