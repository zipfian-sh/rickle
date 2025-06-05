import os
import re
import sys
import warnings
from pathlib import Path

from rickle.tools import CLIError

from rickle import Rickle, UnsafeRickle

def serve(args):
    try:
        from rickle.net import serve_rickle_http
    except NameError:
        warnings.warn('Required Python package "twisted" not found.', ImportWarning)
        return

    output_type = args.OUTPUT_TYPE.lower() if args.OUTPUT_TYPE else 'json'
    try:
        if args.UNSAFE:
            if args.INPUT:
                _input = args.INPUT
            else:
                _input = sys.stdin.read()
            rick = UnsafeRickle(_input, load_lambda=args.LOAD_LAMBDA, RICKLE_PATH_SEP='/')
        else:
            if args.INPUT:
                _input = args.INPUT
            else:
                _input = sys.stdin.read()
            rick = Rickle(_input, load_lambda=args.LOAD_LAMBDA, RICKLE_PATH_SEP='/')

        if args.AUTH:
            if os.path.exists(args.AUTH) and Path(args.AUTH).is_file():
                creds = Rickle(args.AUTH).dict()
            elif re.match(r'(\w+):(\w+)', args.AUTH):
                m = re.match(r'(\w+):(\w+)', args.AUTH)
                creds = { m.group(1): m.group(2) }
            else:
                raise ValueError(f"Could not determine what the auth values ({args.AUTH}) are!")
        else:
            creds = None

        if args.BROWSER:
            import webbrowser

            scheme = 'https' if args.CERTIFICATE and args.PRIVATE_KEY else 'http'
            webbrowser.open(f'{scheme}://{args.HOST}:{args.PORT}', new=2)

        serve_rickle_http(rickle=rick,
                          port=args.PORT,
                          interface=args.HOST,
                          serialised=args.SERIALISED,
                          basic_auth=creds,
                          output_type=output_type,
                          path_to_certificate=args.CERTIFICATE,
                          path_to_private_key=args.PRIVATE_KEY,
                        )
    except Exception as exc:
        raise CLIError(message=str(exc), cli_tool=CLIError.CLITool.SERVE)
