from Jumpscale import j

JSBASE = j.application.JSBaseClass


#dataformat

SCHEMA = """

@url = jumpscale.schemas.meta.1
schemas = (LO) !jumpscale.schemas.meta.schema.1

@url = jumpscale.schemas.meta.schema.1
url = ""
sid = 0  #schema id  
text = ""


"""


class ZDBMeta(JSBASE):

    def __init__(self, db):
        JSBASE.__init__(self)
        self.db = db
        self._schema = j.data.schema.get(SCHEMA)
        self.reset()

    @property
    def data(self):
        if self._data is None:
            data = self.db.redis.get(0)
            if data is None:
                self._data = self._schema.new()
                self.db.redis.execute_command("SET", '', self._data)
            self._schemas_load()
        return self._data

    def reset(self):
        self._data = None
        self.data
        self.url2schema = {}
        self.id2schema = {}
        self.schema_last_id = 0
        self.url2model = {}
        self.id2model = {}
        self.url2id = {}


    def save(self):
        if self._data is None:
            self.data
        self.db.redis.execute_command("SET",b'\x00\x00\x00\x00', self._data)


    def schema_get_id(self,schema_id):
        return self.id2schema[schema_id]

    def schema_get_url(self,url):
        return self.url2id[url],self.url2schema[url]

    def model_get_id(self,schema_id,bcdb):
        if not schema_id in self.id2model:
            schema = self.schema_get_id(schema_id)
            self.id2model[schema_id] = self._model_load(schema,bcdb)
        return self.id2model[schema_id]

    def model_get_url(self,url,bcdb):
        if not url in self.url2model:
            schema = self.schema_get_url(url)
            self.url2model[url] = self._model_load(schema,bcdb)
        return self.url2model[url]

    def schema_set(self, schema):
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        if "schema_id" in schema.__dict__ or "id" in schema.__dict__:
            raise RuntimeError("should be no id in schema")

        if schema.url in self.url2schema:
            return self.schema_get_url(schema.url)
        else:
            #not known yet in namespace in ZDB
            s = self.data.schemas.new()
            s.url = schema.url
            self.schema_last_id +=1
            s.sid = self.schema_last_id
            s.text = schema.text.strip()+"\n"  #only 1 \n at end
            self.save()

            self._schema_load(s.sid, schema)

            return s.sid,schema

    def _schemas_load(self):
        for schema in self._data.schemas:
            schema_obj=j.data.schema.get(schema.text)
            schema_obj.id = schema.sid  #make sure we know the id on the schema
            if schema_obj.url != schema.url:
                raise RuntimeError("schema url needs to be same")
            self._schema_load(schema.sid, schema_obj)
            if schema.sid > self.schema_last_id:
                self.schema_last_id = schema.sid

    def _schema_load(self,sid,schema_obj):
        self.url2schema[schema_obj.url]=schema_obj
        self.id2schema[sid]=schema_obj
        self.url2id[schema_obj.url]=sid

    def _models_load(self,bcdb):
        self.data #make sure we load when needed
        for schema in self.id2schema.values():
            self._model_load(schema,bcdb)

    def _model_load(self,schema,bcdb):
        model = bcdb.model_get_from_schema(schema=schema, reload=False, dest=None, overwrite=True)
        bcdb.models[model.url]=model
        self.url2model[schema.url] = model
        self.id2model[ model.schema_id] = model
        return model


    def __repr__(self):
        return str(self._data)

    __str__ = __repr__
