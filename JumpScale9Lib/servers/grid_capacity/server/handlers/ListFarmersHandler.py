# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.
from flask import request
from ..models import FarmerRegistration


def ListFarmersHandler():
    name = request.values.get('name')

    farmers = FarmerRegistration.list(name)
    return farmers.to_json(), 200, {'Content-type': 'application/json'}
