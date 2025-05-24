# Extended usage

---

## Environment variables

Using the `Rickle` class we can add a lot more extended types. One being the environment variable.

Here we have a file ``db_conf.yaml`` again, but this time we are loading the values from OS env:

```yaml title="db_conf.yaml" linenums="1"
database:
  host:
     type: env
     load: DB_HOST
     default: 127.0.0.1
  user:
     type: env
     load: DB_USERNAME
  passw:
     type: env
     load: DB_PASSWORD
```


!!! note   

    A default value can be defined. The default is always `#!python None`, so no exception is raised if the env var does not exist.

Now when loading the file:

```pycon
>>> conf = Rickle("db_conf.yaml")
>>> print(conf.to_yaml())
database:
  host:
    127.0.0.1
  user:
    HE-MAN
  passw:
    grayskull
```

And this data can be dumped in serialised form again:

```pycon
>>> conf = Rickle("db_conf.yaml")
>>> print(conf.to_yaml(serialised=True))
database:
  host:
    type: env
    load: DB_HOST
    default: 127.0.0.1
  user:
    type: env
    load: DB_USERNAME
    default: null
  passw:
    type: env
    load: DB_PASSWORD
    default: null
```

## Add CSV


A local CSV file can be loaded as a list of lists, or as a list of `rickle`s.

If we have a CSV file with the following contents:

```text title="table.csv" linenums="1"
A,B,C,D
j,1,0.2,o
h,2,0.9,o
p,1,1.0,c
```

Where ``A,B,C,D`` are the columns, the following will load a list of three ``rickle`` objects.

```yaml title="csv_example1.yaml" linenums="1" hl_lines="4"
csv:
  type: csv
  file_path: './table.csv'
  load_as_rick: true
  fieldnames: null
```

The data appears as in the following examples:

```pycon
>>> rick = Rickle('csv_example1.yaml')

>>> rick.csv[0].A == 'j'
True

>>> rick.csv[0].C == 0.2
True

>>> rick.csv[-1].D == 'c'
True
```

!!! info "Fieldnames undefined"

    If ``fieldnames`` is null, the first row in the file is assumed to be the names.

If the file is not loaded as a Rickle, lists of lists are loaded, and this assumes that the first row is not the field names.

```yaml title="csv_example2.yaml" linenums="1" hl_lines="4"
csv:
  type: csv
  file_path: './table.csv'
  load_as_rick: false
  fieldnames: null
```

resulting in the examples:

```pycon
>>> rick = Rickle('csv_example2.yaml')

>>> rick.csv[0]
['A','B','C','D']

>>> rick.csv[-1]
['p',1,1.0,'c']
```

Finally, a third way to load the CSV is to load the columns as lists. Changing the previous CSV file and removing the header:

```text title="table2.csv" linenums="1"
j,1,0.2,o
h,2,0.9,o
p,1,1.0,c
```

And defining the fieldnames in the YAML:

```yaml title="csv_example2.yaml" linenums="1" hl_lines="5"
csv:
  type: csv
  file_path: './table2.csv'
  load_as_rick: false
  fieldnames: [A, B, C, D]
```

Result in the following behaviour:

```pycon
>>> rick = Rickle('csv_example2.yaml')

>>> rick.csv.A
['j','h','p']

>>> rick.csv.C
[0.2,0.9,1.0]
```


## Add from file


Other files can also be loaded, either as another ``rickle``, a binary file, or a plain text file.


```yaml title="example_file1.yaml" linenums="1" hl_lines="4"
another_rick:
  type: file
  file_path: './tests/test_config.json'
  load_as_rick: true
  deep: true
  load_lambda: true
```

This will load the contents of the file as a ``rickle`` object.

```yaml title="example_file2.yaml" linenums="1" hl_lines="4"
another_rick:
  type: file
  file_path: './tests/placebos/test.txt'
  load_as_rick: false
  encoding: UTF-16
```

This will load the contents as plain text.

```yaml title="example_file3.yaml" linenums="1" hl_lines="4"
another_rick:
  type: file
  file_path: './img/output.bin'
  is_binary: true
```

This will load the data as binary.

### Hot load!

The data in the file can also be loaded on function call. This is done with the ``hot_load: true`` property.

!!! tip

    To use the ``hot_load`` functionality, the `Rickle` object needs to be initialised with ``load_lambda=True``.

    !!! warning "Never `load_lambda` unknown sources"

        Using ``load_lambda=True`` and ``hot_load`` could come with potential security risks as the ``eval`` function is used to execute code.
        Code injection is a high risk and this advanced usage is only recommend when a high level of trust in the source is established.
        Do not blindly load files with ``load_lambda=True``.

Referring to example `example_file2.yaml`:

```pycon
>>> rick = Rickle("example_file2.yaml")
>>> rick.another_rick
"bush hid the facts"
```

Where if the contents of this text file changes, we can simply read its contents when called:

```yaml title="example_file2.yaml" linenums="1" hl_lines="4"
another_rick:
  type: file
  file_path: './tests/placebos/test.txt'
  hot_load: true
```

Then (assuming the contents of the text file changed since):

```pycon
>>> rick = Rickle("example_file2.yaml", load_lambda=True)
>>> rick.another_rick()
"bush hid the facts"

>>> rick.another_rick()
"this app can break"
```

## Add from API

Data can also be loaded from an API, expecting a JSON response.

```yaml linenums="1"
crypt_exchanges:
  type: api
  url: https://cryptingup.com/api/exchanges
  expected_http_status: 200
```

This will load the JSON response as a dictionary. But the contents can also be loaded as a ``rickle``.

!!! danger

    Note, this can be dangerous, therefore a ``load_lambda`` property is defined. 
    **However, this response can point to another API call with ``load_lambda`` set as true.**
    
    Only load API responses as Rickles when you trust the contents, or set the ENV ``RICKLE_SAFE_LOAD=1``.

```yaml linenums="1" hl_lines="5 6 7"
crypt_exchanges:
  type: api
  url: https://cryptingup.com/api/exchanges
  expected_http_status: 200
  load_as_rick: true
  deep: true
  load_lambda: false
```

Other properties that can be defined:

| Prop                   | Value / Type         |
|------------------------|----------------------|
| `url`                  | string               |
| `http_verb`            | 'GET' or 'POST'      | 
| `headers`              | object               | 
| `params`               | object               | 
| `body`                 | object               | 
| `load_as_rick`         | bool / true or false | 
| `deep`                 | bool / true or false | 
| `load_lambda`          | bool / true or false | 
| `expected_http_status` | integer              | 
| `hot_load`             | bool / true or false | 

### Hot load!

The property ``hot_load`` will turn this into a function that, when called, does the request with the params/headers.

```yaml title="crypt.yaml" linenums="1" hl_line="5" 
crypt_exchanges:
  type: api
  url: https://cryptingup.com/api/exchanges
  hot_load: true
```

This example will load the results hot off the press.

```pycon
>>> rick = Rickle('crypt.yaml', load_lambda=True)
>>> rick.crypt_exchanges()
{...}
```

Notice how it is called with parentheses because it is now a function (``hot_load=true``).

!!! note

    To use the ``hot_load`` functionality, the Rickle object needs to be initialised with ``load_lambda=True``.

!!! danger

    Using ``load_lambda=True`` and ``hot_load`` could come with potential security risks as the ``eval`` function is used to execute code.
    Code injection is a high risk and this advanced usage is only recommend when a high level of trust in the source is established.
    
    **Do not blindly load files with ``load_lambda=True``.**

???+ tip "Dynamic `params`, `body`, `headers`"

    What's even more useful of a hot load is that the `body`, `params`, and `headers` can be passed when calling the function:
    
    ```pycon
    >>> rick = Rickle('secret_api.yaml', load_lambda=True)
    >>> rick.user_list(headers={'api_key': 'XXX'}, params={'gender': 'female'})
    {...}
    ```

## Add base 64 encoded

A base 64 string can be loaded as bytes.

```yaml linenums="1"
bin_encoded:
  type: base64
  load: dG9vIG1hbnkgc2VjcmV0cw==
```

## Add secrets

!!! note "Install the required Python package"

    The required Python packages need to be installed, see the table below.

Cloud secret providers are important to modern configuration files. `rickle` loosely supports some of the major cloud providers.

To add a secret:

```yaml linenums="1"
some_cloud_secret:
    secret_id: your-secret-id
    provider: aws
    provider_access_key: key
    secret_version: latest
    load_as_rick: false
    deep: false
    load_lambda: false
```

| Cloud provider      | value         | `provider_access_key`      | `provider_access_key` required props                        | Required Python package                                                                     | 
|---------------------|---------------|----------------------------|-------------------------------------------------------------|---------------------------------------------------------------------------------------------| 
| **AWS**             | `aws`         | `object`, file or `null`   |                                                             | `boto3`  [PyPI](https://pypi.org/project/boto3/)                                            |
| **Google Cloud**    | `google`      | `object`, file or `null`   | `project_id`                                                | `google-cloud-secret-manager` [PyPI](https://pypi.org/project/google-cloud-secret-manager/) |
| **Microsoft Azure** | `azure`       | `object`, file or `null`   | `key_vault_name`, `tenant_id`, `client_id`, `client_secret` | `azure-keyvault-secrets`  [PyPI](https://pypi.org/project/azure-keyvault-secrets/)          |
| **HashiCorp**       | `hashicorp`   | `object`, file or `null`   |                                                             | `hvac`     [PyPI](https://pypi.org/project/hvac/)                                           |
| **Oracle**          | `oracle`      | `object`, file or `null`   |                                                             | `oci`         [PyPI](https://pypi.org/project/oci/)                                         |
| **IBM Cloud**       | `ibm`         | `object`, file or `null`   | `apikey` and `service_url`                                  | `ibmcloud-python-sdk`  [PyPI](https://pypi.org/project/ibmcloud-python-sdk/)                |

### Examples

Below are some different examples with different ways to getting to the provider access key:

```yaml linenums="1"
aws_secret:
    secret_id: my-secret-id
    provider: aws
    provider_access_key: null # assuming boto picks up env.
gcp_secret:
    secret_id: my-secret-id
    provider: google
    provider_access_key: gcp_secret.json # will thus load SA key from JSON file
azure_secret:
    secret_id: my-secret-id
    provider: google
    provider_access_key: 
      key_vault_name: XXXX
      tenant_id: XXXX
      client_id: XXXX
      client_secret: XXXX
```