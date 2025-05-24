# Value type 

---

Consider the example input YAML file:

```yaml title="conf.yaml" linenums="1"
root_node:
  level_one:
    pswd: password
    usr: name
```


---

The ``type`` option will print the `JSON` value type, for example:

```shell
cat conf.yaml | rickle obj type /root_node/level_one/pswd
```

Outputs:

```text
string
```


Or:

```shell
cat conf.yaml | rickle obj type /root_node/level_one
```

Outputs:

```text
object
```

Using ``--output-type`` the printed type changes. Available types include ``YAML``, ``JSON`` (default), ``TOML``, ``XML``, and ``python``.

Depending on this type, the value could be:


   | Python | YAML      | JSON     | TOML       | XML                 |
   |--------|-----------|----------|------------|---------------------|
   | str    | str       | string   | String     | xs:string           |
   | int    | int       | number   | Integer    | xs:integer          |
   | float  | float     | number   | Float      | xs:decimal          |
   | bool   | boolean   | boolean  | Boolean    | xs:boolean          |
   | list   | seq       | array    | Array      | xs:sequence         |
   | dict   | map       | object   | Key/Value  | xs:complexType      |
   | bytes  | binary    |          |            |                     |
   | *      | Python    | object   | Other      | xs:any              |

Examples:

```shell
cat conf.yaml | rickle --output-type XML obj type /root_node/level_one
```

Prints:

```text
xs:complexType
```
