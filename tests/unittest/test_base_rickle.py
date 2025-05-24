import unittest
from rickle import BaseRickle

class TestBaseRickle(unittest.TestCase):

    def setUp(self):
        self.expected_dict = {
            'key_one': 'value_one',
            'key_three': 'value_three',
        }
        self.base_rickle = BaseRickle(self.expected_dict)

        self.expanded_dict = {
            "path": {"to": {"value": "expected_value"}},
            "different_path": {"to": {"value": "different_expected_value"}}
         }
        self.expanded_rickle = BaseRickle(self.expanded_dict)

    def test_items(self):
        items = list(self.base_rickle.items())
        self.assertListEqual(list(self.expected_dict.items()), items)

    def test_get(self):
        self.assertEqual(self.base_rickle.get("key_one"), "value_one")
        self.assertIsNone(self.base_rickle.get("nonexistent_key"))

    def test_put(self):
        self.base_rickle.put("key_two", "value_two")
        self.assertEqual(self.base_rickle.get("key_two"), "value_two")

    def test_set(self):
        # Updating an existing key
        self.base_rickle.set("key_one", "new_value")
        self.assertEqual(self.base_rickle.get("key_one"), "new_value")

        # Have to be put
        with self.assertRaises(NameError):
            self.base_rickle.set("/key_one/going", "somewhere")
        # Can not traverse this
        with self.assertRaises(KeyError):
            self.base_rickle.set("/key_one/going/nowhere", "slowly")

    def test_remove(self):
        self.base_rickle.remove("key_one")
        self.assertIsNone(self.base_rickle.get("key_one"))
        with self.assertRaises(KeyError):
            self.base_rickle.remove("nonexistent_key")

    def test_values(self):
        values = list(self.base_rickle.values())
        self.assertIn("value_one", values)
        self.assertIn("value_three", values)

    def test_keys(self):
        keys = list(self.base_rickle.keys())
        self.assertIn("key_one", keys)
        self.assertIn("key_three", keys)

    def test_dict(self):
        as_dict = self.base_rickle.dict()
        self.assertDictEqual(as_dict, self.expected_dict)

    def test_has(self):
        self.assertTrue(self.base_rickle.has("key_one"))
        self.assertFalse(self.base_rickle.has("nonexistent_key"))

    def test_add(self):
        self.base_rickle.add("new_added", 6.667)
        self.assertEqual(self.base_rickle.new_added, 6.667)
        # Check if it raises an error when adding property that already exists
        with self.assertRaises(NameError):
            self.base_rickle.add("new_added", "new_value")

    def test_meta(self):
        self.base_rickle.add("new_added", 6.667)

        self.assertDictEqual(self.base_rickle.meta("new_added"), {'type': 'attribute', 'value': 6.667})

    def test_item_get(self):
        for key in self.expected_dict.keys():
            self.assertEquals(self.base_rickle[key], self.expected_dict[key])

    def test_item_set(self):
        self.base_rickle['new_key'] = 88

        self.assertEquals(self.base_rickle['new_key'], 88)
        self.assertEquals(self.base_rickle.new_key, 88)

    def test_item_del(self):
        del self.base_rickle['key_one']

        with self.assertRaises(KeyError):
            is_true = self.base_rickle['key_one'] == "value_one"

        with self.assertRaises(AttributeError):
            is_true = self.base_rickle.key_one == "value_one"
    def test_iterator(self):
        expected = {
            'first': {
                'message': 'hello world'
            },
            'second': {
                'message': 'hello world'
            }
        }

        base_rickle = BaseRickle(expected)

        for obj in base_rickle:
            self.assertTrue(obj in expected.keys())

    def test_get_by_path(self):
        result = self.expanded_rickle.get("/path/to/value")
        self.assertEqual(result, "expected_value", "Failed to get the value by path")

        result = self.expanded_rickle.get("/different_path/to/value")
        self.assertEqual(result, "different_expected_value", "Failed to get the value by different path")

    def test_search(self):
        result = self.expanded_rickle.search_path("value")
        expected_paths = ["/path/to/value", "/different_path/to/value"]

        # Check if all expected paths are in the result
        for path in expected_paths:
            self.assertIn(path, result, f"Path {path} not found in search results")

        # Test searching for a term with no matches
        result = self.expanded_rickle.search_path("nonexistent")
        self.assertEqual(result, [], "Expected no results for nonexistent search term")

    def test_find(self):
        # TODO create expanded test
        pass

    def test_callable_with_path(self):
        # Assuming the object can be called like custom_dict("/path/to/value")
        result = self.expanded_rickle("/path/to/value")
        self.assertEqual(result, "expected_value", "Failed to retrieve value when called with path")

        # Test calling with a non-existent path
        with self.assertRaises(NameError):
            self.expanded_rickle("/nonexistent/path")

    def test_name_clean_up(self):
        self.base_rickle.add('name_with_numbers1929', 'buy_stock')

        self.assertEqual(self.base_rickle.dict().get('name_with_numbers1929'), 'buy_stock')
        self.assertEqual(self.base_rickle.name_with_numbers, 'buy_stock')
        self.assertEqual(self.base_rickle.get('name_with_numbers1929'), 'buy_stock')
        self.assertEqual(self.base_rickle.get('name_with_numbers'), 'buy_stock')




if __name__ == "__main__":
    unittest.main()