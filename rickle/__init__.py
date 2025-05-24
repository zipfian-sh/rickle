from .__version__ import __version__, __date__
from collections import OrderedDict
import os
import json
import copy
import warnings
from typing import Union, TypeVar
from io import TextIOWrapper, BytesIO, StringIO
import yaml
import base64
import re
import inspect
from functools import partial
import uuid
import sys
from pathlib import Path
import importlib.util
import configparser
import tomli_w as tomlw

try:
    import requests
except ModuleNotFoundError as exc:
    warnings.warn(f"The module requests is not installed. This will break API calls.")

if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml

from rickle.tools import toml_null_stripper, inflate_dict, flatten_dict, parse_ini, unparse_ini, supported_encodings, \
    generate_random_value, object_to_dict

yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data.items()))

class BaseRickle:
    """
        A base class that creates internal structures from embedded structures.

        Args:
            base (str,dict,TextIOWrapper, list): String (YAML or JSON, file path to YAML/JSON file, URL), text IO stream, dict (default = None).
            deep (bool): Internalize dictionary structures in lists (default = False).
            strict (bool): Check keywords, if YAML/JSON key is Rickle keyword (or member of object) raise ValueError (default = True).
            **init_args (kw_args): Additional arguments for string replacement

        Raises:
            ValueError: If the given base object can not be handled. Also raises if YAML key is already member of Rickle.
    """

    @staticmethod
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
        return flatten_dict(dictionary=dictionary, path_sep=path_sep, list_brackets=list_brackets)

    @staticmethod
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
        return inflate_dict(flat_dict=flat_dict, path_sep=path_sep, list_brackets=list_brackets)

    def __create_dict_from_string(self, base: str, **init_args):

        stringed = ''
        file_ext = ''

        if os.path.exists(base) and Path(base).is_file():
            file_path = Path(base)
            file_ext = file_path.suffix.lower()

            # handle dotenv
            if file_path.stem.lower() == '.env':
                file_ext = '.env'
            with file_path.open(mode='r', encoding=init_args.get('encoding', 'utf-8')) as f:
                stringed = f.read()
        elif isinstance(base, str):
            try:
                from urllib3.util import parse_url
                try:
                    parsed = parse_url(base)
                    if all([parsed.scheme, parsed.host]):
                        response = requests.get(url=base.strip(), )
                        if response.status_code == 200:
                            _d = response.json()
                            self._input_type = "url"
                            return _d
                        else:
                            sys.stderr.write(f"Non-200 status {response.status_code} returned for URL {base}")
                            raise ValueError(f"Non-200 status {response.status_code} returned for URL {base}")
                except:
                    pass
            except (ImportError, ModuleNotFoundError):
                pass

            stringed = base

        if not init_args is None:
            for k, v in init_args.items():
                _handlebars = init_args.get("RICKLE_HANDLEBARS", os.getenv('RICKLE_HANDLEBARS', "{{}}"))
                if len(_handlebars) % 2 > 0:
                    raise ValueError(f"The string length ({len(_handlebars)}) of the handlebars passed ({_handlebars}) are not even, i.e. can not split in the 'middle'")

                _halfpoint = int(len(_handlebars)/2)
                _opening = _handlebars[:_halfpoint]
                _closing = _handlebars[_halfpoint:]
                _k = "{opening}{key}{closing}".format(
                    opening=_opening,
                    key=k,
                    closing=_closing
                )
                stringed = stringed.replace(_k, json.dumps(v))

        error_list = list()

        if file_ext in [".yaml", ".yml"]:
            try:
                _d = list(yaml.safe_load_all(stringed))
                if len(_d) == 1:
                    self._input_type = "yaml"
                    return _d[0]
                self._input_type = "array"
                return _d
            except Exception as exc:
                error_list.append(f"YAML: {exc}")
        if file_ext in [".json"]:
            try:
                _d = json.loads(stringed)
                self._input_type = "json"
                return _d
            except Exception as exc:
                error_list.append(f"JSON: {exc}")
        if file_ext in [".jsonl"]:
            try:
                _d = [json.loads(line) for line in stringed.split('\n')]
                self._input_type = "array"
                return _d
            except Exception as exc:
                error_list.append(f"JSON: {exc}")
        if file_ext in [".toml"]:
            try:
                _d = toml.loads(stringed)
                self._input_type = "toml"
                return _d
            except Exception as exc:
                error_list.append(f"TOML: {exc}")
        if file_ext in [".ini"]:
            try:
                config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
                config.read_string(stringed)

                path_sep = init_args.get('RICKLE_INI_PATH_SEP', os.getenv("RICKLE_INI_PATH_SEP", "."))
                list_brackets = (
                    init_args.get("RICKLE_INI_OPENING_BRACES", os.getenv("RICKLE_INI_OPENING_BRACES", "(")),
                    init_args.get("RICKLE_INI_CLOSING_BRACES", os.getenv("RICKLE_INI_CLOSING_BRACES", ")"))
                )

                _d = parse_ini(config=config, path_sep=path_sep, list_brackets=list_brackets)

                self._input_type = "ini"
                return _d
            except Exception as exc:
                error_list.append(f"INI: {exc}")
        if file_ext == ".env":
            try:
                if importlib.util.find_spec('dotenv'):
                    from io import StringIO
                    from dotenv import dotenv_values

                    _d = dotenv_values(stream=StringIO(stringed))

                    self._input_type = "env"
                    return _d
            except Exception as exc:
                error_list.append(f"ENV: {exc}")
        if file_ext == ".xml":
            try:
                if importlib.util.find_spec('xmltodict'):
                    import xmltodict

                    _d = xmltodict.parse(stringed, process_namespaces=init_args.get('process_namespaces', False))

                    self._input_type = "xml"
                    return _d
            except Exception as exc:
                error_list.append(f"XML: {exc}")

        # Brute force it
        try:
            _d = [json.loads(l) for l in stringed.splitlines()]
            if len(_d) == 1:
                self._input_type = "json"
                return _d[0]
            self._input_type = "array"
            return _d
        except Exception as exc:
            error_list.append(f"JSONL: {exc}")
        try:
            _d = json.loads(stringed)
            self._input_type = "json"
            return _d
        except Exception as exc:
            error_list.append(f"JSON: {exc}")
        try:
            _d = list(yaml.safe_load_all(stringed))
            if len(_d) == 1:
                self._input_type = "yaml"
                return _d[0]
            self._input_type = "array"
            return _d
        except Exception as exc:
            error_list.append(f"YAML: {exc}")
        try:
            _d = toml.loads(stringed)
            self._input_type = "toml"
            return _d
        except Exception as exc:
            error_list.append(f"TOML: {exc}")
        try:
            config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            config.read_string(stringed)

            path_sep = init_args.get('RICKLE_INI_PATH_SEP', os.getenv("RICKLE_INI_PATH_SEP", "."))
            list_brackets = (
                init_args.get("RICKLE_INI_OPENING_BRACES", os.getenv("RICKLE_INI_OPENING_BRACES", "(")),
                init_args.get("RICKLE_INI_CLOSING_BRACES", os.getenv("RICKLE_INI_CLOSING_BRACES", ")"))
            )

            _d = parse_ini(config=config, path_sep=path_sep, list_brackets=list_brackets)

            self._input_type = "ini"
            return _d
        except Exception as exc:
            error_list.append(f"INI: {exc}")
        try:
            if importlib.util.find_spec('dotenv'):
                from io import StringIO
                from dotenv import dotenv_values

                _d = dotenv_values(stream=StringIO(stringed))

                self._input_type = "env"
                return _d
        except Exception as exc:
            error_list.append(f"ENV: {exc}")
        try:
            if importlib.util.find_spec('xmltodict'):
                import xmltodict

                _d = xmltodict.parse(stringed, process_namespaces=init_args.get('process_namespaces', False))

                self._input_type = "xml"
                return _d
        except Exception as exc:
            error_list.append(f"XML: {exc}")

        for error in error_list:
            print(error)

        raise ValueError("Unable to infer data type")

    def _iternalize(self, obj: Union[dict, list], deep: bool, **init_args):
        if isinstance(obj, dict):
            for k, v in obj.items():
                k = self._check_kw(k)
                if isinstance(v, dict):
                    self.__dict__.update({k: BaseRickle(base=v, deep=deep, strict=self._strict, **init_args)})
                    continue
                if isinstance(v, list) and deep:
                    new_list = list()
                    for i in v:
                        if isinstance(i, dict):
                            new_list.append(BaseRickle(base=i, deep=deep, strict=self._strict, **init_args))
                        else:
                            new_list.append(i)
                    self.__dict__.update({k: new_list})
                    continue

                self.__dict__.update({k: v})
        if isinstance(obj, list):
            for b in obj:
                if isinstance(b, dict):
                    self.__list__.append(BaseRickle(base=b, deep=deep, strict=self._strict, **init_args))

    def __init__(self, base: Union[dict, str, TextIOWrapper, list] = None,
                 deep: bool = False,
                 strict: bool = True,
                 **init_args):
        self._meta_info = dict()
        self.__list__ = list()
        self._strict = strict
        self._input_type = None
        self._allowed_chars_pat = re.compile('[^a-zA-Z_]')
        self._keys_map = dict()
        self._path_sep = init_args.get('RICKLE_PATH_SEP', os.getenv("RICKLE_PATH_SEP", "/"))
        self._name_cleanup = init_args.get('RICKLE_NAME_CLEAN_UP', os.getenv("RICKLE_NAME_CLEAN_UP", True))

        self._init_args = init_args

        if base is None:
            return

        if isinstance(base, dict):
            self._iternalize(base, deep=deep, **init_args)
            self._input_type = 'object'
            return

        if isinstance(base, TextIOWrapper):
            _d = self.__create_dict_from_string(base.read(), **init_args)
            self._iternalize(_d, deep=deep, **init_args)
            return

        if isinstance(base, str):
            _d = self.__create_dict_from_string(base, **init_args)
            self._iternalize(_d, deep=deep, **init_args)

        if isinstance(base, list):
            _l = list()
            for i in base:
                if isinstance(i, dict):
                    _l.append(i)
                elif isinstance(i, str):
                    _l.append( self.__create_dict_from_string(i, **init_args) )
                elif isinstance(i, TextIOWrapper):
                    _l.append( self.__create_dict_from_string(i.read(), **init_args) )
                else:
                    raise TypeError(f"Unable to add type {type(i)}")

            self._iternalize(_l, deep=deep, **init_args)
            self._input_type = 'array'

    def __repr__(self):
        if self._input_type == 'array':
            return "[{}]".format( ", ".join([repr(i) for i in self.__list__]) )
        keys = self.__dict__
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys if not str(k).__contains__(self.__class__.__name__)
                 and not str(k).endswith('_meta_info') and not str(k).startswith('_'))
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __str__(self):
        return self.to_yaml()

    def __eq__(self, other):
        raise NotImplementedError("Removed since version 1.2.3")

    def __len__(self):
        if self._input_type == 'array':
            return len(self.__list__)
        return len(self.dict())

    def __iter__(self):
        self.__n = 0
        return self

    def __next__(self):
        if self._input_type == "array":
            try:
                item = self.__list__[self.__n]
            except IndexError:
                raise StopIteration()
            self.__n += 1
            return item
        else:
            try:
                item = list(self.dict().keys())[self.__n]
            except IndexError:
                raise StopIteration()
            self.__n += 1
            return item

    def __getitem__(self, key):
        if key is None:
            raise KeyError("NoneType is not a valid key type")
        if isinstance(key, str):
            return self.__dict__[key]
        elif isinstance(key, int):
            return self.__list__[key]
        else:
            raise TypeError("Key can only be of case sensitive string type or if created from list, an integer index!")


    def __setitem__(self, key, value):
        if key is None:
            raise KeyError("NoneType is not a valid key type")
        if isinstance(key, str):
            self.__dict__.update({key: value})
        elif isinstance(key, int):
            self.__list__[key] = value
        else:
            raise TypeError("Key can only be of case sensitive string type or if created from list, an integer index!")

    def __delitem__(self, key):
        if key is None:
            raise KeyError("NoneType is not a valid key type")
        if isinstance(key, str):
            del self.__dict__[key]
        elif isinstance(key, int):
            del self.__list__[key]
        else:
            raise TypeError("Key can only be of case sensitive string type or if created from list, an integer index!")

    def __contains__(self, key):
        return key in self.dict()

    def _find_key_value(self, key, value, op:str, rick=None, parent_path=None, report_parent: bool = False):
        values = list()
        if key in rick or self._path_sep in key:
            try:
                v = rick.get(key)

                if ((v and not value is None) and
                        ((op == '=' and v == value) or \
                        (op == '==' and v == value) or \
                         (op == 'eq' and v == value) or \
                         (op == '!=' and v != value) or \
                        (op == 'ne' and v != value) or \
                    (op == '>' and v > value) or \
                        (op == 'gt' and v > value) or \
                    (op == '>=' and v >= value) or \
                        (op == 'gte' and v >= value) or \
                    (op == '<' and v < value) or \
                        (op == 'lt' and v < value) or \
                    (op == '<=' and v <= value) or\
                        (op == 'lte' and v <= value))):
                    if report_parent:
                        values = [f'{parent_path}']
                    elif key.startswith(self._path_sep):
                        values = [f'{parent_path}{key}']
                    else:
                        values = [f'{parent_path}{self._path_sep}{key}']

            except Exception as exc:
                pass

        for k in rick.keys():
            v = rick.get(k)
            if isinstance(v, BaseRickle) or isinstance(v, dict):
                try:
                    paths_list = self._find_key_value(key=key, value=value, op=op, rick=v,
                                              parent_path=f'{parent_path}{self._path_sep}{k}',
                                                      report_parent=report_parent)
                    values.extend(paths_list)
                except StopIteration:
                    continue
            if isinstance(v, list):
                try:
                    for ix, el in enumerate(v):
                        if isinstance(el, dict) or isinstance(el, BaseRickle):
                            paths_list = self._find_key_value(key=key, value=value, op=op, rick=el,
                                                      parent_path=f'{parent_path}{self._path_sep}{k}{self._path_sep}[{ix}]',
                                                              report_parent=report_parent)
                            values.extend(paths_list)
                except StopIteration:
                    continue
        if len(values) > 0:
            return values
        raise StopIteration

    def find_key_value(self, key: str, value, op: str, report_parent: bool = False) -> list:
        """
        Search the current Rickle for all paths that match the search key. Returns empty list if nothing is found.

        Args:
            key (str): The key to search.

        Returns:
            list: all paths found.
        """
        try:
            if self._input_type == 'array':
                return self._find_key_value(key=key,
                                            value=value,
                                            op=op,
                                            rick={f'[{ix}]':_d for ix, _d in enumerate(self.__list__)},
                                            parent_path='',
                                            report_parent=report_parent)
            return self._find_key_value(key=key,
                                        value=value,
                                        op=op,
                                        rick=self,
                                        parent_path='',
                                        report_parent=report_parent)
        except StopIteration:
            return list()

    def _search_path(self, key, dictionary=None, parent_path=None, report_parent: bool = False):
        values = list()
        if key in dictionary:
            if report_parent:
                values = [f'{parent_path}']
            else:
                values = [f'{parent_path}{self._path_sep}{key}']
        for k, v in dictionary.items():
            if isinstance(v, BaseRickle):
                try:
                    value = self._search_path(key=key, dictionary=v.dict(),
                                              parent_path=f'{parent_path}{self._path_sep}{k}', report_parent=report_parent)
                    values.extend(value)
                except StopIteration:
                    continue
            if isinstance(v, dict):
                try:
                    value = self._search_path(key=key, dictionary=v, parent_path=f'{parent_path}{self._path_sep}{k}',
                                              report_parent=report_parent)
                    values.extend(value)
                except StopIteration:
                    continue
            if isinstance(v, list):
                try:
                    for ix, el in enumerate(v):
                        if isinstance(el, dict):
                            value = self._search_path(key=key, dictionary=el,
                                                      parent_path=f'{parent_path}{self._path_sep}{k}{self._path_sep}[{ix}]',
                                                      report_parent=report_parent)
                            values.extend(value)
                        if isinstance(el, BaseRickle):
                            value = self._search_path(key=key, dictionary=el.dict(),
                                                      parent_path=f'{parent_path}{self._path_sep}{k}{self._path_sep}[{ix}]',
                                                      report_parent=report_parent)
                            values.extend(value)
                except StopIteration:
                    continue
        if len(values) > 0:
            return values
        raise StopIteration

    def search_path(self, key: str, report_parent: bool = False) -> list:
        """
        Search the current Rickle for all paths that match the search key. Returns empty list if nothing is found.

        Args:
            key (str): The key to search.

        Returns:
            list: all paths found.
        """
        try:
            if self._input_type == 'array':
                return self._search_path(key=key, dictionary={f'[{ix}]':_d.dict() for ix, _d in enumerate(self.__list__)},
                                         parent_path='', report_parent=report_parent)
            return self._search_path(key=key, dictionary=self.dict(), parent_path='', report_parent=report_parent)
        except StopIteration:
            return list()

    def __call__(self, path: str, **kwargs):
        """
        Rickle objects can be queried via a path string.

        Notes:
            '/' => root.
            '/name' => member.
            '/name/[0]' => for lists.
            '/[0]' => for lists types.

        Args:
            path (str): The path as a string, down to the last mentioned node.

        Returns:
            Any: Value of node of function.
        """
        if path == self._path_sep:
            return self

        if not path.startswith(self._path_sep):
            raise KeyError(f'Missing root path {self._path_sep} at {repr(self)}')

        list_index_match = re.match(r'/\[(\d+)\](/.+)?', path)
        path_start_index = 1
        if list_index_match:
            current_node = self.__list__[int(list_index_match.group(1))]
            path_start_index = 2
        else:
            current_node = self


        path_list = path.split(self._path_sep)

        for node_name in path_list[path_start_index:]:
            list_index_match = re.match(r'\[(\d+)\]', node_name)
            if list_index_match and isinstance(current_node, list):
                current_node = current_node[int(list_index_match.group(1))]
            else:
                current_node = current_node.get(node_name)
            if current_node is None:
                raise NameError(f'The path {path} could not be traversed. Alternatively use "get"')

        return current_node

    def _eval_name(self, name):
        if str(name).__contains__(self.__class__.__name__) or str(name).endswith('__n') or str(name).startswith('_'):
            return True
        else:
            return False

    def _check_kw(self, name):
        if self._strict and name in dir(self):
            raise NameError(f"Unable to add key '{name}', reserved keyword in Rickle. Use strict=False.")

        if not self._name_cleanup:
            return name
        clean_name = self._allowed_chars_pat.sub('', name)
        if clean_name != name:
            self._keys_map[clean_name] = name

        return clean_name

    def _recursive_search(self, dictionary, key):
        if key in dictionary:
            return dictionary[key]
        for k, v in dictionary.items():
            if isinstance(v, BaseRickle):
                try:
                    value = self._recursive_search(v.__dict__, key)
                    return value
                except StopIteration:
                    continue
            if isinstance(v, dict):
                try:
                    value = self._recursive_search(v, key)
                    return value
                except StopIteration:
                    continue
        raise StopIteration

    def items(self):
        """
        Iterate through all key value pairs. Rickle is destructed into dict.

        Yields:
            tuple: str, object.
        """
        d = self.dict()
        for key in d.keys():
            if self._eval_name(key):
                continue
            yield key, d[key]

    def get(self, key: str, default=None, do_recursive: bool = False):
        """
        Acts as a regular get from a dictionary but can employ a recursive search of structure and returns the first found key-value pair.

        Note:
            Document paths like '/root/to/path' can also be used. If the path can not be traversed, the default value is returned.

        Args:
            key (str): key string being searched.
            default (any): Return value if nothing is found.
            do_recursive (bool): Search recursively until first match is found (default = False).

        Returns:
            obj: value found, or None for nothing found.
        """
        try:
            if self._path_sep in key:
                v = self(key)
                return v
            if do_recursive:
                value = self._recursive_search(self.__dict__, key)
            else:
                if key in self._keys_map.values():
                    key = next((k for k, v in self._keys_map.items() if v == key), None)
                value = self.__dict__.get(key, default)
            return value
        except StopIteration:
            return default
        except NameError:
            return default
        except Exception as ex:
            raise ex

    def set(self, key: str, value):
        """
        As with the `get` method, this method can be used to update the inherent dictionary with new values.

        Note:
            Document paths like '/root/to/path' can also be used. If the path can not be traversed, an error is raised.

        Args:
            key (str): key string to set.
            value: Any Python like value that can be deserialised.
        """

        if self._path_sep in key and not key.startswith(self._path_sep):
            raise KeyError(f'Missing root path {self._path_sep}')
        if not self._path_sep in key:
            key = f"{self._path_sep}{key}"

        if key == self._path_sep:
            raise KeyError('Can not set a value to self')

        list_index_match = re.match(r'/\[(\d+)\](/.+)?', key)
        path_start_index = 1
        if list_index_match:
            current_node = self.__list__[int(list_index_match.group(1))]
            path_start_index = 2
        else:
            current_node = self
        path_list = key.split(self._path_sep)

        for node_name in path_list[path_start_index:-1]:
            if not isinstance(current_node, self.__class__):
                raise KeyError(f'The path {key} could not be traversed')
            current_node = current_node.get(node_name)
            if current_node is None:
                raise KeyError(f'The path {key} could not be traversed')

        if '?' in path_list[-1]:
            raise KeyError(f'Function params "{path_list[-1]}" included in path!')

        if not isinstance(current_node, self.__class__):
            raise NameError(f'The path {key} could not be set, try using put')

        if current_node.has(path_list[-1]):
            current_node[path_list[-1]] = value
        else:
            raise NameError(f'The path {key} could not be set, try using put')

    def put(self, key: str, value):
        """
        As with the `get` method, this method can be used to update the inherent dictionary with new values.

        Note:
            Document paths like '/root/to/path' can also be used. If the path can not be traversed, an error is raised.

        Args:
            key (str): key string to set.
            value: Any Python like value that can be deserialised.
        """

        if self._path_sep in key and not key.startswith(self._path_sep):
            raise KeyError(f'Missing root path {self._path_sep}')
        if not self._path_sep in key:
            key = f"{self._path_sep}{key}"

        if key == self._path_sep:
            raise KeyError('Can not set a value to self')

        list_index_match = re.match(r'/\[(\d+)\](/.+)?', key)
        path_start_index = 1
        if list_index_match:
            current_node = self.__list__[int(list_index_match.group(1))]
            path_start_index = 2
        else:
            current_node = self
        path_list = key.split(self._path_sep)

        for node_name in path_list[path_start_index:-1]:
            if not isinstance(current_node, self.__class__):
                raise KeyError(f'The path {key} could not be traversed')
            next_node = current_node.get(node_name)
            if next_node is None or not isinstance(next_node, self.__class__):
                next_node = self.__class__()
                if current_node.has(node_name):
                    current_node.remove(node_name)
                current_node.add(node_name, next_node)
            current_node = next_node


        if '?' in path_list[-1]:
            raise KeyError(f'Function params "{path_list[-1]}" included in path!')

        if not isinstance(current_node, self.__class__):
            raise NameError(f'The path {key} could not be set, try using put')

        if current_node.has(path_list[-1]):
            current_node[path_list[-1]] = value
        else:
            current_node.add(path_list[-1], value)

    def remove(self, key: str):
        """
        Removes using path.

        Args:
            key (str): Path to key-value to be removed.
        """
        if self._path_sep in key and not key.startswith(self._path_sep):
            raise KeyError(f'Missing root path {self._path_sep}')
        if not self._path_sep in key:
            key = f"{self._path_sep}{key}"

        if key == self._path_sep:
            raise NameError('Can not remove self')

        list_index_match = re.match(r'/\[(\d+)\](/.+)?', key)
        path_start_index = 1
        if list_index_match:
            current_node = self.__list__[int(list_index_match.group(1))]
            path_start_index = 2
        else:
            current_node = self

        path_list = key.split(self._path_sep)

        for node_name in path_list[path_start_index:-1]:
            current_node = current_node.get(node_name)
            if current_node is None:
                raise NameError(f'The path {key} could not be traversed')

        if '?' in path_list[-1]:
            raise KeyError(f'Function params "{path_list[-1]}" included in path!')

        del current_node.__dict__[path_list[-1]]

    def values(self):
        """
        Gets the higher level values of the current Rick object.

        Returns:
            list: of objects.
        """
        d = self.dict()
        keys = list(d.keys())
        objects = [d[k] for k in keys if not self._eval_name(k)]

        return objects

    def keys(self):
        """
        Gets the higher level keys of the current Rick object.

        Returns:
            list: of keys.
        """
        d = self.dict()
        keys = list(d.keys())
        keys = [k for k in keys if not self._eval_name(k)]

        return keys

    def dict(self, serialised: bool = False):
        """
        Deconstructs the whole object into a Python dictionary.

        Args:
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).

        Notes:
            Functions and lambdas are always given in serialised form.

        Returns:
            dict: of object.
        """
        d = dict()
        for key, value in self.__dict__.items():
            actual_key = key
            if key in self._keys_map.keys():
                actual_key = self._keys_map[key]
            if self._eval_name(key) or str(key).endswith('_meta_info'):
                continue
            if isinstance(value, BaseRickle) or isinstance(value, Rickle):
                d[actual_key] = value.dict(serialised=serialised)
            elif isinstance(value, list):
                new_list = list()
                for element in value:
                    if isinstance(element, BaseRickle):
                        new_list.append(element.dict(serialised=serialised))
                    else:
                        new_list.append(element)
                d[actual_key] = new_list
            else:
                d[actual_key] = value
        return d

    def list(self, serialised: bool = False):
        """
        Deconstructs the whole object into a Python list (of dictionaries) if type is 'array'.

        Args:
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).

        Notes:
            Functions and lambdas are always given in serialised form.

        Returns:
            list: of self.
        """
        return [_d.dict(serialised=serialised) for _d in self.__list__]

    def has(self, key: str, deep=False) -> bool:
        """
        Checks whether the key exists in the object.

        Args:
            key (str): key string being searched.
            deep (bool): whether to search deeply (default = False).

        Returns:
            bool: if found.
        """
        if key in self.dict():
            return True
        if deep:
            try:
                self._recursive_search(self.dict(), key)
                return True
            except StopIteration:
                return False
        return False

    def to_yaml(self, output: Union[str, TextIOWrapper] = None, serialised: bool = False, encoding: str = 'utf-8'):
        """
        Does a self dump to a YAML file or returns as string.

        Args:
            output (str, TextIOWrapper): File path or stream (default = None).
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).
            encoding (str): Output stream encoding (default = 'utf-8').

        Notes:
            Functions and lambdas are always given in serialised form.
        """
        if self._input_type == "array":
            self_as_primitive = self.list(serialised=serialised)
        else:
            self_as_primitive = self.dict(serialised=serialised)

        if output:
            if isinstance(output, TextIOWrapper):
                if self._input_type == "array":
                    yaml.safe_dump_all(self_as_primitive, stream=output, encoding=encoding)
                else:
                    yaml.safe_dump(self_as_primitive, stream=output, encoding=encoding)
            elif isinstance(output, str):
                with open(output, 'w', encoding=encoding) as fs:
                    if self._input_type == "array":
                        yaml.safe_dump_all(self_as_primitive, fs)
                    else:
                        yaml.safe_dump(self_as_primitive, fs)
        else:
            if self._input_type == "array":
                return yaml.safe_dump_all(self_as_primitive, stream=None, encoding=encoding).decode(encoding)
            else:
                return yaml.safe_dump(self_as_primitive, stream=None, encoding=encoding).decode(encoding)

    def to_json(self, output: Union[str, TextIOWrapper] = None, serialised: bool = False, encoding: str = 'utf-8', lines: bool = True):
        """
        Does a self dump to a JSON file or returns as string.

        Args:
            output (str, TextIOWrapper): File path or stream (default = None).
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).
            encoding (str): Output stream encoding (default = 'utf-8').
            lines (bool): Whether to dump as JSON lines when rickle is an array (default = True).

        Notes:
            Functions and lambdas are always given in serialised form.
            To not dump as JSON lines when rickle is an array, use lines=False.

        """
        if self._input_type == "array":
            self_as_primitive = self.list(serialised=serialised)
        else:
            self_as_primitive = self.dict(serialised=serialised)

        if output:
            if isinstance(output, TextIOWrapper):
                if self._input_type == "array" and lines:
                    for l in self_as_primitive:
                        output.write(json.dumps(l))
                        output.write('\n')
                else:
                    json.dump(self_as_primitive, output)
            elif isinstance(output, str):
                with open(output, 'w', encoding=encoding) as fs:
                    if self._input_type == "array" and lines:
                        for l in self_as_primitive:
                            fs.write(json.dumps(l))
                            fs.write('\n')
                    else:
                        json.dump(self_as_primitive, fs)
        else:
            if self._input_type == "array" and lines:
                return '\n'.join([json.dumps(l) for l in self_as_primitive])
            else:
                return json.dumps(self_as_primitive)

    def to_toml(self, output: Union[str, BytesIO] = None, serialised: bool = False, encoding: str = 'utf-8'):
        """
        Does a self dump to a TOML file or returns as string.

        Args:
            output (str, BytesIO): File path or stream (default = None).
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).
            encoding (str): Output stream encoding (default = 'utf-8').

        Notes:
            Functions and lambdas are always given in serialised form.
            IO stream "output" needs to be BytesIO object
        """
        if self._input_type == "array":
            raise TypeError("Can not dump array type as TOML, convert to object type.")
        else:
            self_as_primitive = toml_null_stripper(self.dict(serialised=serialised))

        if output:
            if isinstance(output, BytesIO):
                tomlw.dump(self_as_primitive, output)
            elif isinstance(output, str):
                with open(output, 'wb', encoding=encoding) as fs:
                    tomlw.dump(self_as_primitive, fs)
        else:
            return tomlw.dumps(self_as_primitive)

    def to_xml(self, output: Union[str, BytesIO] = None, serialised: bool = False, encoding: str = 'utf-8'):
        """
        Does a self dump to a XML file or returns as string.

        Args:
            output (str, BytesIO): File path or stream (default = None).
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).
            encoding (str): Output stream encoding (default = 'utf-8').

        Notes:
            Functions and lambdas are always given in serialised form.
            IO stream "output" needs to be BytesIO object
        """
        if importlib.util.find_spec('xmltodict'):
            import xmltodict

            if self._input_type == "array":
                raise TypeError("Can not dump array type as XML, convert to object type.")
            else:
                self_as_primitive = self.dict(serialised=serialised)

            if output:
                if isinstance(output, BytesIO):
                    xmltodict.unparse(input_dict=self_as_primitive, output=output, encoding=encoding, pretty=True)
                elif isinstance(output, str):
                    with open(output, 'wb', encoding=encoding) as fs:
                        xmltodict.unparse(input_dict=self_as_primitive, output=fs, encoding=encoding, pretty=True)
            else:
                return xmltodict.unparse(input_dict=self_as_primitive, encoding=encoding, pretty=True)
        else:
            raise ModuleNotFoundError("Missing 'xmltodict' package!")

    def to_ini(self, output: Union[str, TextIOWrapper] = None, serialised: bool = False, encoding: str = 'utf-8',
               path_sep: str = None, list_brackets: tuple = None):
        """
        Flattens self into a thin dict and does a dump to INI string or file.

        Args:
            output (str, TextIOWrapper): File path or stream (default = None).
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).
            encoding (str): Output stream encoding (default = 'utf-8').
            path_sep (str): For flattened dictionary, use path separator or default (default = None).
            list_brackets (tuple): Tuple of strings, defining opening and closing brackets of list indexes (default = None).

        Notes:
            Functions and lambdas are always given in serialised form.
            IO stream "output" needs to be BytesIO object

        """
        if self._input_type == "array":
            raise TypeError("Can not dump array type as INI, convert to object type.")
        else:
            self_as_primitive = toml_null_stripper(self.dict(serialised=serialised))

        _path_sep = path_sep if path_sep else os.getenv("RICKLE_INI_PATH_SEP",
                                                        self._init_args.get('RICKLE_INI_PATH_SEP', "."))

        if list_brackets is None:
            list_brackets = (
                os.getenv("RICKLE_INI_OPENING_BRACES", self._init_args.get('RICKLE_INI_OPENING_BRACES', "(")),
                os.getenv("RICKLE_INI_CLOSING_BRACES", self._init_args.get('RICKLE_INI_CLOSING_BRACES', ")"))
            )

        output_ini = unparse_ini(dictionary=self_as_primitive, path_sep=_path_sep, list_brackets=list_brackets)

        if output:
            if isinstance(output, TextIOWrapper):
                output_ini.write(output)
            elif isinstance(output, str):
                with open(output, 'w', encoding=encoding) as fs:
                    output_ini.write(fs)
        else:
            out = StringIO()
            output_ini.write(out)
            out.seek(0)

            return out.read()

    def meta(self, name: str = None):
        """
        Get the metadata for a property.

        Args:
            name (str): The name of the property (default = None).

        Returns:
            dict: The metadata as a dict.
        """
        if name:
            if name in self._keys_map.values():
                name = next((k for k, v in self._keys_map.items() if v == name), None)
            return self._meta_info[name]
        return self._meta_info

    def add_attr(self, name, value):
        warnings.warn(message="'add_attr' will be removed after version 1.4. Use 'add' instead")
        self.add(name=name, value=value)

    def add(self, name, value):
        """
        Add a new key (attribute) and value member to Rick.

        Args:
            name (str): Key / property name.
            value (any): Value of new key.
        """
        name = self._check_kw(name)
        self.__dict__.update({name: value})
        self._meta_info[name] = {'type': 'attribute', 'value': value}

class Rickle(BaseRickle):
    """
        An extended version of the BasicRick that can load OS environ variables and Python functions.

        Args:
            base (str, list): String (YAML or JSON, file path to YAML/JSON file) or list of file paths, text IO stream, dict.
            deep (bool): Internalize dictionary structures in lists.
            load_lambda (bool): Load lambda as code or strings.
            strict (bool): Check keywords, if YAML/JSON key is Rickle keyword (or member of object) raise ValueError (default = True).
            **init_args (kw_args): Additional arguments for string replacement

        Raises:
            ValueError: If the given base object can not be handled. Also raises if YAML key is already member of Rickle.
    """

    def _iternalize(self, obj: dict, deep: bool, **init_args):
        if isinstance(obj, dict):
            for k, v in obj.items():
                k = self._check_kw(k)  # Redundant but easier to check twice than to paste 10 times
                if isinstance(v, dict):
                    if 'type' in v.keys():
                        if v['type'] == 'env':
                            self.add_env(name=k,
                                                  load=v['load'],
                                                  default=v.get('default', None))
                            continue
                        if v['type'] == 'base64':
                            self.add_base64(name=k,
                                            load=v['load'])
                            continue
                        if v['type'] == 'file':
                            self.add_file(name=k,
                                               file_path=v['file_path'],
                                               load_as_rick=v.get('load_as_rick', False),
                                               deep=v.get('deep', False),
                                               load_lambda=v.get('load_lambda', False),
                                               is_binary=v.get('is_binary', False),
                                               encoding=v.get('encoding', 'utf-8'),
                                               hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'csv':
                            self.add_csv(name=k,
                                              file_path_or_str=v['file_path'],
                                              fieldnames=v.get('fieldnames', None),
                                              load_as_rick=v.get('load_as_rick', False),
                                              encoding=v.get('encoding', 'utf-8'))
                            continue
                        if v['type'] == 'api':
                            self.add_api(name=k,
                                           url=v['url'],
                                           http_verb=v.get('http_verb', 'GET'),
                                           headers=v.get('headers', None),
                                           params=v.get('params', None),
                                           body=v.get('body', None),
                                           load_as_rick=v.get('load_as_rick', False),
                                           load_lambda=v.get('load_lambda', False),
                                           deep=v.get('deep', False),
                                           expected_http_status=v.get('expected_http_status', 200),
                                           hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'secret':
                            self.add_secret(name=k,
                                            secret_id=v['secret_id'],
                                            provider=v['provider'],
                                            provider_access_key=v.get('provider_access_key', dict()),
                                            secret_version=v.get('secret_version', None),
                                            load_as_rick=v.get('load_as_rick', False),
                                            load_lambda=v.get('load_lambda', False),
                                            deep=v.get('deep', False),
                                            hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'html_page':
                            self.add_html_page(name=k,
                                               url=v['url'],
                                               headers=v.get('headers', None),
                                               params=v.get('params', None),
                                               expected_http_status=v.get('expected_http_status', 200),
                                               hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'random':
                            self.add_random_value(name=k,
                                                  value_type=v['value_type'],
                                                  value_properties=v.get('value_properties', dict()),
                                                  hot_load=v.get('hot_load', False))
                            continue

                    self.__dict__.update({k: Rickle(base=v, deep=deep, strict=self._strict, **init_args)})
                    continue
                if isinstance(v, list) and deep:
                    new_list = list()
                    for i in v:
                        if isinstance(i, dict):
                            new_list.append(Rickle(base=i, deep=deep, strict=self._strict, **init_args))
                        else:
                            new_list.append(i)
                    self.__dict__.update({k: new_list})
                    continue
                self.__dict__.update({k: v})
        if isinstance(obj, list):
            for b in obj:
                if isinstance(b, dict):
                    self.__list__.append(Rickle(base=b, deep=deep, strict=self._strict, **init_args))

    def __init__(self, base: Union[dict, str, TextIOWrapper, list] = None,
                 deep: bool = False,
                 load_lambda: bool = False,
                 strict: bool = True,
                 **init_args):
        # self._meta_info = dict()
        init_args['load_lambda'] = load_lambda
        init_args['deep'] = deep
        init_args['strict'] = strict
        super().__init__(base, **init_args)

    def __call__(self, path: str, **kwargs):
        """
        Rickle objects can be queried via a path string.

        Notes:
            '/' => root.
            '/name' => member.
            '/name/[0]' => for lists.

        Args:
            path (str): The path as a string, down to the last mentioned node.

        Returns:
            Any: Value of node of function.
        """

        if path == self._path_sep:
            return self

        if not path.startswith(self._path_sep):
            raise KeyError(f'Missing root path {self._path_sep} at {repr(self)}')

        list_index_match = re.match(r'/\[(\d+)\](/.+)?', path)
        path_start_index = 1
        if list_index_match:
            current_node = self.__list__[int(list_index_match.group(1))]
            path_start_index = 2
        else:
            current_node = self

        path_list = path.split(self._path_sep)

        for node_name in path_list[path_start_index:]:
            list_index_match = re.match(r'\[(\d+)\]', node_name)
            if list_index_match and isinstance(current_node, list):
                current_node = current_node[int(list_index_match.group(1))]
            else:
                current_node = current_node.get(node_name)
            if current_node is None:
                raise NameError(f'The path {path} could not be traversed. Alternatively use "get"')

        if self._init_args['load_lambda'] and inspect.isfunction(current_node):
            try:
                return current_node(**kwargs)
            except Exception as exc:
                raise TypeError(
                    f'{exc} occurred. The node in the path {path} is of type {type(current_node)} or does not match the query')

        return current_node

    def dict(self, serialised: bool = False):
        """
        Deconstructs the whole object into a Python dictionary.

        Args:
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).

        Notes:
            Functions and lambdas are always given in serialised form.

        Returns:
            dict: of object.
        """
        d = dict()
        for key, value in self.__dict__.items():
            actual_key = key
            if key in self._keys_map.keys():
                actual_key = self._keys_map[key]
            if self._eval_name(key):
                continue
            if serialised and key in self._meta_info.keys():
                d[actual_key] = self._meta_info[key]
            # Revisit this at some later point
            elif key in self._meta_info.keys() and \
                    self._meta_info[key]['type'] in ['base64']:
                # d[actual_key] = self._meta_info[key]
                continue
            elif key in self._meta_info.keys() and \
                    self._meta_info[key]['type'] in ['file', 'api', 'secret', 'random'] and \
                    self._meta_info[key]['hot_load']:
                # d[actual_key] = self._meta_info[key]
                continue
            elif isinstance(value, BaseRickle):
                d[actual_key] = value.dict(serialised=serialised)
            elif isinstance(value, list):
                new_list = list()
                for element in value:
                    if isinstance(element, BaseRickle):
                        new_list.append(element.dict(serialised=serialised))
                    else:
                        new_list.append(element)
                d[actual_key] = new_list
            else:
                d[actual_key] = value
        return d

    def add_random_value(self, name, value_type: str, value_properties: dict = None, hot_load: bool = False):
        """
        Adds a completely random value, useful for generating mock data.

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
            name (str): Key / property name.
            value_type (str): Either 'string', 'integer', 'number', 'enum', 'array', 'object', or 'any'.
            value_properties (dict): Extra properties defining what the randomly generated value should look like.
            hot_load (bool): Load the data on calling or load it only once on start (cold) (default = False).
        """
        name = self._check_kw(name)
        value_type = value_type.strip().lower()
        if value_properties is None:
            value_properties = dict()

        if hot_load:
            try:
                _load = f"""lambda: generate_random_value(value_type='{str(value_type)}',
                                                        value_properties={value_properties})"""

                self.__dict__.update({name: eval(_load)})
            except Exception as exc:
                raise ValueError(f"At 'add_random_value', when trying to add lambda, this happened {exc}")
        else:
            value = generate_random_value(value_type=value_type, value_properties=value_properties)

            self.__dict__.update({name: value})

        self._meta_info[name] = {'type': 'random',
                                 'value_type': value_type,
                                 'value_properties': value_properties,
                                 'hot_load': hot_load}

    def add_env(self, name, load, default=None):
        """
        Add a new OS ENVIRONMENT VARIABLE to Rick.

        Args:
            name (str): Property name.
            load (str): ENV var name.
            default (any): Default to value (default = None).
        """
        name = self._check_kw(name)
        self.__dict__.update({name: os.getenv(load, default)})
        self._meta_info[name] = {'type': 'env', 'load': load, 'default': default}

    def add_base64(self, name, load):
        """
        Add Base 64 encoded byte string data.

        Args:
            name (str): Property name.
            load (str): Base 64 encoded data.
        """
        name = self._check_kw(name)
        b = base64.b64decode(load)
        self.__dict__.update({name: b})
        self._meta_info[name] = {'type': 'base64',
                                 'load': load
                                 }

    def add_csv(self,
                     name,
                     file_path_or_str: str,
                     fieldnames: list = None,
                     load_as_rick: bool = False,
                     encoding: str = 'utf-8'
                     ):
        """
        Adds the ability to load CSV data as lists or even a list of Ricks where the column names are the properties.

        Args:
            name (str): Property name.
            file_path_or_str (str): File path to load from, or CSV string.
            fieldnames (list): Column headers (default = None).
            load_as_rick (bool): If true, loads and creates Rick from source, else loads the contents as text (default = False).
            encoding (str): If text, encoding can be specified (default = 'utf-8').

        """
        name = self._check_kw(name)
        import csv

        if Path(file_path_or_str).exists():
            stream = Path(file_path_or_str).open()
        else:
            stream = StringIO(file_path_or_str)


        dialect = csv.Sniffer().sniff(stream.read(1024))
        stream.seek(0)
        l = list()

        if load_as_rick:
            csv_file = csv.DictReader(stream, fieldnames=fieldnames, dialect=dialect)

            for row in csv_file:
                l.append(dict(row))

            self._iternalize({name: l}, deep=True)
        elif not fieldnames is None:

            columns = {c: list() for c in fieldnames}

            csv_file = csv.DictReader(stream, fieldnames=fieldnames, dialect=dialect)

            for row in csv_file:
                for k, v in row.items():
                    columns[k].append(v)

            self._iternalize({name: columns}, deep=False)
        else:
            csv_file = csv.reader(stream, dialect=dialect)

            for row in csv_file:
                l.append(row)

            self.__dict__.update({name: l})

        stream.close()

        self._meta_info[name] = {'type': 'csv',
                                 'file_path_or_str': file_path_or_str,
                                 'load_as_rick': load_as_rick,
                                 'fieldnames': fieldnames,
                                 'encoding': encoding
                                 }

    def _load_file(self,
                        file_path: str,
                        load_as_rick: bool = False,
                        deep: bool = False,
                        load_lambda: bool = False,
                        is_binary: bool = False,
                        encoding: str = 'utf-8'):
        if load_as_rick and not is_binary:
            args = copy.copy(self._init_args)
            args['load_lambda'] = load_lambda
            args['deep'] = deep
            return Rickle(file_path, **args)
        else:
            if is_binary:
                with open(file_path, 'rb') as fn:
                    return fn.read()
            else:
                with open(file_path, 'r', encoding=encoding) as fn:
                    return fn.read()

    def add_file(self, name,
                      file_path: str,
                      load_as_rick: bool = False,
                      deep: bool = False,
                      load_lambda: bool = False,
                      is_binary: bool = False,
                      encoding: str = 'utf-8',
                      hot_load: bool = False):
        """
        Adds the ability to further load Ricks from other YAML or JSON files, or alternatively load a text file.
        This opens up dynamic possibility, but with that it also opens up extreme security vulnerabilities.
        Only ever load files from trusted sources.
        **Important note: Even with ``deep`` and ``load_lambda`` set to False, further file or API calls could be found within the source that loads lambda functions.**
        **Important note: Be careful to never self-reference a file, i.e. don't load the same file from within itself to avoid infinte looping.**

        Args:
            name (str): Property name.
            file_path (str): File path to load from.
            load_as_rick (bool): If true, loads and creates Rick from source, else loads the contents as text (default = False).
            deep (bool): Internalize dictionary structures in lists (default = False).
            load_lambda (bool): Load lambda as code or strings (default = False).
            is_binary (bool): If the file is a binary file (default = False).
            encoding (str): If text, encoding can be specified (default = 'utf-8').
            hot_load (bool): Load the data on calling or load it only once on start (cold) (default = False).
        """
        name = self._check_kw(name)
        if hot_load:
            if (encoding in supported_encodings() and Path(file_path).is_file()
                    and self._init_args['load_lambda']):

                _load = f"""lambda self=self: self._load_file(file_path='{str(file_path)}',
                                              load_as_rick={load_as_rick == True},
                                              deep={deep == True},
                                              load_lambda={load_lambda == True},
                                              is_binary={is_binary == True},
                                              encoding='{str(encoding)}')"""

                self.__dict__.update({name: eval(_load)})
            else:
                raise ValueError(f"At 'add_from_file', when trying to add lambda, one or more checks failed")
        else:
            result = self._load_file(file_path=file_path,
                                          load_as_rick=load_as_rick,
                                          deep=deep,
                                          load_lambda=load_lambda,
                                          is_binary=is_binary,
                                          encoding=encoding)

            self.__dict__.update({name: result})

        self._meta_info[name] = {'type': 'file',
                                 'file_path': file_path,
                                 'load_as_rick': load_as_rick,
                                 'deep': deep,
                                 'load_lambda': load_lambda,
                                 'is_binary': is_binary,
                                 'encoding': encoding,
                                 'hot_load': hot_load
                                 }


    def _load_api(self,
                            url: str,
                            http_verb: str = 'GET',
                            headers: dict = None,
                            params: dict = None,
                            body: dict = None,
                            load_as_rick: bool = False,
                            deep: bool = False,
                            load_lambda: bool = False,
                            expected_http_status: int = 200):
        if http_verb.lower() == 'post':
            r = requests.post(url=url, data=body, headers=headers)
        else:
            r = requests.get(url=url, params=params, headers=headers)

        if r.status_code == expected_http_status:
            if r.headers.get('content-type', '').lower() == 'application/json':
                resp_input = r.json()
            else:
                resp_input = r.text

            if load_as_rick:
                args = copy.copy(self._init_args)
                args['load_lambda'] = load_lambda
                args['deep'] = deep

                return Rickle(resp_input, **args)
            else:
                return resp_input
        else:
            raise ValueError(f'Unexpected HTTP status code in response {r.status_code}')


    def add_api(self, name,
                      url: str,
                      http_verb: str = 'GET',
                      headers: dict = None,
                      params: dict = None,
                      body: dict = None,
                      load_as_rick: bool = False,
                      deep: bool = False,
                      load_lambda: bool = False,
                      expected_http_status: int = 200,
                      hot_load: bool = False):
        """
        Load a JSON response from a URL and create a Rick from it. This opens up dynamic possibility,
        but with that it also opens up extreme security vulnerabilities. Only ever load JSON objects from trusted sources.
        **Important note: Even with ``deep`` and ``load_lambda`` set to False, further API calls could be found within the source that loads lambda functions.**
        **Important note: Be careful to never self-reference an API call, i.e. don't load the same API from within itself to avoid infinte looping.**

        Args:
            name (str): Property name.
            url (str): URL to load from.
            http_verb (str): Either 'POST' or 'GET' allowed (default = 'GET').
            headers (dict): Key-value pair for headers (default = None).
            params (dict): Key-value pair for parameters (default = None).
            body (dict): Key-value pair for data (default = None).
            load_as_rick (bool): If true, loads and creates Rick from source, else loads the contents as dictionary (default = False).
            deep (bool): Internalize dictionary structures in lists (default = False).
            load_lambda (bool): Load lambda as code or strings (default = False).
            expected_http_status (int): Should a none 200 code be expected (default = 200).
            hot_load (bool): Load the data on calling or load it only once on start (cold) (default = False).

        """
        name = self._check_kw(name)
        if hot_load:
            try:
                from urllib3.util import parse_url
                try:
                    parsed = parse_url(url)
                    if (all([parsed.scheme, parsed.host]) and self._init_args['load_lambda']
                            and http_verb.lower().strip() in ['get', 'post', 'put']):
                        _body = dict(body) if body else None
                        _headers = dict(headers) if headers else None
                        _params = dict(params) if params else None
                        _load = f"""lambda self=self,\
                                            headers={_headers},\
                                            params={_params},\
                                            body={_body}:\
                                    self._load_api(url='{str(url)}', 
                                        http_verb='{str(http_verb)}', 
                                        headers=headers, 
                                        params=params, 
                                        body=body,
                                        load_as_rick={load_as_rick == True},
                                        deep={deep == True},
                                        load_lambda={load_lambda == True},
                                        expected_http_status={int(expected_http_status)})"""

                        self.__dict__.update({name: eval(_load)})
                    else:
                        raise ValueError(f"When trying to add lambda, one or more checks failed")
                except Exception as exc:
                    raise exc
            except Exception as exc:
                raise ValueError(f"At 'add_api', when trying to add lambda, this happened {exc}")

        else:
            result = self._load_api(url=url,
                                              http_verb=http_verb,
                                              headers=headers,
                                              params=params,
                                              body=body,
                                              load_as_rick=load_as_rick,
                                              deep=deep,
                                              load_lambda=load_lambda,
                                              expected_http_status=expected_http_status)

            self.__dict__.update({name: result})

        self._meta_info[name] = {'type': 'api',
                                 'url': url,
                                 'http_verb': http_verb,
                                 'headers': headers,
                                 'params': params,
                                 'body': body,
                                 'load_as_rick': load_as_rick,
                                 'deep': deep,
                                 'load_lambda': load_lambda,
                                 'expected_http_status': expected_http_status,
                                 'hot_load': hot_load
                                 }

    def _add_secret(self,
                    secret_id: str,
                    provider: str,
                    provider_access_key: Union[str, dict],
                    secret_version: str = None,
                    load_as_rick: bool = False,
                    deep: bool = False,
                    load_lambda: bool = False
                    ):
        provider = provider.strip().lower()

        if isinstance(provider_access_key, str):
            provider_access_key = Rickle(provider_access_key).dict()

        if provider == 'aws':
            import boto3
            from botocore.exceptions import ClientError

            client = boto3.session.Session(**provider_access_key).client('secretsmanager')
            try:
                args = {'SecretId': secret_id}
                if secret_version:
                    args['VersionId'] = secret_version
                secret = client.get_secret_value(**args)

            except ClientError as e:
                sys.stderr.write(f"Error while accessing secret {e.response['Error']['Code']}")
                raise e
            else:
                if 'SecretString' in secret:
                    secret_string = secret['SecretString']

                    if load_as_rick:
                        args = copy.copy(self._init_args)
                        args['load_lambda'] = load_lambda
                        args['deep'] = deep
                        return Rickle(secret_string, **args)
                    return secret_string
                else:
                    return secret['SecretBinary']
        elif provider == 'google':
            from google.cloud import secretmanager
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_info(
                provider_access_key)

            if secret_version:
                _secret_version_id = secret_version
            else:
                _secret_version_id = 'latest'

            client = secretmanager.SecretManagerServiceClient(credentials=credentials)
            name = f"projects/{provider_access_key['project_id']}/secrets/{secret_id}/versions/{_secret_version_id}"

            response = client.access_secret_version(name=name)

            if load_as_rick:
                args = copy.copy(self._init_args)
                args['load_lambda'] = load_lambda
                args['deep'] = deep
                return Rickle(response.payload.data.decode('UTF-8'), **args)

            return response.payload.data.decode('UTF-8')
        elif provider == 'azure':
            from azure.identity import ClientSecretCredential
            from azure.keyvault.secrets import SecretClient

            key_vault_uri = f"https://{provider_access_key['key_vault_name']}.vault.azure.net"

            credential = ClientSecretCredential(
                tenant_id=provider_access_key['tenant_id'],
                client_id=provider_access_key['client_id'],
                client_secret=provider_access_key['client_secret']
            )

            client = SecretClient(vault_url=key_vault_uri, credential=credential)

            secret = client.get_secret(name=secret_id, version=secret_version)

            if load_as_rick:
                args = copy.copy(self._init_args)
                args['load_lambda'] = load_lambda
                args['deep'] = deep
                return Rickle(secret.value, **args)
            return secret.value
        elif provider == 'hashicorp':
            import hvac

            client = hvac.Client(
                **provider_access_key
            )

            read_response = client.secrets.kv.read_secret_version(path=secret_id)

            secret = read_response['data']['data']

            if load_as_rick:
                args = copy.copy(self._init_args)
                args['load_lambda'] = load_lambda
                args['deep'] = deep
                return Rickle(secret, **args)
            return secret
        elif provider == 'oracle':
            import oci

            vault_client = oci.vault.VaultsClient(provider_access_key)

            secret_response = vault_client.get_secret(secret_id=secret_id)

            if load_as_rick:
                args = copy.copy(self._init_args)
                args['load_lambda'] = load_lambda
                args['deep'] = deep
                return Rickle(secret_response.data, **args)
            return secret_response.data
        elif provider == 'ibm':
            from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
            from ibm_secrets_manager_sdk.secrets_manager_v2 import SecretsManagerV2

            secrets_manager = SecretsManagerV2(
                authenticator=IAMAuthenticator(provider_access_key['apikey'])
            )
            secrets_manager.set_service_url(provider_access_key['service_url'])

            response = secrets_manager.get_secret(
                id=secret_id
            )

            secret_payload = response.result['payload']

            if load_as_rick:
                args = copy.copy(self._init_args)
                args['load_lambda'] = load_lambda
                args['deep'] = deep
                return Rickle(secret_payload, **args)
            return secret_payload
        else:
            raise ValueError(f"Provider name '{provider}' not supported")

    def add_secret(self,
                   name,
                   secret_id: str,
                   provider: str,
                   provider_access_key: Union[str, dict],
                   secret_version: str = None,
                   load_as_rick: bool = False,
                   deep: bool = False,
                   load_lambda: bool = False,
                   hot_load: bool = False):
        """
        Adds a secret from a cloud provider. Providers include ASW, Google, Azure, and Hashicorp.

        Note:
            The provider_access_key can either be a string or dict.
            A string can either be a JSON (or YAML) string or a file path to an access key file.

        Args:
            name (str): Property name.
            secret_id (str): The ID or name of the secret in the secret manager / key vault.
            provider (str): Either 'aws', 'google', 'azure'.
            provider_access_key (dict, str): Key/secrets or other access information. Dependent on ``provider``.
            secret_version (str): Version ID of the secret (default = None).
            load_as_rick (bool): If true, loads and creates Rick from source, else loads the contents as dictionary (default = False).
            deep (bool): Internalize dictionary structures in lists (default = False).
            load_lambda (bool): Load lambda as code or strings (default = False).
            hot_load (bool): Load the data on calling or load it only once on start (cold) (default = False).

        """
        name = self._check_kw(name)
        if hot_load:
            try:
                if isinstance(provider_access_key, str):
                    provider_access_key = f"'{provider_access_key}'"
                _load = f"""lambda self=self: self._add_secret(secret_id='{str(secret_id)}', 
                                                        provider='{str(provider)}', 
                                                        provider_access_key={provider_access_key}, 
                                                        secret_version={secret_version},
                                                        load_as_rick={load_as_rick == True},
                                                        deep={deep == True},
                                                        load_lambda={load_lambda == True})"""

                self.__dict__.update({name: eval(_load)})
            except Exception as exc:
                raise ValueError(f"At 'add_secret', when trying to add lambda, this happened {exc}")

        else:
            result = self._add_secret(secret_id=secret_id,
                                              provider=provider,
                                              provider_access_key=provider_access_key,
                                              secret_version=secret_version,
                                              load_as_rick=load_as_rick,
                                              deep=deep,
                                              load_lambda=load_lambda)

            self.__dict__.update({name: result})

        self._meta_info[name] = {'type': 'secret',
                                 'secret_id': secret_id,
                                 'provider': provider,
                                 'provider_access_key': provider_access_key,
                                 'secret_version': secret_version,
                                 'load_as_rick': load_as_rick,
                                 'deep': deep,
                                 'load_lambda': load_lambda,
                                 'hot_load': hot_load
                                 }


class UnsafeRickle(Rickle):

    def _iternalize(self, obj: dict, deep: bool, **init_args):
        if isinstance(obj, dict):
            for k, v in obj.items():
                k = self._check_kw(k)
                if isinstance(v, dict):
                    if 'type' in v.keys():
                        if v['type'] == 'env':
                            self.add_env(name=k,
                                                  load=v['load'],
                                                  default=v.get('default', None))
                            continue
                        if v['type'] == 'base64':
                            self.add_base64(name=k,
                                            load=v['load'])
                            continue
                        if v['type'] == 'file':
                            self.add_file(name=k,
                                               file_path=v['file_path'],
                                               load_as_rick=v.get('load_as_rick', False),
                                               deep=v.get('deep', False),
                                               load_lambda=v.get('load_lambda', False),
                                               is_binary=v.get('is_binary', False),
                                               encoding=v.get('encoding', 'utf-8'),
                                               hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'csv' :
                            self.add_csv(name=k,
                                              file_path_or_str=v['file_path'],
                                              fieldnames=v.get('fieldnames', None),
                                              load_as_rick=v.get('load_as_rick', False),
                                              encoding=v.get('encoding', 'utf-8'))
                            continue
                        if v['type'] == 'api':
                            self.add_api(name=k,
                                                   url=v['url'],
                                                   http_verb=v.get('http_verb', 'GET'),
                                                   headers=v.get('headers', None),
                                                   params=v.get('params', None),
                                                   body=v.get('body', None),
                                                   load_as_rick=v.get('load_as_rick', False),
                                                   load_lambda=v.get('load_lambda', False),
                                                   deep=v.get('deep', False),
                                                   expected_http_status=v.get('expected_http_status', 200),
                                                   hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'secret':
                            self.add_secret(name=k,
                                            secret_id=v['secret_id'],
                                            provider=v['provider'],
                                            provider_access_key=v.get('provider_access_key', dict()),
                                            secret_version=v.get('secret_version', None),
                                            load_as_rick=v.get('load_as_rick', False),
                                            load_lambda=v.get('load_lambda', False),
                                            deep=v.get('deep', False),
                                            hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'random':
                            self.add_random_value(name=k,
                                                  value_type=v['value_type'],
                                                  value_properties=v.get('value_properties', dict()),
                                                  hot_load=v.get('hot_load', False))
                            continue
                        if v['type'] == 'python':
                            name = v.get('name', k)
                            load = v['load']
                            args_dict = v.get('args', None)
                            imports = v.get('import', None)
                            is_method = v.get('is_method', False)

                            safe_load = os.getenv("RICKLE_UNSAFE_LOAD", False)
                            if init_args and init_args['load_lambda'] and safe_load:
                                self.add_python(name=name,
                                                  load=load,
                                                  args=args_dict,
                                                  imports=imports,
                                                  is_method=is_method)
                            else:
                                self.__dict__.update({k: v})
                            continue

                    self.__dict__.update({k: UnsafeRickle(base=v, deep=deep, strict=self._strict, **init_args)})
                    continue
                if isinstance(v, list) and deep:
                    new_list = list()
                    for i in v:
                        if isinstance(i, dict):
                            new_list.append(UnsafeRickle(base=i, deep=deep, strict=self._strict, **init_args))
                        else:
                            new_list.append(i)
                    self.__dict__.update({k: new_list})
                    continue
                self.__dict__.update({k: v})
        if isinstance(obj, list):
            for b in obj:
                if isinstance(b, dict):
                    self.__list__.append(UnsafeRickle(base=b, deep=deep, strict=self._strict, **init_args))

    def __init__(self, base: Union[dict, str, TextIOWrapper, list] = None,
                 deep: bool = False,
                 load_lambda: bool = False,
                 strict: bool = True,
                 **init_args):
        init_args['load_lambda'] = load_lambda
        init_args['deep'] = deep
        init_args['strict'] = strict
        super().__init__(base, **init_args)

    def __call__(self, path: str, **kwargs):
        """
        Rickle objects can be queried via a path string.

        Notes:
            '/' => root.
            '/name' => member.
            '/path/to/name?param=1' => lambda/function.
            '/name/[0]' => for lists.
            If '?' is in path the inline parameters are used and kwargs are ignored.

        Args:
            path (str): The path as a string, down to the last mentioned node.

        Returns:
            Any: Value of node of function.
        """

        if path == self._path_sep:
            return self

        if not path.startswith(self._path_sep):
            raise KeyError(f'Missing root path {self._path_sep} at {repr(self)}')

        list_index_match = re.match(r'/\[(\d+)\](/.+)?', path)
        path_start_index = 1
        if list_index_match:
            current_node = self.__list__[int(list_index_match.group(1))]
            path_start_index = 2
        else:
            current_node = self

        path_list = path.split(self._path_sep)

        for node_name in path_list[path_start_index:]:
            if '?' in node_name:
                node_name = node_name.split('?')[0]

            list_index_match = re.match(r'\[(\d+)\]', node_name)
            if list_index_match and isinstance(current_node, list):
                current_node = current_node[int(list_index_match.group(1))]
            else:
                current_node = current_node.get(node_name)
            if current_node is None:
                raise NameError(f'The path {path} could not be traversed. Alternatively use "get"')

        if '?' in path_list[-1]:
            import ast
            args_string = path_list[-1].split('?')[-1]
            args = {a.split('=')[0]: a.split('=')[1] for a in args_string.split('&')}
            type_guessed_args = dict()
            for n, v in args.items():
                v_stripped = v.strip()
                try:
                    literal = ast.literal_eval(v_stripped)
                except Exception as exc:
                    raise TypeError(f"Could not guess the parameter type, {exc}")

                if isinstance(literal, str):
                    # This is intentionally done to strip away the literal quotes
                    type_guessed_args[n] = v_stripped[1:-1]
                else:
                    type_guessed_args[n] = literal
            try:
                return current_node(**type_guessed_args)
            except Exception as exc:
                raise TypeError(
                    f'{exc} occurred. The node in the path {path} is of type {type(current_node)} or does not match the query')

        if inspect.isfunction(current_node):
            try:
                return current_node(**kwargs)
            except Exception as exc:
                raise TypeError(
                    f'{exc} occurred. The node in the path {path} is of type {type(current_node)} or does not match the query')

        else:
            return current_node

    def dict(self, serialised: bool = False):
        """
        Deconstructs the whole object into a Python dictionary.

        Args:
            serialised (bool): Give a Python dictionary in serialised (True) form or deserialised (default = False).

        Notes:
            Functions and lambdas are always given in serialised form.

        Returns:
            dict: of object.
        """
        d = dict()
        for key, value in self.__dict__.items():
            actual_key = key
            if key in self._keys_map.keys():
                actual_key = self._keys_map[key]
            if self._eval_name(key):
                continue
            if serialised and key in self._meta_info.keys():
                d[actual_key] = self._meta_info[key]
            # Revisit this at some later point
            elif key in self._meta_info.keys() and \
                    self._meta_info[key]['type'] in ['function', 'class_definition', 'module_import',
                                                     'base64']:
                # d[actual_key] = self._meta_info[key]
                continue
            elif key in self._meta_info.keys() and \
                    self._meta_info[key]['type'] in ['file', 'html_page', 'api_json'] and \
                    self._meta_info[key]['hot_load']:
                # d[actual_key] = self._meta_info[key]
                continue
            elif isinstance(value, BaseRickle):
                d[actual_key] = value.dict(serialised=serialised)
            elif isinstance(value, list):
                new_list = list()
                for element in value:
                    if isinstance(element, BaseRickle):
                        new_list.append(element.dict(serialised=serialised))
                    else:
                        new_list.append(element)
                d[actual_key] = new_list
            else:
                d[actual_key] = value
        return d

    def add_python(self, name, load, args: dict = None, imports: list = None,
                     return_function: bool = False,
                     is_method: bool = False):
        """
        Add a new Python function to Rick.

        Args:
            name (str): Property name.
            load (str): Python code containing the function.
            args (dict): Key-value pairs of arguments with default values (default = None).
            imports (list): Python modules to import (default = None).
            return_function (bool): Add to rickle or return the function (default = False).
            is_method (bool): Indicates whether class method source includes `self` (default = False).

        Examples:
            Basic example for adding to a PickleRick:
                >> test_rick = UnsafeRickle()

                >> load = '''
                        def tester(x, c):
                            y = x * 2 + c
                            return math.cos(y)
                        '''

                >> args = { 'x' : 0.42, 'c' : 1.7 }

                >> imports = ['math']

                >> test_rick.add_python('tester',load, args, imports)

                >> y = test_rick.tester(x=0.66, c=1.6)

        """
        if not return_function:
            name = self._check_kw(name)
        if imports and isinstance(imports, list):
            for i in imports:
                if 'import' in i:
                    exec(i, globals())
                else:
                    exec('import {}'.format(i), globals())
        suffix = str(uuid.uuid4().hex)

        _load = load.replace(f'def {name}(', f'def {name}{suffix}(')
        exec(_load, globals())
        if args and isinstance(args, dict):
            if is_method:
                arg_list = ['self=self']
                arg_list_defaults = ['self=self']
            else:
                arg_list = list()
                arg_list_defaults = list()
            for arg in args.keys():
                default_value = args[arg]
                if isinstance(default_value, str):
                    arg_list_defaults.append(f"{arg}='{default_value}'")
                else:
                    arg_list_defaults.append(f"{arg}={default_value}")
                arg_list.append(f"{arg}={arg}")

            func_string = 'lambda {args_default}: {name}({args})'.format(
                args_default=','.join(arg_list_defaults),
                args=','.join(arg_list),
                name=name + suffix)
        else:
            if is_method:
                func_string = 'lambda self: {name}(self)'.format(name=name + suffix)
            else:
                func_string = 'lambda: {name}()'.format(name=name + suffix)

        if return_function:
            return eval(func_string)
        self.__dict__.update({name: eval(func_string)})

        self._meta_info[name] = {'type': 'add_python', 'name': name, 'args': args, 'import': imports,
                                 'load': load, 'is_method': is_method}

T = TypeVar('T')

def object_to_rickle(obj, deep: bool = False, load_lambda: bool = False) -> UnsafeRickle:
    """
    Transforms a Python object into a Rickle.

    Args:
        obj: Any initialised Python object.
        deep (bool): Internalize dictionary structures in lists (default = False).
        load_lambda (bool): Load python code as code or strings (default = False).

    Returns:
        UnsafeRickle: A constructed UnsafeRickle object.
    """
    d = object_to_dict(obj)
    return UnsafeRickle(d, deep=deep, load_lambda=load_lambda)

def rickle_to_object(rickle: UnsafeRickle, cls: T, **args) -> T:
    """
    Takes an UnsafeRickle and initialises the class and updates attributes with the ones from the Rickle.

    Args:
        rickle (UnsafeRickle): Rickle to create from.
        cls (type): The class to initialise from.

    Returns:
        object: Initiliased `cls`.
    """
    if len(args) > 0:
        obj = cls(**args)
    else:
        obj = cls()

    for name, value in rickle.dict(True).items():
        if isinstance(value, dict) and 'type' in value.keys():
            if value['type'] == 'python':
                _name = value.get('name', name)
                _load = value['load']
                _args = value.get('args', None)
                _import = value.get('import', None)
                f = rickle.add_python(name=_name, load=_load, args=_args, imports=_import,
                                        return_function=True, is_method=True)

                obj.__dict__.update({_name: partial(f, obj)})
            continue
        obj.__dict__.update({name: value})

    return obj

