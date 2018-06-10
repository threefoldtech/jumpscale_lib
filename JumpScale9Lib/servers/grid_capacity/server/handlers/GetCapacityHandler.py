# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from flask import jsonify, request
from ..models import NodeRegistration, NodeNotFoundError


def GetCapacityHandler(node_id):
    try:
        node = NodeRegistration.get(node_id)
    except NodeNotFoundError:
        return jsonify(), 404

    return node.to_json(use_db_field=False), 200, {'Content-type': 'application/json'}
