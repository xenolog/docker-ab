#!/usr/bin/python

import unittest
import gen_json_adder
import textwrap

income_json = """
{
  "vnf_name": "AVI LB",
  "test_run_id": "1",
  "test_scenario_id": "2",
  "test_id": "3",
  "test_name": "ApacheBench smoke test",
  "result_details": [
    {"name": "Complete requests",
     "value": "0"},
    {"name": "Failed requests",
     "value": "0"}],
  "test_errors": [],
  "test_parameters": [
    {"name": "Server Hostname",
     "value": "172.17.0.2"},
    {"name": "Server Port",
     "value": "80"},
    {"name": "Server Proto",
     "value": "http"},
    { "name": "Document Path",
      "value": "/" },
    {"name": "Requests Number",
     "value": "10000"},
    {"name": "Concurrency Level",
     "value": 10}],
}
"""

result_json = """
{
  "test_parameters": [
    { "name": "Server Software",
      "value": "nginx/1.13.7"},
    { "name": "Server Hostname",
      "value": "172.17.0.2" },
    { "name": "Server Port",
      "value": "80" },
    { "name": "Document Path",
      "value": "/" },
    { "name": "Document Length, bytes",
      "value": "612" },
    { "name": "Concurrency Level",
      "value": "10" }
  ],
  "test_errors": [],
  "result_details": [
    { "name": "Time taken for tests, seconds",
      "value": "3.949" },
    { "name": "Complete requests",
      "value": "10000" },
    { "name": "Failed requests",
      "value": "0" },
    { "name": "Total transferred, bytes",
      "value": "8450000" },
    { "name": "HTML transferred, bytes",
      "value": "6120000" },
    { "name": "Time per request, ms",
      "value": "0.395" },
    { "name": "Requests per second, #/sec",
      "value": "2532.48" },
    { "name": "Transfer rate, Kbytes/sec",
      "value": "2089.79" }
  ]
}
"""

class TestStringMethods(unittest.TestCase):

    def test_init(self):
        a = gen_json_adder.JsonAdder()
        a.load_incoming(income_json)
        a.load_result(result_json)
        self.assertEqual(a.data, {})

    # def test_process(self):
    #     a = json2env.JsonToEnv()
    #     a.load(income_json)
    #     a.prepare()
    #     # result will be sorted, except embedded k/v pairs.
    #     # embedded k/v pairs wil be in their orders
    #     self.assertEqual(a.result, [
    #         ('result_details__complete_requests', '4000'),
    #         ('result_details__failed_requests', '1000'),
    #         ('test_parameters__requests_number', '5000'),
    #         ('test_parameters__concurrency', '100'),
    #         ('vnf_id', '1'),
    #         ('vnf_name', 'AVI LB')
    #     ])

    # def test_output(self):
    #     a = json2env.JsonToEnv()
    #     a.load(income_json)
    #     a.prepare()
    #     # result will be sorted
    #     self.assertEqual(str(a), textwrap.dedent("""\
    #         result_details__complete_requests="4000"
    #         result_details__failed_requests="1000"
    #         test_parameters__concurrency="100"
    #         test_parameters__requests_number="5000"
    #         vnf_id="1"
    #         vnf_name="AVI LB"
    #     """))

    # def test_exported_output(self):
    #     a = json2env.JsonToEnv(export=True)
    #     a.load(income_json)
    #     a.prepare()
    #     # result will be sorted
    #     self.assertEqual(str(a), textwrap.dedent("""\
    #         export result_details__complete_requests="4000"
    #         export result_details__failed_requests="1000"
    #         export test_parameters__concurrency="100"
    #         export test_parameters__requests_number="5000"
    #         export vnf_id="1"
    #         export vnf_name="AVI LB"
    #     """))


if __name__ == '__main__':
    unittest.main()
