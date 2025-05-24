---
icon: material/translate
---

# Conversion tool

---

The conversion process between YAML, JSON, TOML, XML, and INI using rickle involves a few straightforward steps that can be executed via its command-line interface.

To see all the available options:

``` shell
rickle conv -h
```

Which will show the list of available options:

```text
optional arguments:
     -h, --help          show this help message and exit
     --input  [ ...]     input file(s) to convert
     --input-directory   directory of input files
     --output  [ ...]    output file names, only if --input given
     --input-type        optional input type (type inferred if none)
     --verbose, -v       verbose output
```

---

## Convert file

To convert an input file ``config.json``, use the following:

```shell
cat config.json | rickle conv
```

This will print the converted file ``config.json`` as YAML (which is the default), or if specified ``--output-type`` type.

!!! note
    
    Because the input is piped, the input type is inferred but can explicitly be defined using the ``--input-type`` option.

If input is given as ``--input`` flag (or ``--input-directory``), the output will be a file with the same filename (with new extension).

```shell
rickle conv --input config.json
```

This will create a file ``config.yaml`` instead of printing.
 
!!! note
    
    The default output format is YAML. Use ``--output-type`` option for other formats.

To specify the output type:

```shell
cat config.yaml | rickle --output-type JSON conv
```

This will output the converted file (in this example as JSON).

---

## Glob whole directory

If the ``--input-directory`` option is used with a directory name, all files with an extension are converted to the same directory.
The ``--output-type`` option is needed to specify the format or else ``YAML`` will be the default output format.

```shell
rickle --output-type TOML conv --input-directory ./configs --verbose
```
This will glob all files in the directory ``./configs``, including TOML files, and output them as TOML files with the same names.

The ``--verbose`` prints a line of the input/output filenames for each conversion.

!!! note
    
    The file extensions ``yaml``, ``yml``, ``json``, ``toml``, ``ini``, ``xml``, and ``env`` will be globbed.

## Define output filenames

Input files can have output filenames explicitly defined:

```shell
rickle conv --input config.yaml --output ./configs/config_dev.toml
```

This will convert ``config.yaml`` to type ``TOML`` (because the type is inferred from the file extension)
with a new name ``config_dev.toml`` in the directory ``./configs``.

??? tip "Output types inferred from file extensions"

    Thanks to file types ommiting `--output-type` is possible.  

Multiple files can be converted at once:

```shell
rickle --output-type JSON conv --input config_dev.yaml config_tst.yaml config_prd.yaml
```

When specifying the output names, the order of output filenames must match the order of input files:

```shell
rickle conv --input config_dev.yaml config_prod.yaml --output conf-dev.json conf-prd.json
```

---

## Troubleshooting 

Most likely any occurring error would be a failure to read the file in the given format. File types are inferred from file extensions.
If no file extensions are present, files are inferred by trying to read them in the different formats.
If all fails, no operation is performed and an error message printed.