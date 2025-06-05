
# Find key-value pairs

---

Find is useful for find paths of key/value pairs. Using ``--help`` shows some examples along with the following table:


   | Comparison         | Op   | Alternative |
   |--------------------|------|-------------|
   | equals             | `=`  | `eq`        |
   | not equals         | `!=` | `ne`        |
   | less than          | `<`  | `lt`        |
   | greater than       | `>`  | `gt`        |
   | less than equal    | `<=` | `lte`       |
   | greater than equal | `>=` | `gte`       |

To find a path, the key, comparison operator (as show above, including alternatives) and value must be given.

Consider the following JSONL file:

```json title="arr-dev.jsonl" linenums="1"
{"name": "Lindsay", "surname": "Funke", "score": 29}
{"name": "Gob", "surname": "Bluth", "score": 14}
{"name": "Tobias", "surname": "Funke", "score": 19}
{"name": "Buster", "surname": "Bluth", "score": 25}
```

Key / values can be found for example:

```shell
cat arr-dev.jsonl | rickle obj find "surname = Bluth"
```

Prints the following output:

```text
/[1]/surname
/[3]/surname
```

Comparisons can also be disjunct using ``--or``:

```shell
cat arr-dev.jsonl | rickle obj find --or "score < 19" "score > 25"
```

Outputting the result:

```text
/[0]/score
/[1]/score
```

Likewise comparisons can also be conjunct using ``--and``:

```shell
cat arr-dev.jsonl | rickle obj find --and "score > 14" "score < 20"
```
    
Outputting the result:

```text
/[2]/score
```

Using the ``--parent`` or shorthand ``-p`` can be used in combination with the ``--and`` to get the path of a object.

```shell
cat arr-dev.jsonl | rickle obj find --and "surname = Bluth" "score < 20" -p
```

Outputting the result:

```text
/[1]
```

Using paths can be used to do relative matching is also possible:

```json title="arr-dev.jsonl" linenums="1"
{"name": "Lindsay", "surname": "Funke", "score": 29, "details": {"age": 36 }}
{"name": "Gob", "surname": "Bluth", "score": 14, "details": {"age": 40 }}
{"name": "Tobias", "surname": "Funke", "score": 19, "details": {"age": 45 }}
{"name": "Buster", "surname": "Bluth", "score": 25, "details": {"age": 30 }}
```

```shell
cat arr-dev.jsonl | rickle obj find --and "surname = Funke" "/details/age = 36" -p
```

Outputting the result:

```text
/[0]
```

