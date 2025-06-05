# Search matching paths

---

Searching is a useful way to find the paths in a document. The following file with multiple repeated names is used in the examples:

```yaml title="conf-multi.yaml" linenums="1"
root_node:
    level_one:
        pswd: password
        usr: name
    other:
        usr: joe
    usr: admin
```

To get the path to ``pswd``:

```shell
cat conf-multi.yaml | rickle obj search pswd
```

Which will print the path as a YAML list by default (use the type ``--output-type`` flag for other output):

```text
- /root_node/level_one/pswd
```


Where searching for the ``usr`` key:

```shell
cat conf-multi.yaml | rickle obj search usr
```

prints the following paths:

```text
/root_node/usr
/root_node/level_one/usr
/root_node/other/usr
```


To print the values as YAML (or JSON), use the ``--output-type`` type ``YAML``:

```shell
cat conf-multi.yaml | rickle --output-type YAML obj search usr
```

prints the following paths:

```text
- /root_node/usr
- /root_node/level_one/usr
- /root_node/other/usr
```

The path separator will be used as is set in the env:

```shell
export RICKLE_PATH_SEP=.
cat conf-multi.yaml | rickle obj search usr
```

results in:

```text
.root_node.usr
.root_node.level_one.usr
.root_node.other.usr
```

