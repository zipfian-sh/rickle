import importlib.util
import os
import sys
from pathlib import Path

from rickle.tools import cli_bcolors, CLIError, infer_read_file_type

from rickle.schema import Schema, validate_files

def check(args):
    try:
        if args.INPUT:

            validate_files(Schema(args.SCHEMA),
                           output_dir=args.FAIL_DIRECTORY,
                           input_files=args.INPUT,
                           use_json_schema=args.JSON_SCHEMA,
                           verbose_print=args.VERBOSE,
                           silent=args.SILENT)
        elif args.INPUT_DIRECTORY:
            input_files = list()

            dir_path = Path(args.INPUT_DIRECTORY)
            input_files.extend(list(dir_path.glob("*.yaml")))
            input_files.extend(list(dir_path.glob("*.yml")))
            input_files.extend(list(dir_path.glob("*.json")))
            input_files.extend(list(dir_path.glob("*.toml")))
            input_files.extend(list(dir_path.glob("*.xml")))

            validate_files(Schema(args.SCHEMA),
                           output_dir=args.FAIL_DIRECTORY,
                           input_files=input_files,
                           use_json_schema=args.JSON_SCHEMA,
                           verbose_print=args.VERBOSE,
                           silent=args.SILENT)

        else:
            data = sys.stdin.read()

            schema = Schema(args.SCHEMA)
            passed = schema.validate(obj=data, use_json_schema=args.JSON_SCHEMA, verbose_print=args.VERBOSE)

            if not args.SILENT:
                result = f"{cli_bcolors.OKGREEN}OK{cli_bcolors.ENDC}" if passed else f"{cli_bcolors.FAIL}FAIL{cli_bcolors.ENDC}"
                print(f"{cli_bcolors.OKBLUE}INPUT{cli_bcolors.ENDC} -> {result}")

            if not passed:
                sys.exit(1)

    except Exception as exc:
        raise CLIError(message=str(exc), cli_tool=CLIError.CLITool.SCHEMA_CHECK)

def gen(args):
    output_type = args.OUTPUT_TYPE.lower().strip() if args.OUTPUT_TYPE else 'yaml'
    supported_output = ['yaml', 'json', 'toml', 'xml']
    try:
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


            for pair in zipped:
                input_data = infer_read_file_type(pair[0])
                output_file = Path(pair[1])

                suffix = output_file.suffix.lower() if output_file.suffix else f".{output_type}"

                schema = Schema.generate_from_obj(input_data, include_extended_properties=args.EXTRAS)

                if suffix == '.yaml':
                    schema.to_yaml(str(output_file))

                elif suffix == '.json':
                    schema.to_json(str(output_file))

                elif suffix == '.toml':
                    schema.to_toml(str(output_file))
                elif suffix == '.xml':
                    if importlib.util.find_spec('xmltodict'):
                        schema.to_xml(str(output_file))
                    else:
                        raise ModuleNotFoundError("Missing 'xmltodict' package!")
                else:
                    raise ValueError(f"Cannot dump to format {suffix}, only supported {supported_output}")

                if not args.SILENT:
                    print(f"{cli_bcolors.OKBLUE}{pair[0]}{cli_bcolors.ENDC} -> {cli_bcolors.OKBLUE}{pair[1]}{cli_bcolors.ENDC}")
                continue
        else:
            data = sys.stdin.read()

            schema = Schema.generate_from_obj(obj=data, include_extended_properties=args.EXTRAS)


            if output_type == 'yaml':
                print(schema.to_yaml())
            elif output_type == 'json':
                print(schema.to_json())
            elif output_type == 'toml':
                print(schema.to_toml())
            elif output_type == 'xml':
                if importlib.util.find_spec('xmltodict'):
                    print(schema.to_xml())
                else:
                    raise CLIError(message='Missing dependency "xmltodict" for type xml',
                                   cli_tool=CLIError.CLITool.SCHEMA_GEN)
            elif output_type == 'ini' or output_type == '.env':
                raise CLIError(message='INI and .ENV output unsupported for schema generation', cli_tool=CLIError.CLITool.SCHEMA_GEN)
            else:
                raise CLIError(message=f'Unknown type "{output_type}"', cli_tool=CLIError.CLITool.SCHEMA_GEN)

    except Exception as exc:
        raise CLIError(message=str(exc), cli_tool=CLIError.CLITool.SCHEMA_GEN)
