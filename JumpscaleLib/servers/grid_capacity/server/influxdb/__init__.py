from jumpscale import j

_client = None
influxlog = j.logger.get("grid-influx")

def init(settings):
    if not settings.INFLUX_HOST:
        return False

    if not settings.INFLUX_DB:
        return False

    global _client
    _client = j.clients.influxdb.get(settings.INFLUX_DB, {
        'host': settings.INFLUX_HOST,
        'port': settings.INFLUX_PORT,
        'username': "root",
        'password': "",
        'database': settings.INFLUX_DB
    })

    for db in _client.get_list_database():
        if db['name'] == settings.INFLUX_DB:
            influxlog.notice("database <%s> already exists, using it" % settings.INFLUX_DB)
            return True

    influxlog.notice("creating database <%s>" % settings.INFLUX_DB)
    _client.create_database(settings.INFLUX_DB)


def write(data):
    global _client
    if not _client:
        return
    _client.write_points(data)
