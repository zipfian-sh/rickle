# Check schema

---

The check tool is used to validate file(s) against a schema.

```shell
rickle schema check -h
```

Prints the following options:

```text
optional arguments:
 -h, --help          show this help message and exit
 --input  [ ...]     input file(s) to check
 --input-directory   directory(s) of files to check
 --schema            schema definition file to compare
 --fail-directory    directory to move failed files to
 --verbose, -v       verbose output
 --silent, -s        silence output
 --json-schema, -j   validate as json schema
```

???+ tip "JSON Schema" 

    Using ``--json-schema`` will, if ``jsonschema`` is installed, validate using the JSON Schema specification.

    For support using JSON schema, install the Python package using:
    ```shell 
    pip install rickle[jsonschema]
    ```

---

Example:

```shell
cat my-example.yaml | rickle schema check --schema my-example.schema.json
```

Will print the following if passed:

```text
INPUT -> OK
```

Or if failed the test:

```text
INPUT -> FAIL
```

!!! note

    If the input is piped and the input fails the check, the program exits with code 1.

Furthermore a message detailing the failure can be printed using ``--verbose`` output, for example:

```shell
cat my-example.yaml | rickle schema check --schema my-example.schema.json --verbose
```

```text
Type 'key_one' == 'string',
 Required type 'integer' (per schema {'type': 'integer'}),
 In {'key_one': '99', 'key_two': 'text'},
 Path /root/dict_type/key_one
```

Should output be suppressed, adding the ``--silent`` can be used.
Furthermore, input files that fail the check can be moved to directory using ``--fail-directory``:

```shell
rickle schema check --input-directory ./configs --schema my-example.schema.json --fail-directory ./failed -s
```

