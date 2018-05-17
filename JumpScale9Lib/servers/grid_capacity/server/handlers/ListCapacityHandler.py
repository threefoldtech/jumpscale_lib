# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from ..models import NodeRegistration
from flask import request

def ListCapacityHandler():
    nodes = []
    country = request.values.get('country')
    mru = request.values.get('mru')
    cru = request.values.get('cru')
    hru = request.values.get('hru')
    sru = request.values.get('sru')
    nodes = NodeRegistration.search(country, mru, cru, hru, sru).to_json()
    return nodes, 200
