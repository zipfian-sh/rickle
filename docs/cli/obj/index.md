---
icon: material/cog-outline
---

# Object tools

---

The `rickle obj` subcommand is a powerful extension of the `rickle` ecosystem, designed to bring config "object" manipulation into the command-line environment. It empowers users to read, explore, and modify YAML (or JSON, TOML, INI, XML, ENV, etc.) representations of "objects" without writing any Python code.

This tool serves as a dynamic interface to interact with serialized objects—allowing users to traverse attributes, retrieve or update values, remove keys, or even invoke object methods—all from the terminal. With just a single command, deeply nested values can be accessed or quick tweaks to configuration objects made.

Whether debugging a config, prototyping behavior, or orchestrating scripts that depend on specific object structures, `rickle obj` makes the process interactive and efficient. Its expressiveness is particularly well-suited for developers and automation engineers who want granular control over object structures without the boilerplate of full Python scripts.

By enabling command-line-level introspection and manipulation, `rickle obj` becomes an indispensable utility for quick adjustments, CI/CD integration, configuration management, and scriptable workflows in complex Python projects.
To see all the available options:

```shell
rickle obj -h
```
Which will show the following list of options:

```text
positional arguments:
     {get,set,del,type,search,func}
       get                 Getting values from objects
       set                 Setting values in objects
       put                 Putting values in objects
       rm                  For removing keys (paths) in objects
       type                Printing value type
       search              For searching keys (paths) in objects
       find                For finding key/value (paths) in objects

   optional arguments:
     -h, --help            show this help message and exit
     --input               input file to create object from
     --output              write to output file
     --load-lambda, -l     load lambda types
```

Using this tool requires input of a YAML, JSON, TOML (etc.) file. This is done with the ``--input`` option or alternatively piped.

=== "Piping input"

    ```shell
    cat config.yaml | rickle obj <VERB>
    ```

=== "Using `--input`"
    ```shell
    rickle obj --input config.yaml <VERB>
    ```


Where ``<VERB>`` can be one of the following:


| Verb     | Description                     |
|----------|---------------------------------|
| `get`    | Get the value at the given path |
| `set`    | Set a value at the path         |
| `put`    | Put a new value at the path     |
| `rm`     | Remove path/value               |
| `type`   | Return value type at path       |
| `search` | Search for matching paths       |
| `find`   | Find key/vlaue pairs            |
| `func`   | Exec function at path           |

These `verbs` will be elaborated on in the next subsections.

---

## Example input

In the next examples, the following YAML file will be used as example input:

```yaml title="conf.yaml" linenums="1"
root_node:
  level_one:
    pswd: password
    usr: name
```

---

## Document paths

An important first concept to understand about using most of the tools ``rickle`` has to offer is
understanding the document paths. A path is the Unix style file and directory path concept applied to
a YAML (or JSON) document.

In the `conf.yaml` file, the path to the ``pswd`` key-value pair would be:

```text
/root_node/level_one/pswd
```


Which would have the value ``password``.

!!! note
    
    The path must always start the slash ``/`` to be valid.

???+ tip
    
    The path separator can be specified by setting an environment variable "RICKLE_PATH_SEP", for example ``RICKLE_PATH_SEP=.`` for dots.

    ```shell
    export RICKLE_PATH_SEP=.
    ```
