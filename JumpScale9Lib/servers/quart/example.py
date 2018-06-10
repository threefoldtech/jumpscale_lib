from gevent import monkey
monkey.patch_all()
from flask import Flask
from gevent import wsgi
import flask

app = Flask(__name__)

class TTT():

    def __init__(self):
        self.r=1

    def test(self,var):
        return var

T=TTT()

@app.route('/')
def index():
    return 'Hello World'

@app.route('/hello/<user>')
def hello_name(user):
    return flask.render_template('hello.html', name = user, obj=T)


server = wsgi.WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()