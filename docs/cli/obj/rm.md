# Remove key

---

Consider the example input YAML file:

```yaml title="conf.yaml" linenums="1"
root_node:
  level_one:
    pswd: password
    usr: name
```

---

To remove a value, use the ``rm`` option:

```shell
cat conf.yaml | rickle obj rm /root_node/level_one/pswd
```

Resulting in:

```text
root_node:
    level_one:
        usr: name
```

