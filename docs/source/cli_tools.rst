.. _cli-page:

CLI Tools
**************************

The command-line interface (CLI) of ``rickle`` enhances its utility by allowing users to perform tasks directly from the terminal without writing extensive scripts.
With this CLI, you can easily convert YAML files to JSON and vice versa, making it an invaluable tool for developers who often need to interchange these formats to accommodate various technologies and frameworks.
Furthermore, the CLI supports schema validation and generation, enabling quick checks and schema creation from YAML or JSON files.
This functionality is especially useful for ensuring data integrity and for rapid prototyping where adherence to predefined data structures is critical.
Overall, rickle's CLI makes it a breeze to manage and transform structured data with simple command-line commands.

Getting started
========================

To see help and usage:

.. code-block:: shell

    rickle -h

Which will show the list of available options:

.. code-block:: text

   positional arguments:
     {conv,obj,serve,schema}
       conv                Converting files between formats
       obj                 Tool for reading or editing  objects
       serve               Serving objects through http(s)
       schema              Generating and checking schemas of YAML files

   optional arguments:
     -h, --help            show this help message and exit
     --version, -v         show version number
     --output-type         output file type (default = YAML)


.. note::

   Outputs may differ from the documentation.

The main tools that the ``rickle`` CLI exposes are:

1. conv
2. obj
3. schema
4. serve

All of which are discussed in the following sections.

Input/Output to tools
---------------------

All CLI tools support Unix pipes, i.e. the output of the previous command or process will be used as input. For example:

.. code-block:: shell

    cat config.yml | rickle obj get /

.. note::

   On Windows systems the command ``type`` can be used instead of ``cat``.

This is the preferred usage of ``rickle``. Similarly the output can always be piped or redirected:

.. code-block:: shell

    cat config.yaml | rickle obj get /config/database > db_config.yaml

or for example:

.. code-block:: shell

    cat config.yaml | rickle obj get /config/ecr/password | aws ecr get-login-password --password-stdin

For all tools, the input can be a file flagged with ``--input`` and output can be directed to a file with ``--output``:

.. code-block:: shell

    rickle obj --input config.yaml --output db_config.yaml get /config/database

Although this is often a less readable way and is only recommended for when it makes sense to do so.

Output types
---------------------

For most of the tools the output types can be specified with the ``--output-type`` flag and can be one of the following strings:

.. hlist::
   :columns: 1

   * yaml
   * json
   * toml
   * xml
   * ini
   * env

.. note::

   The default output type for all tools (except ``serve``) will be based on what the input is. For ``serve`` the default output is ``JSON``.

Certain tools have more output type options. Both ``search`` and ``type`` have ``ARRAY`` and ``PYTHON`` as extra types.

Conversion tool
========================

The conversion process between YAML and JSON using rickle involves a few straightforward steps that can be executed via its command-line interface or programmatically within a Python script.

To see all the available options:

.. code-block:: shell

    rickle conv -h

Which will show the list of available options:

.. code-block:: text

   optional arguments:
     -h, --help          show this help message and exit
     --input  [ ...]     input file(s) to convert
     --input-directory   directory of input files
     --output  [ ...]    output file names, only if --input given
     --input-type        optional input type (type inferred if none)
     --verbose, -v       verbose output



Convert X to Y
---------------------

To convert an input file ``config.json``, use the following:

.. code-block:: shell

    cat config.json | rickle conv

This will print the converted file ``config.json`` as YAML (which is the default), or if specified ``--output-type`` type.

.. note::

   Because the input is piped, the input type is inferred but can explicitly be defined using the ``--input-type`` option.

If input is given as ``--input`` flag (or ``--input-directory``), the output will be a file with the same filename (with new extension).

.. code-block:: shell

    rickle conv --input config.json

This will create a file ``config.yaml`` instead of printing.

.. note::

   The default output format is YAML. Use ``--output-type`` option for other formats.

To specify the output type:

.. code-block:: shell

    cat config.yaml | rickle --output-type JSON conv

This will output the converted file (in this example as JSON).

Glob whole directory
---------------------

If the ``--input-directory`` option is used with a directory name, all files with an extension are converted to the same directory.
The ``--output-type`` option is needed to specify the format or else ``YAML`` will be the default output format.

.. code-block:: shell

    rickle --output-type TOML conv --input-directory ./configs --verbose

This will glob all files in the directory ``./configs``, including TOML files, and output them as TOML files with the same names.

The ``--verbose`` prints a line of the input/output filenames for each conversion.

.. note::

   The file extensions ``yaml``, ``yml``, ``json``, ``toml``, ``ini``, ``xml``, and ``env`` will be globbed.

Define output filenames
---------------------

Input files can have output filenames explicitly defined:

.. code-block:: shell

    rickle conv --input config.yaml --output ./configs/config_dev.toml

This will convert ``config.yaml`` to type ``TOML`` (because the type is inferred from the file extension)
with a new name ``config_dev.toml`` in the directory ``./configs``.

Multiple files can be converted at once:

.. code-block:: shell

    rickle --output-type JSON conv --input config_dev.yaml config_tst.yaml config_prd.yaml

When specifying the output names, the order of output filenames must match the order of input files:

.. code-block:: shell

    rickle conv --input config_dev.yaml config_prod.yaml --output conf-dev.json conf-prd.json

Troubleshooting Conv
---------------------

Most likely any occurring error would be a failure to read the file in the given format. File types are inferred from file extensions.
If no file extensions are present, files are inferred by trying to read them in the different formats.
If all fails, no operation is performed and an error message printed.

Object tools
========================

``rickle obj`` is a versatile command-line tool that enhances the functionality of the rickle library by enabling users to
interact directly with YAML (or other formats like JSON) objects from the command line.
With ``rickle obj``, users can perform a variety of operations such as getting the value of an object's attribute,
setting an attribute, deleting an attribute, or executing functions associated with the object.
This tool is especially useful for quick modifications, testing, or automation tasks where direct manipulation of
objects without the need to write full Python scripts can save time and effort.

To see all the available options:

.. code-block:: shell

    rickle obj -h

Which will show the following list of options:

.. code-block:: text

   positional arguments:
     {get,set,del,type,search,func}
       get                 Getting values from objects
       set                 Setting values in objects
       put                 Putting values in objects
       del                 For deleting keys (paths) in objects
       type                Printing value type
       search              For searching keys (paths) in objects
       find                For finding key/value (paths) in objects
       func                Executing functions defined in objects

   optional arguments:
     -h, --help            show this help message and exit
     --input               input file to create object from
     --output              write to output file
     --load-lambda, -l     load lambda types

Using this tool requires input of a YAML, JSON, TOML (etc.) file. This is done with the ``--input`` option or alternatively piped.

.. code-block:: shell

    rickle obj --input config.yaml <VERB>

Or

.. code-block:: shell

    cat config.yaml | rickle obj <VERB>

Where ``<VERB>`` can be one of the following:

.. hlist::
   :columns: 2

   * get
   * set
   * del
   * type
   * search
   * func

These `verbs` will be elaborated on in the next subsections.

Example input
---------------------

In the next examples, the following YAML file will be used as example input:

.. code-block:: yaml
   :linenos:
   :caption: conf.yaml
   :name: conf-yaml

    root_node:
        level_one:
            pswd: password
            usr: name

Document paths
---------------------

An important first concept to understand about using most of the tools ``rickle`` has to offer is
understanding the document paths. A path is the Unix style file and directory path concept applied to
a YAML (or JSON) document.

In the :ref:`example input <conf-yaml>` file, the path to the ``pswd`` key-value pair would be:

.. code-block:: shell

    /root_node/level_one/pswd

Which would have the value ``password``.

.. note::

   The path must always start the slash ``/`` to be valid.

.. note::

   The path separator can be specified by setting an environment variable "RICKLE_PATH_SEP", for example ``RICKLE_PATH_SEP=.`` for dots.

.. code-block:: shell

    export RICKLE_PATH_SEP=.

Get
---------------------

To get a value from a document, the key needs to a path in the document.

For example, getting the value of ``pswd``:

.. code-block:: shell

    cat conf.yaml | rickle obj get /root_node/level_one/pswd

This will output the value to the command line:

.. code-block:: shell

    password

Just about any paths value can be printed to the command line:

.. code-block:: shell

    cat conf.yaml | rickle obj get /root_node/level_one

This will output:

.. code-block:: shell

    pswd: password
    usr: name

To output the entire document:

.. code-block:: shell

    cat conf.yaml | rickle obj get /

Will result in:

.. code-block:: shell

    root_node:
      level_one:
         pswd: password
         usr: name

.. note::

   The default output is always YAML. To change the format, add the ``--output-type`` type.

Outputting the same in JSON:

.. code-block:: shell

    cat conf.yaml | rickle --output-type JSON obj get /

.. code-block:: shell

    {"root_node": {"level_one": {"usr": "name", "pswd": "password"}}}

.. note::

   If the ``--output`` option in ``obj`` is used to output to a file, the result is not printed to screen.

Set
---------------------

To set a value in a document, the key needs be to a path, along with a value.

.. code-block:: shell

    cat conf.yaml | rickle obj set /root_node/level_one/pswd **********

This will set the ``pswd`` value to ``**********`` and print the whole document with new value to the command line.

.. code-block:: shell

    root_node:
      level_one:
         pswd: '*********'
         usr: name

.. note::

   If the ``--output`` option in ``obj`` is used to output to a file, the result is not printed to screen.

For example, the following will output to a file:

.. code-block:: shell

    cat conf.yaml | rickle --output-type JSON obj --output conf.json set /root_node/level_one/pswd *********

.. code-block:: json
   :linenos:
   :caption: conf.json
   :name: conf-json

    {"root_node": {"level_one": {"usr": "name", "pswd": "*********"}}}

Of course this could also be directed:

.. code-block:: shell

    cat conf.yaml | rickle --output-type JSON obj > conf.json

.. note::

   Values can only be set for paths that exist. To create a new path, use ``put``.

This will, however, not work in the following example and result in an error:

.. code-block:: shell

    cat conf.yaml | rickle obj set /root_node/level_one/unknown/email not@home.com


Which results in the error message:

.. code-block:: shell

   error: The path /root_node/level_one/unknown/email could not be traversed

Put
---------------------

A new key-value can be added, for example:

.. code-block:: shell

    cat conf.yaml | rickle obj put /root_node/level_one/email not@home.com

Results in the added key:

.. code-block:: shell

    root_node:
      level_one:
         pswd: password
         usr: name
         email: not@home.com

Any path input to put will be created:

.. code-block:: shell

    cat conf.yaml | rickle obj put /root_node/level_one/config/host/address 127.0.0.1

Results in the added key:

.. code-block:: shell

    root_node:
      level_one:
         pswd: password
         usr: name
         email: not@home.com
         config:
            host:
               address: 127.0.0.1

Del
---------------------

To remove a value, use the ``del`` option:

.. code-block:: shell

    cat conf.yaml | rickle obj del /root_node/level_one/pswd

Resulting in:

.. code-block:: text

   root_node:
      level_one:
         usr: name

Type
---------------------

The ``type`` option will print the Python value type, for example:

.. code-block:: shell

    cat conf.yaml | rickle obj type /root_node/level_one/pswd

.. code-block:: text

   str

Or:

.. code-block:: shell

    cat conf.yaml | rickle obj type /root_node/level_one

.. code-block:: text

   map

Using ``--output-type`` the printed type changes. Available types include ``YAML``, ``JSON`` (default), ``TOML``, ``XML``, and ``python``.

Depending on this type, the value could be:

.. code-block:: text

   Python |    YAML |    JSON |      TOML |            XML |
   =========================================================
   str    |     str |  string |    String |      xs:string |
   int    |     int |  number |   Integer |     xs:integer |
   float  |   float |  number |     Float |     xs:decimal |
   bool   | boolean | boolean |   Boolean |     xs:boolean |
   list   |     seq |   array |     Array |    xs:sequence |
   dict   |     map |  object | Key/Value | xs:complexType |
   bytes  |  binary |         |           |                |
   ---------------------------------------------------------
   *      |  Python |  object |     Other |         xs:any |

Examples:

.. code-block:: shell

    cat conf.yaml | rickle --output-type XML obj type /root_node/level_one

.. code-block:: text

   xs:complexType

.. code-block:: shell

    cat conf.yaml | rickle --output-type PYTHON obj type /root_node/level_one

.. code-block:: text

   Rickle

Search
---------------------

Searching is a useful way to find the paths in a document. The following file with multiple repeated names is used in the examples:

.. code-block:: yaml
   :linenos:
   :caption: conf-multi.yaml
   :name: conf-multi-yaml

    root_node:
        level_one:
            pswd: password
            usr: name
        other:
            usr: joe
        usr: admin


To get the path to ``pswd``:

.. code-block:: shell

    cat conf-multi.yaml | rickle obj search pswd

Which will print the path as a YAML list by default (use the type ``--output-type`` flag for other output):

.. code-block:: yaml

   - /root_node/level_one/pswd

Where searching for the ``usr`` key:

.. code-block:: shell

    cat conf-multi.yaml | rickle obj search usr

...prints the following paths:

.. code-block:: yaml

   /root_node/usr
   /root_node/level_one/usr
   /root_node/other/usr

To print the values as YAML (or JSON), use the ``--output-type`` type ``YAML``:

.. code-block:: shell

    cat conf-multi.yaml | rickle --output-type YAML obj search usr

...prints the following paths:

.. code-block:: text

   - /root_node/usr
   - /root_node/level_one/usr
   - /root_node/other/usr

The path separator will be used as is set in the env:

.. code-block:: shell

    export RICKLE_PATH_SEP=.
    cat conf-multi.yaml | rickle obj search usr

.. code-block:: text

   .root_node.usr
   .root_node.level_one.usr
   .root_node.other.usr

Find
---------------------

Find is useful for find paths of key/value pairs. Using ``--help`` shows some examples along with the following table:

.. code-block:: text

   Comparison         |  op | alt |
   ================================
   equals             |   = |  eq |
   not equals         |  != |  ne |
   less than          |   < |  lt |
   greater than       |   > |  gt |
   less than equal    |  <= | lte |
   greater than equal |  >= | gte |
   --------------------------------

To find a path, the key, comparison operator (as show above, including alternatives) and value must be given.

Consider the following JSONL file:

.. code-block:: json
   :linenos:
   :caption: arr-dev.jsonl
   :name: arr-dev-jsonl

   {"name": "Lindsay", "surname": "Funke", "score": 29}
   {"name": "Gob", "surname": "Bluth", "score": 14}
   {"name": "Tobias", "surname": "Funke", "score": 19}
   {"name": "Buster", "surname": "Bluth", "score": 25}

Key / values can be found for example:

.. code-block:: shell

    cat arr-dev.jsonl | rickle obj find "surname = Bluth"

Prints the following output:

.. code-block:: text

   /[1]/surname
   /[3]/surname

Comparisons can also be disjunct using ``--or``:

.. code-block:: shell

    cat arr-dev.jsonl | rickle obj find --or "score < 19" "score > 25"

Outputting the result:

.. code-block:: text

   /[0]/score
   /[1]/score

Likewise comparisons can also be conjunct using ``--and``:

.. code-block:: shell

    cat arr-dev.jsonl | rickle obj find --and "score > 14" "score < 20"

Outputting the result:

.. code-block:: text

   /[2]/score

Using the ``--parent`` or shorthand ``-p`` can be used in combination with the ``--and`` to get the path of a object.

.. code-block:: shell

    cat arr-dev.jsonl | rickle obj find --and "surname = Bluth" "score < 20" -p

Outputting the result:

.. code-block:: text

   /[1]

Using paths can be used to do relative matching is also possible:

.. code-block:: json
   :linenos:
   :caption: arr-dev.jsonl
   :name: arr-dev-jsonl-2

   {"name": "Lindsay", "surname": "Funke", "score": 29, "details": {"age": 36 }}
   {"name": "Gob", "surname": "Bluth", "score": 14, "details": {"age": 40 }}
   {"name": "Tobias", "surname": "Funke", "score": 19, "details": {"age": 45 }}
   {"name": "Buster", "surname": "Bluth", "score": 25, "details": {"age": 30 }}

.. code-block:: shell

    cat arr-dev.jsonl | rickle obj find --and "surname = Funke" "/details/age = 36" -p

Outputting the result:

.. code-block:: text

   /[0]

Func
---------------------

.. warning::

   Loading unknown code can be potentially dangerous. Only load files that you are fully aware what the Python code will do once executed.
   In general, a safe rule of thumb should be: don't load any Python code.

For using functions, see :ref:`functions <sect-ext-usage-functions>` usage.

.. code-block:: text

   positional arguments:
     key         Key (name) of function
     params      Params for function

   optional arguments:
     -h, --help  show this help message and exit
     --infer          infer parameter types

Where ``key`` is the path to the function. As a slight but by no means foolproof safe gaurd, it is required to set the environment variable
``RICKLE_UNSAFE_LOAD=1``. This is not a security measure but an added step to make the user more aware of the risks involved.

For the following example a function ``get_area`` is defined:

.. code-block:: yaml
   :linenos:
   :caption: get-area.yaml
   :name: get-area-yaml

    get_area:
      type: function
      name: get_area
      args:
         x: 10
         y: 10
         z: null
         f: 0.7
      import:
         - math
      load: >
         def get_area(x, y, z, f):
            if not z is None:
               area = (x * y) + (x * z) + (y * z)
               area = 2 * area
            else:
               area = x * y
            return math.floor(area * f)

To run the function and get the resulting:

.. code-block:: shell

    export RICKLE_UNSAFE_LOAD=1
    cat get-area.yaml | rickle obj --load-lambda func /get_area z:int=10

.. note::

   To load the function the ``--load-lambda`` flag must be added. Please see the warning above again before proceeding.
   Running unknown code is dangerous and should not be done without fully understanding what the code does.

Which will output:

.. code-block:: shell

    420

.. note::

   Parameter types need to be explicitly defined as in the above example ``z:int=10``.
   If no type is defined, all parameters values are assumed to be strings.

The parameter types are:

.. hlist::
   :columns: 2

   * int
   * str
   * float
   * bool
   * list
   * dict

Optionally types can be inferred using the ``--infer`` option:

.. code-block:: shell

    export RICKLE_UNSAFE_LOAD=1
    cat get-area.yaml | rickle obj --load-lambda func --infer /get_area z=10

Which should infer that ``z`` is an integer.

Consider the following example to work with lists and dictionaries:

.. code-block:: yaml
   :linenos:
   :caption: list-and-dict.yaml
   :name: list-and-dict-yaml

    list_and_dict:
     type: function
     name: list_and_dict
     args:
       list_of_string: null
       dict_type: null
     import:
       - json
     load: >
       def list_and_dict(list_of_string, dict_type):
         if list_of_string:
           for s in list_of_string:
             print(f"{s} - of length {len(s)}")
         if dict_type:
           print(json.dumps(dict_type))

When running:

.. code-block:: shell

    export RICKLE_UNSAFE_LOAD=1
    cat list-and-dict.yaml | rickle obj --load-lambda func --infer /list_and_dict list_of_string="['shrt','looong']" dict_type="{'fifty' : 50}"

The output would be:

.. code-block:: shell

   shrt - of length 4
   looong - of length 6
   {"fifty": 50}

Without using the ``--infer`` option to infer the values and explicitly defining them:

.. code-block:: shell

    export RICKLE_UNSAFE_LOAD=1
    cat list-and-dict.yaml | rickle obj --load-lambda func /list_and_dict list_of_string:list="['shrt','looong']" dict_type:dict="{'fifty' : 50}"

Would produce the same results.

cURL alternative
---------------------

Seeing as a ``Rickle`` can be loaded with the JSON response from a URL, it could be used in a cURL-like manner:

.. code-block:: shell

    rickle --output-type JSON obj --input https://official-joke-api.appspot.com/random_joke get /

Or alternatively

.. code-block:: shell

    echo https://official-joke-api.appspot.com/random_joke | rickle --output-type JSON obj get /

.. code-block:: json

    {"type": "general", "setup": "Why did the girl smear peanut butter on the road?", "punchline": "To go with the traffic jam.", "id": 324}

with the ability to get a specific value from the JSON response, using paths:

.. code-block:: shell

    echo https://official-joke-api.appspot.com/random_joke | rickle --output-type JSON obj get /punchline

printing the fantastic punchline to the setup "The punchline often arrives before the set-up.":

.. code-block:: shell

   Do you know the problem with UDP jokes?

Troubleshooting Obj
---------------------

1. Get

The most likely problem to occur is if the path can not be traversed, i.e. the path is incorrect:

.. code-block:: shell

     cat conf.yaml | rickle --output-type JSON obj get /path_to_nowhere

And this will result in printing nothing (default behaviour).

Another likely problem is that the scalar can not be output in the given type.
I.e. TOML, INI, and XML for example need at least a root node.

2. Set

The most likely problem to occur is if the path can not be traversed, i.e. the path is incorrect:

.. code-block:: shell

   error: The path /root_node/level_one/unknown/email could not be traversed

3. Func

Any number of errors could occur here, and that's due to the fact that Python code is being executed. A typical problem
that could occur is the parameters not having explicit types defined. If the types are not defined they are interpreted
as being strings.

Schema tools
========================

Schema tools are useful for either generating schema definitions of files or check files against definitions.

Gen
---------------------

For generating a schema from a file, ``gen`` is used.
The gen tool is used for generating schemas from input. This is a useful step to start from, where a developer can then further define the schema.

.. code-block:: shell

    rickle schema gen -h

Prints the following options:

.. code-block:: text

   optional arguments:
     -h, --help          show this help message and exit
     --input  [ ...]     input file(s) to generate from
     --output  [ ...]    output file(s) to write to
     --input-directory   directory(s) of files to generate from
     --silent, -s        silence output
     --extras, -e        include extra properties

Consider the following example file:

.. code-block:: yaml
   :linenos:
   :caption: my-example.yaml
   :name: my-example-yaml

   root:
     null_type: null
     dict_type:
       key_one: 99
       key_two: 'text'
     a_string_list:
       - lorem
       - ipsum
     a_floats_list:
       - 0.8
       - 0.9
     a_mixed_list:
       - lorem
       - 0.9

Running the ``gen`` tool:

.. code-block:: shell

    rickle schema gen --input my-example.yaml

will create the file ``my-example.schema.yaml`` as the following:

.. code-block:: yaml
   :linenos:
   :caption: my-example.schema.yaml
   :name: my-example-schema-yaml

   type: object
   properties:
     root:
       type: object
       properties:
         null_type:
           type: 'null'
         dict_type:
           type: object
           properties:
             key_one:
               type: integer
             key_two:
               type: string
         a_string_list:
           type: array
           items:
           - type: string
         a_floats_list:
           type: array
           items:
           - type: number
         a_mixed_list:
           type: array
           items:
           - type: 'null'

It will print the following to STDOUT:

.. code-block:: shell

   .\my-example.yaml -> .\my-example.schema.yaml

.. note::

   This can be suppressed by using the ``--silent`` flag.

.. note::

   Note that if no output name is given the filename becomes ``<filename>.schema.<ext>``.

Of course the type can also be defined by either using ``--output-type``:

.. code-block:: shell

    rickle --output-type JSON schema gen --input my-example.yaml

Or implicitly with extensions in filenames:

.. code-block:: shell

    rickle schema gen --input my-example.yaml --output my-schema.json

Which will result in:

.. code-block:: json
   :linenos:
   :caption: my-schema.json
   :name: my-schema-json

   {
       "type": "object",
       "properties": {
           "root": {
               "type": "object",
               "properties": {
                   "null_type": {
                       "type": "null"
                   },
                   "dict_type": {
                       "type": "object",
                       "properties": {
                           "key_one": {
                               "type": "integer
                               "
                           },
                           "key_two": {
                               "type": "string"
                           }
                       }
                   },
                   "a_string_list": {
                       "type": "array",
                       "items": [{
                               "type": "string"
                           }
                       ]
                   },
                   "a_floats_list": {
                       "type": "array",
                       "items": [{
                               "type": "number"
                           }
                       ]
                   },
                   "a_mixed_list": {
                       "type": "array",
                       "items": [{
                               "type": "null"
                           }
                       ]
                   }
               }
           }
       }
   }



Check
---------------------

The check tool is used to validate file(s) against a schema.

.. code-block:: shell

    rickle schema check -h

Prints the following options:

.. code-block:: text

   optional arguments:
     -h, --help          show this help message and exit
     --input  [ ...]     input file(s) to check
     --input-directory   directory(s) of files to check
     --schema            schema definition file to compare
     --fail-directory    directory to move failed files to
     --verbose, -v       verbose output
     --silent, -s        silence output
     --json-schema, -j   validate as json schema

.. hint:: Using ``--json-schema`` will, if ``jsonschema`` is installed, validate using the JSON Schema specification.

Example:

.. code-block:: shell

    cat my-example.yaml | rickle schema check --schema my-example.schema.json

Will print the following if passed:

.. code-block:: shell

   INPUT -> OK

Or if failed the test:

.. code-block:: shell

   INPUT -> FAIL

.. note::

   If the input is piped and the input fails the check, the program exits with code 1.

Furthermore a message detailing the failure can be printed using ``--verbose`` output, for example:

.. code-block:: shell

    cat my-example.yaml | rickle schema check --schema my-example.schema.json --verbose

.. code-block:: shell

   Type 'key_one' == 'string',
    Required type 'integer' (per schema {'type': 'integer'}),
    In {'key_one': '99', 'key_two': 'text'},
    Path /root/dict_type/key_one

Should output be suppressed, adding the ``--silent`` can be used.
Furthermore, input files that fail the check can be moved to directory using ``--fail-directory``:

.. code-block:: shell

    rickle schema check --input-directory ./configs --schema my-example.schema.json --fail-directory ./failed -s

Serve tool
========================

This is a little tool to serve the a YAML or JSON (or TOML, XML, INI) file as a mini API.

.. note::

   If ``Rickle`` is not installed with ``net`` extras the serve tool will not appear.

.. code-block:: shell

    pip install rickled[net]


.. code-block:: shell

    rickle schema check -h

Prints the following options:

.. code-block:: text

   optional arguments:
     -h, --help        show this help message and exit
     --input           input file to serve
     --host            host address (default = localhost)
     --port            port number (default = 8080)
     --private-key     private key file path
     --certificate     ssl certificate file path
     --auth            basic auth (username:password)
     --load-lambda     load lambda true
     --unsafe          load UnsafeRickle (VERY UNSAFE)
     --browser, -b     open browser
     --serialised, -s  serve as serialised data (default = false)

.. note::

   The default output type is set to ``JSON``.

.. note::

   The ``/`` overrides ``RICKLE_PATH_SEP`` as the path separator.

Example
------------------------

Take the following example:

.. code-block:: yaml
   :linenos:
   :caption: mock-example.yaml
   :name: mock-example-yaml

   root:
     env_var:
       type: env
       load: USERNAME
       default: noname
     encoded:
       type: base64
       load: dG9vIG1hbnkgc2VjcmV0cw==
     heavens_gate:
       type: html_page
       url: https://www.heavensgate.com/
     random_joke:
       type: api_json
       url: https://official-joke-api.appspot.com/random_joke
       expected_http_status: 200
       load_as_rick: true
       hot_load: true
       deep: true
     data:
       dict_type:
         a: 1
         b: 2
         c: 3
       list_type:
         - hello
         - world

If running the serve tool with the option ``-b`` a new tab in the browser will be opened, directed to the listening port:

.. code-block:: shell

   cat mock-example.yaml | rickle serve -b

A port number can be defined specified using ``--port``:

.. code-block:: shell

   cat mock-example.yaml | rickle serve -b --port 3301

Using the given example input file the following JSON data will be returned:

.. code-block:: json

   {
     "root": {
       "env_var": "do",
       "heavens_gate": ".......",
       "data": {
         "dict_type": {
           "a": 1,
           "b": 2,
           "c": 3
         },
         "list_type": [
           "hello",
           "world"
         ]
       }
     }
   }

.. note::

   The text for ``heavens_gate`` is excluded for space (and your sanity).

Calling ``http://localhost:3301/root/random_joke`` will return (example):

.. code-block:: json

   {
     "type": "general",
     "setup": "What kind of award did the dentist receive?",
     "punchline": "A little plaque.",
     "id": 255
   }

Furthermore, SSL can be used:

.. code-block:: shell

   cat mock-example.yaml | rickle serve -b --port 3301 --private-key .\local.pem --certificate .\local.crt

And finally, if the given YAML or JSON file needs to be given in serialised form, use ``-s``:

.. code-block:: shell

   cat mock-example.yaml | rickle serve -b -s

which will give the following:

.. code-block:: json

   {
     "root": {
       "env_var": {
         "type": "env",
         "load": "USERNAME",
         "default": "noname"
       },
       "encoded": {
         "type": "base64",
         "load": "dG9vIG1hbnkgc2VjcmV0cw=="
       },
       "heavens_gate": {
         "type": "html_page",
         "url": "https://www.heavensgate.com/",
         "headers": null,
         "params": null,
         "expected_http_status": 200,
         "hot_load": false
       },
       "random_joke": {
         "type": "api_json",
         "url": "https://official-joke-api.appspot.com/random_joke",
         "http_verb": "GET",
         "headers": null,
         "params": null,
         "body": null,
         "deep": true,
         "load_lambda": false,
         "expected_http_status": 200,
         "hot_load": true
       },
       "data": {
         "dict_type": {
           "a": 1,
           "b": 2,
           "c": 3
         },
         "list_type": [
           "hello",
           "world"
         ]
       }
     }
   }

Output can also be given as ``application/yaml`` with YAML output using the ``--output-type`` option:

.. code-block:: shell

   cat mock-example.yaml | rickle --output-type YAML serve -b

Which will produce the YAML output:

.. code-block:: yaml

   root:
     data:
       dict_type:
         a: 1
         b: 2
         c: 3
       list_type:
       - hello
       - world
     env_var: do
     heavens_gate: "......."

.. note::

   In some browsers, the YAML output will be downloaded as data and not rendered in the browser.

Basic auth
------------------------

Basic auth can be added by using the ``--auth`` flag with input ``username:password`` or filename (YAML, JSON etc.).
For example:

.. code-block:: yaml
   :linenos:
   :caption: auth-users.yaml
   :name: auth-users-yaml

   dark-4venger: p@ssword
   phiberOptik: l33th@xor
   larry: ken sent me

.. code-block:: shell

   cat mock-example.yaml | rickle serve -b --auth auth-users.yaml

Or just using a single username combination:

.. code-block:: shell

   cat mock-example.yaml | rickle serve -b --auth "user:password"

Unsafe usage
------------------------

.. warning::

   Loading unknown code can be potentially dangerous. Only load files that you are fully aware what the Python code will do once executed.
   In general, a safe rule of thumb should be: don't load any Python code.

To enabled functions, the environment variable ``RICKLE_UNSAFE_LOAD`` has to be set, and ``--load-lambda`` and ``--unsafe`` passed.
Using the ``get-area.yaml`` example again:

.. code-block:: yaml
   :linenos:
   :caption: get-area.yaml
   :name: get-area-yaml

    get_area:
      type: function
      name: get_area
      args:
         x: 10
         y: 10
         z: null
         f: 0.7
      import:
         - math
      load: >
         def get_area(x, y, z, f):
            if not z is None:
               area = (x * y) + (x * z) + (y * z)
               area = 2 * area
            else:
               area = x * y
            return math.floor(area * f)

.. code-block:: shell

   export RICKLE_UNSAFE_LOAD=1
   cat get-area.yaml | rickle serve --load-lambda --unsafe

Then the endpoint can be called:

.. code-block:: shell

   curl http://localhost:8080/get_area?x=15&y=5&z=25