# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from flask import request, redirect
from ..flask_itsyouonline import authenticated

import json as JSON
import jsonschema
from jsonschema import Draft4Validator
from ..models import Farmer

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
Farmer_schema = JSON.load(open(dir_path + '/schema/Farmer_schema.json'))
Farmer_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Farmer_schema)
Farmer_schema_validator = Draft4Validator(Farmer_schema, resolver=Farmer_schema_resolver)


@authenticated
def RegisterFarmerHandler():
    wallet_addresses = []
    address = request.args.get('walletAddress')
    if address:
        wallet_addresses.append(address)
    farmer = Farmer(name=request.args['name'], iyo_organization=request.args['organization'], wallet_addresses=wallet_addresses)
    farmer.save()
    return redirect('/farm_registered')
