import unittest
import gen_json_adder
import textwrap

incoming_json = """
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
     "value": 10}]
}
"""

test_result_json = """
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
  ],
  "test_errors": []
}
"""

class TestStringMethods(unittest.TestCase):

    def test_summarize(self):
        a = gen_json_adder.JsonAdder(test_result='passed')
        a._incoming_string_load(str(incoming_json))
        a._result_string_load(str(test_result_json))
        a._prepare()
        self.maxDiff = None
        self.assertEqual(a.rv, {
            "vnf_name": "AVI LB",
            "test_run_id": "1",
            "test_scenario_id": "2",
            "test_id": "3",
            "test_name": "ApacheBench smoke test",
            "test_result": "passed",
            "result_details": [
                { "name": "Time taken for tests, seconds", "value": "3.949" },
                { "name": "Complete requests", "value": "10000" },
                { "name": "Failed requests", "value": "0" },
                { "name": "Total transferred, bytes", "value": "8450000" },
                { "name": "HTML transferred, bytes", "value": "6120000" },
                { "name": "Time per request, ms", "value": "0.395" },
                { "name": "Requests per second, #/sec", "value": "2532.48" },
                { "name": "Transfer rate, Kbytes/sec", "value": "2089.79" }
            ],
            "test_parameters": [
                { "name": "Server Software", "value": "nginx/1.13.7"},
                { "name": "Server Hostname", "value": "172.17.0.2" },
                { "name": "Server Port", "value": "80" },
                { "name": "Document Path", "value": "/" },
                { "name": "Document Length, bytes", "value": "612" },
                { "name": "Concurrency Level", "value": "10" }
            ],
            "test_errors": []
        })

if __name__ == '__main__':
    unittest.main()
