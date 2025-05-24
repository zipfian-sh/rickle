import base64
import configparser
import importlib.util
import inspect
import random
import string
import types
from enum import Enum
from typing import List, Union
from pathlib import Path
import yaml
import json
import os
import sys
import re
from collections import OrderedDict, namedtuple, defaultdict
from io import StringIO

# Add ordered dictionary to dumper
yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data.items()))

import tomli_w as tomlw
if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml

class CLIError(Exception):

    class CLITool(Enum):
        CONV = 1
        OBJ = 2
        SERVE = 3
        SCHEMA = 4
        OBJ_GET = 5
        OBJ_SET = 6
        OBJ_PUT = 7
        OBJ_DEL = 8
        OBJ_TYPE = 9
        OBJ_SEARCH = 10
        OBJ_FIND = 11
        OBJ_FUNC = 12
        SCHEMA_CHECK = 13
        SCHEMA_GEN = 14

    def __init__(self, message, cli_tool: CLITool):
        self.message = message
        self.cli_tool = cli_tool

    def __str__(self):
        return f"{self.cli_tool} {self.message}"

def object_to_dict(obj, include_imports: bool = False, include_class_source: bool = False,
                include_methods: bool = False):
    """
    Takes (almost) any Python object and deconstructs it into a dict.

    Args:
        obj: Any object.
        include_imports (bool): Add a list of modules to import as is imported in current env (default = False).
        include_class_source (bool): Add the source of the object's class (default = False).
        include_methods (bool): Include object methods (default = False).

    Returns:
        dict: Deconstructed object in typical Rickle dictionary format.
    """

    def _destruct(value, name=None):
        pat = re.compile(r'^( )*')
        if type(value) in (int, float, bool, str):
            return value

        if isinstance(value, list) or isinstance(value, tuple):
            new_list = list()
            for v in value:
                new_list.append(_destruct(v))
            return new_list

        if isinstance(value, dict):
            new_dict = dict()
            for k, v in value.items():
                new_dict.update({k: _destruct(v)})
            return new_dict

        if type(value) in (bytes, bytearray):
            return {
                'type': 'base64',
                'load': str(base64.b64encode(value))
            }

        if include_methods and (inspect.ismethod(value) or inspect.isfunction(value)):
            signature = inspect.signature(value)
            args = dict()
            for k, v in dict(signature.parameters).items():
                if repr(v.default) == "<class 'inspect._empty'>":
                    default = None
                else:
                    default = v.default
                args.update({
                    k: default
                })

            if len(args) == 0:
                args = None

            _source_lines = inspect.getsourcelines(value)[0]
            match = pat.match(_source_lines[0])
            s = match.group(0)
            length = len(s)

            source = _source_lines[0][length:]

            for s in _source_lines[1:]:
                source = f'{source}{s[length:]}'

            return {
                'type': 'function',
                'name': name,
                'load': source,
                'args': args,
                'is_method': inspect.ismethod(value)
            }

        # Value is an object that needs flattening into dict.

        d = dict()

        if include_class_source:
            source_lines = inspect.getsource(obj.__class__)
            d['class_source'] = {
                'type': 'class_source',
                'load': source_lines
            }

        if include_imports:
            imports = list()

            for name, val in globals().items():
                if isinstance(val, types.ModuleType):
                    imports.append(val.__name__)

            if len(imports) > 0:
                d['python_modules'] = {
                    'type': 'module_import',
                    'import': imports
                }

        for _name in dir(value):
            if _name.startswith('__'):
                continue
            _value = getattr(value, _name)

            d[name] = _destruct(_value, _name)

        return d

    return _destruct(obj)

def generate_random_value(value_type, value_properties):
    """
    Helper function to generate a random value.

    Notes:
        integer: Properties include ``min`` and ``max``. Defaults to 0 and 256.
        number: Properties include ``min`` and ``max``. Defaults to 0 and 256.
        string: Properties include ``chars`` and ``length``. Defaults to ASCII chars and 10.
        enum: Properties include ``values``.  Defaults to ASCII uppercase chars.
        array: Properties include ``values`` and ``length``.  Defaults to 'integer' and 10.
            ``values`` can be a string of ``value_type``.
        object: Properties include ``keys``, ``values``, ``min``, and ``max``.
            Defaults to random ASCII uppercase and 10 random integers, min and max of 1 and 5.
            ``values`` can be a string of ``value_type``.

    Args:
        value_type (str): Either 'string', 'integer', 'number', 'enum', 'array', 'object', or 'any'.
        value_properties (dict): Properties about the randomly generated value. See notes.

    Returns:
        value: Randomly generated value.
    """
    if value_type == 'any':
        return generate_random_value(value_type=random.choice(['integer', 'string', 'number', 'enum', 'array', 'object']),
                                     value_properties=value_properties)
    if value_type == 'integer':
        return random.randint(value_properties.get('min', 0), value_properties.get('max', 256))
    if value_type == 'number':
        return random.uniform(value_properties.get('min', 0), value_properties.get('max', 256))
    if value_type == 'string':
        chars = value_properties.get('chars', string.ascii_lowercase + string.digits)
        length = value_properties.get('length', 10)
        return ''.join([random.choice(chars) for _ in range(length)])
    if value_type == 'enum':
        return random.choice(value_properties.get('values', string.ascii_uppercase))
    if value_type == 'array':
        length = value_properties.get('length', 10)
        values = value_properties.get('values', 'integer')
        if isinstance(values, str):
            return [generate_random_value(value_type=values, value_properties=value_properties) for _ in range(length)]
        else:
            return [random.choice(values) for _ in range(length)]

    if value_type == 'object':
        keys = value_properties.get('keys', [random.choice(string.ascii_uppercase) for _ in range(10)])
        values = value_properties.get('values', 'integer')
        if isinstance(values, str):
            values = [generate_random_value(value_type=values, value_properties=value_properties) for _ in range(10)]

        value = dict()
        for i in range(random.randint(value_properties.get('min', 1), value_properties.get('max', 5))):
            value[random.choice(keys)] = random.choice(values)

        return value

    raise ValueError(f"Unsupported value_type '{value_type}'")

def get_native_type_name(python_type_name: str, format_type: str, default: str = None):
    """
    Helper mapping from Python type names to format names.

    Args:
        python_type_name (str): Python type name.
        format_type (str): Format type, either yaml, json, toml, xml, ini, env, or python.
        default (str): If unmatched, return this default (default = None).

    Returns:
        str: Native name for the given format.
    """
    python_type_name = python_type_name.strip()
    format_type = format_type.lower().strip()

    yaml_types = {
        'str': 'str',
        'int': 'int',
        'float': 'float',
        'bool': 'boolean',
        'list': 'seq',
        'dict': 'map',
        'Rickle': 'map',
        'UnsafeRickle': 'map',
        'BaseRickle': 'map',
        'bytes': 'binary',
        'NoneType': 'null'
    }

    json_types = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'list': 'array',
        'dict': 'object',
        'Rickle': 'object',
        'UnsafeRickle': 'object',
        'BaseRickle': 'object',
        'NoneType': 'null'
    }

    toml_types = {
        'str': 'String',
        'int': 'Integer',
        'float': 'Float',
        'bool': 'Boolean',
        'list': 'Array',
        'dict': 'Key/Value',
        'Rickle': 'Key/Value',
        'UnsafeRickle': 'Key/Value',
        'BaseRickle': 'Key/Value',
    }

    xml_types = {
        'str': 'xs:string',
        'int': 'xs:integer',
        'float': 'xs:decimal',
        'bool': 'xs:boolean',
        'list': 'xs:sequence',
        'dict': 'xs:complexType',
        'Rickle': 'xs:complexType',
        'UnsafeRickle': 'xs:complexType',
        'BaseRickle': 'xs:complexType',
    }

    if format_type == 'yaml':
        return yaml_types.get(python_type_name, default if default else 'Python')
    elif format_type == 'json':
        return json_types.get(python_type_name, default if default else 'object')
    elif format_type == 'toml':
        return toml_types.get(python_type_name, default if default else 'Other')
    elif format_type == 'xml':
        return xml_types.get(python_type_name, default if default else 'xs:any')
    elif format_type in ["ini", "env", "python"]:
        return python_type_name
    else:
        raise ValueError(f'Unknown format type "{format_type}"')

def supported_encodings() -> list:
    """
    A very rudimentary way to figure out the different supported file encodings supported.

    Returns:
        list: List (str) of encoding names.
    """

    supported = []

    for i in os.listdir(os.path.split(__import__("encodings").__file__)[0]):
        name = os.path.splitext(i)[0]
        try:
            "".encode(name)
        except:
            pass
        else:
            supported.append(name.replace("_", "-").strip().lower())
    return supported

def classify_string(input_string: str):
    """
    Try to classify the type from a string. This is done by attempting to load the string as each type.
    In the cases where the base decoder is not installed a simple Regex match is attempted.

    Args:
        input_string (str): String to classify.

    Returns:
        str: The classified type ("json", "yaml", "toml", "xml", "ini", "env", "unknown")
    """

    try:
        json.loads(input_string)
        return "json"
    except json.JSONDecodeError:
        pass

    try:
        yaml.safe_load(input_string)
        return "yaml"
    except yaml.YAMLError:
        pass

    try:
        toml.loads(input_string)
        return "toml"
    except toml.TOMLDecodeError:
        pass

    if importlib.util.find_spec('xmltodict'):
        import xmltodict
        try:
            xmltodict.parse(input_string, process_namespaces=True)
            return "xml"
        except xmltodict.ParsingInterrupted:
            pass
    elif input_string.startswith("<") and input_string.endswith(">"):
        if re.match(r'<\?xml\s+version\s*=\s*["\']1\.\d["\']', input_string) or re.match(r'<[a-zA-Z]', input_string):
            return "xml"

    config = configparser.ConfigParser()
    if input_string.strip().startswith("["):
        try:
            config.read_string(input_string)
            return "ini"
        except configparser.Error:
            pass

    if importlib.util.find_spec('dotenv'):
        try:
            from dotenv import dotenv_values
            dotenv_values(stream=StringIO(input_string))
            return "env"
        except:
            pass
    elif re.match(r'^\s*[A-Za-z_][A-Za-z0-9_]*\s*=', input_string):
        return "env"

    return "unknown"

def toml_null_stripper(input: Union[dict, list]):
    """
    Remove null valued key-value pairs or list items.

    Args:
        dictionary (dict,list): Input dictionary or list.

    Returns:
        dict: Output dictionary (or list).
    """
    if isinstance(input, dict):
        new_dict = dict()

        for k, v in input.items():
            if isinstance(v, dict):
                v = toml_null_stripper(v)
            if isinstance(v, list):
                v = toml_null_stripper(v)
            if v not in (u"", None, {}):
                new_dict[k] = v

        return new_dict
    elif isinstance(input, list):
        new_list = list()

        for v in input:
            if isinstance(v, dict):
                v = toml_null_stripper(v)
            if isinstance(v, list):
                v = [toml_null_stripper(vv) if (isinstance(vv, dict) or isinstance(vv, list)) else vv for vv in v]
            if v not in (u"", None, {}):
                new_list.append(v)

        return new_list
    else:
        raise TypeError(f"toml_null_stripper can not strip nulls from input type {type(input)}")


def parse_ini(config: configparser.ConfigParser, path_sep: str = None, list_brackets: tuple = None):
    """
    Func to create a dictionary from an initialised config parser and then returns inflated dictionary.

    Args:
        config (ConfigParser): Initialised ConfigParser.
        path_sep (str): For inflating sections from deeply nested structures (default = None).
        list_brackets (tuple): For list indexes, type of bracket (default = None).

    Returns:
        dict:
    """
    _d = {section_name: dict(config[section_name]) for section_name in config.sections()}

    if path_sep is None:
        path_sep = os.getenv("RICKLE_INI_PATH_SEP", ".")

    if list_brackets is None:
        list_brackets = (os.getenv("RICKLE_INI_OPENING_BRACES", "("),
                                                os.getenv("RICKLE_INI_CLOSING_BRACES", ")"))

    __d = dict()
    for k, v in _d.items():
        for kk, vv in v.items():
            __d[f"{k}{path_sep}{kk}"] = vv

    _d = inflate_dict(flat_dict=__d, path_sep=path_sep, list_brackets=list_brackets)
    return _d

def unparse_ini(dictionary: dict, path_sep: str = None, list_brackets: tuple = None) -> configparser.ConfigParser:
    """
    Function to flatten a dictionary and create ConfigParser from the result.

    Args:
        dictionary (dict): Any dictionary.
        path_sep (str): For creating sections from deeply nested structures (default = None).
        list_brackets (tuple): For list indexes, type of bracket (default = None).

    Returns:
        ConfigParser: Config parser with flattened dictionary set.
    """
    flattened_dict = flatten_dict(dictionary=dictionary, path_sep=path_sep, list_brackets=list_brackets)

    ini_dict = defaultdict(dict)
    for k, v in flattened_dict.items():
        splits = k.split(path_sep)
        sect = path_sep.join(splits[:-1])
        sect = path_sep if sect == '' else sect
        ini_dict[sect][splits[-1]] = str(v)

    output_ini = configparser.ConfigParser()
    output_ini.read_dict(ini_dict)

    return output_ini

def flatten_dict(dictionary, path_sep: str = None, list_brackets: tuple = ('(', ')')):
    """
    Flattens a deepl structure python dictionary into a shallow (or 'thin') dictionary of depth 1.

    Notes:
        Dictionary can only contain types str, bool, int, float, dict, list. Any other types won't be expanded upon.

    Args:
        dictionary (dict): Input dictionary.
        path_sep (str): Path separator.
        list_brackets (tuple): Tuple of strings for list index values (default = ('(', ')')).

    Returns:
        dict: Flattened to depth 1.
    """
    def __flatten_dict(d, parent_path: str = None, sep: str = None):

        values = list()
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, dict):
                    value = __flatten_dict(d=v, parent_path=f'{parent_path}{sep}{k}', sep=sep)
                    values.extend(value)
                elif isinstance(v, list):
                    value = __flatten_dict(d=v, parent_path=f'{parent_path}{sep}{k}', sep=sep)
                    values.extend(value)
                else:
                    values.append({f'{parent_path}{sep}{k}': v})
        if isinstance(d, list):
            for i, val in enumerate(d):
                if isinstance(val, dict):
                    value = __flatten_dict(d=val, parent_path=f'{parent_path}{sep}{list_brackets[0]}{i}{list_brackets[1]}', sep=sep)
                    values.extend(value)
                elif isinstance(val, list):
                    value = __flatten_dict(d=val, parent_path=f'{parent_path}{sep}{list_brackets[0]}{i}{list_brackets[1]}', sep=sep)
                    values.extend(value)
                else:
                    values.append({f'{parent_path}{sep}{list_brackets[0]}{i}{list_brackets[1]}': val})
        return values

    list_dicts = __flatten_dict(d=dictionary, parent_path='', sep=path_sep)
    flattened_dict = dict()
    for d in list_dicts:
        for k, v in d.items():
            flattened_dict[k.lstrip(path_sep)] = v
    return flattened_dict


def inflate_dict(flat_dict: dict, path_sep: str = None, list_brackets: tuple = ('(', ')')):
    """
    Does reverse operation of ``flatten_dict`` and inflates a shallow dictionary.

    Args:
        flat_dict (dict): Input dictionary, can be any dict (won't have an effect).
        path_sep (str): Path separator.
        list_brackets (tuple): Tuple of strings for list index values (default = ('(', ')')).

    Returns:
        dict: Inflated dictionary.
    """
    Node = namedtuple('Node', ['key', 'struc_type'])

    def unravel(key, path_sep: str = None, list_brackets: tuple = ('(', ')')):

        if key.startswith(path_sep):
            key = key[1:]
        keys = key.split(path_sep)

        _list = list()
        for k in keys:
            pat = f'\\{list_brackets[0]}(\\d+)\\{list_brackets[1]}'

            m = re.match(pat, k)
            if m:
                _list.append(Node(key=int(m.group(1)), struc_type='list'))
            else:
                _list.append(Node(key=k, struc_type='dict'))

        return _list

    main_d = dict()
    lists = dict()
    dicts = dict()

    for key, value in flat_dict.items():
        d = main_d

        keys = unravel(key, path_sep=path_sep, list_brackets=list_brackets)

        for i, k in enumerate(keys[:-1]):
            if k.struc_type == 'dict':
                if k.key not in d:
                    d[k.key] = list() if keys[i + 1].struc_type == 'list' else dict()
                d = d[k.key]
            if k.struc_type == 'list':

                f = '/'.join([str(p.key) for p in keys[:i + 1]])
                if f in lists:
                    _ = lists[f]
                elif f in dicts:
                    _ = dicts[f]
                else:
                    _ = list() if keys[i + 1].struc_type == 'list' else dict()
                    if isinstance(_, list):
                        lists[f] = _
                    else:
                        dicts[f] = _
                    d.insert(k.key, _)
                d = _

        if isinstance(d, dict):
            d[keys[-1].key] = value
        if isinstance(d, list):
            d.insert(keys[-1].key, value)

    return main_d


class cli_bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Schema:
    """
    Tool for inferring schemas from Python dicts and validating schemas.

    Args:
        input_files (list): List of input file paths (default = None).
        input_directories (list): List of directories (default = None).
        schema (str, dict): The dict definition of schema or path to schema file (default = None).
        output_dir (str): Directory to move output files to (default = None).
        silent (bool): Suppress verbose output (default = None).
        use_json_schema (bool): If installed and is true, the schema will be validated as a JSON schem (default = False).
        include_extended_properties (bool): Whether to include "required", "nullable", etc. (default = True).
    """

    JSON_SCHEMA_STRING = "string"
    JSON_SCHEMA_INTEGER = "integer"
    JSON_SCHEMA_NUMBER = "number"
    JSON_SCHEMA_OBJECT = "object"
    JSON_SCHEMA_ARRAY = "array"
    JSON_SCHEMA_BOOLEAN = "boolean"
    JSON_SCHEMA_NULL = "null"

    JSON_SCHEMA_TYPES = ['string', 'integer', 'number', 'object', 'array', 'boolean', 'null']

    supported_list = [f"{cli_bcolors.OKBLUE}YAML (r/w){cli_bcolors.ENDC}",
                      f"{cli_bcolors.OKBLUE}JSON (r/w){cli_bcolors.ENDC}",
                      f"{cli_bcolors.OKBLUE}TOML (r/w){cli_bcolors.ENDC}"]

    if importlib.util.find_spec('xmltodict'):
        supported_list.append(f"{cli_bcolors.OKBLUE}XML (r/w){cli_bcolors.ENDC}")
    supported = '- ' + '\n- '.join(supported_list)

    supported_output = ['yaml', 'json', 'toml', 'xml']

    def __init__(self,
                 input_files: List[str] = None,
                 input_directories: List[str] = None,
                 schema: Union[str, dict] = None,
                 output_files: List[str] = None,
                 output_dir: str = None,
                 verbose: bool = False,
                 silent: bool = False,
                 default_output_type: str = 'yaml',
                 use_json_schema: bool = False,
                 include_extended_properties: bool = True
                 ):
        self.input_files = input_files
        self.input_directories = input_directories

        if isinstance(schema, str):
            self.schema = Converter.infer_read_file_type(schema)

        else:
            self.schema = schema

        self.output_files = output_files

        self.output_dir = output_dir

        self.verbose = verbose
        self.silent = silent
        if default_output_type.strip().lower() == 'yml':
            default_output_type = 'yaml'
        self.default_output_type = default_output_type.strip().lower()
        self.use_json_schema = use_json_schema
        self.include_extended_properties = include_extended_properties

    def do_generation(self):
        """
        Generates schema files for the given input files.
        """
        if self.input_files is None and self.input_directories is None:
            raise ValueError("Either input_files or input_directories must be defined!")

        if self.input_files is None and not self.input_directories is None:
            self.input_files = list()
            for d in self.input_directories:
                dir_path = Path(d)
                self.input_files.extend(list(dir_path.glob("*.yaml")))
                self.input_files.extend(list(dir_path.glob("*.yml")))
                self.input_files.extend(list(dir_path.glob("*.json")))
                self.input_files.extend(list(dir_path.glob("*.toml")))
                self.input_files.extend(list(dir_path.glob("*.xml")))

        if self.output_files is None:
            self.output_files = list()
            out_dir = f"{self.output_dir}/" if self.output_dir else './'
            for input_file in self.input_files:
                self.output_files.append(f"{out_dir}{os.path.splitext(input_file)[0]}.schema.{self.default_output_type.lower()}")


        zipped = zip(self.input_files, self.output_files)

        for pair in zipped:
            try:
                input_data = Converter.infer_read_file_type(pair[0])
                output_file = Path(pair[1])

                suffix = output_file.suffix.lower() if output_file.suffix else f".{self.default_output_type}"

                schema = Schema.generate_schema_from_obj(input_data,
                                                         include_extended_properties=self.include_extended_properties)

                if suffix == '.yaml':
                    with output_file.open("w") as fout:
                        yaml.dump(schema, fout)

                elif suffix == '.json':
                    with output_file.open("w") as fout:
                        json.dump(schema, fout)

                elif suffix == '.toml':
                    with output_file.open("wb") as fout:
                        tomlw.dump(toml_null_stripper(schema), fout)
                else:
                    raise ValueError(f"Cannot dump to format {suffix}, only supported {Schema.supported_output}")

                if not self.silent:
                    print(f"{cli_bcolors.OKBLUE}{pair[0]}{cli_bcolors.ENDC} -> {cli_bcolors.OKBLUE}{pair[1]}{cli_bcolors.ENDC}")
                continue
            except Exception as exc:
                if not self.silent:
                    print(f"{cli_bcolors.FAIL}{str(exc)}{cli_bcolors.ENDC}")
                continue

    def do_validation(self):
        """
        Validates input files against schema definition.

        Returns:
            list: List of files that did not pass validation.
        """
        failed_validation = list()

        if self.input_files is None and self.input_directories is None:
            raise ValueError("Either input_files or input_directories must be defined!")

        if self.input_files is None and not self.input_directories is None:
            self.input_files = list()
            for d in self.input_directories:
                dir_path = Path(d)
                self.input_files.extend(list(dir_path.glob("*.yaml")))
                self.input_files.extend(list(dir_path.glob("*.yml")))
                self.input_files.extend(list(dir_path.glob("*.json")))
                self.input_files.extend(list(dir_path.glob("*.toml")))
                self.input_files.extend(list(dir_path.glob("*.xml")))

        for file in self.input_files:
            try:
                input_data = Converter.infer_read_file_type(file)

                passed = Schema.schema_validation(obj=input_data, schema=self.schema, no_print=not self.verbose,
                                                  use_json_schema=self.use_json_schema)

                if not passed:
                    failed_validation.append(file)

                if not self.silent:
                    result = f"{cli_bcolors.OKGREEN}OK{cli_bcolors.ENDC}" if passed else f"{cli_bcolors.FAIL}FAIL{cli_bcolors.ENDC}"
                    print(f"{cli_bcolors.OKBLUE}{file}{cli_bcolors.ENDC} -> {result}")
                continue
            except Exception as exc:
                if not self.silent:
                    print(f"{cli_bcolors.FAIL}{str(exc)}{cli_bcolors.ENDC}")
                continue

        if self.output_dir:
            outdir = Path(self.output_dir)
            if not outdir.is_dir():
                outdir.mkdir()

            for f in failed_validation:
                f_path = Path(f)
                f_path.rename(outdir / f_path.name)


        return failed_validation

    @staticmethod
    def _extract_data_types(value: Union[list, dict, str, int, float, bool]):
        if isinstance(value, list):
            schema = list()
            for v in value:
                schema.append(Schema._extract_data_types(v))
            return schema
        if isinstance(value, dict):
            schema = OrderedDict()
            for k, v in value.items():
                schema[k] = Schema._extract_data_types(v)
            return schema
        if isinstance(value, str):
            return str
        if isinstance(value, bool):
            return bool
        if isinstance(value, int):
            return int
        if isinstance(value, float):
            return float


    @staticmethod
    def _data_types_to_schema(value: Union[list, dict, str, int, float, bool, None], include_extended_properties: bool = True):
        if include_extended_properties:
            named_schema = OrderedDict({'type': None, 'required': False, 'nullable': True, 'description': None})
        else:
            named_schema = OrderedDict({'type': None})
        if value == bool:
            named_schema['type'] = Schema.JSON_SCHEMA_BOOLEAN
            return named_schema
        if value == str:
            named_schema['type'] = Schema.JSON_SCHEMA_STRING
            return named_schema
        if value == int:
            named_schema['type'] = Schema.JSON_SCHEMA_INTEGER
            return named_schema
        if value == float:
            named_schema['type'] = Schema.JSON_SCHEMA_NUMBER
            return named_schema
        if value is None:
            named_schema['type'] = Schema.JSON_SCHEMA_NULL
            return named_schema

        if isinstance(value, dict) or isinstance(value, OrderedDict):
            named_schema['type'] = Schema.JSON_SCHEMA_OBJECT
            named_schema['properties'] = OrderedDict()
            for k, v in value.items():
                named_schema['properties'][k] = Schema._data_types_to_schema(v,
                                                            include_extended_properties=include_extended_properties)
            return named_schema

        if isinstance(value, list):
            named_schema['type'] = Schema.JSON_SCHEMA_ARRAY
            if include_extended_properties:
                named_schema['length'] = -1
                named_schema['min'] = -1
                named_schema['max'] = -1

            named_schema['items'] = list()
            list_data_types = set([type(v) if not isinstance(v, type) else v for v in value])

            if len(list_data_types) > 1:
                named_schema['items'].append(Schema._data_types_to_schema(None,
                                                            include_extended_properties=include_extended_properties))
            if len(list_data_types) == 1:
                named_schema['items'].append(Schema._data_types_to_schema(value[0],
                                                            include_extended_properties=include_extended_properties))
            return named_schema

    @staticmethod
    def generate_schema_from_obj(obj, include_extended_properties: bool = True):
        """
        Generate a schema definition from a Python object.

        Args:
            obj: Dict like object.
            include_extended_properties (bool): Whether to include "required", "nullable", etc. (default = True).

        Returns:
            dict: Schema detected from obj.

        """
        rep = Schema._extract_data_types(obj)
        return Schema._data_types_to_schema(rep, include_extended_properties=include_extended_properties)

    @staticmethod
    def schema_validation(obj, schema: dict, path: str = '', no_print: bool = False, use_json_schema: bool = False) -> bool:
        """
        Validates if obj conforms to schema.

        Args:
            obj: The object to check.
            schema (dict): The schema in dict form.
            path (str): The current path of the object tree (default = 'root').
            no_print (bool): If failures should not be printed (default = False).
            use_json_schema (bool): If true and jsonschema is installed, performs JSON schema instead (default = False).

        Returns:
            bool: True if the object conforms.
        """
        _path_sep = os.getenv("RICKLE_PATH_SEP", "/")

        if use_json_schema:
            if importlib.util.find_spec('jsonschema'):
                from jsonschema import validate
                from jsonschema.exceptions import ValidationError

                try:
                    validate(instance=obj, schema=schema)
                    return True
                except ValidationError as exc:
                    if not no_print:
                        print(
                            f"{cli_bcolors.FAIL}{exc.message}{cli_bcolors.ENDC} at {cli_bcolors.WARNING}{_path_sep.join(exc.absolute_path)}{cli_bcolors.ENDC} as per {cli_bcolors.OKBLUE}{_path_sep.join(exc.absolute_schema_path)}{cli_bcolors.ENDC}")
                    return False
            else:
                raise ImportError('Could not find package "jsonschema"!')

        if not 'type' in schema.keys():
            raise ValueError(f'No type defined in {str(schema)}!')

        def _check_type(object_value, schema_info, is_nullable):

            if not 'type' in schema_info.keys():
                raise ValueError(f'No type defined in {str(schema_info)}!')
            schema_type = schema_info['type'].lower().strip()
            object_type = type(object_value).__name__
            object_type_matches = False

            if schema_type == 'regex':
                pattern = schema_info['pattern']
                match = re.match(pattern=pattern, string=object_value)
                object_type_matches = match is not None
            if importlib.util.find_spec('pyvalidator'):
                if schema_type == 'regex-pattern':
                    from pyvalidator import is_regex

                    object_type_matches = is_regex(object_value)
                if schema_type == 'ip-address':
                    from pyvalidator import is_ip
                    ver = schema_info.get('version', None)

                    object_type_matches = is_ip(object_value, version=ver)
                if schema_type == 'port-number':
                    from pyvalidator import is_port
                    object_type_matches = is_port(object_value)
                if schema_type == 'fqdn':
                    from pyvalidator import is_fqdn
                    options = {
                        'require_tld': schema_info.get('require_tld', True),
                        'allow_underscores': schema_info.get('allow_underscores', False),
                        'allow_trailing_dot': schema_info.get('allow_trailing_dot', False),
                        'allow_numeric_tld': schema_info.get('allow_numeric_tld', False),
                        'allow_wildcard': schema_info.get('allow_wildcard', False),
                    }

                    object_type_matches = is_fqdn(object_value, options=options)
                if schema_type == 'url':
                    from pyvalidator import is_url
                    options = {
                        'no_scheme': schema_info.get('no_scheme', False),
                        'with_no_path': schema_info.get('with_no_path', False),
                        'insensitive': schema_info.get('insensitive', True),
                        'top_level_domains': schema_info.get('top_level_domains', list()),
                        'allow_wildcard': schema_info.get('allow_wildcard', list()),
                    }

                    object_type_matches = is_url(object_value, options=options)
                if schema_type == 'mac-address':
                    from pyvalidator import is_mac_address
                    options = {
                        'no_separators': schema_info.get('no_separators', False),
                        'eui': schema_info.get('eui', None),
                    }

                    object_type_matches = is_mac_address(object_value, options=options)
                if schema_type == 'pyval-number':
                    from pyvalidator import is_number
                    object_type_matches = is_number(object_value)
                if schema_type == 'prime-number':
                    from pyvalidator import is_prime
                    object_type_matches = is_prime(object_value)
                if schema_type == 'hex':
                    from pyvalidator import is_hexadecimal
                    object_type_matches = is_hexadecimal(object_value)
                if schema_type == 'base64':
                    from pyvalidator import is_base64
                    options = {
                        'url_safe': schema_info.get('url_safe', False),
                    }

                    object_type_matches = is_base64(object_value, options=options)
                if schema_type == 'ean':
                    from pyvalidator import is_ean
                    object_type_matches = is_ean(object_value)
                if schema_type == 'colour-hex':
                    match = re.match(pattern=r'^#(?:[0-9a-fA-F]{3,4}){1,2}$',
                                     string=object_value)
                    object_type_matches = match is not None
                if schema_type == 'colour-rgb':
                    from pyvalidator import is_rgb_color

                    object_type_matches = is_rgb_color(object_value,
                                                       include_percent_values=schema_info.get('include_percent_values',
                                                                                              True))
                if schema_type == 'email':
                    from pyvalidator import is_email
                    options = {
                        'allow_display_name': schema_info.get('allow_display_name', False),
                        'require_display_name': schema_info.get('require_display_name', False),
                        'allow_utf8_local_part': schema_info.get('allow_utf8_local_part', True),
                        'require_tld': schema_info.get('require_tld', True),
                        'allow_ip_domain': schema_info.get('allow_ip_domain', False),
                        'domain_specific_validation': schema_info.get('domain_specific_validation', False),
                        'ignore_max_length': schema_info.get('ignore_max_length', False),
                        'blacklisted_chars': schema_info.get('blacklisted_chars', ''),
                        'host_blacklist': schema_info.get('host_blacklist', list()),
                    }

                    object_type_matches = is_email(object_value, options=options)
                if schema_type == 'phone':
                    from pyvalidator import is_mobile_number
                    options = {
                        'strict_mode': schema_info.get('strict_mode', True),
                    }
                    object_type_matches = is_mobile_number(object_value, locale=schema_info.get('locale', 'any'),
                                                           options=options)
                if schema_type == 'iso-6391' or schema_type == 'iso-lang':
                    from pyvalidator import is_iso6391

                    object_type_matches = is_iso6391(object_value)
                if schema_type == 'iso-31661' or schema_type == 'iso-country':
                    from pyvalidator import is_ISO31661_alpha2

                    object_type_matches = is_ISO31661_alpha2(object_value)

                if schema_type == 'locale':
                    from pyvalidator.is_mobile_number import mobile_number_patterns

                    object_type_matches = object_value in mobile_number_patterns.keys()
                if schema_type == 'lat-long':
                    from pyvalidator import is_lat_long
                    options = {
                        'check_dms': schema_info.get('check_dms', False),
                    }

                    object_type_matches = is_lat_long(object_value, options=options)
                if schema_type == 'date':
                    from pyvalidator import is_date
                    options = {
                        'format': schema_info.get('format', 'YYYY/MM/DD'),
                        'strict_mode': schema_info.get('strict_mode', False),
                        'delimiters': schema_info.get('delimiters', ['/', '-']),
                    }

                    object_type_matches = is_date(object_value, options=options)
                if schema_type == 'uuid':
                    from pyvalidator import is_uuid
                    object_type_matches = is_uuid(object_value, version=schema_info.get('version', 'all'))
                if schema_type == 'sem-ver':
                    from pyvalidator import is_semantic_version
                    object_type_matches = is_semantic_version(object_value)
                if schema_type == 'mime-type':
                    from pyvalidator import is_mime_type
                    object_type_matches = is_mime_type(object_value)
                if schema_type == 'cloud-aws-region':
                    match = re.match(
                        pattern=r'^(af|il|ap|ca|eu|me|sa|us|cn|us-gov|us-iso|us-isob)-(central|north|(north(?:east|west))|south|south(?:east|west)|east|west)-\d{1}$',
                        string=object_value)
                    object_type_matches = match is not None
                if schema_type == 'cloud-aws-arn':
                    from pyvalidator import is_aws_arn
                    object_type_matches = is_aws_arn(object_value, resource=schema_info.get('resource', 'any'))

                if schema_type == 'bic' or schema_type == 'swift':
                    from pyvalidator import is_bic
                    object_type_matches = is_bic(object_value)
                if schema_type == 'credit-card':
                    from pyvalidator import is_credit_card
                    object_type_matches = is_credit_card(object_value)
                if schema_type == 'iban':
                    from pyvalidator import is_iban
                    options = {
                        'insensitive': schema_info.get('insensitive', False),
                    }
                    object_type_matches = is_iban(object_value, country_code=schema_info.get('country_code', None),
                                                  options=options)
                if schema_type == 'ethereum-address' or schema_type == 'eth-address':
                    from pyvalidator import is_ethereum_address

                    object_type_matches = is_ethereum_address(object_value)
                if schema_type == 'bitcoin-address' or schema_type == 'btc-address':
                    from pyvalidator import is_btc_address

                    object_type_matches = is_btc_address(object_value)
                if schema_type == 'magnet-uri':
                    from pyvalidator import is_magnet_uri

                    object_type_matches = is_magnet_uri(object_value)
                if schema_type == 'hash':
                    from pyvalidator import is_hash

                    object_type_matches = is_hash(object_value, algorithm=schema_info.get('algorithm', None))

            if schema_type in Schema.JSON_SCHEMA_TYPES:
                object_type_name = get_native_type_name(python_type_name=object_type, format_type='json')
                if object_type_name == "integer" and schema_type == "number":
                    object_type_matches = True
                else:
                    object_type_matches = object_type_name == schema_type

            null_no_type = is_nullable & ((schema_type == 'any') | (object_type == 'NoneType'))
            null_with_type = is_nullable & (schema_type != 'any') & object_type_matches
            non_null = (is_nullable is False) & ((schema_type == 'any') | object_type_matches)

            if not (null_no_type or null_with_type or non_null):
                if not no_print:
                    print(
                        f"Type '{k}' == {cli_bcolors.FAIL}'{get_native_type_name(object_type, 'json')}'{cli_bcolors.ENDC},\n Required type {cli_bcolors.OKBLUE}'{schema_type}'{cli_bcolors.ENDC} (per schema {v}),\n In {obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                return False

            return True

        new_path = path
        if schema['type'] == Schema.JSON_SCHEMA_OBJECT:
            for k, v in schema['properties'].items():
                new_path = f"{new_path}{_path_sep}{k}"
                req = v.get('required', False)
                nullable = v.get('nullable', False)
                present = k in obj.keys()
                if not present:
                    if req:
                        if not no_print:
                            print(f"Required {cli_bcolors.FAIL}'{k}'{cli_bcolors.ENDC} (per schema {v}),\n In {obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                        return False
                    else:
                        new_path = path
                        continue

                type_passed = _check_type(object_value=obj[k], schema_info=v, is_nullable=nullable)
                if not type_passed:
                    return False


                if v['type'] in [Schema.JSON_SCHEMA_OBJECT, Schema.JSON_SCHEMA_ARRAY]:
                    if not Schema.schema_validation(obj[k], v, path=new_path, no_print=no_print):
                        return False
                new_path = path
            return True
        if schema['type'] == Schema.JSON_SCHEMA_ARRAY:

            nullable = schema.get('nullable', False)

            if nullable and obj is None:
                return True

            length = schema.get('length', -1)
            min_ = schema.get('min', -1)
            max_ = schema.get('max', -1)
            obj_length = len(obj)

            if length > -1 and obj_length != length:
                if not no_print:
                    print(
                    f"Length '{obj}' == {cli_bcolors.FAIL}{obj_length}{cli_bcolors.ENDC},\n Required length {cli_bcolors.OKBLUE}{length}{cli_bcolors.ENDC} (per schema {schema['items']}),\n In {obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                return False

            if min_ > -1 and obj_length < min_:
                if not no_print:
                    print(
                    f"Length '{obj}' == {cli_bcolors.FAIL}{obj_length}{cli_bcolors.ENDC},\n Required minimum length {cli_bcolors.OKBLUE}{min_}{cli_bcolors.ENDC} (per schema {schema['items']}),\n In {obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                return False

            if max_ > -1 and obj_length > max_:
                if not no_print:
                    print(
                    f"Length '{obj}' == {cli_bcolors.FAIL}{obj_length}{cli_bcolors.ENDC},\n Required maximum length {cli_bcolors.OKBLUE}{max_}{cli_bcolors.ENDC} (per schema {schema['items']}),\n In {obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                return False


            if 'items' in schema.keys():
                schema_len = len(schema['items'])

                if schema_len > 0:
                    single_type = schema['items'][0]

                    for i in range(obj_length):
                        new_path = f"{new_path}{_path_sep}[{i}]"
                        o = obj[i]
                        elem_type = get_native_type_name(type(o).__name__, 'json')
                        if (single_type['type'] != 'any' and elem_type != single_type['type']) or (elem_type == 'integer' and single_type['type'] == 'number'):
                            if not no_print:
                                print(
                                f"Type '{o}' == {cli_bcolors.FAIL}'{elem_type}'{cli_bcolors.ENDC},\n Required type {cli_bcolors.OKBLUE}'{single_type['type']}'{cli_bcolors.ENDC} (per schema {single_type}),\n In {o},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                            return False
                        if single_type['type'] in [Schema.JSON_SCHEMA_OBJECT, Schema.JSON_SCHEMA_ARRAY]:
                            if not Schema.schema_validation(o, single_type, path=new_path, no_print=no_print):
                                return False
                        new_path = path
            return True

class Converter:
    """
    Tool for converting between YAML and JSON (and TOML, XML, INI, .ENV), mainly to be used in CLI.

    Args:
        input_files (list): List of input file paths (default = None).
        input_directories (list): List of directories (default = None).
        output_files (list): List of output file paths (default = None).
        default_output_type (str): Default type to convert to if output files are not provided (default = 'yaml').
        silent (bool): Suppress verbose output (default = None).
    """

    supported_list = [f"{cli_bcolors.OKBLUE}YAML (r/w){cli_bcolors.ENDC}",
                      f"{cli_bcolors.OKBLUE}JSON (r/w){cli_bcolors.ENDC}",
                      f"{cli_bcolors.OKBLUE}TOML (r/w){cli_bcolors.ENDC}",
                      f"{cli_bcolors.OKBLUE}INI (r/w){cli_bcolors.ENDC}"]

    if importlib.util.find_spec('xmltodict'):
        supported_list.append(f"{cli_bcolors.OKBLUE}XML (r/w){cli_bcolors.ENDC}")
    if importlib.util.find_spec('dotenv'):
        supported_list.append(f"{cli_bcolors.OKBLUE}ENV ({cli_bcolors.WARNING}r{cli_bcolors.OKBLUE}){cli_bcolors.ENDC}")
    supported = '- ' + '\n- '.join(supported_list)

    supported_output = ['yaml', 'json', 'toml', 'xml', 'ini']
    supported_input = ['yaml', 'json', 'toml', 'xml', 'ini', 'env']

    def __init__(self,
                 input_files: List[str] = None,
                 input_directory: str = None,
                 output_files: List[str] = None,
                 default_output_type: str = 'yaml',
                 verbose: bool = False,
                 ):
        self.input_files = input_files
        self.input_directory = input_directory
        self.output_files = output_files if output_files else list()

        if not default_output_type.strip().lower() in Converter.supported_output:
            raise ValueError(f"Output type must be string of value {','.join(Converter.supported_output)}")

        self.default_output_type = default_output_type
        self.verbose = verbose


    @staticmethod
    def convert_string(input_string: str, output_type: str, input_type: str = None):
        """
        Convert a string from one format to another. Supported input types:

        Args:
            input_string (str): Data in input_type format.
            output_type (str): Output type, either ['yaml', 'json', 'toml', 'xml'].
            input_type (str): Input type, either ['yaml', 'json', 'toml', 'xml', 'env'] (default = None).

        Notes:
            Output can not be of type .ENV .
            If no input type is given, the type is inferred.

        Returns:
            str: Converted string
        """

        output_type = output_type.strip().lower()

        path_sep = os.getenv("RICKLE_INI_PATH_SEP", ".")
        list_brackets = (os.getenv("RICKLE_INI_OPENING_BRACES", "("), os.getenv("RICKLE_INI_CLOSING_BRACES", ")"))

        if input_type is None:
            d = Converter.infer_read_string_type(input_string)
        else:
            input_type = input_type.strip().lower()
            if input_type == 'yaml':
                d = yaml.safe_load(input_string)
            elif input_type == 'json':
                d = json.loads(input_string)
            elif input_type == 'toml':
                d = toml.loads(input_string)
            elif input_type == 'xml':
                if importlib.util.find_spec('xmltodict'):
                    import xmltodict
                    d = xmltodict.parse(input_string, process_namespaces=True)
                else:
                    raise ValueError('Cannot parse XML without required package xmltodict')
            elif input_type == 'ini':
                config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
                config.read_string(input_string)

                d = parse_ini(config=config, path_sep=path_sep, list_brackets=list_brackets)
            elif input_type == 'env':
                if importlib.util.find_spec('dotenv'):
                    from dotenv import dotenv_values

                    d = dotenv_values(stream=StringIO(input_string))
                else:
                    raise ValueError('Cannot parse .ENV without required package dotenv')
            else:
                raise ValueError(f"Input type must be string of value {','.join(Converter.supported_input)}")

        if output_type == 'yaml':
            return yaml.safe_dump(d)
        elif output_type == 'json':
            return json.dumps(d)
        elif output_type == 'toml':
            return tomlw.dumps(toml_null_stripper(d))
        elif output_type == 'xml':
            if importlib.util.find_spec('xmltodict'):
                import xmltodict
                return xmltodict.unparse(d)
            else:
                raise ValueError('Cannot parse XML without required package xmltodict')
        elif output_type == 'ini':

            output_ini = unparse_ini(dictionary=d, path_sep=path_sep, list_brackets=list_brackets)

            out = StringIO()
            output_ini.write(out)
            out.seek(0)

            return out.read()
        elif output_type == 'env':
            raise ValueError('Conversion to .ENV is unsupported')
        else:
            raise ValueError(f"Output type must be string of value {','.join(Converter.supported_output)}")

    @staticmethod
    def infer_read_string_type(string: str):
        """
        Brute force try every possible loading.

        Args:
            string (str): Input.

        Returns:
            dict: Loaded.
        """
        try:
            return json.loads(string)
        except:
            pass

        try:
            return yaml.safe_load(string)
        except:
            pass

        try:
            return toml.loads(string)
        except:
            pass

        try:
            if importlib.util.find_spec('xmltodict'):
                import xmltodict

                return xmltodict.parse(string, process_namespaces=True)
        except:
            pass

        try:
            config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            config.read_string(string=string)
            path_sep = os.getenv("RICKLE_INI_PATH_SEP", ".")
            list_brackets = (os.getenv("RICKLE_INI_OPENING_BRACES", "("), os.getenv("RICKLE_INI_CLOSING_BRACES", ")"))

            return parse_ini(config=config, path_sep=path_sep, list_brackets=list_brackets)
        except:
            pass

        try:
            if importlib.util.find_spec('dotenv'):
                from dotenv import dotenv_values

                return dotenv_values(stream=StringIO(string))
        except:
            pass

        raise ValueError(f"Input type could not be inferred!")


    @staticmethod
    def infer_read_file_type(file_path: str):
        """
        Infer the file type and return loaded contents. By default, the type is inferred from the suffix of the
        file path. Thus, `file.yaml` will be read as a YAML file. If the file extension is not known, the file will be
        read and tried to be loaded as both types.

        Raises:
             ValueError: If the type could not be inferred.

        Args:
            file_path (str): Input file path to read.

        Returns:
            dict: Loaded YAML (or JSON).
        """

        input_file = Path(file_path)

        suffix = input_file.suffix.lower() if input_file.suffix else None

        if suffix == '.json':
            with input_file.open("r") as fin:
                return json.load(fin)

        if suffix in ['.yaml', '.yml']:
            with input_file.open("r") as fin:
                return yaml.safe_load(fin)

        if suffix == '.toml':
            with input_file.open("rb") as fin:
                return toml.load(fin)

        if suffix == '.ini':
            config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            with input_file.open("r") as fin:
                config.read_file(fin)

            path_sep = os.getenv("RICKLE_INI_PATH_SEP", ".")
            list_brackets = (os.getenv("RICKLE_INI_OPENING_BRACES", "("), os.getenv("RICKLE_INI_CLOSING_BRACES", ")"))

            return parse_ini(config=config, path_sep=path_sep, list_brackets=list_brackets)


        if suffix == '.xml':
            if importlib.util.find_spec('xmltodict'):
                import xmltodict

                with input_file.open("rb") as fin:
                    return xmltodict.parse(fin, process_namespaces=True)

        if input_file.stem.lower() == '.env' or suffix == '.env':
            if importlib.util.find_spec('dotenv'):
                from dotenv import dotenv_values

                return dotenv_values(dotenv_path=str(input_file.absolute()))

        try:
            with input_file.open("r") as fin:
                return json.load(fin)
        except:
            pass

        try:
            with input_file.open("r") as fin:
                return yaml.safe_load(fin)
        except:
            pass

        try:
            with input_file.open("rb") as fin:
                return toml.load(fin)
        except:
            pass

        try:
            if importlib.util.find_spec('xmltodict'):
                import xmltodict

                with input_file.open("rb") as fin:
                    return xmltodict.parse(fin, process_namespaces=True)
        except:
            pass

        try:
            config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            with input_file.open("r") as fin:
                config.read_file(fin)
            path_sep = os.getenv("RICKLE_INI_PATH_SEP", ".")
            list_brackets = (os.getenv("RICKLE_INI_OPENING_BRACES", "("), os.getenv("RICKLE_INI_CLOSING_BRACES", ")"))

            return parse_ini(config=config, path_sep=path_sep, list_brackets=list_brackets)
        except:
            pass

        try:
            if importlib.util.find_spec('dotenv'):
                from dotenv import dotenv_values

                return dotenv_values(dotenv_path=str(input_file.absolute()))
        except:
            pass

        raise ValueError(f"Input file {input_file.name} could not be inferred")

    def do_convert(self):
        """
        Converts all input files to output type(s).
        """
        if self.input_files is None and self.input_directory is None:
            raise ValueError("Either input_files or input_directories must be defined!")

        if self.input_files is None and not self.input_directory is None:
            # set output to none as it should not be defined in this scenario
            self.output_files = list()
            self.input_files = list()

            dir_path = Path(self.input_directory)

            known_extensions = ['yaml', 'yml', 'json', 'toml', 'ini']
            if importlib.util.find_spec('xmltodict'):
                known_extensions.append('xml')
            if importlib.util.find_spec('dotenv'):
                known_extensions.append('env')

            for ext in known_extensions:
                self.input_files.extend(list(dir_path.glob(f"*.{ext}")))


        if len(self.output_files) < 1:
            for input_file in self.input_files:
                self.output_files.append(f"{os.path.splitext(input_file)[0]}.{self.default_output_type.lower()}")


        zipped = zip(self.input_files, self.output_files)

        for pair in zipped:
            try:
                input_data = Converter.infer_read_file_type(pair[0])
                output_file = Path(pair[1])

                suffix = output_file.suffix.lower() if output_file.suffix else f".{self.default_output_type}"

                if suffix == '.yaml':
                    with output_file.open("w") as fout:
                        yaml.safe_dump(input_data, fout)

                if suffix == '.json':
                    with output_file.open("w") as fout:
                        json.dump(input_data, fout)

                if suffix == '.toml':
                    with output_file.open("wb") as fout:
                        tomlw.dump(toml_null_stripper(input_data), fout)

                if suffix == '.xml':
                    if importlib.util.find_spec('xmltodict'):
                        import xmltodict

                        with output_file.open("wb") as fout:
                            xmltodict.unparse(input_data, fout)
                    else:
                        raise ImportError("Missing 'xmltodict' dependency")

                if suffix == '.ini':
                    path_sep = os.getenv("RICKLE_INI_PATH_SEP", ".")
                    list_brackets = (
                            os.getenv("RICKLE_INI_OPENING_BRACES", "("), os.getenv("RICKLE_INI_CLOSING_BRACES", ")")
                    )
                    output_ini = unparse_ini(dictionary=input_data, path_sep=path_sep, list_brackets=list_brackets)

                    with output_file.open("w") as fout:
                        output_ini.write(fout)

                if self.verbose:
                    print(f"{cli_bcolors.OKBLUE}{pair[0]}{cli_bcolors.ENDC} -> {cli_bcolors.OKBLUE}{pair[1]}{cli_bcolors.ENDC}")
                continue
            except Exception as exc:
                if self.verbose:
                    print(f"{cli_bcolors.FAIL}{str(exc)}{cli_bcolors.ENDC}")
                continue