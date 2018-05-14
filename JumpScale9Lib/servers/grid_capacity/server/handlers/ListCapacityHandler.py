# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from ..models import NodeRegistration
from flask import jsonify, request
import json

def ListCapacityHandler():
    nodes = []
    country = request.values.get('country')
    mru = request.values.get('mru')
    cru = request.values.get('cru')
    hru = request.values.get('hru')
    sru = request.values.get('sru')
    for capacity in NodeRegistration.search(country, mru, cru, hru, sru):
        nodes.append(json.loads(capacity.to_json()))

    return jsonify(nodes),200,
