# from __future__ import print_function
from js9 import j


class CeleryFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.celery"
        self.actors = {}
        self.app = None
        self.url = "redis://localhost:6379/0"
        self.actorsPath = "actors"

    def flowerStart(self):
        from flower.command import FlowerCommand
        from flower.utils import bugreport

        flower = FlowerCommand()

        argv = ['flower.py', '--broker=%s' % self.url]

        flower.execute_from_commandline(argv=argv)

    def _getCode(self, path):
        state = "start"
        C = j.sal.fs.fileGetContents(path)
        basename = j.sal.fs.getBaseName(path)
        name = basename.replace(".py", "").lower()
        out = "class %s():\n" % name
        for line in C.split("\n"):
            # if state=="method":
            #     if line.strip().find("def")==0:

            if state == "class":
                # now processing the methods
                if line.strip().find("def") == 0:
                    # state=="method"
                    pre = line.split("(", 1)[0]
                    pre = pre.replace("def ", "")
                    method_name = pre.strip()
                    out += "    @app.task(name='%s_%s')\n" % (name,
                                                              method_name)

                out += "%s\n" % line

            if line.strip().find("class") == 0:
                state = "class"
        out += "\n"
        return out

    def getCodeServer(self):
        path = self.actorsPath
        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input("could not find actors path:%s" % path)
        code = ""
        for item in j.sal.fs.listFilesInDir(path, filter="*.py", recursive=False, followSymlinks=True):
            code += self._getCode(item)
        return code

    def getCodeClient(self, actorName):
        path2 = "%s/%s.py" % (self.actorsPath, actorName)
        if not j.sal.fs.exists(path=path2):
            raise j.exceptions.Input("could not find actor path:%s" % path2)
        code = self._getCode(path2)
        return code

    def celeryStart(self, concurrency=4, actorsPath="actors"):

        from celery import Celery

        # j.clients.redis.start4core()

        app = Celery('tasks', broker=self.url)

        app.conf.update(
            CELERY_TASK_SERIALIZER='json',
            CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
            CELERY_RESULT_SERIALIZER='json',
            CELERY_TIMEZONE='Europe/Oslo',
            CELERY_ENABLE_UTC=True,
            # CELERY_RESULT_BACKEND='rpc',
            CELERY_RESULT_PERSISTENT=True,
            CELERY_RESULT_BACKEND=self.url,
        )

        app.conf["CELERY_ALWAYS_EAGER"] = False
        app.conf["CELERYD_CONCURRENCY"] = concurrency

        code = self.getCodeServer()
        exec(code, locals(), globals())

        app.worker_main()

    def getCeleryClient(self, actorName, local=False):

        if actorName in self.actors:
            return self.actors[actorName]

        if self.app is None:

            from celery import Celery

            app = Celery('tasks', broker=self.url)

            app.conf.update(
                CELERY_TASK_SERIALIZER='json',
                CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
                CELERY_RESULT_SERIALIZER='json',
                CELERY_TIMEZONE='Europe/Oslo',
                CELERY_ENABLE_UTC=True,
                # CELERY_RESULT_BACKEND='rpc',
                CELERY_RESULT_PERSISTENT=True,
                CELERY_RESULT_BACKEND=self.url,
            )

            # if local:
            #     app.conf["CELERY_ALWAYS_EAGER"] = False

            self.app = app
        else:
            app = self.app

        code = self.getCodeClient(actorName=actorName)
        exec(code, locals(), globals())

        self.actors[actorName] = eval("%s" % actorName)

        return self.actors[actorName]
