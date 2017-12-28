import argparse
import json
import yaml
import sys
import os
import subprocess
import logging
import shlex
import datetime
import yaql

from io import StringIO

from ab2json.ab2json import ab_output_to_dict, ab_dict_to_generic_format


TEST_RESULT_KEY = '__test_result'
TEST_RESULT_PASSED = 'passed'
TEST_RESULT_FAILED = 'failed'


def dict_merger(*args):
    for i in args:
        if not isinstance(i, dict):
            raise TypeError("all argiments should be a dict, not {}".format(type(i)))
    rv = {}
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
        self.ts = None

        self.YaqlEngine = yaql.factory.YaqlFactory().create()

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
        self._scenario_id = overrided_config.get('scenario_id')
        if self._scenario_id is None:
            raise ValueError("Scenario-ID should be defined")
        self.config = DefaultizeConfig(overrided_config.get('tasks', {}))
        self._scenarios = DefaultizeConfig(overrided_config.get('scenarios', {}))

    def _loader(self, infile):
        self._settings.append(yaml.load(infile))

    def _load(self, filename):
        with open(filename, 'r') as datafile:
            self._loader(datafile)

    def _loads(self, string):
        strio = StringIO(string)
        self._loader(strio)

    def _scenario(self):
        rv = self._scenarios.get(self._scenario_id, {}).get('tasks', [])
        count = len(rv)
        for i in rv:
            if self.config.get(i) is None:
                self.log.warning("Scenario with id '{}' contains unknown task '{}'".format(self._scenario_id, i))
                count -= 1
        if count < 1:
            self.log.warning("Scenario with id '{}' is empty".format(self._scenario_id))
        return rv

    def _exec_subprocess(self, logfilename, script, env):
        for k, v in env.items():
            env[k] = str(v)
        p = subprocess.Popen(script,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.out_dir,
            env=env
        )
        p.wait()
        rc = p.returncode
        # create logfiles
        stdout = p.stdout.read().decode('utf8')
        stderr = p.stderr.read().decode('utf8')
        with open("{}/{}__stdout.txt".format(self.out_dir, logfilename), "w") as f:
            f.write(stdout)
        rctxt = '' if rc == 0 else "rc{:03d}__".format(rc)
        with open("{}/{}__{}stderr.txt".format(self.out_dir, logfilename, rctxt), "w") as f:
            f.write(stderr)
        return rc, stdout, stderr

    def run(self, runner=None):  # fake runner may be used for testing purpose
        grc = 0
        self.ts = datetime.datetime.now().isoformat(timespec='seconds')
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
                rc, stdout, stderr = self._exec_subprocess(
                    "{}__sc{:04d}__task{:04d}".format(self.ts, self._scenario_id, task_id), script, env
                )
            else:
                # fake runner for test purposes
                rc, stdout, stderr = runner(script, task, env)
            if rc > grc:
                grc = rc
            # analize AB result
            if rc == int(task.get('criteria', {}).get('rc', {}).get('value', 0)) and stdout is not None:
                self.results[task_id] = ab_output_to_dict(infile=StringIO(stdout))
            elif rc == int(task.get('criteria', {}).get('rc', {}).get('value', 0)):
                # no stdout, use only RC
                self.results[task_id] = {TEST_RESULT_KEY: TEST_RESULT_PASSED}
            else:
                # was error
                self.results[task_id] = {TEST_RESULT_KEY: TEST_RESULT_FAILED}
        return rc

    def add_scenario_metadata(self, result):
        scenario = self._scenarios.get(self._scenario_id, {})
        for k, v in scenario.get('metadata', {}).items():
            result[k] = v

    def add_task_metadata(self, result, task_id=0, prefix='test_'):
        fields = ('name', 'description')
        task = self.config[task_id]
        for k in fields:
            v = task.get(k)
            if v is not None:
                result["{}{}".format(prefix, k)] = v
        result["{}id".format(prefix)] = str(task_id)
        result["{}scenario_id".format(prefix)] = str(self._scenario_id)
        result['timestamp'] = self.ts

    def generate_report(self, outfile=None, format="json", proxy_sc_metadata=True, proxy_task_metadata=True):
        for k, v in self.results.items():
            generic_result = ab_dict_to_generic_format(v)
            if v.get(TEST_RESULT_KEY) is None:
                # Calculate test criteria by YAQL expression
                generic_result['test_result'] = self.evaluate_test_result(v, task_id=k)
            else:
                generic_result['test_result'] = v[TEST_RESULT_KEY]
            # add metadata to result file
            if proxy_sc_metadata:
                self.add_scenario_metadata(generic_result)
            if proxy_task_metadata:
                self.add_task_metadata(generic_result, task_id=k)
            if outfile is None:
                # Write file with auto-generated name
                report_filename = "{}/{}__sc{:04d}__task{:04d}__report.json".format(
                    self.out_dir, self.ts, self._scenario_id, k
                )
                report_file = open(report_filename, "w")
            else:
                # this need for pass file-like object from unit-tests.
                report_file = outfile
            try:
                if format == "json":
                    report_file.write(json.dumps(generic_result, sort_keys=True, indent=2))
                else:
                    report_file.write(yaml.dump(generic_result, indent=2))
            finally:
                if outfile is None:
                    report_file.close()

    def evaluate_test_result(self, result, task_id=0):
        rv = TEST_RESULT_FAILED
        task = self.config[task_id]
        req = task.get('criteria', {}).get('expression', {}).get('query', 'nul')
        res = task.get('criteria', {}).get('expression', {}).get('result', 'true')
        if isinstance(res, bool):
            # this required for simplify settings.yaml file writing. i.e. mean True == 'true'
            res = str(res).lower()
        expression = self.YaqlEngine("({req}) = ({res})".format(req=req, res=res))
        if expression.evaluate(data=result):
            rv = TEST_RESULT_PASSED
        return rv


def main():
    parser = argparse.ArgumentParser(
        prog='sc-runner',
        description='Scenario runner'
    )
    parser.add_argument("--config", help="Config file",
                        action="append", dest='configs', required=True)
    parser.add_argument("--outputs-dir", help="Directory for store stderr and stdout of tasks",
                        action="store", dest='outputs_dir', required=True)
    parser.add_argument("--result-dir", help="Directory for store test results in 'generic' format",
                        action="store", dest='result_dir', required=True)
    #todo: --debug key
    args = parser.parse_args()

    tt = ScRunner(configpaths=args.configs, out_dir=args.outputs_dir, res_dir=args.result_dir)
    rc = tt.run()
    tt.generate_report()
    return rc


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
