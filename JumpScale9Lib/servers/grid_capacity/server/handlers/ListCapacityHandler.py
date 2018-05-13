# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from ..models import NodeRegistration
from flask import jsonify
import json

def ListCapacityHandler():
    nodes = []
    for capacity in NodeRegistration.list():
        nodes.append(json.loads(capacity.to_json()))

    return jsonify(nodes),200,
