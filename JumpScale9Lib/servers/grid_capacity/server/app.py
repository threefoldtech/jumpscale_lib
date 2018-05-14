import sys

from flask import Flask, jsonify
from js9 import j

from .nodes_api import nodes_api
from .frontend_blueprint import frontend_bp


app = Flask(__name__)

app.register_blueprint(nodes_api)
app.register_blueprint(frontend_bp)
j.clients.mongoengine.get('capacity', interactive=False)


@app.errorhandler(500)
def internal_error(err):
    _, _, exc_traceback = sys.exc_info()
    eco = j.core.errorhandler.parsePythonExceptionObject(err, tb=exc_traceback)
    return jsonify(code=500, message=eco.errormessage, stack_trace=eco.traceback), 500


if __name__ == "__main__":
    app.run(debug=True, port=6601, host='0.0.0.0')
