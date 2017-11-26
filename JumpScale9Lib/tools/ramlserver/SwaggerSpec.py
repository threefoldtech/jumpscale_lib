
from js9 import j


class SwaggerSpec():

    def __init__(self, path):
        self.json = j.data.serializer.json.load(path)
        self.rootObjNames = [item.lstrip(
            "/") for item in self.json["paths"].keys() if item.find("{") == -1]
