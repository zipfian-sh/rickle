# ASCCI Text found in this file was generated on
# https://patorjk.com/software/taag/
# Large heading using "Shaded Blocky" font
# Sub headings using "Small" font
import importlib.util
import sys

import rickle.__version__ as ver
import argparse
from rickle.tools import cli_bcolors
from rickle.tools import Schema
from rickle.tools import Converter
from rickle.tools import CLIError

from rickle.cli.schema import gen, check
from rickle.cli.conv import conv
from rickle.cli.serve import serve
from rickle.cli.obj import obj_get, obj_set, obj_put, obj_rm, obj_search, obj_type, obj_func, obj_find

GITHUB_DOCS_URL = "https://github.com/zipfian-sh/rickle/blob/master/docs/source/cli_tools.rst#cli-tools"

def main():
    supported_list = f"""
- {cli_bcolors.OKBLUE}YAML (r/w){cli_bcolors.ENDC}
- {cli_bcolors.OKBLUE}JSON (r/w){cli_bcolors.ENDC}
- {cli_bcolors.OKBLUE}TOML (r/w){cli_bcolors.ENDC}
- {cli_bcolors.OKBLUE}INI (r/w){cli_bcolors.ENDC}"""

    if importlib.util.find_spec('dotenv'):
        supported_list = f"{supported_list}\n- {cli_bcolors.OKBLUE}ENV (r){cli_bcolors.ENDC}"
    if importlib.util.find_spec('xmltodict'):
        supported_list = f"{supported_list}\n- {cli_bcolors.OKBLUE}XML (r/w){cli_bcolors.ENDC}"

    parser = argparse.ArgumentParser(
        prog='rickle',
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"""
---------------------------------------------------------------------------------------------{cli_bcolors.OKGREEN}
██████╗ ██╗ ██████╗██╗  ██╗██╗     ███████╗
██╔══██╗██║██╔════╝██║ ██╔╝██║     ██╔════╝
██████╔╝██║██║     █████╔╝ ██║     █████╗  
██╔══██╗██║██║     ██╔═██╗ ██║     ██╔══╝  
██║  ██║██║╚██████╗██║  ██╗███████╗███████╗
╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝{cli_bcolors.ENDC}

{cli_bcolors.HEADER}YAML (+JSON, TOML...) tools for Python{cli_bcolors.ENDC} (version {ver}).
---------------------------------------------------------------------------------------------
Supported file types ({cli_bcolors.OKBLUE}-t{cli_bcolors.ENDC}) include:
{supported_list}
---------------------------------------------------------------------------------------------
""",
        epilog=f"""
---------------------------------------------------------------------------------------------
\nFor usage examples, visit:\n{cli_bcolors.UNDERLINE}{GITHUB_DOCS_URL}{cli_bcolors.ENDC}\n\n
---------------------------------------------------------------------------------------------
        """
    )
    parser.add_argument(
        "--version",
        "-v",
        help="show version number",
        action="version",
        version=f'%(prog)s {ver}'
    )
    parser.add_argument('--output-type',
                             dest='OUTPUT_TYPE',
                             type=str,
                             metavar='',
                             help=f"output {cli_bcolors.OKBLUE}file type{cli_bcolors.ENDC} (default = input type or YAML)",
                             default=None)


    subparsers = parser.add_subparsers()

    #################### CONV #####################
    # ░░      ░░░      ░░   ░░░  ░  ░░░░  ░
    # ▒  ▒▒▒▒  ▒  ▒▒▒▒  ▒    ▒▒  ▒  ▒▒▒▒  ▒
    # ▓  ▓▓▓▓▓▓▓  ▓▓▓▓  ▓  ▓  ▓  ▓▓  ▓▓  ▓▓
    # █  ████  █  ████  █  ██    ███    ███
    # ██      ███      ██  ███   ████  ████

    parser_conv = subparsers.add_parser('conv',
                                        help=f'{cli_bcolors.OKBLUE}converting{cli_bcolors.ENDC} files between formats',
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        description=f"""
{cli_bcolors.HEADER}Tool for converting files to or from different formats{cli_bcolors.ENDC}.
If input is piped, output is printed. For INPUT or INPUT_DIRECTORY output is written to file(s).

Examples: 

    $ cat config.yaml | rickle --output-type JSON conv
    $ rickle --output-type JSON conv --input conf1.yaml conf2.yaml 

When no output type is defined, the file extension (suffix) is used to infer the output type.    

    $ rickle conv --input conf1.yaml --output config.toml

Supported formats: 
{Converter.supported}
    """)

    parser_conv.add_argument('--input',
                             dest='INPUT',
                             type=str,
                             help=f"{cli_bcolors.OKBLUE}input file{cli_bcolors.ENDC}(s) to convert",
                             nargs='+',
                             metavar='',
                             default=None)
    parser_conv.add_argument('--input-directory',
                             dest='INPUT_DIRECTORY',
                             type=str,
                             metavar='',
                             help=f"{cli_bcolors.OKBLUE}directory{cli_bcolors.ENDC} of input files",
                             default=None)
    parser_conv.add_argument('--output',
                             dest='OUTPUT',
                             type=str,
                             metavar='',
                             help=f"{cli_bcolors.OKBLUE}output file{cli_bcolors.ENDC} names, only if --input given",
                             nargs='+',
                             default=None)
    parser_conv.add_argument('--input-type',
                             dest='INPUT_TYPE',
                             type=str,
                             metavar='',
                             help=f"optional input {cli_bcolors.OKBLUE}type{cli_bcolors.ENDC} (type inferred if none)",
                             default=None)
    parser_conv.add_argument('--verbose',
                             '-v',
                             dest='VERBOSE',
                             action='store_true',
                             help=f"{cli_bcolors.OKBLUE}verbose{cli_bcolors.ENDC} output", )

    parser_conv.set_defaults(func=conv)

    #################### OBJ #####################
    # ░░      ░░       ░░        ░
    # ▒  ▒▒▒▒  ▒  ▒▒▒▒  ▒▒▒▒▒▒▒  ▒
    # ▓  ▓▓▓▓  ▓       ▓▓▓▓▓▓▓▓  ▓
    # █  ████  █  ████  █  ████  █
    # ██      ██       ███      ██

    parser_obj = subparsers.add_parser('obj',
                                       help=f'tool for reading or editing {cli_bcolors.OKBLUE}objects{cli_bcolors.ENDC}',
                                       formatter_class=argparse.RawTextHelpFormatter,
                                       description=f"""
{cli_bcolors.HEADER}Tool for reading or editing files in different formats{cli_bcolors.ENDC}.
Input is used to create a Rickle {cli_bcolors.HEADER}object{cli_bcolors.ENDC} which can then be queried and further modified.
        """,
                                       )

    parser_obj.add_argument('--input',
                            dest='INPUT',
                            type=str,
                            metavar='',
                            help=f"{cli_bcolors.OKBLUE}input file{cli_bcolors.ENDC} to create object from",
                            default=None)
    parser_obj.add_argument('--output',
                            dest='OUTPUT',
                            type=str,
                            metavar='',
                            help=f"write to {cli_bcolors.OKBLUE}output file{cli_bcolors.ENDC}",
                            required=False)
    parser_obj.add_argument('--load-lambda',
                            '-l',
                            dest='LOAD_LAMBDA',
                            action='store_true',
                            help=f"load {cli_bcolors.OKBLUE}lambda{cli_bcolors.ENDC} types",
                            default=False)

    subparsers_obj = parser_obj.add_subparsers()

    #################### OBJ - GET #####################
    #   ___ ___ _____
    #  / __| __|_   _|
    # | (_ | _|  | |
    #  \___|___| |_|

    get_obj_parser = subparsers_obj.add_parser('get',
                                               help=f'{cli_bcolors.OKBLUE}getting{cli_bcolors.ENDC} values from objects',
                                               formatter_class=argparse.RawTextHelpFormatter,
                                               description=f"""
{cli_bcolors.HEADER}Tool for getting values from objects{cli_bcolors.ENDC}.

Examples: 

    $ cat config.yaml | rickle obj get /path/to
    $ rickle --output-type JSON obj --input conf1.yaml get /path/to  

""", )

    get_obj_parser.add_argument('key',
                                type=str,
                                help=f"{cli_bcolors.OKBLUE}key{cli_bcolors.ENDC} (path) to get value",
                                metavar='key')

    get_obj_parser.set_defaults(func=obj_get)

    #################### OBJ - SET #####################
    #  ___ ___ _____
    # / __| __|_   _|
    # \__ \ _|  | |
    # |___/___| |_|

    set_obj_parser = subparsers_obj.add_parser('set',
                                               formatter_class=argparse.RawTextHelpFormatter,
                                               help=f'{cli_bcolors.OKBLUE}setting{cli_bcolors.ENDC} values in objects',
                                               description=f"""
{cli_bcolors.HEADER}Tool for setting values in objects{cli_bcolors.ENDC}.

Setting a value requires the path to exist in the input. Use "put" for creating new document paths.

Examples: 

    $ cat config.yaml | rickle obj set /path/to new_value
    $ rickle obj --input conf1.yaml --output-type JSON set /path/to new_value  

""",
                                               )

    set_obj_parser.add_argument('key',
                                type=str,
                                help=f"{cli_bcolors.OKBLUE}key{cli_bcolors.ENDC} to set value",
                                metavar='key')
    set_obj_parser.add_argument('value',
                                type=str,
                                help=f"{cli_bcolors.OKBLUE}value{cli_bcolors.ENDC} to set",
                                metavar='value')

    set_obj_parser.set_defaults(func=obj_set)

    #################### OBJ - PUT #####################
    #   ___ _   _ _____
    #  | _ \ | | |_   _|
    #  |  _/ |_| | | |
    #  |_|  \___/  |_|
    #

    put_obj_parser = subparsers_obj.add_parser('put',
                                               formatter_class=argparse.RawTextHelpFormatter,
                                               help=f'{cli_bcolors.OKBLUE}putting{cli_bcolors.ENDC} values in objects',
                                               description=f"""
    {cli_bcolors.HEADER}Tool for putting values in objects with new paths{cli_bcolors.ENDC}.

    Examples: 

        $ cat config.yaml | rickle obj put /path/not/existing new_value
        $ rickle obj --input conf1.yaml --output-type JSON set /newly/created/path/to new_value  

    """,
                                               )

    put_obj_parser.add_argument('key',
                                type=str,
                                help=f"{cli_bcolors.OKBLUE}key{cli_bcolors.ENDC} to put value",
                                metavar='key')
    put_obj_parser.add_argument('value',
                                type=str,
                                help=f"{cli_bcolors.OKBLUE}value{cli_bcolors.ENDC} to put",
                                metavar='value')

    put_obj_parser.set_defaults(func=obj_put)


    #################### OBJ - DEL #####################
    #  ___  ___ _
    # |   \| __| |
    # | |) | _|| |__
    # |___/|___|____|

    rm_obj_parser = subparsers_obj.add_parser('rm',
                                               formatter_class=argparse.RawTextHelpFormatter,
                                               help=f'for {cli_bcolors.OKBLUE}removing{cli_bcolors.ENDC} keys (paths) in objects',
                                               description=f"""
{cli_bcolors.HEADER}Tool for removing keys (paths) in objects{cli_bcolors.ENDC}.

Examples: 

    $ cat config.yaml | rickle obj rm /path/to 
""", )

    rm_obj_parser.add_argument('key',
                                type=str,
                                help=f"{cli_bcolors.OKBLUE}key{cli_bcolors.ENDC} to delete",
                                metavar='key')

    rm_obj_parser.set_defaults(func=obj_rm)

    #################### OBJ - TYPE #####################
    #  _______   _____ ___
    # |_   _\ \ / / _ \ __|
    #   | |  \ V /|  _/ _|
    #   |_|   |_| |_| |___|

    type_obj_parser = subparsers_obj.add_parser('type',
                                                formatter_class=argparse.RawTextHelpFormatter,
                                                help=f'printing value {cli_bcolors.OKBLUE}type{cli_bcolors.ENDC} ',
                                                description=f"""
{cli_bcolors.HEADER}Tool for printing the type of the value for a key in the object{cli_bcolors.ENDC}.

Examples: 

    $ cat config.yaml | rickle obj type /path/to 

Types depend on --output-type and can be the following (default is JSON):

    Python |    YAML |    JSON |      TOML |            XML |
    =========================================================
    str    |     str |  string |    String |      xs:string |
    int    |     int | integer |   Integer |     xs:integer |
    float  |   float |  number |     Float |     xs:decimal |
    bool   | boolean | boolean |   Boolean |     xs:boolean |
    list   |     seq |   array |     Array |    xs:sequence |
    dict   |     map |  object | Key/Value | xs:complexType |
    bytes  |  binary |         |           |                |
    ---------------------------------------------------------
    *      |  Python |  object |     Other |         xs:any |

""", )

    type_obj_parser.add_argument('key',
                                 type=str,
                                 help=f"{cli_bcolors.OKBLUE}key{cli_bcolors.ENDC} to print value type",
                                 metavar='key')

    type_obj_parser.set_defaults(func=obj_type)

    #################### OBJ - SEARCH #####################
    #  ___ ___   _   ___  ___ _  _
    # / __| __| /_\ | _ \/ __| || |
    # \__ \ _| / _ \|   / (__| __ |
    # |___/___/_/ \_\_|_\\___|_||_|

    search_obj_parser = subparsers_obj.add_parser('search',
                                                  formatter_class=argparse.RawTextHelpFormatter,
                                                  help=f'for {cli_bcolors.OKBLUE}searching{cli_bcolors.ENDC} keys (paths) in objects',
                                                  description=f"""
{cli_bcolors.HEADER}Tool for searching keys in objects{cli_bcolors.ENDC}.

Examples: 

    $ cat config.yaml | rickle obj search key

Only the following --output-type is allowed: YAML, JSON, and ARRAY (default). Using ARRAY will only print the path(s).


""", )

    search_obj_parser.add_argument('key',
                                   type=str,
                                   help=f"{cli_bcolors.OKBLUE}key{cli_bcolors.ENDC} to search",
                                   metavar='key')
    search_obj_parser.add_argument('--parent',
                                 '-p',
                                 dest="PARENT_ONLY",
                                 action='store_true',
                                 default=False,
                                 help=f"only list {cli_bcolors.OKBLUE}parent{cli_bcolors.ENDC} node", )

    search_obj_parser.set_defaults(func=obj_search)

    #################### OBJ - FIND #####################
    #   ___ ___ _  _ ___
    #  | __|_ _| \| |   \
    #  | _| | || .` | |) |
    #  |_| |___|_|\_|___/
    #

    find_obj_parser = subparsers_obj.add_parser('find',
                                                  formatter_class=argparse.RawTextHelpFormatter,
                                                  help=f'for {cli_bcolors.OKBLUE}finding{cli_bcolors.ENDC} key/value (paths) in objects',
                                                  description=f"""
{cli_bcolors.HEADER}Tool for finding key/value pairs in objects{cli_bcolors.ENDC}.

Examples: 

    $ cat config.yaml | rickle obj find "key=value"
    $ cat config.yaml | rickle obj find --or "threshold < 0.2" "/mean/param_one > 0.8"
    $ cat config.yaml | rickle obj find --and "threshold gt 0.2" "threshold lt 0.8" -p

Only the following --output-type is allowed: YAML, JSON, and ARRAY (default). Using ARRAY will only print the path(s).
Either key or --or / --and can be used, with key taking precedence. Both --or and --and can be combined with the first 
being executed and then the later. Using --parent / -p will output the parent node paths. Comparison operators include:
    
    Comparison         |  op | alt |
    ================================
    equals             |   = |  eq |
    not equals         |  != |  ne |
    less than          |   < |  lt |
    greater than       |   > |  gt |
    less than equal    |  <= | lte |
    greater than equal |  >= | gte |
    --------------------------------

    """, )

    find_obj_parser.add_argument('key',
                                   type=str,
                                   help=f"{cli_bcolors.OKBLUE}key / value{cli_bcolors.ENDC} to find",
                                   nargs='?',
                                   default=None,
                                   metavar='key')
    find_obj_parser.add_argument('--or',
                                 help=f"list of {cli_bcolors.OKBLUE}OR{cli_bcolors.ENDC} conditions",
                                 nargs='+',
                                 default=[],
                                 dest='OR')
    find_obj_parser.add_argument('--and',
                                 help=f"list of {cli_bcolors.OKBLUE}AND{cli_bcolors.ENDC} conditions",
                                 nargs='+',
                                 default=[],
                                 dest='AND')
    find_obj_parser.add_argument('--parent',
                              '-p',
                              dest="PARENT_ONLY",
                              action='store_true',
                              default=False,
                              help=f"only list {cli_bcolors.OKBLUE}parent{cli_bcolors.ENDC} node(s)", )

    find_obj_parser.set_defaults(func=obj_find)


    #################### OBJ - FUNC #####################
    #  ___ _   _ _  _  ___
    # | __| | | | \| |/ __|
    # | _|| |_| | .` | (__
    # |_|  \___/|_|\_|\___|

    func_obj_parser = subparsers_obj.add_parser('func',
                                                formatter_class=argparse.RawTextHelpFormatter,
                                                help=f'executing {cli_bcolors.OKBLUE}functions{cli_bcolors.ENDC} defined in objects',
                                                description=f"""
{cli_bcolors.HEADER}Tool for executing functions defined in objects{cli_bcolors.ENDC}.
To enable unsafe usage, the environment variable {cli_bcolors.WARNING}RICKLE_UNSAFE_LOAD{cli_bcolors.ENDC} must be set and {cli_bcolors.WARNING}--load-lambda{cli_bcolors.ENDC} passed.  

Examples: 

    $ export RICKLE_UNSAFE_LOAD=1 
    $ cat config.yaml | rickle obj --load-lambda func /path/to param1:int=1 param2:str=2 

Every param needs to have an explicit type, indicated by a colon and the Python type name:

    - int    - str
    - float  - list
    - bool   - dict

Examples: 

    $ cat app.yaml | rickle obj --load-lambda func /path/to things:list="['foo','bar']"

This will pass a list called "things". To automatically infer the types, use --infer:

    $ cat app.yaml | rickle obj --load-lambda func /path/to --infer things="['foo','bar']"

This will infer input params. 

{cli_bcolors.WARNING}There are major security risks involved in using this functionality!{cli_bcolors.ENDC}

{cli_bcolors.FAIL}{cli_bcolors.BOLD}{cli_bcolors.UNDERLINE}Warning: Only use on trusted sources (files, urls, etc.){cli_bcolors.ENDC}
""", )

    func_obj_parser.add_argument('--infer',
                                 action='store_true',
                                 help=f"{cli_bcolors.OKBLUE}infer parameter{cli_bcolors.ENDC} types",
                                 default=False)
    func_obj_parser.add_argument('key',
                                 type=str,
                                 help=f"{cli_bcolors.OKBLUE}key{cli_bcolors.ENDC} (name) of function",
                                 metavar='key')
    func_obj_parser.add_argument('params',
                                 type=str,
                                 help=f"{cli_bcolors.OKBLUE}params{cli_bcolors.ENDC} for function",
                                 metavar='params', nargs='+')

    func_obj_parser.set_defaults(func=obj_func)

    #################### SERVE #####################
    # ░░      ░░        ░       ░░  ░░░░  ░        ░
    # ▒  ▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒  ▒▒▒▒  ▒  ▒▒▒▒  ▒  ▒▒▒▒▒▒▒
    # ▓▓      ▓▓      ▓▓▓       ▓▓▓  ▓▓  ▓▓      ▓▓▓
    # ███████  █  ███████  ███  ████    ███  ███████
    # ██      ██        █  ████  ████  ████        █

    if importlib.util.find_spec('twisted'):
        parser_serve = subparsers.add_parser('serve',
                                             help=f'serving objects through {cli_bcolors.OKBLUE}http(s){cli_bcolors.ENDC}',
                                             formatter_class=argparse.RawTextHelpFormatter,
                                             description=f"""
{cli_bcolors.HEADER}Tool for serving objects through http(s){cli_bcolors.ENDC}.
By default served as JSON. The path separator is set to / as default. 

Examples: 

    $ cat app.yaml | rickle serve

The host and port can be specified:

    $ cat app.yaml | rickle serve --host localhost --port 8087

Adding --private-key and --certificate will serve the object over SSL:

    $ cat app.yaml | rickle serve --private-key my_local.pem --certificate my_local.crt

Unsafe usage like functions can be enabled:

    $ export RICKLE_UNSAFE_LOAD=1 
    $ cat app.yaml | rickle serve --load-lambda --unsafe 

{cli_bcolors.WARNING}There are major security risks involved in using this functionality!{cli_bcolors.ENDC}

{cli_bcolors.FAIL}{cli_bcolors.BOLD}{cli_bcolors.UNDERLINE}Warning: Only use on trusted sources (files, urls, etc.){cli_bcolors.ENDC}
""", )

        parser_serve.add_argument('--input',
                                  dest="INPUT",
                                  type=str,
                                  help=f"{cli_bcolors.OKBLUE}input{cli_bcolors.ENDC} file to serve",
                                  default=None,
                                  metavar='')
        # TODO implement config
        # parser_serve.add_argument('--config',
        #                           dest='CONFIG',
        #                           type=str,
        #                           help=f"{cli_bcolors.OKBLUE}config{cli_bcolors.ENDC} file path",
        #                           default=None,
        #                           metavar='')
        parser_serve.add_argument('--host',
                                  dest='HOST',
                                  type=str,
                                  help=f"{cli_bcolors.OKBLUE}host address{cli_bcolors.ENDC} (default = localhost)",
                                  default='localhost',
                                  metavar=''
                                  )
        parser_serve.add_argument('--port',
                                  dest="PORT",
                                  type=int,
                                  help=f"{cli_bcolors.OKBLUE}port{cli_bcolors.ENDC} number (default = 8080)",
                                  default=8080,
                                  metavar='')
        parser_serve.add_argument('--private-key',
                                  dest='PRIVATE_KEY',
                                  type=str,
                                  help=f"{cli_bcolors.OKBLUE}private key{cli_bcolors.ENDC} file path",
                                  default=None,
                                  metavar='')
        parser_serve.add_argument('--certificate',
                                  dest='CERTIFICATE',
                                  type=str,
                                  help=f"ssl {cli_bcolors.OKBLUE}certificate{cli_bcolors.ENDC} file path",
                                  default=None,
                                  metavar='')
        parser_serve.add_argument('--auth',
                                  dest='AUTH',
                                  type=str,
                                  help=f"basic {cli_bcolors.OKBLUE}auth{cli_bcolors.ENDC} (username:password)",
                                  default=None,
                                  metavar='')
        parser_serve.add_argument('--load-lambda',
                                  '-l',
                                  dest="LOAD_LAMBDA",
                                  action='store_true',
                                  help=f"load {cli_bcolors.OKBLUE}lambda{cli_bcolors.ENDC} true",
                                  default=False)

        parser_serve.add_argument('--unsafe',
                                  dest="UNSAFE",
                                  action='store_true',
                                  help=f"load {cli_bcolors.OKBLUE}UnsafeRickle{cli_bcolors.ENDC} ({cli_bcolors.FAIL}VERY UNSAFE{cli_bcolors.ENDC})",
                                  default=False, )

        parser_serve.add_argument('--browser',
                                  '-b',
                                  dest="BROWSER",
                                  action='store_true',
                                  help=f"open {cli_bcolors.OKBLUE}browser{cli_bcolors.ENDC}", )
        parser_serve.add_argument('--serialised',
                                  '-s',
                                  dest="SERIALISED",
                                  action='store_true',
                                  help=f"serve as {cli_bcolors.OKBLUE}serialised{cli_bcolors.ENDC} data (default = false)",
                                  default=False)

        parser_serve.set_defaults(func=serve)

    #################### SCHEMA #####################
    # ░░      ░░░      ░░  ░░░░  ░        ░  ░░░░  ░░      ░░
    # ▒  ▒▒▒▒▒▒▒  ▒▒▒▒  ▒  ▒▒▒▒  ▒  ▒▒▒▒▒▒▒   ▒▒   ▒  ▒▒▒▒  ▒
    # ▓▓      ▓▓  ▓▓▓▓▓▓▓        ▓      ▓▓▓        ▓  ▓▓▓▓  ▓
    # ███████  █  ████  █  ████  █  ███████  █  █  █        █
    # ██      ███      ██  ████  █        █  ████  █  ████  █

    parser_schema = subparsers.add_parser('schema',
                                          help=f'generating and checking {cli_bcolors.OKBLUE}schemas{cli_bcolors.ENDC} of files',
                                          formatter_class=argparse.RawTextHelpFormatter,
                                          description=f"""
{cli_bcolors.HEADER}Tool for generating and checking schemas of several different formats{cli_bcolors.ENDC}.

Supported formats: 
{Schema.supported}
""", )

    schema_subparsers = parser_schema.add_subparsers()

    #################### SCHEMA - CHECK ############
    #   ___ _  _ ___ ___ _  __
    #  / __| || | __/ __| |/ /
    # | (__| __ | _| (__| ' <
    #  \___|_||_|___\___|_|\_\

    parser_schema_check = schema_subparsers.add_parser('check',
                                                       help=f'{cli_bcolors.OKBLUE}checking{cli_bcolors.ENDC} schemas of files',
                                                       formatter_class=argparse.RawTextHelpFormatter,
                                                       description=f"""
{cli_bcolors.HEADER}Tool for checking schemas of files{cli_bcolors.ENDC}.

Examples: 

    $ cat config.yaml | rickle schema check --schema config.schema.yaml

Which will print OK or FAIL depending on success. For more detailed output the --verbose option can be used:

    $ cat config.yaml | rickle schema check --schema config.schema.yaml --verbose

To silence the OK/FAIL output, --silence can be used. If input is piped and the check fails, exit code 1 is returned.

Can also be validated using {cli_bcolors.OKBLUE}jsonschema{cli_bcolors.ENDC} (if installed) by using --json-schema.
See {cli_bcolors.UNDERLINE}https://python-jsonschema.readthedocs.io{cli_bcolors.ENDC} for more.
""", )

    parser_schema_check.add_argument('--input',
                                     dest='INPUT',
                                     type=str,
                                     help=f"{cli_bcolors.OKBLUE}input file{cli_bcolors.ENDC}(s) to check",
                                     nargs='+',
                                     metavar='')
    parser_schema_check.add_argument('--input-directory',
                                     type=str,
                                     dest='INPUT_DIRECTORY',
                                     help=f"{cli_bcolors.OKBLUE}directory{cli_bcolors.ENDC}(s) of files to check",
                                     default=None,
                                     metavar='')

    parser_schema_check.add_argument('--schema',
                                     dest='SCHEMA',
                                     type=str,
                                     help=f"{cli_bcolors.OKBLUE}schema definition file{cli_bcolors.ENDC} to compare",
                                     metavar='',
                                     )

    parser_schema_check.add_argument('--fail-directory',
                                     dest='FAIL_DIRECTORY',
                                     type=str,
                                     help=f"{cli_bcolors.OKBLUE}directory{cli_bcolors.ENDC} to move failed files to",
                                     metavar='')

    parser_schema_check.add_argument('--verbose',
                                     '-v',
                                     dest='VERBOSE',
                                     action='store_true',
                                     help=f"{cli_bcolors.OKBLUE}verbose{cli_bcolors.ENDC} output", )
    parser_schema_check.add_argument('--silent',
                                     '-s',
                                     dest='SILENT',
                                     action='store_true',
                                     help=f"{cli_bcolors.OKBLUE}silence{cli_bcolors.ENDC} output", )
    parser_schema_check.add_argument('--json-schema',
                                     '-j',
                                     dest='JSON_SCHEMA',
                                     action='store_true',
                                     help=f"validate as {cli_bcolors.OKBLUE}json schema{cli_bcolors.ENDC}", )

    parser_schema_check.set_defaults(func=check)

    #################### SCHEMA - GEN ############
    #   ___ ___ _  _
    #  / __| __| \| |
    # | (_ | _|| .` |
    #  \___|___|_|\_|

    parser_schema_gen = schema_subparsers.add_parser('gen',
                                                     help=f'tool for {cli_bcolors.OKBLUE}generating{cli_bcolors.ENDC} schemas of files',
                                                     formatter_class=argparse.RawTextHelpFormatter,
                                                     description=f"""
{cli_bcolors.HEADER}Tool for generating schemas of files{cli_bcolors.ENDC}.
Generates schemas from input. 

Examples: 

    $ cat config.yaml | rickle schema gen 
    $ rickle --output-type JSON schema gen --input config.yaml --extras

If --input or --input-directory are passed the output will be to files. If piped, the output is printed.
""", )

    parser_schema_gen.add_argument('--input',
                                   dest='INPUT',
                                   type=str,
                                   help=f"{cli_bcolors.OKBLUE}input file{cli_bcolors.ENDC}(s) to generate from",
                                   nargs='+',
                                   metavar='')
    parser_schema_gen.add_argument('--output',
                                   dest='OUTPUT',
                                   type=str,
                                   help=f"{cli_bcolors.OKBLUE}output file{cli_bcolors.ENDC}(s) to write to",
                                   nargs='+',
                                   metavar='')
    parser_schema_gen.add_argument('--input-directory',
                                   dest='INPUT_DIRECTORY',
                                   type=str,
                                   help=f"{cli_bcolors.OKBLUE}directory{cli_bcolors.ENDC}(s) of files to generate from",
                                   default=None,
                                   metavar='')
    parser_schema_gen.add_argument('--silent',
                                   '-s',
                                   dest='SILENT',
                                   action='store_true',
                                   help=f"{cli_bcolors.OKBLUE}silence{cli_bcolors.ENDC} output", )
    parser_schema_gen.add_argument('--extras',
                                   '-e',
                                   dest='EXTRAS',
                                   action='store_true',
                                   help=f"include {cli_bcolors.OKBLUE}extra{cli_bcolors.ENDC} properties", )

    parser_schema_gen.set_defaults(func=gen)

    #################################################
    # Making a bit more friendly for debugging
    try:
        args = parser.parse_args()
        args.func(args)
    except AttributeError:
        parser.print_help(sys.stderr)
        sys.exit(2)
    except CLIError as cli_exc:
        sys.stderr.write(f'\n{cli_bcolors.FAIL}error: {cli_exc.message}{cli_bcolors.ENDC}\n\n')
        if cli_exc.cli_tool == CLIError.CLITool.CONV:
            parser_conv.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.OBJ:
            parser_obj.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.SERVE:
            parser_serve.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.SCHEMA:
            parser_schema.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.OBJ_GET:
            get_obj_parser.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.OBJ_SET:
            set_obj_parser.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.OBJ_DEL:
            rm_obj_parser.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.OBJ_TYPE:
            type_obj_parser.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.OBJ_SEARCH:
            search_obj_parser.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.OBJ_FUNC:
            func_obj_parser.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.SCHEMA_CHECK:
            parser_schema_check.print_help(sys.stderr)
        elif cli_exc.cli_tool == CLIError.CLITool.SCHEMA_GEN:
            parser_schema_gen.print_help(sys.stderr)
        else:
            parser.print_help(sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()