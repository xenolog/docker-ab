#!/usr/bin/python3

import json
import os
import argparse
import sys

def Normalize(s):
    if s is not None:
        rv = s.replace(' ', '_')
        rv = rv.lower()
    else:
        rv = None
    return rv


class JsonToEnv(object):
    data = {}
    result = []

    def __init__(self, separator="__", export=False):
        self._separator = separator
        self._export = export

    def load(self, js):
        self.data = json.loads(js)
        self.result = []

    def loadfile(self, filename):
        with open(filename, 'r') as jsonfile:
            self.data = json.load(jsonfile)
        self.result = []

    def prepare(self):
        for i in sorted(self.data.items()):  # sorted need here for easement testing
            if type(i[1]) is list:
                for j in i[1]:
                    if type(j) is not dict:
                        continue
                    k = Normalize(j.get("name", None))
                    v = str(j.get("value", None))
                    if k is None or v is None:
                        continue
                    self.result.append((str("{}{}{}".format(i[0], self._separator,k)), str(v)))
            else:
                self.result.append((str(Normalize(i[0])), str(i[1])))

    def __str__(self):
        ex = "export " if self._export else ""
        rv = ""
        for i in sorted(self.result):
            rv += "{}{}=\"{}\"\n".format(ex, i[0], str(i[1]))
        return rv

def main(filename, export=False):
    try:
        os.stat(filename)
    except OSError as e:
        return (1, e)
    env = JsonToEnv(export=export)
    env.loadfile(filename)
    env.prepare()
    return (0, str(env))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='json2env',
        description='Json to ENV converter'
    )
    parser.add_argument('filename', help='json file')
    parser.add_argument("--export", help="add 'export' to the output",
        action="store_true")
    args = parser.parse_args()

    rc = main(args.filename, export=args.export)
    if rc[0] == 0:
        sys.stdout.write(rc[1])
    else:
        sys.stderr.write("ERROR:\n  {}\n".format(rc[1]))
        sys.exit(rc[0])

###