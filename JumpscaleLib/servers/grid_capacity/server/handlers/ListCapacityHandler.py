# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from ..models import NodeRegistration
from flask import request, jsonify
from io import StringIO


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

    max_per_page = 100
    total = nodes.count()
    per_page = min(max_per_page, (max_per_page + (total - (page * max_per_page))))
    if per_page < 0:
        per_page = 0

    paginated = nodes.paginate(page=page, per_page=per_page)

    for node in paginated.items:
        if node.farmer.location and node.farmer.location.latitude and node.farmer.location.longitude:
            node.location = node.farmer.location
        d = node.to_mongo().to_dict()
        d["node_id"] = d.pop("_id")
        d["farmer_id"] = d.pop("farmer")
        output.append(d)

    resp = jsonify(output)
    resp.headers.set("page", str(paginated.pages))
    return resp
