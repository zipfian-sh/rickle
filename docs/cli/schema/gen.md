# Generate schema

---

???+ info "RSF only"

    Schema generation only supports RSF and not JSON Schema. Future development may include this functionality.

For generating a schema from a file, ``gen`` is used.
The gen tool is used for generating schemas from input. This is a useful step to start from, where a developer can then further define the schema.

```shell
rickle schema gen -h
```

Prints the following options:

```text
optional arguments:
 -h, --help          show this help message and exit
 --input  [ ...]     input file(s) to generate from
 --output  [ ...]    output file(s) to write to
 --silent, -s        silence output
 --extras, -e        include extra properties
```

Consider the following example file:

```yaml title="my-example.yaml" linenums="1"
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
```

Running the ``gen`` tool:

```shell
rickle schema gen --input my-example.yaml
```


will create the file ``my-example.schema.yaml`` as the following:


```yaml title="my-example.schema.yaml" linenums="1"
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
```

It will print the following:

```text
.\my-example.yaml -> .\my-example.schema.yaml
```

!!! note

    This can be suppressed by using the ``--silent`` flag.

!!! note

    Note that if no output name is given the filename becomes ``<filename>.schema.<ext>``.

Of course the type can also be defined by either using ``--output-type``:

```shell
rickle --output-type JSON schema gen --input my-example.yaml
```

Or implicitly with extensions in filenames:

```shell
rickle schema gen --input my-example.yaml --output my-schema.json
```

Which will result in:

```json title="my-schema.json" linenums="1"
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
```

