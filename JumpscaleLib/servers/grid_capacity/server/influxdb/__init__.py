from jumpscale import j
_client = None


def init(settings):
    if not settings.INFLUX_HOST or \
            not settings.INFLUX_PORT or \
            not settings.INFLUX_DB:
        return
    global _client
    _client = j.clients.influxdb.get(settings.INFLUX_DB, {
        'host': settings.INFLUX_HOST,
        'port': settings.INFLUX_PORT,
        'username': "root",
        'password': "",
        'database': settings.INFLUX_DB})
    _client.create_database(settings.INFLUX_DB)


def write(data):
    global _client
    if not _client:
        return
    _client.write_points(data)
