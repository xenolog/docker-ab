#!/usr/bin/python

import unittest
import json2env
import textwrap

income_json = """
{
  "vnf_name": "AVI LB",
  "vnf_id": "1",
  "result_details": [
    {"name": "Complete requests",
     "value": "4000"},
    {"name": "Failed requests",
     "value": "1000"}],
  "test_errors": [],
  "test_parameters": [
    {"name": "requests number",
     "value": 5000},
    {"name": "concurrency",
     "value": 100}]
}
"""
income_dict = {
    'vnf_name': 'AVI LB',
    'vnf_id': '1',
    'test_errors': [],
    'test_parameters': [
        {'name': 'requests number', 'value': 5000},
        {'name': 'concurrency', 'value': 100}
    ],
    'result_details': [
        {'name': 'Complete requests', 'value': '4000'},
        {'name': 'Failed requests', 'value': '1000'}
    ]
}

class TestStringMethods(unittest.TestCase):

    def test_init(self):
        a = json2env.JsonToEnv()
        a.load(income_json)
        self.assertEqual(a.data, income_dict)

    def test_process(self):
        a = json2env.JsonToEnv()
        a.load(income_json)
        a.prepare()
        # result will be sorted, except embedded k/v pairs.
        # embedded k/v pairs wil be in their orders
        self.assertEqual(a.result, [
            ('result_details__complete_requests', '4000'),
            ('result_details__failed_requests', '1000'),
            ('test_parameters__requests_number', '5000'),
            ('test_parameters__concurrency', '100'),
            ('vnf_id', '1'),
            ('vnf_name', 'AVI LB')
        ])

    def test_output(self):
        a = json2env.JsonToEnv()
        a.load(income_json)
        a.prepare()
        # result will be sorted
        self.assertEqual(str(a), textwrap.dedent("""\
            result_details__complete_requests="4000"
            result_details__failed_requests="1000"
            test_parameters__concurrency="100"
            test_parameters__requests_number="5000"
            vnf_id="1"
            vnf_name="AVI LB"
        """))

    def test_exported_output(self):
        a = json2env.JsonToEnv(export=True)
        a.load(income_json)
        a.prepare()
        # result will be sorted
        self.assertEqual(str(a), textwrap.dedent("""\
            export result_details__complete_requests="4000"
            export result_details__failed_requests="1000"
            export test_parameters__concurrency="100"
            export test_parameters__requests_number="5000"
            export vnf_id="1"
            export vnf_name="AVI LB"
        """))


if __name__ == '__main__':
    unittest.main()