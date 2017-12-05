
import unittest
import sc_runner
# import textwrap
import yaml
from io import StringIO

AbstractYaml = """
scenario_id: 1
scenarios:
  1:
    - 1
    - 2
  2:
    - 2
    - 1
  3:
    - 2
tasks:
  defaults:
    script: test_case__0.sh
    outputs: /tmp/
    timeout: 120
    properties:
      prop3: val3
      prop4: val4
    criteria:
      rc:
        value: 0
  1:
    description: Get web page 100 times by one thread
    script: test_case__2.sh
    properties:
      prop1: val11
      prop2: val12
    criteria: "???"
  2:
    properties:
      prop1: val11
      prop3: val13
"""

OverrideAbstractYaml = """
tasks:
  defaults:
    properties:
      host_ip: 127.0.0.1
  2:
    properties:
      host_ip: 192.168.0.1
"""

DefaultizedAbstractYaml = """
  1:
    description: Get web page 100 times by one thread
    script: test_case__2.sh
    properties:
      prop1: val11
      prop2: val12
      prop3: val3
      prop4: val4
    criteria: "???"
    implementation: sh
    outputs: /tmp/
    timeout: 120
  2:
    script: test_case__0.sh
    implementation: sh
    outputs: /tmp/
    timeout: 120
    properties:
      prop1: val11
      prop3: val13
      prop4: val4
    criteria:
      rc:
        value: 0
"""

AVItestYaml = """
---
scenarios:
  1:
    - 1
    - 2
  2:
    - 3
    - 4
    - 5

tasks:
  defaults:
    implementation: inline-sh
    script: ab -c {concurrency} -n {requests} http://{host_ip}/
    outputs: /tmp/           # script will generate two files script_name__[stderr/stdout].{test_case_id}
    timelimit: 120           # sec
    properties:
      concurrency: 1
      requests: 10
    criteria:
      rc:
        value: 0

  1:
    description: Get web page 100 times by one thread
    properties:
      concurrency: 1
      requests: 100
    criteria: "???"
  2:
    properties:
      concurrency: 100
      requests: 100000
      timelimit: 6000
  3:
    implementation: inline-sh
    script: ab -c {concurrency} -n {requests} http://{host_ip}:80/
    properties:
      concurrency: 1
      requests: 100
  4:
    implementation: inline-sh
    script: ab -c {concurrency} -n {requests} -i http://{host_ip}:80/
    properties:
      concurrency: 1
      requests: 100
  5:
    properties:
      concurrency: 1
      requests: 1
"""
OverrideAVIyaml = """
scenario_id: 1
tasks:
  defaults:
    properties:
      host_ip: 127.0.0.1
"""


class T(unittest.TestCase):

    def test_dict_merger_1(self):
        a = {
            'a': 99,
            'b': 2,
        }
        b = {
            'a': 1,
            'c': 99
        }
        c = {
            'c': 3
        }
        self.assertEqual(sc_runner.dict_merger(a, b, c), {
            'a': 1,
            'b': 2,
            'c': 3
        })

    def test_dict_merger_2(self):
        config = {
            'a': 1,
            'b': [1, 2, 3],
            'c': [1, 2, 3],
            'd': {
                'aa': 11,
                'bb': 12,
                'cc': 13
            }
        }
        defaults = {
            'a': 55,
            'c': [4, 5, 6],
            'd': {
                'aa': 111,
                'cc': 155,
                'dd': 14
            },
            'e': 42
        }
        self.assertEqual(sc_runner.dict_merger(defaults, config), {
            'a': 1,
            'b': [1, 2, 3],
            'c': [1, 2, 3],
            'd': {
                'aa': 11,
                'bb': 12,
                'cc': 13,
                'dd': 14
            },
            'e': 42
        })

    def test_defaultized_config(self):
        config = {
            'defaults': {
                'a': 11,
                'b': 12,
                'c': 13,
            },
            1: {
                'a': 1,
                'b': 2,
            },
            2: {
                'b': 2,
                'c': 3,
            }
        }
        self.assertEqual(sc_runner.DefaultizeConfig(config), {
            1: {
                'a': 1,
                'b': 2,
                'c': 13,
            },
            2: {
                'a': 11,
                'b': 2,
                'c': 3,
            }
        })

    def test_defaultized_yaml(self):
        self.maxDiff = None
        c = sc_runner.ScRunner()
        c._loads(AbstractYaml)
        c._prepare()
        self.assertEqual(c.config, yaml.load(StringIO(DefaultizedAbstractYaml)))

    def test_overrided_yaml(self):
        self.maxDiff = None
        c = sc_runner.ScRunner()
        c._loads(AbstractYaml)
        c._loads(OverrideAbstractYaml)
        c._prepare()
        overrided_config = yaml.load(StringIO(DefaultizedAbstractYaml))
        overrided_config[1]['properties']['host_ip'] = "127.0.0.1"
        overrided_config[2]['properties']['host_ip'] = "192.168.0.1"
        self.assertEqual(c.config, overrided_config)


if __name__ == '__main__':
    unittest.main()
