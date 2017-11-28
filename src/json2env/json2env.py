#!/usr/bin/python

import json
import os

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

    def prepare(self):
        for i in sorted(self.data.items()):  # sorted need here for easement trsting
            if type(i[1]) is list:
                for j in i[1]:
                    if type(j) is not dict:
                        continue
                    k = Normalize(j.get("name", None))
                    v = str(j.get("value", None))
                    if k is None or v is None:
                        continue
                    self.result.append((str("{}{}{}".format(i[0],self._separator,k)), str(v)))
            else:
                self.result.append((str(Normalize(i[0])), str(i[1])))

    def __str__(self):
        ex = "export " if self._export else ""
        rv = ""
        for i in sorted(self.result):
            rv += "{}{}=\"{}\"\n".format(ex, i[0], str(i[1]))
        return rv

# if __name__ == '__main__':
