# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

import json as JSON
import os

import jsonschema
from jsonschema import Draft4Validator

from flask import jsonify, request
from js9 import j
from JumpScale9Lib.tools.capacity.registration import Capacity

registration = j.tools.capacity.registration

dir_path = os.path.dirname(os.path.realpath(__file__))
Capacity_schema = JSON.load(open(dir_path + '/schema/Capacity_schema.json'))
Capacity_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Capacity_schema)
Capacity_schema_validator = Draft4Validator(Capacity_schema, resolver=Capacity_schema_resolver)


def RegisterCapacityHandler():

    inputs = request.get_json()

    try:
        Capacity_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return jsonify(errors="bad request body"), 400

    capacity = Capacity.from_dict(inputs)
    registration.nodes.register(capacity)

    return jsonify(capacity.to_dict())
