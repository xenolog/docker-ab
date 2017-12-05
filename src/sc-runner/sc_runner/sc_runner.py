import argparse
import json
import yaml
import sys
import os
import subprocess
import logging
import shlex
import datetime
from io import StringIO

from ab2json.ab2json import ab_output_to_dict, ab_dict_to_generic_format

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
    for t in sorted(h.keys() - ['defaults']):
            rv[t] = dict_merger(defaults, h[t])
    return rv


class ScRunner(object):

    def __init__(self, configpaths=[], out_dir='/tmp', res_dir='/tmp'):
        self.log = logging.getLogger(__name__)

        self._settings = []  # incoming settings will be merged hierarchicaly
        self.config = {}     # merged config for run tasks
        self.results = {}    # result storage
        self._scenarios = {}
        self._scenario_id = None

        self.out_dir = out_dir
        self.res_dir = res_dir

        self._settings.append({
            # defaults for tasks
            'tasks': {
                'defaults': {
                    'implementation': 'inline-sh',
                    'script': 'echo'
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

    def _exec_subprocess(self, logfilename, script, env, task_id=None):
        p = subprocess.Popen(script,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.out_dir,
            env=env
        )
        p.wait()
        rc = p.returncode
        # create logfiles
        with open("{}/{}__stdout.txt".format(self.out_dir, logfilename), "w") as f:
            f.write(p.stdout.read())
        with open("{}/{}__stderr.txt".format(self.out_dir, logfilename), "w") as f:
            f.write(p.stderr.read())
        p.stdout.seek(0)
        p.stderr.seek(0)
        return rc, p.stdout, p.stderr

    def run(self, runner=None):  # fake runner may be used for testing purpose
        grc = 0
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
            env = {}
            env.update(os.environ)
            env.update(task.get('properties', {}))
            if task['implementation'] == 'inline-sh':
                script = script.format(**task.get('properties', {}))
                script = shlex.split(script)
            elif task['implementation'] == 'sh':
                script = [script]
            else:
                raise NotImplemented("Implementation '{}' not ready :(".format(task['implementation']))
            if runner is None:
                # run by subprocess runner
                ts = datetime.datetime.now().isoformat(timespec='seconds')
                rc, stdout, stderr = self._exec_subprocess(
                    "{}__sc{:04d}__task{:04d}".format(ts, self.scenario_id, task_id), script, env
                )
            else:
                # fake runner for test purposes
                rc, stdout, stderr = runner(script, task, env)
            if rc > grc:
                grc = rc
            # analize AB result
            if rc == 0 and stdout is not None:
                self.results[task_id] = ab_output_to_dict(infile=stdout)
        return rc

    def generate_report(self):
        for k, v in self.results.items():
            with open("{}/sc{:04d}__task{:04d}__report.json".format(self.out_dir, self.scenario_id, k), "w") as f:
                f.write(json.dump(ab_dict_to_generic_format(v), ident=2))
        # result weight analitics should be here


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

    tt = ScRunner(*args.configs, out_dir=args.outputs_dir, res_dir=args.result_dir)
    rc = tt.run()
    tt.generate_report()
    return rc


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
