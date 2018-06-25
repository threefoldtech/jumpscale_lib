# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

import json as JSON
import os
from datetime import datetime

import jsonschema
from jsonschema import Draft4Validator

from flask import jsonify, request
from js9 import j

from ..models import Capacity
from .jwt import validate_farmer_id, FarmerInvalid

dir_path = os.path.dirname(os.path.realpath(__file__))
Capacity_schema = JSON.load(open(dir_path + '/schema/Capacity_schema.json'))
Capacity_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Capacity_schema)
Capacity_schema_validator = Draft4Validator(Capacity_schema, resolver=Capacity_schema_resolver)


def RegisterCapacityHandler():
    inputs = request.get_json()
    try:
        iyo_organization = validate_farmer_id(inputs.pop('farmer_id'))
    except FarmerInvalid:
        return jsonify(errors='Unauthorized farmer'), 403

    try:
        Capacity_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return jsonify(errors="bad request body: {}".format(e)), 400

    inputs['farmer'] = iyo_organization
    inputs['updated'] = datetime.now()
    capacity = Capacity(**inputs)

    if farmer.location:
        capacity.location = farmer.location

    capacity.save()

    return capacity.to_json(use_db_field=False), 201, {'Content-type': 'application/json'}
