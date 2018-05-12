import os
import sys

from flask import Flask, jsonify, send_file, send_from_directory, render_template, request
from js9 import j

dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory(dir_path, os.path.join('static', path))


@app.route('/', methods=['GET'])
def capacity():
    reg = j.tools.capacity.registration

    countries = reg.nodes.all_countries()
    nodes = []
    form = {
        'mru': 0,
        'cru': 0,
        'sru': 0,
        'hru': 0,
        'country': '',
    }

    if len(request.args) != 0:
        mru = request.args.get('mru') or None
        if mru:
            form['mru'] = int(mru)
        cru = request.args.get('cru') or None
        if cru:
            form['cru'] = int(cru)
        sru = request.args.get('sru') or None
        if sru:
            form['sru'] = int(sru)
        hru = request.args.get('hru') or None
        if hru:
            form['hru'] = int(hru)
        form['country'] = request.args.get('country') or ''

        nodes = list(reg.nodes.search(**form))

    return render_template('capacity.html', nodes=nodes, form=form, countries=countries)


@app.route('/farmers', methods=['GET'])
def farmers():
    return render_template('farmers.html')


@app.errorhandler(500)
def internal_error(err):
    _, _, exc_traceback = sys.exc_info()
    eco = j.core.errorhandler.parsePythonExceptionObject(err, tb=exc_traceback)
    return jsonify(code=500, message=eco.errormessage, stack_trace=eco.traceback), 500


if __name__ == "__main__":
    app.run(debug=True, port=6601, host='0.0.0.0')
