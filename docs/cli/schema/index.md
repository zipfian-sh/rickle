---
icon: material/file-check
---

# Schema tools

---

Schema development is at the heart of `rickle`'s configuration tooling with support for schema generation and validation, ensuring that structured data is not only easy to manage — but also reliable, predictable, and ready to use in production environments.

`rickle` supports two distinct schema frameworks, offering flexibility depending on your needs:

---

## `rickle` Schema Framework (RSF)

???+ tip "Install the validators"

    For support using the validators, install the Python package using :
    ```shell 
    pip install rickle[validators]
    ```

The default schema engine in `rickle` is built around the **Rickle Schema Framework** (RSF), a simple and expressive system tailored for working directly with Python-native data structures. It is lightweight by design but extensible enough to handle more advanced validation scenarios. This framework optionally integrates with `py.validator`, allowing for enhanced type checking of complex fields like IP addresses, URLs, file paths, and more.

This native schema format is ideal for fast prototyping, internal tooling, and environments where Python-centric validation rules are preferred. It enables auto-generation of schemas from YAML or JSON files, and provides clear error reporting when validating data against expected structures.

---

## JSON Schema Support

???+ tip "Install `jsonschema`"

    For support using JSON schema, install the Python package using:
    ```shell 
    pip install rickle[jsonschema]
    ```

For teams and applications that require interoperability with standard tools and formats, `rickle` also offers support for [JSON Schema](https://json-schema.org/), a widely adopted open standard for validating JSON documents. This is particularly useful when sharing schemas across services, generating documentation, or integrating with frontend frameworks, API tools, and other external systems.

With JSON Schema, `rickle` can validate configuration structures against a universally accepted format, ensuring future-proof config management and interoperability options beyond RSF. 

---

Whether you're using RSF for its simplicity and Python alignment, or the JSON Schema standard for compatibility and broader tooling support, `rickle` gives you the power to generate schemas from real data and validate your configuration files with confidence.