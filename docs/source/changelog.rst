

.. _changelog-page:

Changelog
**************************

History
==========================

Version 1.2.4 (2025-05-20)
--------------------------

* Documentation and README cleanup and fixing errors (spelling, examples, etc.).
* Added ``Basic Auth`` to serve tool.
* Extending ``find`` by using paths for relative matching.
* Updating links to new repository.

Version 1.2.3 (2025-03-25)
--------------------------

* Adding ability to load list (array) instead of dict (object), opening way for lists of configs.
* New list type internal representation "array".
* Added new ``put`` method for putting values in Rickle with any path. Where the path does not exist, the path will be created.
* Changed ``set`` to only mutate paths that already exist. Creating clear distinction between set and put.
* Added multi document YAML support.
* Added JSONL support.
* Added new ``find`` CLI tool to find key / value pairs.

Version 1.2.2 (2025-02-17)
--------------------------

* Rename of entire project from ``rickled`` to ``rickle``!
* Fixed bug in CLI tool not able to run
* Made ``provider_access_key`` optional for ``secret`` type.
* Can now use list type in path method, for example ``[0]/path/to`` will reference the first object in the list.

Version 1.2.1 (2025-02-12)
--------------------------

* Major additions and changes, bumped version to ``1.5.0``.
* Init args now parsed with opening braces ``{{`` and closing braces ``}}``.
* Opening and closing braces can be defined using environment variables ``RICKLE_OPENING_BRACES`` and ``RICKLE_CLOSING_BRACES``.
* ``RICKLE_OPENING_BRACES`` and ``RICKLE_CLOSING_BRACES`` can also be passed as init arguments.
* Added optional INI support.
* Added optional .ENV support if extras installed ``pip install rickled[dotenv]``.
* Added optional XML support if extras installed ``pip install rickled[xml]``.
* Renamed optional extras for twisted, now installed ``pip install rickled[net]``.
* With added ability to use XML, keys are now cleansed of non alphabetic characters, but kept for serialisation.
* Added more customisation. Path separator can now be define with init arg ``RICKLE_PATH_SEP`` or environment variable ``RICKLE_PATH_SEP``.
* Added list type index getter to paths, for example ``/path/to/a_list[0]`` returns first element (if ``a_list`` is of list type)
* Added static method ``flatten_dict`` to squash a Python dictionary into a thin dictionary with depth of 1.
* Undo the flattening of a dictionary with static method ``inflate_dict``.
* Now able to dump to INI file or string using ``to_ini``.
* When reading INI, dictionaries are automatically inflated, split on ``RICKLE_INI_PATH_SEP`` env var or init arg.
* Furthermore, ``RICKLE_INI_OPENING_BRACES`` and ``RICKLE_INI_CLOSING_BRACES`` can be set with env var or init arg.
* Removed unsafe code and usage into separate class, ``UnsafeRickle``.
* Added optional schema validator if extras installed (only for Python>3.8) ``pip install rickled[validators]``.
* Adding ability to pipe into CLI tool, i.e. perform ``cat file.json | rickle conv -x json -t yaml``.
* Added a helper ``classify_string`` to tools to classify a string type.
* Renaming optional arguments for CLI in order to be more clear on their meaning.
* ``-i`` becomes ``--input``
* ``-d`` becomes ``--dir``
* ``-o`` becomes ``--output``
* ``-t`` becomes ``--output-type``
* Added ``full`` to install extras to install all extras.
* Alternative for ``from_file`` type is now ``file``. Will be deprecated in the future.
* Alternative for ``from_csv`` type is now ``csv``. Will be deprecated in the future.
* Deprecating ``add_env_variable`` for ``add_env``.
* Deprecating ``add_csv_file`` for ``add_csv``.
* Deprecating ``add_from_file`` for ``add_from``.
* Deprecating ``add_api_json_call`` for ``add_api_json``.
* Deprecating ``add_attr`` for ``add``.
* New init arg ``RICKLE_NAME_CLEAN_UP`` to skip cleaning key names of disallowed chars.
* Fixed logical flaw in ``dict`` where cleaned up keys not being used.
* Added helper mapping ``get_native_type_name`` to map Python type names to format native names.
* Renamed schema types to conform more to JSON schema, i.e. ``dict`` becomes ``object``, ``list`` becomes ``array`` etc.
* Added ``min`` and ``max`` to array type in schema validation.
* Added ability to use ``jsonschema`` instead in ``Schema.schema_validation`` by setting ``use_json_schema=True`` if jsonschema is installed.
* Added ``--extras`` to schema generation to add things like "required" etc.
* Renamed ``schema`` to ``properties`` for objects in default rickle schema.
* Renamed ``schema`` to ``items`` for objects in default rickle schema.
* Added ``add_secret`` to Rickle, now able to add secrets from cloud providers ``aws``, ``google``, ``azure``.
* Added ``add_random_value`` to Rickle, using ``generate_random_value`` in tools. Useful for mock data.
* Moved ``--output-type`` to the main argument parser ``rickle``.

Version 1.1.3 (2024-05-05)
--------------------------

* New addition: TOML now supported

Version 1.1.2 (2024-04-23)
--------------------------

* Minor fix in schema tool where bool mistaken as int.
* Added CLI tools documentation.
* Fixed bug when using CLI tool and twisted not installed, better error handling in CLI tools.
* Changed the default ``serialised=False`` for the to YAML and JSON file/string methods.
* Changed default behaviour of ``serve`` to return deserialised form.
* Added 404 response to serve when path can not be traversed.
* Added ``-s`` to ``serve`` to serve the file in serialised form.
* Added ``-t`` to ``serve`` to serve the file in output type JSON or YAML (JSON by default).
* Changed ``-f`` to ``-i`` in ``serve`` tool for consistency.

Version 1.1.1 (2024-03-19)
--------------------------

* Updated documentation and links to pages.

Version 1.1.0 (2024-02-05)
--------------------------

* Added ``set`` to BaseRickle, as a equivalent to the ``get`` method.
* Updated the ``get`` method to handle document paths.
* Added ``remove`` method to delete items from object.
* Added the ``__delitem__`` dunder, now able to ``del rickle['key']``.
* Fixed bug where ``search_path`` was exiting loops in dictionary too early (after first find).
* Implemented type guessing of params for functions when using path like calling.
* Added ability to add params to callable. Example ``rickle('/path/to/func', x=1, y='str')``.
* Bug fix in trying to parse URL by user ``deajan``, commit ``7cb1773``.


Version 1.0.2 (2023-12-12)
--------------------------

* Added ``strict`` boolean parameter for allowing properties that are reserved keywords.

Version 1.0.1 (2023-10-03)
--------------------------

* Added the ability to load a Rickle from URL at init.
* Added the ``-b`` flag to ``serve`` CLI tool to open host on browser.
* Bug fix in ``infer_read_file_type`` when reading unknown file suffix.
* Renamed the ``-i`` flag to ``-a`` in ``serve`` CLI tool.

Version 1.0.0 (2023-09-20)
--------------------------

* Added the schema validation tool ``schema`` in ``tools``.
* Added all CLI tools.
* Now releasing version 1.0.0

Version 0.3.5 (2023-09-09)
--------------------------

* Added the first of the ``rickled.tools``, the ``converter``.
* Added first CLI tools ``rickle conv`` and ``rickle serve``.

Version 0.3.4 (2023-07-20)
--------------------------

* Fixed error when importing from ``rickled.net`` when openssl is not installed.

Version 0.3.3 (2023-07-20)
--------------------------

* Adding optional install of ``twisted`` library.
* Added ``serve_rickle_http`` and ``serve_rickle_https`` to ``rickled.net`` to serve Rickles as REST API.


Version 0.3.2 (2023-04-07)
--------------------------

* When calling ``dict`` on rickle, hot loaded items were not being serialised. Fixed.

Version 0.3.1 (2023-04-02)
--------------------------

* Fixed issue for path based query, where Rickle objects are considered callable (rightfully).
* Uses ``inspect.isfunction`` instead of ``callable``.
* Added ``meta`` to base class for getting metadata of a property.

Version 0.3.0 (2023-02-16)
--------------------------

* Bumped up to minor 3, close to releasing version 1.0 after http server is implemented.
* Added the ``hot_load`` property to API calls, making it load on call instead of only on start.
* Added the ``hot_load`` property to HTML page, making it load on call instead of only on start.
* Added the ``hot_load`` property to add file, making it load on call instead of only on start.

Version 0.2.7 (2023-02-15)
--------------------------

* Complete revamp of internal versioning.

Version 0.2.6 (2023-02-15)
--------------------------

* Fixed the same bug, but the root cause. The fact that modules are imported before proper install.

Version 0.2.5 (2023-01-18)
--------------------------

* Fixed a bug where requests is not installed


Version 0.2.4 (2022-09-02)
--------------------------

* Added ability to get nodes by using Unix style paths to get to nodes.
* Added a safe load environment variable "RICKLE_SAFE_LOAD" to override all lambda loads (as a safety measure).
* Added ``search_path`` to search for a key in the Rickle.
* Removed ``includes_self_reference`` due to confusion.
* Added a third way to load CSV files, see example documentation.
* Added ``load_as_rick`` to ``add_api_json_call``.


Version 0.2.3 (2022-03-13)
--------------------------

* Merged but cleaned up contributions by Fabian.

Version 0.2.2 (2022-02-14)
--------------------------

* Added ``do_recursive`` param to ``.get`` to optionally do a deeper recursive search.
* Do you agree that valentine's day is bullshit? Because my gf doesn't.

Version 0.2.1 (2021-12-08)
--------------------------

* Added ``add_class_definition`` to define classes.
* Created a new class, ``ObjectRickler``, to dump (almost) any object or convert to Rickle.
* Added ``add_module_import`` to Rickle, with functionality to add global Python module imports.

Version 0.2.0 (2021-12-06)
--------------------------

* Renamed project to ``Rickled`` to avoid any possible lawsuits from money hungry media execs.
* Pickle Rick was a great name, possibly even considered a parody which is protected under copyright law.
* But rather safe than sued..

Version 0.1.14 (2021-10-28)
--------------------------

* Added new ``add_html_page`` to load HTML text.
* Added new ``add_csv_file`` to load CSV files as either a list of lists, or list of PickleRicks.

Version 0.1.13 (2021-10-07)
--------------------------

* Added ability to load from multiple YAML files or JSON files from start up.

Version 0.1.12 (2021-09-23)
--------------------------

* Fixed major bug, YAML was not loaded!
* Adding preload arguments for load and replace values within YAML files using ``_|PARAM|_``
* Added new API JSON call method, to load and create a Rick from an API response ``add_api_json_call``.
* Added new ability to load other YAML, JSON, or text files from within, using ``add_from_file``.
* Added ``add_base64`` to load base 64 encoded data.

Version 0.1.11 (2021-09-09)
--------------------------

* Fixed bug in ``get`` for finding values.

Version 0.1.10 (2021-05-01)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history


Version 0.1.9 (2020-12-17)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.7 (2020-12-17)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.6 (2020-12-17)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.5 (2020-12-17)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.4 (2020-12-17)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.3 (2020-12-17)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.2 (2020-12-17)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.1 (2020-11-19)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.1.0 (2020-11-11)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.0.2 (2020-10-02)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history

Version 0.0.1 (2020-10-02)
--------------------------

Under previous name ``pickle-rick``.
See https://pypi.org/project/pickle-rick/#history