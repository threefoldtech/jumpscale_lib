from flask import Flask
import rq_dashboard
from flask import request
import sys
from js9 import j

mydir = j.sal.fs.getcwd()
if mydir not in sys.path:
    sys.path.append(mydir)

from site_threefold import app as app_threefold

class JSMainApp(Flask):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config.from_object(rq_dashboard.default_settings)
        self.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
        self.register_blueprint(app_threefold.bp, url_prefix="/threefold")

        self.add_url_rule('/hello', view_func=self.hello)
        self.add_url_rule('/files/<name>', view_func=self.files1)
        self.add_url_rule('/files/<ns>/<name>', view_func=self.files2)

        self.config["DEBUG"]=True


    def load(self,path):
        j.tools.docgenerator.load(path)
        i = j.tools.docgenerator.item_get("threefold-token-what-is-it-threefold-foundation.html",die=False)
        print("load app")
        from IPython import embed;embed(colors='Linux')

    ############

    def files1(self,name=None):
        from IPython import embed;embed(colors='Linux')
    

    def files2(self,ns=None, name=None):
        name=name.lower()
        ns=ns.lower()
        # return render_template('hello.html', name=name) 
        from IPython import embed;embed(colors='Linux')        

    def hello(self):
        from IPython import embed;embed(colors='Linux')
        return "Hello World!"

        #http://flask.pocoo.org/docs/1.0/quickstart/#static-files
        request.args.get('key', '')
        username = request.cookies.get('username')
