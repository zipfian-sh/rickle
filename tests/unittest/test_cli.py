import unittest
import subprocess
import sys
from rickle.tools import classify_string
import os
from pathlib import Path
import yaml
import json

os.putenv('COMSPEC',r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe')



class TestCLITool(unittest.TestCase):

    base_dir = Path(__file__).parent
    yaml_file = base_dir / 'test_config.yaml'
    json_schema_file = base_dir / 'test_config.schema.json'
    sample_data = {
        "config": {
            "version" : "0.1.0",
            "name" : "rickle_unittest",
            "threshold": 3.14
        }
    }

    sample_schema = {
        "type" : "object",
        "properties": {
            "config" : {
                "type" : "object",
                "properties": {
                    "version" : {
                        "type" : "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "threshold": {
                        "type": "number"
                    }
                }
            }
        }
    }

    @classmethod
    def setUpClass(cls):
        with cls.yaml_file.open('w') as yf:
            yaml.dump(cls.sample_data, yf)

        with cls.json_schema_file.open('w') as jf:
            json.dump(cls.sample_schema, jf, indent=2)

    @classmethod
    def tearDownClass(cls):
        if cls.yaml_file.exists():
            cls.yaml_file.unlink()

        if cls.json_schema_file.exists():
            cls.json_schema_file.unlink()

    def setUp(self) -> None:
        self.cat_command = 'type' if sys.platform == 'win32' else 'cat'

        self.python_command = 'python'
        self.rickled_command = 'rickle.cli'

    def test_cli_schema_check(self):
        command_cat = f'{self.cat_command} "{str(self.yaml_file)}"'

        result = subprocess.Popen(command_cat,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        command_rickle = f'{self.python_command} -m {self.rickled_command} schema check --schema "{str(self.json_schema_file)}"'

        result = subprocess.run(command_rickle,
                                shell=True,
                                stdin=result.stdout,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)



        # Check if the command was successful
        self.assertEqual(result.returncode, 0, msg=f"CLI returned non-zero exit code: {result.returncode}")

        # Compare actual and expected output
        self.assertEqual(result.stdout, '\x1b[94mINPUT\x1b[0m -> \x1b[92mOK\x1b[0m\n', msg=f"Unexpected CLI output: {result.stdout}")


    def test_cli_schema_gen(self):
        command_cat = f'{self.cat_command} "{str(self.yaml_file)}"'

        result = subprocess.Popen(command_cat,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        command_rickle = f'{self.python_command} -m {self.rickled_command} schema gen'

        result = subprocess.run(command_rickle,
                                shell=True,
                                stdin=result.stdout,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)



        # Check if the command was successful
        self.assertEqual(result.returncode, 0, msg=f"CLI returned non-zero exit code: {result.returncode}")

        _actual = yaml.safe_load(result.stdout)

        # Compare actual and expected output
        self.assertDictEqual(_actual, self.sample_schema, msg=f"Unexpected CLI output!")

if __name__ == "__main__":
    unittest.main()
