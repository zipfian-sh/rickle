import importlib
import json
import os
import sys
from pathlib import Path

import yaml
import tomli_w as tomlw


from rickle.tools import CLIError, convert_string, infer_read_file_type, unparse_ini, cli_bcolors, toml_null_stripper


def conv(args):
    try:
        output_type = args.OUTPUT_TYPE.lower() if args.OUTPUT_TYPE else 'yaml'
        if args.INPUT:

            if args.OUTPUT:
                if len(args.OUTPUT) != len(args.INPUT):
                    raise CLIError(f"Length mismatch input ({len(args.INPUT)}) and output ({len(args.OUTPUT)})!",
                                   cli_tool=CLIError.CLITool.SCHEMA_GEN)
                zipped = zip(args.INPUT, args.OUTPUT)
            else:
                output_files = list()
                for input_file in args.INPUT:
                    output_files.append(f"{os.path.splitext(input_file)[0]}.schema.{output_type}")
                zipped = zip(args.INPUT, output_files)

            convert_files(output_type, zipped, args.VERBOSE)
        elif args.INPUT_DIRECTORY:

            input_files = list()

            dir_path = Path(args.INPUT_DIRECTORY)

            known_extensions = ['yaml', 'yml', 'json', 'toml', 'ini']
            if importlib.util.find_spec('xmltodict'):
                known_extensions.append('xml')
            if importlib.util.find_spec('dotenv'):
                known_extensions.append('env')

            for ext in known_extensions:
                input_files.extend(list(dir_path.glob(f"*.{ext}")))

            output_files = list()
            for input_file in args.INPUT:
                output_files.append(f"{os.path.splitext(input_file)[0]}.schema.{output_type}")
            zipped = zip(args.INPUT, output_files)

            convert_files(output_type, zipped, args.VERBOSE)
        else:
            data = sys.stdin.read()

            converted = convert_string(input_string=data,
                                       input_type=args.INPUT_TYPE,
                                       output_type=output_type)

            print(converted)

    except Exception as exc:
        raise CLIError(message=str(exc), cli_tool=CLIError.CLITool.CONV)


def convert_files(output_type, zipped, verbose):
    for pair in zipped:
        input_data = infer_read_file_type(pair[0])
        output_file = Path(pair[1])

        suffix = output_file.suffix.lower() if output_file.suffix else f".{output_type}"

        if suffix == '.yaml':
            with output_file.open("w") as fout:
                yaml.safe_dump(input_data, fout, sort_keys=False)

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

        if verbose:
            print(f"{cli_bcolors.OKBLUE}{pair[0]}{cli_bcolors.ENDC} -> {cli_bcolors.OKBLUE}{pair[1]}{cli_bcolors.ENDC}")
        continue
