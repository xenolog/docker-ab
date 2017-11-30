#!/usr/bin/python3

import argparse
import json
import os
import sys

class JsonAdder(object):
    incoming = {}
    result = {}
    rv = {}

    def __init__(self, in_file=None, res_file=None, test_result='failed', indent=2):
        self.indent = indent
        self.test_result = test_result
        if in_file:
            self._incoming_file_load(in_file)
        if res_file:
            self._result_file_load(res_file)

    def _incoming_string_load(self, js):
        self.incoming = json.loads(js)
        self.rv = {}

    def _incoming_file_load(self, filename):
        with open(filename, 'r') as jsonfile:
            self.incoming = json.load(jsonfile)
        self.rv = {}

    def _result_string_load(self, js):
        self.result = json.loads(js)
        self.rv = {}

    def _result_file_load(self, filename):
        with open(filename, 'r') as jsonfile:
            self.result = json.load(jsonfile)
        self.rv = {}

    def _prepare(self):
        if not self.incoming:
            sys.stderr.write("WARNING: incoming json file is empty")
        if not self.result:
            sys.stderr.write("WARNING: test result json file is empty")
        self.rv.update(self.incoming)
        self.rv["test_result"] = self.test_result
        self.rv["result_details"] = self.result.get("result_details", [])
        self.rv["test_errors"] = self.result.get("test_errors", [])
        self.rv["test_parameters"] = self.result.get("test_parameters", [])


    def __str__(self):
        if self.rv == {}:
            self._prepare()
        return json.dumps(self.rv, indent=self.indent)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--incoming", action="store",
        help="JSON file with test case description")
    parser.add_argument("--result", action="store",
        help="JSON file with test case result in 'generic' format")
    parser.add_argument("--test-result", dest='test_result', action="store", default='unknown',
        help="whether test was 'passed' or 'failed'. ENV variable 'test_result' will be used if ommited")
    args = parser.parse_args()

    test_result = os.getenv("test_result", "failed") if args.test_result=='unknown' else args.test_result

    # ab_output_to_json(generic=args.generic)
    rv = JsonAdder(in_file=args.incoming, res_file=args.result, test_result=test_result)
    sys.stdout.write(str(rv))

if __name__ == "__main__":
    main()
