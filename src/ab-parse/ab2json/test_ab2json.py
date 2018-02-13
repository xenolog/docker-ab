import copy
import json
import mock
import os
import unittest

try:
    from ab2json import ab2json  # py3
except ImportError:
    import ab2json

try:
    from StringIO import StringIO  # py2
except ImportError:
    from io import StringIO


class TestAbUtils(unittest.TestCase):
    """Common stuff for ab2json testing"""

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "tests")

    def load_json(self, filename):
        return json.load(open(os.path.join(self.path, filename)))


class TestAbToDict(TestAbUtils):
    """Tests for ab_output_to_dict()"""

    @classmethod
    def parse_from_string(cls, str):
        return ab2json.ab_output_to_dict(infile=StringIO(str))

    def test_ab_output_to_dict_full_ab_output(self):
        result = ab2json.ab_output_to_dict(
            infile=open(self.path + "/es_ab.out"))

        # It is a trick to convert result to unicode as JSON is unicode-based.
        # So, json.load() returns unicode but ab_output_to_dict() returns ASCII
        # therefore these two outputs cannot be compared directly.
        enc, dec = json.JSONEncoder(), json.JSONDecoder()
        result = dec.decode(enc.encode(result))

        expected = self.load_json("es_json.out")
        self.assertEqual(expected, result)

    def test_ab_output_to_dict_empty(self):
        result = ab2json.ab_output_to_dict(infile=open("/dev/null"))
        self.assertEqual(ab2json.result_template, result)

    def test_ab_output_to_dict_known_variable(self):
        for key in ab2json.key_wl:
            result = self.parse_from_string("{0}: 5000".format(key))
            expected = copy.deepcopy(ab2json.result_template)
            expected[key] = {"value": "5000"}
            self.assertEqual(expected, result)

            result = self.parse_from_string("{0}: 5000 pieces".format(key))
            expected[key] = {"value": "5000", "units": "pieces"}
            self.assertEqual(expected, result)

            result = self.parse_from_string(
                "{0}: 5000 [pieces] average".format(key))
            expected[key] = \
                {"value": "5000", "units": "pieces", "note": "average"}
            self.assertEqual(expected, result)

    def test_ab_output_to_dict_unknown_variable(self):
        result = self.parse_from_string("Some score: 5000")

        # unknown key is not taken into account
        self.assertEqual(ab2json.result_template, result)

    def test_ab_output_to_dict_known_and_unknown_variables(self):
        instr = ": 1\n".join(k for k in ab2json.key_wl)
        instr += ": 1\nSome score: 1\n"
        result = self.parse_from_string(instr)

        expected = copy.deepcopy(ab2json.result_template)
        expected.update(dict([(k, {"value": "1"}) for k in ab2json.key_wl]))
        self.assertEqual(expected, result)


class TestDictToGeneric(TestAbUtils):
    """Tests for ab_dict_to_generic_format()"""

    def test_ab_dict_to_generic_format_full_output(self):
        result = ab2json.ab_dict_to_generic_format(
            self.load_json("es_json.out"))

        expected = self.load_json("es_generic.out")
        self.assertEqual(expected, result)

    def test_ab_dict_to_generic_format_empty(self):
        dict_input = copy.deepcopy(ab2json.result_template)
        result = ab2json.ab_dict_to_generic_format(dict_input)
        self.assertEqual(ab2json.generic_template, result)

    def test_ab_dict_to_generic_format_known_variable(self):
        for section in ("test_parameters", "result_details"):
            for key in getattr(ab2json, section):
                # just value
                dict_input = copy.deepcopy(ab2json.result_template)
                dict_input[key] = {"value": "5000"}
                result = ab2json.ab_dict_to_generic_format(dict_input)

                expected = copy.deepcopy(ab2json.generic_template)
                expected[section][key] = "5000"
                self.assertEqual(expected, result)

                # value and units
                dict_input[key]["units"] = "pieces"
                result = ab2json.ab_dict_to_generic_format(dict_input)

                expected = copy.deepcopy(ab2json.generic_template)
                expected[section][key + ", pieces"] = "5000"
                self.assertEqual(expected, result)

                # value, units and note
                dict_input[key]["note"] = "average"
                result = ab2json.ab_dict_to_generic_format(dict_input)

                # "note" is not taken into account so expected value remains
                # the same
                self.assertEqual(expected, result)

    def test_ab_dict_to_generic_format_unknown_variable(self):
        dict_input = copy.deepcopy(ab2json.result_template)
        dict_input["Some score"] = {"value": "5000"}
        result = ab2json.ab_dict_to_generic_format(dict_input)

        # unknown key is not taken into account
        self.assertEqual(ab2json.generic_template, result)

    def test_ab_dict_to_generic_format_known_and_unknown_variables(self):
        dict_input = copy.deepcopy(ab2json.result_template)
        dict_input.update(dict([(k, {"value": "1"}) for k in ab2json.key_wl]))
        result = ab2json.ab_dict_to_generic_format(dict_input)

        expected = copy.deepcopy(ab2json.generic_template)
        for section in ("test_parameters", "result_details"):
            for key in getattr(ab2json, section):
                expected[section][key] = "1"
        self.assertEqual(expected, result)


class TestAbToJson(TestAbUtils):
    """Tests for ab_output_to_json()"""

    def call_converter(self, generic):
        with mock.patch('sys.stdout', new=StringIO()) as mock_stdout:
            ab2json.ab_output_to_json(
                generic=generic, infile=open(self.path + "/es_ab.out"))
            # Convert results back to python dict as string versions may have
            # differences
            return json.JSONDecoder().decode(mock_stdout.getvalue())

    def test_ab_output_to_json_simple(self):
        result = self.call_converter(False)

        expected = self.load_json("es_json.out")
        self.assertEqual(expected, result)

    def test_ab_output_to_json_generic(self):
        result = self.call_converter(True)

        expected = self.load_json("es_generic.out")
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
