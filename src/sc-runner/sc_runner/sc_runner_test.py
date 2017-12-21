
import unittest
import sc_runner
import textwrap
import yaml
from io import StringIO

from ab2json.ab2json import ab_output_to_dict #, ab_dict_to_generic_format


class T0(unittest.TestCase):

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


class T1(unittest.TestCase):

    AbstractYaml = textwrap.dedent("""\
        scenario_id: 1
        scenarios:
          1:
            tasks:
              - 1
              - 2
          2:
            tasks:
              - 2
              - 1
          3:
            tasks:
              - 2
        tasks:
          defaults:
            script: test_case__0.sh
            implementation: sh
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
    """)

    OverrideAbstractYaml = textwrap.dedent("""\
    tasks:
      defaults:
        properties:
          host_ip: 127.0.0.1
      2:
        properties:
          host_ip: 192.168.0.1
    """)

    DefaultizedAbstractYaml = textwrap.dedent("""\
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
    """)

    def setUp(self):
        self.maxDiff = None
        self.rnr = sc_runner.ScRunner()
        self.rnr._loads(self.AbstractYaml)

    def tearDown(self):
        del self.rnr

    def test_defaultized_yaml(self):
        self.rnr._prepare()
        self.assertEqual(self.rnr.config, yaml.load(StringIO(self.DefaultizedAbstractYaml)))

    def test_overrided_yaml(self):
        self.rnr._loads(self.OverrideAbstractYaml)
        self.rnr._prepare()
        overrided_config = yaml.load(StringIO(self.DefaultizedAbstractYaml))
        overrided_config[1]['properties']['host_ip'] = "127.0.0.1"
        overrided_config[2]['properties']['host_ip'] = "192.168.0.1"
        self.assertEqual(self.rnr.config, overrided_config)


class T2(unittest.TestCase):

    testYaml = textwrap.dedent("""\
        ---
        scenarios:
          1:
            tasks:
              - 1
              - 2
          2:
            tasks:
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
    """)
    overrideYaml = textwrap.dedent("""\
        scenario_id: 1
        tasks:
          defaults:
            properties:
              host_ip: 127.0.0.1
    """)

    def setUp(self):
        self.maxDiff = None
        self.t2 = sc_runner.ScRunner()
        self.t2._loads(self.testYaml)
        self.t2._loads(self.overrideYaml)

    def tearDown(self):
        del self.t2

    def test_runner_1(self):

        def fake_runner(script, task, env):
            self.fr_result.append(script)
            return 0, None, None

        self.fr_result = []
        self.t2.run(runner=fake_runner)
        self.assertEqual(self.fr_result, [
            ['ab', '-c', '1', '-n', '100', 'http://127.0.0.1/'],
            ['ab', '-c', '100', '-n', '100000', 'http://127.0.0.1/']
        ])

    def test_runner_2(self):

        def fake_runner(script, task, env):
            self.fr_result.append(script)
            return 1, None, None

        self.fr_result = []
        self.t2._settings[-1]['scenario_id'] = 2
        self.t2.run(runner=fake_runner)
        self.assertEqual(self.fr_result, [
            ['ab', '-c', '1', '-n', '100', 'http://127.0.0.1:80/'],
            ['ab', '-c', '1', '-n', '100', '-i', 'http://127.0.0.1:80/'],
            ['ab', '-c', '1', '-n', '1', 'http://127.0.0.1/']
        ])


class T3(unittest.TestCase):
    """
    Testing Scenario's metadata merging
    and pass metadata's fields to "generic" report
    """

    testYaml = textwrap.dedent("""\
        ---
        scenarios:
          defaults:
            metadata:
              vnf_name: "AVI LB"
              vnf_id: "1"
              vnf_version: "1.0"
          1:
            tasks:
              - 2
          2:
            tasks:
              - 3
              - 4

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
              concurrency: 10
              requests: 10000
    """)
    overrideYaml = textwrap.dedent("""\
        ---
        scenario_id: 1
        scenarios:
          defaults:
            metadata:
              vnf_id: "2"
              qwe: 123
        tasks:
          defaults:
            properties:
              host_ip: 127.0.0.1
    """)
    resultScenariosYaml = textwrap.dedent("""\
        ---
        1:
          metadata:
              qwe: 123
              vnf_id: "2"
              vnf_name: "AVI LB"
              vnf_version: "1.0"
          tasks:
              - 2
        2:
          metadata:
              qwe: 123
              vnf_id: "2"
              vnf_name: "AVI LB"
              vnf_version: "1.0"
          tasks:
              - 3
              - 4
    """)
    ABoutput = textwrap.dedent("""\
        This is ApacheBench, Version 2.3 <$Revision: 1796539 $>
        Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
        Licensed to The Apache Software Foundation, http://www.apache.org/

        Benchmarking 172.17.0.2 (be patient)


        Server Software:        nginx/1.13.7
        Server Hostname:        172.17.0.2
        Server Port:            80

        Document Path:          /
        Document Length:        612 bytes

        Concurrency Level:      10
        Time taken for tests:   3.502 seconds
        Complete requests:      10000
        Failed requests:        0
        Total transferred:      8450000 bytes
        HTML transferred:       6120000 bytes
        Requests per second:    2855.13 [#/sec] (mean)
        Time per request:       3.502 [ms] (mean)
        Time per request:       0.350 [ms] (mean, across all concurrent requests)
        Transfer rate:          2356.04 [Kbytes/sec] received

        Connection Times (ms)
                      min  mean[+/-sd] median   max
        Connect:        0    1   0.5      0       3
        Processing:     0    3   0.8      3      10
        Waiting:        0    3   0.8      3      10
        Total:          1    3   0.6      3      10
        WARNING: The median and mean for the initial connection time are not within a normal deviation
                These results are probably not that reliable.

        Percentage of the requests served within a certain time (ms)
          50%      3
          66%      4
          75%      4
          80%      4
          90%      4
          95%      4
          98%      5
          99%      5
         100%     10 (longest request)
    """)

    def setUp(self):
        self.maxDiff = None
        self.rnr = sc_runner.ScRunner()
        self.rnr._loads(self.testYaml)
        self.rnr._loads(self.overrideYaml)

    def tearDown(self):
        del self.rnr

    def test_defaultized_yaml(self):
        self.rnr._prepare()
        self.assertEqual(self.rnr._scenarios, yaml.load(StringIO(self.resultScenariosYaml)))

    def test_runner_1(self):
        """
        fake run one pass of Scenario #1
        """

        def fake_runner(script, task, env):
            self.fr_result.append(script)
            return 0, None, None

        class MyStringIO(StringIO):
            def close(self):
                pass

        self.fr_result = []
        self.rnr.run(runner=fake_runner)
        outfile = MyStringIO()
        self.rnr.results[1] = ab_output_to_dict(infile=StringIO(self.ABoutput))
        outfile.seek(0)
        self.rnr.generate_report(outfile=outfile, format="yaml")
        #
        self.assertEqual(self.fr_result, [
            ['ab', '-c', '10', '-n', '10000', 'http://127.0.0.1/']
        ])
        self.assertEqual(yaml.load(outfile.getvalue()), {
            'result_details': [
                {'name': 'Time taken for tests, seconds', 'value': '3.502'},
                {'name': 'Complete requests', 'value': '10000'},
                {'name': 'Failed requests', 'value': '0'},
                {'name': 'Total transferred, bytes', 'value': '8450000'},
                {'name': 'HTML transferred, bytes', 'value': '6120000'},
                {'name': 'Time per request, ms', 'value': '0.350'},
                {'name': 'Requests per second, #/sec', 'value': '2855.13'},
                {'name': 'Transfer rate, Kbytes/sec', 'value': '2356.04'},
                {'name': 'The median and mean for the initial connection time are not within a normal ' +
                    'deviation These results are probably not that reliable.', 'value': 1}
            ],
            'test_errors': [],
            'test_parameters': [
                {'name': 'Server Software', 'value': 'nginx/1.13.7'},
                {'name': 'Server Hostname', 'value': '172.17.0.2'},
                {'name': 'Server Port', 'value': '80'},
                {'name': 'Document Path', 'value': '/'},
                {'name': 'Document Length, bytes', 'value': '612'},
                {'name': 'Concurrency Level', 'value': '10'}
            ]
        })


if __name__ == '__main__':
    unittest.main()
