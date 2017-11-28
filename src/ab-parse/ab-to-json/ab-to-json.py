#!/usr/bin/python

import argparse
import json
import re
import sys


test_parameters = (
    "Server Software",
    "Server Hostname",
    "Server Port",
    "Document Path",
    "Document Length",
    "Concurrency Level",
)

result_details = (
    "Time taken for tests",
    "Complete requests",
    "Failed requests",
    "Non-2xx responses",
    "Total transferred",
    "HTML transferred",
    "Time per request",
    "Requests per second",
    "Transfer rate",
)

# key white list for key-value results
key_wl = test_parameters + result_details

# key-value string (value is any string w/o spaces)
k_v = re.compile("([^:]+)\:\s+(\S+)\s*\Z"), ("key", "value")
# key-value-units string (value is a number)
k_v_u = re.compile("([^:]+)\:\s+(\d*\.\d*|\d+)\s+(\S+)\s*\Z"), \
        ("key", "value", "units")
# key-value-units-note string (value is a number)
k_v_u_n = re.compile("([^:]+)\:\s+(\d*\.\d*|\d+)\s+\[(\S+)\]\s+(.+)"), \
          ("key", "value", "units", "note")
# connection times row, 3 columns
table_row_3 = \
    re.compile("([^:]+)\:\s+(\d*\.\d*|\d+)\s+(\d*\.\d*|\d+)\s+"
               "(\d*\.\d*|\d+)\s*\Z"), \
    ("time_of", "min", "avg", "max")
# connection times row, 5 columns
table_row_5 = \
    re.compile("([^:]+)\:\s+(\d*\.\d*|\d+)\s+(\d*\.\d*|\d+)\s+"
               "(\d*\.\d*|\d+)\s+(\d*\.\d*|\d+)\s+(\d*\.\d*|\d+)\s*\Z"), \
    ("time_of", "min", "mean", "sd", "avg", "max")
# percentile rows
percentile = re.compile("\s+([\d]{1,2})\%\s+(\d+)\s*\Z"), ("perc", "time")
percent100 = re.compile("\s+(100)\%\s+(\d+)\s+\(longest request\)\s*\Z"), \
             ("perc", "time")
# all non-error results
common = \
    (k_v, k_v_u, k_v_u_n, table_row_3, table_row_5, percentile, percent100)

# errors definitions
errors = (
    (re.compile("(apr_.+\(\d+\))"), "Fatal"),
    (re.compile("^ERROR: (.*)"), "Error"),
    (re.compile("^WARNING: (.*)"), "Warning")
)
# possible multi-line error aliases
err_multiline = set((errors[1][1], errors[2][1]))
# last line(s) of multi-line error
ew_cont = re.compile("^ {7,8}([^ ].*)")

# tables' names
perc_table = "Percentile vs Time (ms)"
conn_time_table = "Connection Times (ms)"


def ab_output_to_dict():

    err_alias = ""
    # multi-line error value
    err_ml_value = ""

    result = {
        "Fatal": [],
        "Error": {},
        "Warning": {},
        perc_table: {},
        conn_time_table: {}
    }

    for line in sys.stdin:
        # handling of last line(s) for multi-line error
        if err_ml_value:
            match = ew_cont.search(line)
            if match and len(match.groups()) == 1:
                err_ml_value += (" " + match.group(1))
                continue
            else:
                if result[err_alias].get(err_ml_value):
                    result[err_alias][err_ml_value] += 1
                else:
                    result[err_alias][err_ml_value] = 1
                err_alias = ""
                err_ml_value = ""
        # handling of first line of error
        for re, alias in errors:
            match = re.search(line)
            if match and len(match.groups()) == 1:
                err_alias = alias
                if alias in err_multiline:
                    # can be a multi-line error
                    err_ml_value = match.group(1)
                else:
                    # single-line error
                    result[alias].append(match.group(1))
                break
        if err_alias:
            continue
        # handling of non-error messages:
        for re, fields in common:
            match = re.search(line)
            if match and len(match.groups()) == len(fields):
                kv = dict(zip(fields, match.groups()))
                key = kv.pop(fields[0])
                if fields[0] == "key" and (key in key_wl):
                    result[key] = kv
                elif fields[0] == "time_of":
                    result[conn_time_table][key] = kv
                elif fields[0] == "perc":
                    result[perc_table][key] = kv["time"]
                break
    # handling of last line for multi-line error if any
    if err_ml_value:
        result[err_alias].append(err_ml_value)

    return result


def ab_output_to_json(generic=False):
    data = ab_output_to_dict()
    if generic:
        data = ab_dict_to_generic_format(data)

    sys.stdout.write(json.dumps(data, indent=2))


def ab_dict_to_generic_format(data):
    """Converts parsed ab output to generic format

    Generic format is the one defined for storing test results
    in ElasticSearch
    """
    res = {
        'test_parameters': [],
        'result_details': [],
        'test_errors': []
    }
    for section in ('test_parameters', 'result_details'):
        for key in eval(section):
            if data.get(key):
                name = key
                if 'units' in data[key]:
                    name += ', ' + data[key]['units']
                value = data[key]['value']
                res[section].append({'name': name, 'value': value})
    # placing warnings into result_details
    for k,v in data['Warning'].items():
        res['result_details'].append({'name': k, 'value': v})
    # placing Fatal and Error into test_errors
    for err in data['Fatal']:
        res['test_errors'].append(err)
    for k,v in data['Error'].items():
        res['test_errors'].append('%s: %s' % (k,v))

    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generic", help="print JSON in generic format",
        action="store_true")
    args = parser.parse_args()

    ab_output_to_json(generic=args.generic)