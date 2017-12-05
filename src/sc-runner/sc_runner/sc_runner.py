import argparse
# import json
import yaml
import sys
import os
import subprocess
import logging
import re
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

    def __init__(self, configpaths=[]):
        self._settings = []  # incoming settings will be merged hierarchicaly
        self.config = {}    # result config
        self._scenarios = {}
        self._scenario_id = None

        self.log = logging.getLogger(__name__)
        self._settings.append({
            # defaults for tasks
            'tasks': {
                'defaults': {
                    'implementation': 'sh'
                }
            }
        })
        for cfg in configpaths:
            self._load(cfg)

    def _prepare(self):
        overrided_config = dict_merger(*self._settings)
        self._scenarios = overrided_config.get('scenarios', {})
        self._scenario_id = overrided_config.get('scenario_id')
        if self._scenario_id is None:
            raise ValueError("Scenario-ID should be defined")
        self.config = DefaultizeConfig(overrided_config.get('tasks', {}))

    def _loader(self, infile):
        self._settings.append(yaml.load(infile))

    def _load(self, filename):
        with open(filename, 'r') as datafile:
            self._loader(datafile)

    def _loads(self, string):
        strio = StringIO(string)
        self._loader(strio)

    def _scenario(self):
        rv = self._scenarios.get(self._scenario_id, [])
        count = len(rv)
        for i in rv:
            if self.config.get(i) is None:
                self.log.warning("Scenario with id '{}' contains unknown task '{}'".format(self._scenario_id, i))
                count -= 1
        if count < 1:
            self.log.warning("Scenario with id '{}' is empty".format(self._scenario_id))
        return rv

    def run(self, runner=None):  # fake runner may be used for testing purpose
        if self.config == {}:
            self._prepare()
        for task_id in self._scenario():
            task = self.config[task_id]
            script = task.get('script', None)
            if script is None:
                self.log.error("Task {task} has no script definition: {yml}".format(
                    task=task_id,
                    yml=yaml.dump(task)
                ))
                continue
            if task['implementation'] == 'inline-sh':
                script = script.format(**task.get('properties', {}))
                script = re.split(r'\s+', script)
            elif task['implementation'] == 'sh':
                script = [script]
            else:
                raise NotImplemented("Implementation '{}' not ready :(".format(task['implementation']))

            if runner is None:
                # run by subprocess
                pass
            else:
                runner(script, task)


def main():
    parser = argparse.ArgumentParser(
        prog='sc-runner',
        description='Scenario runner'
    )
    parser.add_argument("--scenario-id", help="Pre-defined scenario ID",
                        action="store", dest='scenario_id', required=True)
    parser.add_argument("--config", help="Config file",
                        action="append", dest='configs', required=True)
    parser.add_argument("--outputs-dir", help="Directory for store stderr and stdout of tasks",
                        action="store", dest='outputs_dir', required=True)
    parser.add_argument("--result-dir", help="Directory for store test results in 'generic' format",
                        action="store", dest='result_dir', required=True)
    args = parser.parse_args()

    tt = ScRunner(*args.configs)
    rc = tt.run()
    return rc


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
