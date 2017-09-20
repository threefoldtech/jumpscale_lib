from js9 import j


class TODO():

    def __init__(self,itenv,path,todo):
        path=path.replace("//","/")
        self.itenv=itenv
        self.path=path
        self.todo=todo

    @property
    def person(self):
        return j.sal.fs.getBaseName(self.path)


    def __repr__(self):
        return "Todo %s:%s:%s:%s   "%(self.itenv.company,self.itenv.name,self.path,self.todo)

    __str__=__repr__        

class itenv():
    def __init__(self,company,name,path):
        self.company = company
        self.path=path
        self.name=name
        self.todo = []

    def addTodo(self,path,todo):
        todo=todo.replace("_","-")
        td=TODO(self,path,todo)
        print(td)
        self.todo.append(td)

    @property
    def todoPerItEnv(self):
        todo2={}
        for todo in self.todo:
            if todo.itenv not in todo2:
                todo2[todo.person]=[]
            todo2[todo.itenv].append(todo)
        return todo2

    @property
    def todo_md(self):
        md="# TODO FOR : %s %s\n\n"%(self.company,self.name)
        for person,todos in self.todoPerPerson.items():
            md+="## %s\n\n"%person
            for todo in todos:
                md+="- %s\n"%(todo.todo)
            md+="\n"

        return md

    def __repr__(self):
        return "itenv %s:%s:%s"%(self.company,self.name,self.path)

    __str__=__repr__

    


class ITEnvManager:
    def __init__(self):
        self.__jslocation__ = "j.tools.itenv_manager"
        self.itenvs = {}

    def _additenv(self,path,company,name):
        key="%s_%s"%(company,name)
        if not key in self.itenvs.keys():
            self.itenvs[key]=itenv(company,name,path)
        return self.itenvs[key]
            

    def process(self,path):

        raise RuntimeError("not implemented yet")

        # def processStrList(newtoml,key):
        #     out=[]
        #     for item in newtoml[key]:
        #         item=item.lower().strip()
        #         out.append(item)
        #     newtoml[key]=out
        #     return newtoml
        
        # for item in ["locations","departments","companies","departments"]:
        #     newtoml=processStrList(newtoml,item)

        # def processStr(newtoml,key):
        #     val=newtoml[key]
        #     val=val.lower().strip()
        #     newtoml[key]=val
        #     return newtoml

        # for item in ["login","first_name","last_name","telegram","skype"]:
        #     newtoml=processStr(newtoml,item)


        # j.data.serializer.toml.dump(dpath,newtoml)

