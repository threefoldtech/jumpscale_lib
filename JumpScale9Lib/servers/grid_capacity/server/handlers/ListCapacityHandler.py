# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from flask import jsonify, request
from js9 import j

registration = j.tools.capacity.registration


def ListCapacityHandler():

    nodes = [cap.to_json() for cap in registration.nodes.list()]
    return nodes,200,
