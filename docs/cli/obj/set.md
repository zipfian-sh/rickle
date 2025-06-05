# Set value at existing path

---

Consider the example input YAML file:

```yaml title="conf.yaml" linenums="1"
root_node:
  level_one:
    pswd: password
    usr: name
```

---

To set a value in a document, the key needs be to a path, along with a value.

```shell
cat conf.yaml | rickle obj set /root_node/level_one/pswd **********
```

This will set the ``pswd`` value to ``**********`` and print the whole document with new value to the command line.

```yaml
root_node:
  level_one:
     pswd: '*********'
     usr: name
```

!!! note

    If the ``--output`` option in ``obj`` is used to output to a file, the result is not printed to screen.

For example, the following will output to a file:

```shell
cat conf.yaml | rickle --output-type JSON obj --output conf.json set /root_node/level_one/pswd *********
```

```json title="conf.json" linenums="1"
{"root_node": {"level_one": {"usr": "name", "pswd": "*********"}}}
```

Of course this could also be directed:

```shell
cat conf.yaml | rickle --output-type JSON obj > conf.json
```

!!! note

    Values can only be set for paths that exist. To create a new path, use ``put``.

This will, however, not work in the following example and result in an error:

```shell
cat conf.yaml | rickle obj set /root_node/level_one/unknown/email not@home.com
```


Which results in the error message:

```shell
error: The path /root_node/level_one/unknown/email could not be traversed
```

---

## Troubleshooting

The most likely problem to occur is if the path can not be traversed, i.e. the path is incorrect:

```text
error: The path /root_node/level_one/unknown/email could not be traversed
```
