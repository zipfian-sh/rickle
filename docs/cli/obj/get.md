
# Get value from path

---

Consider the example input YAML file:

```yaml title="conf.yaml" linenums="1"
root_node:
  level_one:
    pswd: password
    usr: name
```

---

To get a value from a document, the key needs to a path in the document.

For example, getting the value of ``pswd``:

```shell
cat conf.yaml | rickle obj get /root_node/level_one/pswd
```

This will output the value to the command line:

```text
password
```

Just about any paths value can be printed to the command line:

```shell
cat conf.yaml | rickle obj get /root_node/level_one
```

This will output:

```yaml
pswd: password
usr: name
```

To output the entire document:

```shell
cat conf.yaml | rickle obj get /
```
    
Will result in:

```yaml
root_node:
  level_one:
     pswd: password
     usr: name
```

!!! note
    
    The default output is always YAML. To change the format, add the ``--output-type`` type.

Outputting the same in JSON:

```shell
cat conf.yaml | rickle --output-type JSON obj get /
```

Prints:

```json
{"root_node": {"level_one": {"usr": "name", "pswd": "password"}}}
```

!!! note

    If the ``--output`` option in ``obj`` is used to output to a file, the result is not printed to screen.

---

## cURL alternative

Seeing as a ``Rickle`` can be loaded with the JSON response from a URL, it could be used in a cURL-like manner:

```shell
rickle --output-type JSON obj --input https://official-joke-api.appspot.com/random_joke get /
```

Or alternatively

```shell
echo https://official-joke-api.appspot.com/random_joke | rickle --output-type JSON obj get /
```


```json
{
  "type": "general", 
  "setup": "Why did the girl smear peanut butter on the road?", 
  "punchline": "To go with the traffic jam.", 
  "id": 324
}
```

with the ability to get a specific value from the JSON response, using paths:

```shell
echo https://official-joke-api.appspot.com/random_joke | rickle --output-type JSON obj get /punchline
```

printing the fantastic punchline to the setup "The punchline often arrives before the set-up.":

```text
Do you know the problem with UDP jokes?
```

---

## Troubleshooting 

The most likely problem to occur is if the path can not be traversed, i.e. the path is incorrect:

```shell
cat conf.yaml | rickle --output-type JSON obj get /path_to_nowhere
```

And this will result in printing nothing (default behaviour).

Another likely problem is that the scalar can not be output in the given type.
I.e. TOML, INI, and XML for example need at least a root node.