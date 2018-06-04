import os
import sys
import datetime

from flask import Flask, jsonify
from js9 import j

from . import settings
from .flask_itsyouonline import configure
from .models import db

app = Flask(__name__)
app.secret_key = os.urandom(24)
configure(app, settings.IYO_CLIENTID, settings.IYO_SECRET, settings.IYO_CALLBACK, '/callback', None, True, True, 'organization')

# connect to mongodb
j.clients.mongoengine.get('capacity', interactive=False)

db.init_app(app)


from .api_api import api_api
from .frontend_blueprint import frontend_bp

app.register_blueprint(api_api)
app.register_blueprint(frontend_bp)


@app.template_filter()
def uptime(seconds):
    if not seconds:
        return "not available"
    return str(datetime.timedelta(seconds=seconds))


@app.template_filter()
def deltatime_color(time):
    """
    return a color base on the delta time between now and time

    :param time: time we when to compare
    :type time: datetime.datetime
    :return: color
    :rtype: str
    """
    if not time:
        return 'danger'

    delta = datetime.datetime.now() - time
    if delta.seconds < 7200:  # less then 2h
        return 'success'
    if 7200 < delta.seconds and delta.seconds < 10800:  # between 2h and 3h
        return 'warning'
    if delta.seconds > 10800:  # plus de 3h
        return 'danger'


@app.errorhandler(500)
def internal_error(err):
    _, _, exc_traceback = sys.exc_info()
    eco = j.core.errorhandler.parsePythonExceptionObject(err, tb=exc_traceback)
    return jsonify(code=500, message=eco.errormessage, stack_trace=eco.traceback), 500


if __name__ == "__main__":
    app.run(debug=True, port=settings.PORT, host=settings.PORT)
