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
        - integer: Properties include ``min`` and ``max``. Defaults to 0 and 256.
        - number: Properties include ``min`` and ``max``. Defaults to 0 and 256.
        - string: Properties include ``chars`` and ``length``. Defaults to ASCII chars and 10.
        - enum: Properties include ``values``.  Defaults to ASCII uppercase chars.
        - array: Properties include ``values`` and ``length``.  Defaults to 'integer' and 10.
            ``values`` can be a string of ``value_type``.
        - object: Properties include ``keys``, ``values``, ``min``, and ``max``.
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

def convert_string(input_string: str, output_type: str, input_type: str = None):
    """
    Convert a string from one format to another.

    Notes:
        any -> YAML, JSON, TOML, XML, INI.

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
        d = infer_read_string_type(input_string)
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
            raise ValueError(f"Input type must be string of value YAML, JSON, TOML, XML, INI, ENV")

    if output_type == 'yaml':
        return yaml.safe_dump(d, sort_keys=False)
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


class cli_bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
