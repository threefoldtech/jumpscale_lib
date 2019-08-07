# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from ..models import NodeRegistration
from flask import request, jsonify
from io import StringIO
import math


def ListCapacityHandler():

    nodes = []
    country = request.values.get("country")
    mru = request.values.get("mru")
    cru = request.values.get("cru")
    hru = request.values.get("hru")
    sru = request.values.get("sru")
    farmer = request.values.get("farmer")
    page = int(request.values.get("page") or 1)
    nodes = NodeRegistration.search(country, mru, cru, hru, sru, farmer, fulldump=True)

    output = []
    with_proofs = request.args.get("proofs")
    if not with_proofs:
        nodes = nodes.exclude("proofs")

    max_per_page = int(request.args.get('per_page', 100))
    if not max_per_page or max_per_page > 100:
        max_per_page = 100

    offset = (page - 1) * max_per_page
    paginated = nodes.skip(offset).limit(max_per_page)
    nr_page = int(math.ceil(nodes.count() / float(max_per_page)))

    for node in paginated:
        if node.farmer.location and node.farmer.location.latitude and node.farmer.location.longitude:
            node.location = node.farmer.location
        d = node.to_mongo().to_dict()
        d["node_id"] = d.pop("_id")
        d["farmer_id"] = d.pop("farmer")
        output.append(d)

    resp = jsonify(output)
    resp.headers.set("page", str(nr_page))
    return resp
