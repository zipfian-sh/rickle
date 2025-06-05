---
icon: material/web
---

# HTTP server

---

This is a little tool to serve the a YAML or JSON (or TOML, XML, INI) file as a mini API.

???+ info "Requires `twisted` to work"
    
    If ``Rickle`` is not installed with ``net`` extras the serve tool will not appear.

    ```shell
    pip install rickled[net]
    ```

---

```shell
rickle schema check -h
```

Prints the following options:

```text
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
```

!!! note "Default output"

    The default output type is set to ``JSON``.

!!! note "`RICKLE_PATH_SEP` override"
    
    The ``/`` overrides ``RICKLE_PATH_SEP`` as the path separator.

---

## Example

Take the following example:

```yaml title="mock-example.yaml" linenums="1"
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
```

If running the serve tool with the option ``-b`` a new tab in the browser will be opened, directed to the listening port:

```shell
cat mock-example.yaml | rickle serve -b
```

???+ tip "Port number"
    
    A port number can be defined specified using ``--port``:

    ```shell
    cat mock-example.yaml | rickle serve -b --port 3301
    ```

Using the given example input file the following JSON data will be returned:

```json
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
```

??? note
    
    The text for ``heavens_gate`` is excluded for space (and your sanity).

Calling ``http://localhost:3301/root/random_joke`` will return (example):

```json
{
 "type": "general",
 "setup": "What kind of award did the dentist receive?",
 "punchline": "A little plaque.",
 "id": 255
}
```

And finally, if the given YAML or JSON file needs to be given in serialised form, use ``-s``:

```shell
cat mock-example.yaml | rickle serve -b -s
```

which will give the following:

```json
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
```

Output can also be given as ``application/yaml`` with YAML output using the ``--output-type`` option:

```shell
cat mock-example.yaml | rickle --output-type YAML serve -b
```

Which will produce the YAML output:

```yaml
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
```



???+ info "YAML mime types"

    In some browsers, the YAML output will be downloaded as data and not rendered in the browser.

### `PUT` new data

New data can be put using a path and any input data of type YAML, JSON, TOML, or XML.

```shell
cat mock-example.yaml | rickle serve
```

Then running `curl` with `PUT`:

```shell
curl -X PUT http://localhost:8080/root/new_path -d '{"any_data":3.14}'
```

This will create at the new document path `/root/new_path` an object `any_data:3.14`. 
Of course this means that the value `3.14` exists at `/root/new_path/any_data` as the input data is read and is accessible as:

```shell
curl http://localhost:8080/root/new_path/any_data
```

Furthermore, YAML, TOML, XML, INI, and ENV inputs are support:

```shell
curl -X PUT http://localhost:8080/root/new_ini < path/to/file.ini
curl -X PUT http://localhost:8080/root/new_toml < other/to/file.xml
```

### Set `X-rickle-output-type` header

The output type can be set with each `GET` request. Say for example you want the output in TOML:

```shell
curl.exe http://localhost:8080/ --header "X-rickle-output-type: toml"
```

Will respond with TOML.

---

## SSL and Auth

SSL can be used:

```shell
cat mock-example.yaml | rickle serve --private-key ./local.pem --certificate ./local.crt
```

### Basic auth


Basic auth can be added by using the ``--auth`` flag with input ``username:password`` or filename (YAML, JSON etc.).
For example:

```yaml title="auth-users.yaml" linenums="1"
dark-4venger: p@ssword
phiberOptik: l33th@xor
larry: ken sent me
```

And then used:

```shell
cat mock-example.yaml | rickle serve -b --auth auth-users.yaml
```

Or just using a single username combination:

```shell
cat mock-example.yaml | rickle serve -b --auth "user:password"
```

---

## Unsafe usage

!!! danger

    Loading unknown code can be potentially dangerous. Only load files that you are fully aware what the Python code will do once executed.
    In general, a safe rule of thumb should be: don't load any Python code.

    To enabled functions, the environment variable ``RICKLE_UNSAFE_LOAD`` has to be set, and ``--load-lambda`` 
    and ``--unsafe`` passed. Using the ``get-area.yaml`` example again:

```yaml title="get-area.yaml" linenums="1"
get_area:
  type: python
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
```

```shell
export RICKLE_UNSAFE_LOAD=1
cat get-area.yaml | rickle serve --load-lambda --unsafe
```

Then the endpoint can be called:

```shell
curl http://localhost:8080/get_area?x=15&y=5&z=25
```

