# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from flask import jsonify, request

import json as JSON
import jsonschema
from jsonschema import Draft4Validator
from ..models import Farmer

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
Farmer_schema = JSON.load(open(dir_path + '/schema/Farmer_schema.json'))
Farmer_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Farmer_schema)
Farmer_schema_validator = Draft4Validator(Farmer_schema, resolver=Farmer_schema_resolver)


def RegisterFarmerHandler():

    inputs = request.get_json()

    try:
        Farmer_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return jsonify(errors="bad request body"), 400
    farmer = Farmer(**inputs)
    farmer.save()

    return farmer.to_json()
