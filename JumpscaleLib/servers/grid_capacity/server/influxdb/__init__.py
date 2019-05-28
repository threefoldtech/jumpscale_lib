from jumpscale import j

_client = None
influxlog = j.logger.get("grid-influx")

def init(host, port, db):
    global _client
    _client = j.clients.influxdb.get(db, {
        'host': host,
        'port': port,
        'username': "root",
        'password': "",
        'database': db
    })

    for exists in _client.get_list_database():
        if exists['name'] == db:
            influxlog.info("database <%s> already exists, using it" % db)
            return True

    influxlog.info("creating database <%s>" % db)
    _client.create_database(db)


def write(data):
    global _client
    if not _client:
        return

    _client.write_points(data)
