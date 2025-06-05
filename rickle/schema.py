import importlib
import json
import os
import re
from io import TextIOWrapper, BytesIO
from pathlib import Path
from typing import Union

import yaml
import tomli_w as tomlw

from rickle.tools import infer_read_file_type, infer_read_string_type, cli_bcolors, get_native_type_name, \
    toml_null_stripper

JSON_SCHEMA_STRING = "string"
JSON_SCHEMA_INTEGER = "integer"
JSON_SCHEMA_NUMBER = "number"
JSON_SCHEMA_OBJECT = "object"
JSON_SCHEMA_ARRAY = "array"
JSON_SCHEMA_BOOLEAN = "boolean"
JSON_SCHEMA_NULL = "null"
JSON_SCHEMA_TYPES = ['string', 'integer', 'number', 'object', 'array', 'boolean', 'null']

def extract_data_types(value: Union[list, dict, str, int, float, bool]):
    if isinstance(value, list):
        schema = list()
        for v in value:
            schema.append(extract_data_types(v))
        return schema
    if isinstance(value, dict):
        schema = dict()
        for k, v in value.items():
            schema[k] = extract_data_types(v)
        return schema
    if isinstance(value, str):
        return str
    if isinstance(value, bool):
        return bool
    if isinstance(value, int):
        return int
    if isinstance(value, float):
        return float

def data_types_to_schema(value: Union[list, dict, str, int, float, bool, None], include_extended_properties: bool = True):
    if include_extended_properties:
        named_schema = dict({'type': None, 'required': False, 'nullable': True, 'description': None})
    else:
        named_schema = dict({'type': None})
    if value == bool:
        named_schema['type'] = JSON_SCHEMA_BOOLEAN
        return named_schema
    if value == str:
        named_schema['type'] = JSON_SCHEMA_STRING
        return named_schema
    if value == int:
        named_schema['type'] = JSON_SCHEMA_INTEGER
        return named_schema
    if value == float:
        named_schema['type'] = JSON_SCHEMA_NUMBER
        return named_schema
    if value is None:
        named_schema['type'] = JSON_SCHEMA_NULL
        return named_schema

    if isinstance(value, dict):
        named_schema['type'] = JSON_SCHEMA_OBJECT
        named_schema['properties'] = dict()
        for k, v in value.items():
            named_schema['properties'][k] = data_types_to_schema(v,
                                                                 include_extended_properties=include_extended_properties)
        return named_schema

    if isinstance(value, list):
        named_schema['type'] = JSON_SCHEMA_ARRAY
        if include_extended_properties:
            named_schema['length'] = -1
            named_schema['min'] = -1
            named_schema['max'] = -1

        named_schema['items'] = list()
        list_data_types = set([type(v) if not isinstance(v, type) else v for v in value])

        if len(list_data_types) > 1:
            named_schema['items'].append(data_types_to_schema(None,
                                                        include_extended_properties=include_extended_properties))
        if len(list_data_types) == 1:
            named_schema['items'].append(data_types_to_schema(value[0],
                                                        include_extended_properties=include_extended_properties))
        return named_schema

def validate_files(schema, input_files, output_dir, use_json_schema, verbose_print, silent=False):
    """
    Validates input files against schema definition.

    Returns:
        list: List of files that did not pass validation.
    """
    failed_validation = list()

    for file in input_files:
        try:
            passed = schema.validate(obj=file, use_json_schema=use_json_schema, verbose_print=verbose_print)

            if not passed:
                failed_validation.append(file)

            if not silent:
                result = f"{cli_bcolors.OKGREEN}OK{cli_bcolors.ENDC}" if passed else f"{cli_bcolors.FAIL}FAIL{cli_bcolors.ENDC}"
                print(f"{cli_bcolors.OKBLUE}{file}{cli_bcolors.ENDC} -> {result}")
            continue
        except Exception as exc:
            if verbose_print:
                print(f"{cli_bcolors.FAIL}{str(exc)}{cli_bcolors.ENDC}")
            continue

    if output_dir:
        outdir = Path(output_dir)
        if not outdir.is_dir():
            outdir.mkdir()

        for f in failed_validation:
            f_path = Path(f)
            f_path.rename(outdir / f_path.name)


    return failed_validation

class Schema:
    """
    Class to load schema and then validate objects against.

    Args:
        schema (str, dict): Either object or string or empty when generating new (default = None).

    """

    def __init__(self, schema: Union[str, dict] = None):

        if schema is None:
            self.schema = dict()
        elif isinstance(schema, str):
            if Path(schema).is_file():
                _schema = infer_read_file_type(schema)
            else:
                _schema = infer_read_string_type(schema)

            self.schema = _schema
        elif isinstance(schema, dict):
            self.schema = schema
        else:
            raise TypeError("Expected str or dict schema input!")

    def to_yaml(self, output: Union[str, TextIOWrapper] = None, encoding: str = 'utf-8'):
        """
        Does a self dump to a YAML file or returns as string.

        Args:
            output (str, TextIOWrapper): File path or stream (default = None).
            encoding (str): Output stream encoding (default = 'utf-8').

        """

        if output:
            if isinstance(output, TextIOWrapper):
                yaml.safe_dump(self.schema, stream=output, encoding=encoding, sort_keys=False)
            elif isinstance(output, str):
                with open(output, 'w', encoding=encoding) as fs:
                    yaml.safe_dump(self.schema, fs, sort_keys=False)
        else:
            return yaml.safe_dump(self.schema, stream=None, encoding=encoding, sort_keys=False).decode(encoding)

    def to_json(self, output: Union[str, TextIOWrapper] = None, encoding: str = 'utf-8'):
        """
        Does a self dump to a JSON file or returns as string.

        Args:
            output (str, TextIOWrapper): File path or stream (default = None).
            encoding (str): Output stream encoding (default = 'utf-8').

        """

        if output:
            if isinstance(output, TextIOWrapper):
                json.dump(self.schema, output)
            elif isinstance(output, str):
                with open(output, 'w', encoding=encoding) as fs:
                    json.dump(self.schema, fs)
        else:
            return json.dumps(self.schema)

    def to_toml(self, output: Union[str, BytesIO] = None, encoding: str = 'utf-8'):
        """
        Does a self dump to a TOML file or returns as string.

        Args:
            output (str, BytesIO): File path or stream (default = None).
            encoding (str): Output stream encoding (default = 'utf-8').

        """
        schema = toml_null_stripper(self.schema)

        if output:
            if isinstance(output, BytesIO):
                tomlw.dump(schema, output)
            elif isinstance(output, str):
                with open(output, 'wb', encoding=encoding) as fs:
                    tomlw.dump(schema, fs)
        else:
            return tomlw.dumps(schema)

    def to_xml(self, output: Union[str, BytesIO] = None, encoding: str = 'utf-8'):
        """
        Does a self dump to a XML file or returns as string.

        Args:
            output (str, BytesIO): File path or stream (default = None).
            encoding (str): Output stream encoding (default = 'utf-8').

        """
        if importlib.util.find_spec('xmltodict'):
            import xmltodict

            if len(self.schema.keys()) > 1:
                schema = {'rsf_schema' : self.schema}
            else:
                schema = self.schema

            if output:
                if isinstance(output, BytesIO):
                    xmltodict.unparse(input_dict=schema, output=output, encoding=encoding, pretty=True)
                elif isinstance(output, str):
                    with open(output, 'wb', encoding=encoding) as fs:
                        xmltodict.unparse(input_dict=schema, output=fs, encoding=encoding, pretty=True)
            else:
                return xmltodict.unparse(input_dict=schema, encoding=encoding, pretty=True)
        else:
            raise ModuleNotFoundError("Missing 'xmltodict' package!")

    @classmethod
    def generate_from_obj(cls, obj, include_extended_properties: bool = True):
        """
        Generate a schema definition from a Python object.

        Args:
            obj: Dict like object.
            include_extended_properties (bool): Whether to include "required", "nullable", etc. (default = True).

        Returns:
            Schema: Schema with generated definition.

        """
        if isinstance(obj, str):
            if Path(obj).is_file():
                obj = infer_read_file_type(obj)
            else:
                obj = infer_read_string_type(obj)
        rep = extract_data_types(obj)

        return cls(data_types_to_schema(rep, include_extended_properties=include_extended_properties))

    def validate(self, obj: Union[str, dict], use_json_schema: bool = False, verbose_print: bool = False):
        """
        Validate an object against this schema.

        Args:
            obj (dict): Object to validate against schema.
            use_json_schema (bool): Use JSON Schema to validate (default = False).
            verbose_print (bool): Print errors to stdout (default = False).

        Returns:
            bool: Whether validation passed or not.
        """
        _path_sep = os.getenv("RICKLE_PATH_SEP", "/")

        if isinstance(obj, str):
            if Path(obj).is_file():
                obj = infer_read_file_type(obj)
            else:
                obj = infer_read_string_type(obj)


        if use_json_schema:
            if importlib.util.find_spec('jsonschema'):
                from jsonschema import validate
                from jsonschema.exceptions import ValidationError

                try:
                    validate(instance=obj, schema=self.schema)
                    return True
                except ValidationError as exc:
                    if verbose_print:
                        print(
                            f"{cli_bcolors.FAIL}{exc.message}{cli_bcolors.ENDC} at {cli_bcolors.WARNING}{_path_sep.join(exc.absolute_path)}{cli_bcolors.ENDC} as per {cli_bcolors.OKBLUE}{_path_sep.join(exc.absolute_schema_path)}{cli_bcolors.ENDC}")
                    return False
            else:
                raise ImportError('Could not find package "jsonschema"!')

        def schema_validation(_obj, schema: dict, path: str = ''):

            _path_sep = os.getenv("RICKLE_PATH_SEP", "/")

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
                                                           include_percent_values=schema_info.get(
                                                               'include_percent_values',
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

                if schema_type in JSON_SCHEMA_TYPES:
                    object_type_name = get_native_type_name(python_type_name=object_type, format_type='json')
                    if object_type_name == "integer" and schema_type == "number":
                        object_type_matches = True
                    else:
                        object_type_matches = object_type_name == schema_type

                null_no_type = is_nullable & ((schema_type == 'any') | (object_type == 'NoneType'))
                null_with_type = is_nullable & (schema_type != 'any') & object_type_matches
                non_null = (is_nullable is False) & ((schema_type == 'any') | object_type_matches)

                if not (null_no_type or null_with_type or non_null):
                    if verbose_print:
                        print(
                            f"Type '{k}' == {cli_bcolors.FAIL}'{get_native_type_name(object_type, 'json')}'{cli_bcolors.ENDC},\n Required type {cli_bcolors.OKBLUE}'{schema_type}'{cli_bcolors.ENDC} (per schema {v}),\n In {_obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                    return False

                return True

            new_path = path
            if schema['type'] == JSON_SCHEMA_OBJECT:
                for k, v in schema['properties'].items():
                    new_path = f"{new_path}{_path_sep}{k}"
                    req = v.get('required', False)
                    nullable = v.get('nullable', False)
                    present = k in _obj.keys()
                    if not present:
                        if req:
                            if verbose_print:
                                print(
                                    f"Required {cli_bcolors.FAIL}'{k}'{cli_bcolors.ENDC} (per schema {v}),\n In {_obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                            return False
                        else:
                            new_path = path
                            continue

                    type_passed = _check_type(object_value=_obj[k], schema_info=v, is_nullable=nullable)
                    if not type_passed:
                        return False

                    if v['type'] in [JSON_SCHEMA_OBJECT, JSON_SCHEMA_ARRAY]:
                        if not schema_validation(_obj[k], v, path=new_path):
                            return False
                    new_path = path
                return True
            if schema['type'] == JSON_SCHEMA_ARRAY:

                nullable = schema.get('nullable', False)

                if nullable and _obj is None:
                    return True

                length = schema.get('length', -1)
                min_ = schema.get('min', -1)
                max_ = schema.get('max', -1)
                obj_length = len(_obj)

                if length > -1 and obj_length != length:
                    if verbose_print:
                        print(
                            f"Length '{_obj}' == {cli_bcolors.FAIL}{obj_length}{cli_bcolors.ENDC},\n Required length {cli_bcolors.OKBLUE}{length}{cli_bcolors.ENDC} (per schema {schema['items']}),\n In {_obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                    return False

                if min_ > -1 and obj_length < min_:
                    if verbose_print:
                        print(
                            f"Length '{_obj}' == {cli_bcolors.FAIL}{obj_length}{cli_bcolors.ENDC},\n Required minimum length {cli_bcolors.OKBLUE}{min_}{cli_bcolors.ENDC} (per schema {schema['items']}),\n In {_obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                    return False

                if max_ > -1 and obj_length > max_:
                    if verbose_print:
                        print(
                            f"Length '{_obj}' == {cli_bcolors.FAIL}{obj_length}{cli_bcolors.ENDC},\n Required maximum length {cli_bcolors.OKBLUE}{max_}{cli_bcolors.ENDC} (per schema {schema['items']}),\n In {_obj},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                    return False

                if 'items' in schema.keys():
                    schema_len = len(schema['items'])

                    if schema_len > 0:
                        single_type = schema['items'][0]

                        for i in range(obj_length):
                            new_path = f"{new_path}{_path_sep}[{i}]"
                            o = _obj[i]
                            elem_type = get_native_type_name(type(o).__name__, 'json')
                            if (single_type['type'] != 'any' and elem_type != single_type['type']) or (
                                    elem_type == 'integer' and single_type['type'] == 'number'):
                                if verbose_print:
                                    print(
                                        f"Type '{o}' == {cli_bcolors.FAIL}'{elem_type}'{cli_bcolors.ENDC},\n Required type {cli_bcolors.OKBLUE}'{single_type['type']}'{cli_bcolors.ENDC} (per schema {single_type}),\n In {o},\n Path {cli_bcolors.WARNING}{new_path}{cli_bcolors.ENDC}")
                                return False
                            if single_type['type'] in [JSON_SCHEMA_OBJECT, JSON_SCHEMA_ARRAY]:
                                if not schema_validation(o, single_type, path=new_path):
                                    return False
                            new_path = path
                return True

        return schema_validation(_obj=obj, schema=self.schema, path='')
