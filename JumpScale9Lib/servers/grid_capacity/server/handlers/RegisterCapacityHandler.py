# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from js9 import j
import json as JSON
import os

import jose.jwt
import jsonschema
from jsonschema import Draft4Validator

from flask import jsonify, request
from ..models import Capacity
from ..models import Farmer

dir_path = os.path.dirname(os.path.realpath(__file__))
Capacity_schema = JSON.load(open(dir_path + '/schema/Capacity_schema.json'))
Capacity_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Capacity_schema)
Capacity_schema_validator = Draft4Validator(Capacity_schema, resolver=Capacity_schema_resolver)

IYO_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2
7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6
6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv
-----END PUBLIC KEY-----
"""


def RegisterCapacityHandler():
    inputs = request.get_json()
    # refresh jwt is needed otherwise return original
    jwt = j.clients.itsyouonline.refresh_jwt_token(inputs.pop('farmer_id'))
    token = jose.jwt.decode(jwt, IYO_PUBLIC_KEY)
    iyo_organization = token['scope'][0].replace('user:memberof:', '')
    farmers = Farmer.objects(iyo_organization=iyo_organization)
    if not farmers:
        return jsonify(errors='Unauthorized farmer'), 403

    try:
        Capacity_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return jsonify(errors="bad request body: {}".format(e)), 400
    inputs['farmer'] = iyo_organization
    capacity = Capacity(**inputs)
    capacity.save()

    return capacity.to_json()
