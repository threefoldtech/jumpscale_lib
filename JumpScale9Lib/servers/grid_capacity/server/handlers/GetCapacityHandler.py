# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from flask import jsonify, request
from ..models import NodeRegistration


def GetCapacityHandler(node_id):
    node = NodeRegistration.get(node_id)
    return node.to_json(), 200, {'Content-type': 'application/json'}
