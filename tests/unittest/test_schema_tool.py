import unittest
from rickle.schema import Schema

class TestAdvanced(unittest.TestCase):

    def test_regex(self):

        schema = Schema( {
            'type': 'object',
            'properties': {
                'value_regex': {
                    'type': 'regex',
                    'pattern': 'foo(bar)?'
                },
            }
        })

        test_regex = {
            'value_regex': 'foo'
        }
        self.assertTrue(schema.validate(obj=test_regex))

        test_regex = {
            'value_regex': 'foobar'
        }
        self.assertTrue(schema.validate(obj=test_regex, ))

        test_regex = {
            'value_regex': 'fo0bar'
        }
        self.assertFalse(schema.validate(obj=test_regex,))

    def test_lat_lon(self):

        # LAT LONG
        schema = Schema( {
            'type': 'object',
            'properties': {
                'geo': {
                    'type': 'lat-long',
                },
            }
        })

        test_geo = [
            {
                'geo': '+90.0, -127.554334'
            },
            {
                'geo': '45, 180'
            },
            {
                'geo': '-90, -180'
            },
            {
                'geo': '-90.000, -180.0000'
            },
            {
                'geo': '+90, +180'
            },
            {
                'geo': '47.1231231, 179.99999999'
            },
        ]
        for t in test_geo:
            self.assertTrue(schema.validate(obj=t, ))

        test_geo_wrong = [
            {
                'geo': '-90., -180.'
            },
            {
                'geo': '+90.1, -100.111'
            },
            {
                'geo': '-91, 123.456'
            },
            {
                'geo': '045, 180'
            },
        ]
        for t in test_geo_wrong:
            self.assertFalse(schema.validate(obj=t, ))

    def test_date(self):

        schema = Schema( {
            'type': 'object',
            'properties': {
                'dt': {
                    'type': 'date',
                },
            }
        })

        test_dt = [
            {
                'dt': '2018-01-04'
            },
        ]
        for t in test_dt:
            self.assertTrue(schema.validate(obj=t, ))

        test_dt_wrong = [
            {
                'dt': '2018-01-04T05:52:20.00'
            },
        ]
        for t in test_dt_wrong:
            self.assertFalse(schema.validate(obj=t, ))


    def test_arrays(self):
        schema = Schema({
                'type': 'object',
                'properties': {
                    'values_empty': {
                        'type': 'array',
                        'items': []
                    },
                    'values_filled': {
                        'type': 'array',
                        'length': -1,
                        'required': True,
                        'items': [{'type': 'string'}]
                    },
                    'values_filled_max': {
                        'type': 'array',
                        'length': 1,
                        'items': [{'type': 'string'}]
                    },
                    'values_any': {
                        'type': 'array',
                        'items': [{'type': 'any'}]
                    },
                    'values_nullable': {
                        'type': 'array',
                        'nullable': True,
                        'items': [{'type': 'boolean'}]
                    },
                }
            }
        )

        test_all_good = {
            'values_empty': [1, 2, 3],
            'values_filled': ['a', 'b', 'c'],
            'values_filled_max': ['a']
        }

        test_missing_good = {
            'values_empty': [],
            'values_filled': ['a', 'b', 'c']
        }

        test_missing_fail = {
            'values_empty': [1, 2, 3],
            'values_filled_max': ['a']
        }

        test_type_err = {
            'values_empty': [],
            'values_filled': [1, 2, 3]
        }

        test_type_err_second = {
            'values_empty': [],
            'values_filled': ['a', 'b', 'c', 'd', 1, 'e']
        }

        test_too_long = {
            'values_empty': [1, 2, 3],
            'values_filled': ['a', 'b', 'c'],
            'values_filled_max': ['a', 'b']
        }

        test_mixed = {
            'values_empty': [],
            'values_filled': ['a', 'b', 'c'],
            'values_any': [8, '0.1', True, .99]
        }

        test_nullable_okay = {
            'values_empty': [],
            'values_filled': ['a', 'b', 'c'],
            'values_any': [8, '0.1', True, .99],
            'values_nullable': None
        }

        test_nullable_fail_type = {
            'values_empty': [],
            'values_filled': ['a', 'b', 'c'],
            'values_any': [8, '0.1', True, .99],
            'values_nullable': ['true', 'false']
        }

        test_nullable_fail_null = {
            'values_empty': [],
            'values_filled': ['a', 'b', 'c'],
            'values_any': None,
            'values_nullable': None
        }

        test_empty_null_fail = {
            'values_empty': None,
            'values_filled': ['a', 'b', 'c'],
            'values_filled_max': ['a']
        }

        test_empty_fail_type = {
            'values_empty': 'string',
            'values_filled': ['a', 'b', 'c'],
            'values_filled_max': ['a']
        }

        self.assertTrue(schema.validate(obj=test_all_good))

        self.assertTrue(schema.validate(obj=test_missing_good,))

        self.assertFalse(schema.validate(obj=test_missing_fail,))

        self.assertFalse(schema.validate(obj=test_type_err,))
        self.assertFalse(schema.validate(obj=test_type_err_second,))
        self.assertFalse(schema.validate(obj=test_too_long,))

        self.assertTrue(schema.validate(obj=test_mixed,))
        self.assertTrue(schema.validate(obj=test_nullable_okay,))

        self.assertFalse(schema.validate(obj=test_nullable_fail_type,))
        self.assertFalse(schema.validate(obj=test_nullable_fail_null,))
        self.assertFalse(schema.validate(obj=test_empty_fail_type,))
        self.assertFalse(schema.validate(obj=test_empty_null_fail,))


    def test_primitives(self):
        schema = Schema( {
            'type': 'object',
            'properties': {
                'A': {'type': 'integer', 'required': True},
                'a': {'type': 'number'},
                'b': {'type': 'any'},
                'c': {'type': 'boolean'},
                'd': {'type': 'string', 'nullable': True},
                'e': {'type': 'string', 'nullable': True, 'required': True}
            }
        })

        test_all_good = {
            'A': 10,
            'a': .90,
            'e': 'string'
        }

        test_missing_good = {
            'A': 10,
            'e': 'string'
        }

        test_missing_fail = {
            'b': 10,
            'c': .90,
            'e': 'string'
        }

        test_type_err = {
            'A': 10,
            'a': 90,
            'e': 'string'
        }

        test_type_any = {
            'A': 10,
            'a': .89,
            'b': .99,
            'e': 'string'
        }

        test_fail_null = {
            'A': None,
            'e': 'string'
        }

        test_fail_okay = {
            'A': 1,
            'd': None,
            'e': 'string'
        }

        test_fail_missing_nullable = {
            'A': 1,
            'd': None,
        }

        test_okay_nullable = {
            'A': 1,
            'd': None,
            'e': None
        }

        test_fail_nullable_type = {
            'A': 1,
            'd': None,
            'e': 1
        }

        self.assertTrue(schema.validate(obj=test_all_good, ))
        self.assertTrue(schema.validate(obj=test_missing_good, ))

        self.assertFalse(schema.validate(obj=test_missing_fail, ))
        self.assertTrue(schema.validate(obj=test_type_err, ))

        self.assertTrue(schema.validate(obj=test_type_any, ))

        self.assertFalse(schema.validate(obj=test_fail_null, ))

        self.assertTrue(schema.validate(obj=test_fail_okay, ))

        self.assertFalse(schema.validate(obj=test_fail_missing_nullable, ))
        self.assertTrue(schema.validate(obj=test_okay_nullable, ))

        self.assertFalse(schema.validate(obj=test_fail_nullable_type, ))


    def test_gen_schema(self):
        sample_data = {
            "config": {
                "version": "0.1.0",
                "name": "rickle_unittest",
                "threshold": 3.14
            }
        }

        expected_schema = {
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "properties": {
                        "version": {
                            "type": "string"
                        },
                        "name": {
                            "type": "string"
                        },
                        "threshold": {
                            "type": "number"
                        }
                    }
                }
            }
        }

        schema = Schema.generate_from_obj(sample_data, include_extended_properties=False)

        self.assertDictEqual(schema.schema, expected_schema)
