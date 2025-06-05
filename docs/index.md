# `rickle` - Python tools for working with configurations


**`rickle`** is a versatile Python library and command-line tool offering a wide range of functionalities for working with YAML, JSON, TOML, INI, XML, and .ENV data.

### Features

1. **Serialization**  
   Serialize Python objects to formats like YAML or JSON—ideal for converting data structures into human-readable configuration files.

2. **Schema Validation**  
   Validate YAML/JSON/etc. against schemas to ensure structural consistency.

3. **Schema Generation**  
   Automatically generate schemas from existing config files to formalize and document data structures.

4. **Conversion**  
   Seamlessly convert between YAML, JSON, INI, XML, and .ENV formats to ease system interoperability.

5. **Simple Web Server**  
   An experimental feature lets you define REST endpoints via YAML/JSON/etc. files—perfect for prototyping APIs or serving config data.

`rickle` simplifies tasks like serialization, validation, generation, and conversion. It's especially valuable for developers and data engineers working with structured data.

---

## Install

```shell
pip install rickle
```

???+ tip "Optionall extras"

      Extra Python packages required by `rickle` can be installed alongside (see [Installation](installation.md))
      To install **all** extras:

      ```shell
      pip install rickle[full]
      ```

---

## Quick Start

Create a YAML file named `config.yaml`:

```yaml title="config.yaml"
conf:
   db_connection:
      acc_name:
         type: env
         load: ACC_NAME
         default: developer_account
      acc_pass:
         type: env
         load: ACC_PASS
      database_name: public
```

Then use `rickle`:

```pycon
>>> from rickle import Rickle

>>> config = Rickle('./config.yaml')

>>> config.conf.db_connection.dict()
{'acc_name' : 'acceptance_account', 'acc_pass' : 'asd!424iXj', 'database_name' : 'public'}

>>> config.conf.db_connection.acc_pass
'asd!424iXj'

>>> config('/conf/db_connection/acc_pass')
'asd!424iXj'
```

See the [Basic usage](basic_examples.md) for more usage patterns. CLI details are available in the [CLI](cli/index.md) section.

---

## Changes and History

For full changelog, see [Changelog](changelog.md).

**Version 1.2.2 (2025-02-17)**:

- Project renamed from `rickled` to `rickle`
- Fixed CLI execution bug
- Made `provider_access_key` optional for `secret` type


---

## Coverage

For test coverage, see the [coverage report](https://zipfian.science/docs/rickle/coverage/index.html).