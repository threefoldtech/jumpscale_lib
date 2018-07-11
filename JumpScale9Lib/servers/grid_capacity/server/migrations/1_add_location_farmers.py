from js9 import j
from JumpScale9Lib.servers.grid_capacity.server.models import Farmer, Location
# connect to mongodb
j.clients.mongoengine.get('capacity', interactive=False)

loc = Location()
loc.to_mongo()
col = Farmer._get_collection()
col.update({"location": {"$exists":False}}, {"$set": { "location": loc.to_mongo()}}, multi=True, upsert=True)
