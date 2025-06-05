---
icon: octicons/file-code-16
---

# Rickle

!!! info "Inheritance"

    All base function such as `get`, `set`, `dict`, `to_yaml` etc. are inheritted by `Rickle`. 
    These methods are not documented under `Rickle` as they are already covered under `BaseRickle`.
    ``` mermaid
    graph LR
      A[BaseRickle] --> B[Rickle];
      B[Rickle] --> C[UnsafeRickle];
    ```

::: rickle
    handler: python
    options:
      members_order: source
      show_labels: true
      show_signature: false
      show_symbol_type_heading: true
      show_overloads: true
      show_inheritance_diagram: true