
from Jumpscale import j

JSBASE = j.application.JSBaseClass




class ZDBClientNSMeta(JSBASE):

    def __init__(self,db):
        JSBASE.__init__(self)
        self.db=db
        self.load()
        self.schemas = {}

    def schema_data_get(self,id=None,md5=None,url=None,die=False):
        if id is not None:
            cfg = self._data["schemas"].get(id,{})
            if cfg == {}:
                if die:
                    raise RuntimeError("cannot find schema with id:%s"%id)
                else:
                    return None,None
        else:
            if url is None and md5 is None:
                raise RuntimeError("id or md5 needs to be specified")
            if url is not None and md5 is not None:
                raise RuntimeError("can only specify id or md5")
            res = []
            id=None
            for id,item in self._data["schemas"].items():
                if item["md5"]==md5:
                    res.append((id,item))
                elif item["url"]==url:
                    res.append((id,item))
            if len(res)>0:
                id,cfg = res[-1] #only use the most recent one
            else:
                if die:
                    raise RuntimeError("cannot find schema with args: md5:%s url:%s"%(md5,url))
                else:
                    return None,None

        #how we have data from the metadata we are looking for, the schema content
        return id,cfg


    def schema_exists(self,schema):
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")
        id,item = self.schema_data_get(md5=schema.md5)
        if item == None:
            return False
        return True

    def schema_id_incr(self):
        highest = 0
        for key in self._data["schemas"].keys():
            if key>highest:
                highest = key
        return highest+1

    def schema_set(self,schema):
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        id,d = self.schema_data_get(md5=schema.md5)
        if id==None:  #means is new, doesn't exist
            id = self.schema_id_incr()
            d={}
            d["md5"] = schema.md5
            d["url"] = schema.url
            d["schema"] =  schema.text
            self._data["schemas"][id]=d
            self.save()

        return id

    def schemas_load(self):
        ids = [i for i in self._data["schemas"].keys()]
        ids.sort()
        res = {}
        for i in ids:
            d = self._data["schemas"][i]
            res[d["url"]] = (i,d["schema"])
        res2=[]
        #now go over latest found
        self.schemas = {}
        for url,x in res.items():
            id, schema = x
            schema = j.data.schema.get(schema)
            res2.append(schema)
            self.schemas[id]=schema
        return res2

    def config_get(self,name):
        return self._data["config"].get(name,None)

    def config_set(self,name,val):
        if name not in self._data["config"] or self._data["config"][name]!=val:
            self._data["config"][name]=val
            self.save()

    def config_exists(self,name):
        return self.config_get(name)is not None

    # @property
    # def models(self):
    #     return self.config_get("models")
    #
    # def model_add(self,name):
    #     if name not in self.models:
    #         models = self.config_get("models")
    #         models.append(name)
    #         self.config_get("models",models)
    #         self.save()

    def save(self):
        data = j.data.serializers.msgpack.dumps(self._data)
        self.db.set(data,key=0)

    def load(self):
        data = self.db.get(0)
        if data is None:
            self._data = {}
            self._data["schemas"]={}
            self._data["config"]={}
            self.db.set(j.data.serializers.msgpack.dumps(self._data))
        else:
            self._data = j.data.serializers.msgpack.loads(data)
            if not "config" in self._data:
                raise RuntimeError("corrupt config record o in %s"%self)
            if not "schemas" in self._data:
                raise RuntimeError("corrupt config record o in %s"%self)



    def __repr__(self):
        return str(self._data)

    __str__ = __repr__

