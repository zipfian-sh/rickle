# Put value at path

---

Consider the example input YAML file:

```yaml title="conf.yaml" linenums="1"
root_node:
  level_one:
    pswd: password
    usr: name
```


---

A new key-value can be added, for example:

```shell
cat conf.yaml | rickle obj put /root_node/level_one/email not@home.com
```

Results in the added key:

```yaml
root_node:
  level_one:
     pswd: password
     usr: name
     email: not@home.com
```

Any path input to put will be created:

```shell
cat conf.yaml | rickle obj put /root_node/level_one/config/host/address 127.0.0.1
```

Results in the added key:

```yaml
root_node:
  level_one:
     pswd: password
     usr: name
     email: not@home.com
     config:
        host:
           address: 127.0.0.1
```
