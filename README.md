# rickle - Smart Python tools for working with Configs

![PyPI - Version](https://img.shields.io/pypi/v/rickle)
[![Downloads](https://static.pepy.tech/badge/rickle)](https://pepy.tech/project/rickle)
[![Downloads](https://static.pepy.tech/badge/rickle/month)](https://pepy.tech/project/rickle)
[![General badge](https://img.shields.io/badge/Coverage-75+-<COLOR>.svg)](https://zipfian.science/docs/rickle/coverage/index.html)

---

```                                                                
██████╗ ██╗ ██████╗██╗  ██╗██╗     ███████╗
██╔══██╗██║██╔════╝██║ ██╔╝██║     ██╔════╝
██████╔╝██║██║     █████╔╝ ██║     █████╗  
██╔══██╗██║██║     ██╔═██╗ ██║     ██╔══╝  
██║  ██║██║╚██████╗██║  ██╗███████╗███████╗
╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝
                                                                                                                       
by Zipfian.sh                             
```

---

`rickle` is a versatile Python library and command-line tool that offers a wide range of functionalities for working with YAML and JSON (and TOML, INI, XML, .ENV) data

1. **Serialization**: `rickle` allows you to easily serialize Python objects to text formats like YAML or JSON. 
This is particularly useful for converting Python data structures into a human-readable and easily shareable format, such as `config` files.

2. **Schema Validation**: It provides the capability to validate YAML (and JSON, etc.) data against predefined schemas. This ensures that your data adheres to a specific structure or format, helping to maintain data consistency.

3. **Schema Generation**: Start with easy schema definition generations from existing config files. This is helpful when you want to formalize the structure of your data or for documentation purposes.

4. **Conversion**: `rickle` offers seamless conversion between YAML, JSON, INI, XML, and .ENV formats. This facilitates data interchange between systems that use different serialization formats.

5. **Simple Web Server**: An experimental unique feature of `rickle` is its ability to create a basic web server from a YAML (or JSON, TOML, XML, INI) file. This means you can define endpoints, routes, and data sources purely by writing it as a YAML/etc. file, making it easy to prototype web services without extensive coding, or to create mock REST APIs, or even to serve configuration files as REST APIs. 

`rickle` is a powerful utility for working with configuration data in Python. 
It simplifies tasks like serialization, schema validation, schema generation, format conversion, 
and even enables quick web server prototyping. 
This tool is valuable for developers and data engineers working 
with structured data in a flexible and efficient manner.

---

# Usage

For usage examples see [examples](https://zipfian.science/docs/rickle/examples.html) page. 
Documentation can be [found here](https://zipfian.science/docs/rickle/index.html). 

## 1. Install

First install the tool (Python version >= 3.9):

```bash script
pip install rickle
```
---
### 1.1 Extras

Optionally the twisted web server can be installed alongside for the `serve` functionality.

```bash script
pip install rickle[net]
```

For expanded schema validators.

```bash script
pip install rickle[validators]
```

For xml support.

```bash script
pip install rickle[xml]
```

For .env file support.

```bash script
pip install rickle[dotenv]
```

For a fully featured installation.

```bash script
pip install rickle[full]
```

Check if the installation succeeded:

```bash script
rickle --help
```

## 2. And use

```python
from rickle import Rickle
```

Using an example YAML file:

```yaml
conf:
  db_connection:
     acc_name:
        type: env
        load: ACC_NAME
        default: developer_account
     acc_pass:
        type: env
        load: ACC_PASS
     database_name: public
```

Then use Rickle:

```python
>> config = Rickle('./config.yaml')

>> config.conf.db_connection.dict()
{'acc_name' : 'acceptance_account', 'acc_pass' : 'asd!424iXj', 'database_name' : 'public'}

>> config.conf.db_connection.acc_pass
'asd!424iXj'

>> config('/conf/db_connection/acc_pass')
'asd!424iXj'
```


---
## 3. Schema tools

Two main schema tools exist, the `check` and the `gen` tools.

---

### 3.1 Schema `check`

For checking the schema of input files, the `check` tool is used.

```bash script
rickle schema check --help
```

```bash script
rickle schema check --input test.yaml --schema schema.yaml 
```

OR

```bash script
cat test.yaml | rickle schema check --schema schema.yaml 
```

> [!TIP]
> To do a [jsonschema](https://pypi.org/project/jsonschema/) check (if installed), use `--json-schema` or `-j`.


---

### 3.2 Schema `gen`

Schema files can be generated from YAML files with the `gen` tool.

```bash script
rickle schema gen --help
```

```bash script
rickle schema gen --input test.yaml
```

This will generate a schema file called `test.schema.yaml`.

OR

```bash script
cat test.yaml | rickle schema --output-type json gen
```

This will generate a schema and print the output, in this example in JSON.

---

## 4. Conversion tools

`rickle` can also be used for bulk conversion from YAML to JSON or the other way around.

```bash script
rickle conv --help
```

To convert input files (or directories):

```bash script
rickle conv --input test.yaml --output test.json
```

For each input file the output file can be defined and the path suffix is used to infer the desired output type.
Using input and output will read and write to files. Alternatively:

```bash script
cat text.yaml | rickle --output-type json conv 
```

The output type can be specified with the `--output-type` flag.

---

## 5. `object` functions

Certain `jq` like functionality can be achieved using `rickle`. This includes the ability to `get`, `set`, `del`, and `search`
document paths. This is done using the object tool `obj`.

To see more:

```bash script
rickle obj --help
```
```bash script
rickle obj get --help
```
```bash script
rickle obj set --help
```
```bash script
rickle obj put --help
```
```bash script
rickle obj del --help
```
```bash script
rickle obj search --help
```
```bash script
rickle obj find --help
```
---

### 5.1 Paths

To get to a specific value, a path is traversed. This path looks much like a Unix or web path.
To get the whole document, `/` is used. Expanding the path would look something like this: 

```yaml
path:
  to:
    value: "hello world"
```
The path `/path/to/value` would yield the string `hello world`.

```yaml
path:
  to:
    value: "hello world"
    values:
      - one
      - two
      - three
```

Working with lists is possible with indices, for example `/path/to/values/[0]` would yield the string `one`. 
And the path `/path/to` would yield:

```yaml
value: "hello world"
values:
  - one
  - two
  - three
```

> [!NOTE]
> It is possible to change the path separator by setting the env variable `RICKLE_PATH_SEP`.

---

### 5.2 Get

```bash script
rickle obj --input test.yaml get /
```

OR

```bash script
cat test.yaml | rickle obj get /
```

This will output the entire test.yaml. If the path, using the above example with path `/path/to/values/[0]`, the output will 
simply be `one`.

> [!TIP]
> Use rickle as an cURL alternative.

Example using url:

```bash script
echo https://official-joke-api.appspot.com/random_joke | rickle obj get /
```

---

### 5.2 Set

```bash script
rickle obj --input test.yaml set /path/to/values/[1] foo
```

OR

```bash script
cat test.yaml | rickle obj set /path/to/values/[1] foo
```

will output the following: 

```yaml
path:
  to:
    value: "hello world"
    values:
      - one
      - foo
      - three
```

> [!NOTE]
> To put a value with a path that does not exist (i.e. create the path) use `put`

---

### 5.3 Put

```bash script
rickle obj --input test.yaml put /path/to/non/existing bar
```

OR

```bash script
cat test.yaml | rickle put /path/to/non/existing bar
```

will output the following: 

```yaml
path:
  to:
    non:
      existing: bar
    value: "hello world"
    values:
      - one
      - two
      - three
```

---

### 5.4 Search

Consider the following:

```yaml
path:
  to:
    key: "hello world"
  and:
    another:
      key: "ok go"
```

Document paths can be searched:

```bash script
rickle obj --input test.yaml search key
```

OR

```bash script
cat test.yaml | rickle obj search key
```

Will output the following (in YAML):

```
- /path/to/key
- /path/and/another/key
```

Different output types are passed with the `--output-type` flag, including the `array` type to print paths as lines. 

```bash script
cat test.yaml | rickle --output-type list obj search key
```

Will instead output the following:

```
/path/to/key
/path/and/another/key
```

---

### 5.5 Find

Alternative to search where a key with a matching value (condition) is "found":

Consider the file `arr-dev.jsonl`:

```json lines
{"name": "Lindsay", "surname": "Funke", "score": 29}
{"name": "Gob", "surname": "Bluth", "score": 14}
{"name": "Tobias", "surname": "Funke", "score": 19}
{"name": "Buster", "surname": "Bluth", "score": 25}
```

Using the find tool: 

```bash script
cat arr-dev.jsonl | rickle obj find "surname = Bluth" 
```

outputs 

```
/[1]/surname
/[3]/surname
```

Examples of using find:

```bash script
cat arr-dev.jsonl | rickle obj find --or "score < 19" "score > 25"
cat arr-dev.jsonl | rickle obj find --and "score > 14" "score < 20"
cat arr-dev.jsonl | rickle obj find --and "surname = Bluth" "score < 20" -p
```

> [!TIP]
> Use `-p` to output the parent node, making it easier to use multi conditions.


---

## 6. Serving via HTTP(s)

A nifty little use of this Python tool is the ability to host a webserver, using a YAML (or other) file.
For this functionality to work the "net" extras need to be installed, `pip install rickel[net]`.  
 
```bash script
rickle serve --help
```

```bash script
rickle serve --input basic_example.yaml
```

OR

```bash script
cat basic_example.yaml | rickle serve
```

This will start listening on http://localhost:8080, for requests using `GET`. 

Alternatively serve through SSL:

```bash script
cat basic_example.yaml | rickle serve --certificate ./certificate.crt --private-key ./privkey.pem
```

This will start listening on https://localhost:8080. 

Furthermore, define host or port:

```bash script
cat basic_example.yaml | rickle serve --host "0.0.0.0" --port 8077
```

This will start listening on https://0.0.0.0:8077. 

Automatically open a new browser tab:

```bash script
cat basic_example.yaml | rickle serve -b
```

Add Python functions to the YAML file (unsafe!):

> [!CAUTION]
> Using `--unsafe` should only be used on trusted data.

```bash script
export RICKLE_UNSAFE_LOAD=1
cat unsafe_example.yaml | rickle serve --unsafe --load-lambda
```

This will start listening on http://localhost:8080, 
and if there are Python functions defined in the YAML file, these will be executable. 
This holds **serious security risks** though, and should only be used with caution.

---

# Release

See the version history in [changelog](https://zipfian.science/docs/rickle/changelog.html).


---

# Contributing

As this is an open source project, forks and PRs are welcome! 
Please review some of the practices stated in [CONTRIBUTIONS.md](https://github.com/Zipfian-Science/rickled/blob/master/CONTRIBUTING.md).

---

© [Zipfian.sh](https://zipfian.sh) 2020 - 2025
