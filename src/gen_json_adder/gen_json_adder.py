#!/usr/bin/python

import argparse
import json
import os
import sys

class JsonAdder(object):
    pass

def main(in_file, res_file, test_result):
    return 0

if __name__ == "__main__":
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
    rv = main(in_file=args.incoming, res_file=args.result, test_result=test_result)
    sys.stdout.write(str(rv))
