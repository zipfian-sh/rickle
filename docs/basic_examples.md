# Examples of basic usage

---

There are many uses of ``rickle``, and some of the functionality is described here through examples.

## Simple Config

The most basic usage of a ``rickle`` is to use it as a config object. Let's create a scenario in which this might be useful.
Say you have a common API served through a FastAPI app and you need 10 versions of the API, each having the same code base but with different databases in the back, and some different endpoint configurations.

Let's make our first simple config in YAML, call it ``config_US.yaml``.

```yaml title="config_US.yaml" linenums="1"
APP:
    api_info:
        name: users_api
        docs_page: '/dok'
        version: '1.0.0'
    database:
        host: 127.0.0.1
        user: local
        passw: ken-s3nt_me
    endpoints:
        status:
            description: Gets the status for a region in the country.
            params:
                region: US
        users:
            description: Gets the users for a given city.
            params:
                city: Seattle
```

As an example, we will have the simple API:

```python title="app.py" linenums="1" hl_lines="7 8 9 12 18 23 24 25"
from fastapi import FastAPI
from rickle import Rickle
from some_database import DBConnection

config = Rickle('./config_US.yaml')
app = FastAPI(
    title=config.APP.api_info.name,
    version=config.APP.api_info.version,
    docs_url=config.APP.api_info.docs_page,
)

conf_status_ep = config.APP.endpoints.get('status')
if conf_status_ep:
    @app.get('/status', description=conf_status_ep.description)
    async def get_status(region: str):
        return some_function_here(region)

conf_users_ep = config.APP.endpoints.get('users')
if conf_users_ep:
    @app.get('/users', description=conf_users_ep.description)
    async def get_users(city: str):
        def get(self):
            with DBConnection(host=config.APP.database.host,
                              user=config.APP.database.user,
                              passw=config.APP.database.passw
                             ) as conn:
                results = conn.safe_exec(f"SELECT * FROM users WHERE city = [city]", city) 
            return results
```


Here we can see that the config YAML file is loaded as a ``rickle``. In the creation of the FastAPI app, we load details from the ``rickle``.
We then get the settings for the endpoint "status". If the endpoint is not defined in the YAML, we simply don't create it.
That gives us the power to create a new YAML config for another country where the "status" endpoint does not exist.


## Create from different things

The config does not have to be loaded from a YAML file. It does not even have to be loaded.

```python linenums="1"
from rickle import Rickle

# Create an empty Rickle
config = Rickle()

# Loaded from a JSON file
config = Rickle('./config_ZA.json')

# Create from a Python dictionary
d = {
    'APP' : {
        'details': {
            'name': 'user_api',
            'doc_page': '/doc',
            'version': '1.0.0'
        },
        'database': {
            'host': '127.0.0.1',
            'user': 'local',
            'passw': 'ken-s3nt_me'
       },
        'endpoints': {}
    }
}
config = Rickle(d)
```

Or load it from a string of YAML/JSON/TOML etc.

```python linenums="1"
# Create from a YAML string (or a JSON string)
yaml_string = """
APP:
    details:
        name: user_api
        doc_page: '/doc'
        version: '1.0.0'
    database:
        host: 127.0.0.1
        user: local
        passw: ken-s3nt_me
    endpoints: null
"""

config = Rickle(yaml_string)
```



## Add templating-like string replacements


For the less likely event that you need to modify the input string dynamically before loading, arguments can be given as follows.

```yaml title="config_ZA.yaml" linenums="1"
APP:
    details:
        name: user_api
        doc_page: {{documentation_endpoint}}
        version: '1.0.0'
```

And then the string will be searched and replaced before the YAML is loaded and a ``rickle`` is constructed.

```python linenums="1"
from rickle import Rickle

# Loaded from a JSON file
config = Rickle('./config_ZA.yaml', documentation_endpoint='/za_docs')
```

This will in effect change the YAML to the following (before loading it).

```yaml linenums="1"
APP:
    details:
        name: user_api
        doc_page: /za_docs
        version: '1.0.0'
```

Even though the possibilities are opened up here, there are probably better ways to solve this (such as using ENV vars as shown later in this examples page).

???+ question "Is this Jinja?"

    Noticable is that this is very similar to Jinja syntax, but it is is **NOT Jinja**.

???+ tip "Changing the handlebars"

    If you do use Jinja and want to still keep this sort of string replacement functionality, the handlebars can be changed:
    ```python
    conf = Rickle('conf.toml', RICKLE_HANDLEBARS='[[]]', some_parameter='some value')
    ```
    
    !!! note

        The length of the handlebar string MUST be an even number, i.e. 2, 4, 6 etc. This is because the string is *chopped* in the middle and the first half taken as opening braces, the second half as closing.
    

## Loading multiple files

Rickle is not limited to only loading configs from one file/string. Multiple configs can be loaded into one ``rickle`` at once.

```python
# Load a list of YAML files
config = Rickle(['./config_US.yaml', './config_ZA.yaml'])

print(config[0].details.version)
print(config[1].details.version)
```

The behaviour here is that a list input results in the `rickle` itself becoming a list object.  

!!! info "Changing `_input_type`"
    
    When a `rickle` is created from a list object, the input type `array` is assigned. 

### Multiple docs in YAML

`rickle` can load a single YAML file containing multiple documents. For example:

```yaml title="configs.yaml" linenums="1"
app:
  user: name
  pass: admin
  
---

app: 
  user: bob
  pass: god

```

Which, when loaded turn the `rickle` into a list (`array`) type.

```python linenums="1"
configs = Rickle('configs.yaml')

print(configs[0].user)
print(configs.get('/[1]/pass')) # Using path like access
```

### JSONL (JSON lines)

As with multiple docs in YAML, JSON lines files can also be loaded using `rickle`:

```json title="streams.jsonl" linenums="1"
{ "name" : "stream_alpha", "cap": 10 }
{ "name" : "stream_fx", "cap": 1}
```

Which also turn the `rickle` into a list (`array`) type.

```python linenums="1"
streams = Rickle('streams.jsonl')

print(streams[0].name)
print(streams.get('/[1]/cap')) # Using path like access
```

## Referencing in YAML

What is especially powerful of YAML is the ability to add references.
If we had a lot of duplication, we can simply reference the same values.

```yaml linenums="1" hl_lines="11 12 18 19 24 25"
APP:
  details:
      name: user_api
      doc_page: '/doc'
      version: '1.0.0'
  database:
      host: 127.0.0.1
      user: local
      passw: ken-s3nt_me
  default_params:
     db_version: &db_version '1.1.0'
     language: &language 'en-US'
  endpoints:
     status:
        description: Gets the status for a region in the country.
        params:
           region: US
           language: *language
           db_version: *db_version
     users:
        description: Gets the users for a given city.
        params:
           city: Seattle
           language: *language
           db_version: *db_version
```

This results in the values on lines 18 and 24 are pre-filled with the value ``'en-US'`` as defined on line 12.
Similarly lines  19 and 25 are pre-filled with ``'1.1.0'`` as defined on line 11.

## Strings, Repr


A ``rickle`` can have a string representation, which will be in YAML format.

```pycon
>>> rick = Rickle('test.yaml')

>>> print(str(rick))
database:
 host: 127.0.0.1
 user: local
 passw: ken-s3nt_me

>>> print(repr(r))
Rickle(database=Rickle(host='127.0.0.1', user='local', passw='ken-s3nt_me'))
```

!!! note

    `str` will give the deserialised version where `repr` will give a raw (serialised) view.

## Serialise to YAML, JSON, TOML, XML, INI.

A ``rickle`` can also be *dumped* to YAML or JSON (or TOML, XML, INI).

```python linenums="1"
rick = Rickle('test.yaml')

rick.to_yaml('other.yaml')
rick.to_json('other.json')
rick.to_toml('other.toml')
rick.to_xml('other.xml') # If xmldict package is installed
rick.to_ini('other.ini')

# Or if a filename is omitted, the dumped string is returned

rick.to_yaml()
rick.to_json()
rick.to_toml()
rick.to_xml() # If xmldict package is installed
rick.to_ini()
```

By default, the ``dict`` and ``to_yaml`` (etc.) method returns the in deserialised form. For serialised form, ``serialised=True`` can be passed.

```yaml title="" linenums="1"
root:
 USERNAME:
   type: env
   load: USERNAME
 HOST: 123.0.0.1
```

The above example will give two different results based on serialisation:

```pycon
>>> rick = Rickle('db_conf.yaml')
>>> print(rick.to_yaml())
root:
 USERNAME: HE-MAN
 HOST: 123.0.0.1

>>> print(rick.to_yaml(serialised=True))
root:
 USERNAME:
   type: env
   load: USERNAME
 HOST: 123.0.0.1
```

### When `rickle` is an `array`

When initialised as an `array` (list-like) type, different behaviour for `to_json` serialisation becomes available.

By default, if a `rickle` is an `array`, the `to_json` method will serialise as a JSON lines string. This can be avoided by setting `#!python lines=False`:

```pycon
>>> streams = Rickle('streams.jsonl') # Using streams.jsonl example
>>> print(streams.to_json())
{"name": "stream_alpha", "cap": 10}
{"name": "stream_fx", "cap": 1}

>>> print(streams.to_json(lines=False))
[{"name": "stream_alpha", "cap": 10}, {"name": "stream_fx", "cap": 1}]
```

## `dict` like functionality

A ``rickle`` can act like a Python dictionary, like the following examples:

```pycon
>>> rick = Rickle({'key' : 'value', 'k2' : 0.2})

>>> list(rick.items())
[('key', 'value'), ('k2', 0.2)]

>>> rick.values()
['value', 0.2]

>>> rick.keys()
['key', 'k2']

>>> rick.get('k2', default=0.42)
0.2

>>> rick.get('k3', default=0.42)
0.42

>>> rick['new'] = 0.99
>>> rick['new'] * rick['k2'] 
0.198
```

A ``rickle`` can also be converted to a Python dictionary:

```pycon
>>> rick = Rickle('test.yaml')

>>> rick.dict()
{'key' : 'value', 'k2' : 0.2}
```

## `list` like functionality

Similarly, a `rickle` can have list like functionality when it is an `array` type.
Consider the "configs.yaml" example:

```yaml title="configs.yaml" linenums="1"
app:
  user: name
  pass: admin
  
---

app: 
  user: bob
  pass: god

```

The `list` method has to be used to serialise data: 

```pycon
>>> rickle = Rickle("configs.yaml")
>>> rickle.list()
[{'app': {'user': 'name', 'pass': 'admin'}}, {'app': {'user': 'bob', 'pass': 'god'}}]

>>> len(rickle)
2

>>> [rick.app.user for rick in rickle]
['name', 'bob']
```

## Paths and searching

Another useful piece of functionality is the ability to use paths with `rickle`.

### Search keys

We can search for paths by using the ``search_path`` method. Assume a rather large config file has multiple paths to settings concerning a "point": 

```pycon
>>> rickle.search_path('point')
['/config/default/point', '/config/control_A/control/point', '/config/control_B/control/point', '/docs/controls/point']
```

### Finding key/value pairs

Where searching is only useful for finding a key path, when *querying* a key with a certain value, the `find_key_value` method comes in handy: 

```pycon
>>> rickle.find_key_value('point', 42, op="==")
['/config/default/point']
```

And relative paths can be used to search in a more specific *corner* of the config:

```pycon
>>> rickle.find_key_value('/control/point', 42, op=">=")
['/config/control_B/control/point']
```

??? info "Comparison operators"

    
    | Comparison         | Op   | Alternative |
    |--------------------|------|-------------|
    | equals             | `=`  | `eq`        |
    | not equals         | `!=` | `ne`        |
    | less than          | `<`  | `lt`        |
    | greater than       | `>`  | `gt`        |
    | less than equal    | `<=` | `lte`       |
    | greater than equal | `>=` | `gte`       |



### Using paths to `get`, `set`, `put`, or `remove`.

We can access the values by using the paths. If we have the following YAML:

```yaml title="example.yml" linenums="1"
path:
  level_one:
     level_two:
        member: 42
        list_member:
         - 1
         - 0
         - 1
         - 1
         - 1
```
   
Consider the following examples for using paths:

```pycon
>>> rickle = Rickle("example.yml")
>>> rickle.get('/path/level_one/level_two/member') == 42
True

>>> rickle.get('/path/level_one/level_two/list_member')
[1,0,1,1,1]

>>> rickle.get('/path/level_one/level_two/list_member/[1]') == 0
True

>>> rickle.set('/path/level_one/level_two/member', 72)
>>> rickle.path.level_one.level_two.member == 72
True

>>> rickle.remove('/path/level_one/level_two/list_member')
>>> print(str(rickle))
path:
  level_one:
    level_two:
      member: 72
```

!!! tip

    The path separator can be specified by setting an environment variable "RICKLE_PATH_SEP", for example ``RICKLE_PATH_SEP=.`` for dots, or using the init argument ``RICKLE_PATH_SEP``.

    ```pycon
    >>> test_rickle = Rickle('example.yml', RICKLE_PATH_SEP='.')
    
    >>> test_rickle('.path.level_one.level_two.member') == 42
    True
    ```

   






