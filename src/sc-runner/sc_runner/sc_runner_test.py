
import unittest
import sc_runner
# import textwrap
import yaml
# from io import StringIO

BaseYaml = """
tasks:
  defaults:
    script: test_case__0.sh
    putout: /tmp/
    timeout: 120
    properties:
      prop3: val1
      prop4: val2
    criteria:
      rc:
        value: 0

  1:
    description: Get web page 100 times by one thread
    script: test_case__2.sh
    properties:
      prop1: val1
      prop2: val2
    criteria: "???"
  2:
    properties:
      prop1: val1
      prop2: val2
"""

DefaultizedBaseYaml = """
tasks:
  1:
    description: Get web page 100 times by one thread
    script: test_case__2.sh
    properties:
      prop1: val1
      prop2: val2
      prop3: val3
      prop4: val4
    criteria: "???"
    putout: /tmp/
    timeout: 120
  2:
    script: test_case__0.sh
    putout: /tmp/
    timeout: 120
    properties:
      prop1: val1
      prop3: val3
      prop4: val4
    criteria:
      rc:
        value: 0
"""

OverrideYaml = """
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



    # def test_defaultized_yaml(self):
    #     self.maxDiff = None
    #     c = sc_runner.ScRunner()
    #     c._loads('settings', BaseYaml)
    #     c._prepare()
    #     print(yaml.dump(c.settings))
    #     print(yaml.dump(c.config))
    #     self.assertEqual(c.config, {
    #         'tasks': {
    #             1: {
    #                 'description': 'Get web page 100 times by one thread',
    #                 'script': 'test_case__2.sh',
    #                 'properties': {
    #                     'prop1': 'val1',
    #                     'prop2': 'val2',
    #                     'prop3': 'val3',
    #                     'prop4': 'val4'
    #                 },
    #                 'criteria': '???',
    #                 'putout': '/tmp/',
    #                 'timeout': 120
    #             },
    #             2: {
    #                 'script': 'test_case__0.sh',
    #                 'putout': '/tmp/',
    #                 'timeout': 120,
    #                 'properties': {
    #                     'prop1': 'val1',
    #                     'prop3': 'val3',
    #                     'prop4': 'val4'
    #                 },
    #                 'criteria': {
    #                     'rc': {
    #                         'value': 0
    #                     }
    #                 }
    #             }
    #         }
    #     })


if __name__ == '__main__':
    unittest.main()
