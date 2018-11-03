from Jumpscale import j


SCHEMA="""
@url = jumpscale.bcdb.acl.1
groups = (LO) !jumpscale.bcdb.acl.group
users = (LO) !jumpscale.bcdb.acl.user
hash* = ""

@url = jumpscale.bcdb.acl.group
uid= 4294967295 (I)
rights = ""

@url = jumpscale.bcdb.acl.user
uid= 4294967295 (I)
rights = ""

"""

import types

MODEL_CLASS=j.data.bcdb.latest.model_class_get_from_schema(SCHEMA)



class UserModel(MODEL_CLASS):
    def __init__(self, bcdb):

        MODEL_CLASS.__init__(self, bcdb=bcdb)


    # def rights_check(self,acl,userid,rights):
    #     def rights_check2(rights2check,rightsInObj):
    #         for item in rights2check:
    #             if item not in rightsInObj:
    #                 return False
    #         return True
    #     userid=int(userid)
    #     for user in acl.users:
    #         if user.uid ==userid:
    #             return rights_check2(rights,user.rights)
    #     for group in acl.groups:
    #         group = acl.model.bcdb.group.get(group)
    #         if group:
    #             if group.user_exists(userid):
    #                 if rights_check2(rights,group.rights):
    #                     return True
    #     return False
    #
    def _methods_add(self,obj):
        obj.validate = types.MethodType(self.validate,obj)
        return obj

    def validate(self,obj):
        j.shell()

    def _set_pre(self,acl):
        """
        will serialize the acl in a very specific sorted way to make sure we can calculate the hash

        :param acl:
        :return:
        """
        hash=j.data.hash.md5_string(acl._json)
        if acl.hash == hash:
            if acl.id is not None:
                #means the object did not change nothing to do
                #and the object id is already known, so exists already in DB
                self.logger.debug("acl alike, id exists")
                return False, acl
            else:
                self.logger.debug("acl alike, new object")
                return True, acl #is a new one need to save

        #now check if the acl hash is already in the index
        res = self.index.select().where(self.index.hash == hash).first()
        if res:
            self.logger.debug("acl is in index")
            w=self.get(res.id)
            if w is None:
                #means the index is larger than data on backend, need to rebuild
                self.logger.warning("have to rebuild index because index is larger than data on backend")
                self.index_rebuild()
                acl.hash=hash
                return True,acl
            else:
                #means this acl already exists, need to return the id of the one already saved
                acl = w #get the one just fetched
                return False,acl #no need to save
        else:
            #MEANS THE HASH IS DIFFERENT & not found in index
            if acl.id is not None:
                #acl already exists, no need to save but need to index
                #existing acl but hash differently, need to fetch new one & get data from existing one
                acl2 = self.new(capnpbin=acl._data)
                acl2.hash=hash
                j.shell()
                acl = acl2
            acl.hash = hash
            return True,acl



        acl.id = None #needs to be a new one because does not exist yet
        return True,acl


