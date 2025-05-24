import unittest
from rickle import Rickle
import os
import base64
import tempfile
import json
from io import StringIO

class TestBaseRickle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["MY_ENV_VAR"] = "test_value"

    @classmethod
    def tearDownClass(cls):
        del os.environ["MY_ENV_VAR"]

    def setUp(self):
        self.rickle = Rickle()


    def test_add_env(self):
        self.rickle.add_env('my_var', 'MY_ENV_VAR', default='nil')

        self.assertDictEqual(self.rickle.dict(), {'my_var': 'test_value'})
        self.assertDictEqual(self.rickle.dict(serialised=True),
                             {'my_var': {'type': 'env', 'load': 'MY_ENV_VAR', 'default': 'nil'}})

        # test default
        self.rickle.add_env('my_other_var', 'MY_OTHER_VAR', default='nil')
        self.assertDictEqual(self.rickle.dict(),
                             {'my_var': 'test_value', 'my_other_var': 'nil'})

    def test_add_base64(self):
        b_data = b"All your base are belong to us"
        encoded_data = base64.b64encode(b_data).decode("utf-8")
        self.rickle.add_base64("base64_data", encoded_data)

        self.assertEqual(self.rickle.get("base64_data"), b_data)
        self.assertDictEqual(self.rickle.dict(serialised=True),
                             {'base64_data': {'type': 'base64', 'load': encoded_data}})

        self.assertTrue(True)

    def test_add_csv(self):
        csv_content = "id,name\n1,Alice\n2,Bob"

        # Method 1, purely as lists
        self.rickle.add_csv("csv_data", file_path_or_str=csv_content, load_as_rick=True)
        expected_data = { "csv_data":
            [
                {"id": "1", "name": "Alice"},
                {"id": "2", "name": "Bob"}
            ]
        }

        actual_data = self.rickle.dict()

        self.assertDictEqual(actual_data, expected_data)

        # Method 2, as lists of Rickles
        self.rickle.add_csv("csv_data_flat", file_path_or_str=csv_content, load_as_rick=False)

        expected_data = [['id', 'name'], ['1', 'Alice'], ['2', 'Bob']]

        actual_data = self.rickle.get("csv_data_flat")

        self.assertListEqual(actual_data, expected_data)

        # Method 3, as Rickles

        csv_content = "1,Alice\n2,Bob"

        self.rickle.add_csv("csv_data_fieldnames", file_path_or_str=csv_content, fieldnames=['id', 'name'])

        expected_data = {"id": ["1", "2"], "name": ["Alice", "Bob"]}

        actual_data = self.rickle.get("csv_data_fieldnames").dict()

        self.assertDictEqual(actual_data, expected_data)

        # Read file
        self.rickle.add_csv("csv_data_from_file", file_path_or_str='./tests/placebos/test.csv', load_as_rick=True)

        expected_data = {"a": "j", "b": "1", "c": "0.2", "d": "o"}

        actual_data = self.rickle.get("csv_data_from_file")[0].dict()

        self.assertDictEqual(actual_data, expected_data)

    def test_add_file(self):

        self.rickle.add_file("bowser", './tests/placebos/6D6172696F.txt')
        self.assertTrue(self.rickle.get("bowser").startswith("d061"))


    def test_add_api_json(self):
        self.rickle.add_api("api_result", "https://official-joke-api.appspot.com/random_joke")
        keys = self.rickle.get("api_result").keys()
        self.assertTrue('type' in keys)
        self.assertTrue('setup' in keys)
        self.assertTrue('punchline' in keys)


if __name__ == "__main__":
    unittest.main()