"""Reject ambiguous JSON in reviewed release evidence."""
import json


def pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError('duplicate JSON key')
        value[key] = item
    return value


def constant(_):
    raise ValueError('non-finite JSON value')


def load(stream):
    return json.load(stream, object_pairs_hook=pairs, parse_constant=constant)
