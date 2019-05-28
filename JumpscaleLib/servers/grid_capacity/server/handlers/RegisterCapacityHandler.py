# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

import json as JSON
import os
from datetime import datetime

import jsonschema
from flask import jsonify, request
from jsonschema import Draft4Validator
from jumpscale import j

from .. import influxdb
from ..models import Capacity, Farmer, NodeNotFoundError, NodeRegistration, Proof
from .jwt import FarmerInvalid, validate_farmer_id

dir_path = os.path.dirname(os.path.realpath(__file__))
Capacity_schema = JSON.load(open(dir_path + '/schema/Capacity_schema.json'))
Capacity_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Capacity_schema)
Capacity_schema_validator = Draft4Validator(Capacity_schema, resolver=Capacity_schema_resolver)


logger = j.logger.get(__name__)


def RegisterCapacityHandler():
    inputs = request.get_json()
    try:
        iyo_organization = validate_farmer_id(inputs.pop('farmer_id'))
    except FarmerInvalid:
        return jsonify(errors='Unauthorized farmer'), 403

    try:
        Capacity_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return jsonify(errors="bad request body: {}".format(e)), 400

    # Fetch farmer from database first
    farmer = Farmer.objects(iyo_organization=iyo_organization).first()
    if not farmer:
        return jsonify(errors='Unauthorized farmer'), 403

    inputs['updated'] = datetime.now()

    # check if the node also sent some hardware detail
    proof = None
    if inputs.get('hardware') and inputs.get('disks'):
        hardware = inputs.pop('hardware')
        disks = inputs.pop('disks')
        proof = Proof(hardware=hardware,
                      hardware_hash=hash_dump(hardware),
                      disks=disks,
                      disks_hash=hash_dump(disks_dump_remove_date(disks))
                      )

    # Update the node if already exists or create new one using the inputs
    try:
        node = NodeRegistration.get(inputs.get("node_id"))
        if farmer.location:
            node.location = farmer.location
        inputs['farmer'] = farmer
        node.update(**inputs)

    except NodeNotFoundError:
        inputs['farmer'] = iyo_organization
        inputs['created'] = datetime.now()

        node = Capacity(**inputs)
        if farmer.location:
            node.location = farmer.location

        node.save()

    # check if we already have a version of these hardware detail in the db
    if proof:
        logger.info("hardware proof sent")
        found = Capacity.objects(proofs__hardware_hash=proof.hardware_hash, proofs__disks_hash=proof.disks_hash)
        # if not, we add it
        if found.count() <= 0:
            logger.info("hardware proof change detected, save new proof")
            node.proofs.append(proof)
            node.save()

    try:
        write_to_influx(node)
    except Exception as err:
        logger.error('error writting to influxdb :%s', str(err))

    response = JSON.loads(node.to_json(use_db_field=False))
    response['updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return JSON.dumps(response), 201, {'Content-type': 'application/json'}


def hash_dump(dump):
    return j.data.hash.md5_string(
        j.data.serializer.json.dumps(dump))


def disks_dump_remove_date(disks):
    target = 'Local Time is'
    for i, _ in enumerate(disks['devices']):
        if target in disks['devices'][i]:
            disks['devices'][i].pop(target)
    return disks


def write_to_influx(capacity):
    data = [{
        "measurement": "node_capacity",
        "tags": {
            "node_id": capacity.node_id,
            "farmer": capacity.farmer.iyo_organization,
            "version": capacity.os_version,
        },
        "fields": {
            "cru": capacity.total_resources.cru,
            "mru": capacity.total_resources.mru,
            "hru": capacity.total_resources.hru,
            "sru": capacity.total_resources.sru,
            "longitude": capacity.location.longitude,
            "latitude": capacity.location.latitude,
            "uptime": capacity.uptime,
        }
    }]
    influxdb.write(data)
