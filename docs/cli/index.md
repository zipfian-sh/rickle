
# CLI Tools

---

The command-line interface (CLI) of Rickle significantly amplifies its power and usability, providing developers with a streamlined way to **manipulate configuration files directly from the terminal** — no need for verbose scripting or additional tooling.

With just one command, Rickle allows seamless conversion between widely used formats like YAML and JSON (or  TOML, INI, XML). Whether you're adapting to different tech stacks or maintaining compatibility across systems, Rickle eliminates the friction of manual format translation.

But Rickle’s CLI isn’t just about format conversion—it also supports on-the-fly **schema validation and generation**. This empowers users to quickly validate data integrity against a schema or generate new schemas from existing structured data, which is especially useful in prototyping, CI/CD pipelines, and collaborative API development.

The CLI turns complex configuration management into a series of simple, declarative commands. It’s a developer-friendly interface for anyone who works with structured data — and needs that data to be correct, convertible, and easy to handle.

---

## Getting Started

To see help and usage:

```shell
rickle -h
```

Which will show the list of available options:

```text
positional arguments:
  {conv,obj,serve,schema}
    conv                Converting files between formats
    obj                 Tool for reading or editing  objects
    serve               Serving objects through http(s)
    schema              Generating and checking schemas of YAML files

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show version number
  --output-type         output file type (default = YAML)
```

!!! note  

    Outputs may differ from the documentation.

    !!! question "`serve` not showing?"
    
        If `twisted` is not installed the `serve` copmmand will not appear. 

        To install this functionality:

        ```shell
        pip install rickle[net]
        ```

---

The main tools that the `rickle` CLI exposes are:


| Command  | Description                         |
|----------|-------------------------------------|
| `conv`   | Convert between serialisation types |
| `obj`    | CRUD config data                    |
| `schema` | Generate and check schemas          |
| `serve`  | Host config server                  |

All of which are discussed in the following sections.

---

## Input/Output to Tools

All CLI tools support Unix pipes, i.e., the output of the previous command or process will be used as input. For example:

=== "Unix/linux/macOS"

    ```shell
    cat config.yml | rickle obj get /
    ```

=== "Win/Powershell"

    ```shell
    type config.yml | rickle obj get /
    ```

!!! note  

    On Windows systems the command `type` can be used instead of `cat`.



This is the preferred usage of `rickle`. Similarly, the output can always be piped or redirected:

```shell
cat config.yaml | rickle obj get /config/database > db_config.yaml
```

or for example:

```shell
cat config.yaml | rickle obj get /config/ecr/password | aws ecr get-login-password --password-stdin
```

For all tools, the input can be a file flagged with `--input` and output can be directed to a file with `--output`:

```shell
rickle obj --input config.yaml --output db_config.yaml get /config/database
```

Although this is often a less readable way and is only recommended when it makes sense to do so.

---

## Output Types

For most of the tools, the output types can be specified with the `--output-type` flag and can be one of the following:



| Type    | Installation                 | Input             | Output            |
|---------|------------------------------|-------------------|-------------------|
| `yaml`  | `pip install rickle`         | :material-check:  | :material-check:  |
| `json`  | `pip install rickle`         | :material-check:  | :material-check:  |
| `toml`  | `pip install rickle`         | :material-check:  | :material-check:  |
| `xml`   | `pip install rickle[xml]`    | :material-check:  | :material-check:  |
| `ini`   | `pip install rickle`         | :material-check:  | :material-check:  |
| `env`   | `pip install rickle[dotenv]` | :material-check:  | :material-close:  |

!!! note

    The default output type for all tools (except `serve`) will be based on what the input is. For `serve`, the default output is `JSON`.

    Certain tools have more output type options. Both `search` and `type` have `ARRAY` and `PYTHON` as extra types.