from js9 import j

persontoml="""

login =""
first_name = ""
last_name = ""
locations = []
companies = []
departments = []

languageCode = "en-us"
title = []

description_internal =""

description_public_friendly =""

description_public_formal =""

hobbies = ""

pub_ssh_key= ""

skype = ""
telegram = ""
itsyou_online = ""

reports_into = ""

mobile = []

email = []

github = ""
linkedin = ""

links = []


"""


class TODO():

    def __init__(self,team,path,todo):
        path=path.replace("//","/")
        self.team=team
        self.path=path
        self.todo=todo

    @property
    def person(self):
        return j.sal.fs.getBaseName(self.path)


    def __repr__(self):
        return "Todo %s:%s:%s:%s   "%(self.team.company,self.team.name,self.path,self.todo)

    __str__=__repr__        

class Team():
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
    def todoPerPerson(self):
        todo2={}
        for todo in self.todo:
            if todo.person not in todo2:
                todo2[todo.person]=[]
            todo2[todo.person].append(todo)
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
        return "Team %s:%s:%s"%(self.company,self.name,self.path)

    __str__=__repr__

    


class Teammgr:
    def __init__(self):
        self.__jslocation__ = "j.tools.team_manager"
        self.teams = {}

    def _addTeam(self,path,company,name):
        key="%s_%s"%(company,name)
        if not key in self.teams.keys():
            self.teams[key]=Team(company,name,path)
        return self.teams[key]
            

    def process(self,path):

        teampath=path+"/team"

        if not j.sal.fs.exists(teampath):
            raise RuntimeError("Cannot find teampath:%s"%teampath)

        for teamnamePath in j.sal.fs.listDirsInDir(teampath,recursive=False):
            teamname=j.sal.fs.getBaseName(teamnamePath)
            for catPath in j.sal.fs.listDirsInDir(teamnamePath,recursive=False):
                    cat=j.sal.fs.getBaseName(catPath)
                    teamObj=self._addTeam(catPath,teamname,cat)
                    for personPath in j.sal.fs.listDirsInDir(catPath,recursive=False):
                        personName=j.sal.fs.getBaseName(personPath)
                        images=j.sal.fs.listFilesInDir(personPath,filter="*.jpg")
                        unprocessed = [item for item in images if item == "unprocessed.jpg"]
                        processed = [item for item in images if j.sal.fs.getBaseName(item) == "processed.jpg"]
                        images = [item for item in images if not j.sal.fs.getBaseName(item) == "unprocessed.jpg"]  #filter the unprocessed ones
                        images = [item for item in images if not j.sal.fs.getBaseName(item) == "processed.jpg"]  #filter the unprocessed ones

                        if len(images)==1 and unprocessed==[]:
                            #did not have an unprocessed one need to copy to unprocessed name
                            image=images[0]
                            j.sal.fs.renameFile(image,"%s/unprocessed.jpg"%(j.sal.fs.getDirName(image)))
                        elif unprocessed==[]:
                            teamObj.addTodo(personPath,"did not find unprocessed picture, please add")

                        if processed==[]:
                            teamObj.addTodo(personPath,"did not find processed picture, please add")

                        self.fixtoml(teamObj,personPath)

        j.sal.fs.createDir("%s/todo"%path)
        for key,team in self.teams.items():
            path1="%s/todo/%s_%s.md"%(path,team.company,team.name)
            j.sal.fs.writeFile(path1,team.todo_md)



    def fixtoml(self,teamObj,personPath):        

        dpath="%s/fixed.yaml"%(personPath)
        j.sal.fs.remove(dpath)

        dpath="%s/fixed.toml"%(personPath)
        if j.sal.fs.exists(dpath):
            newtoml=j.data.serializer.toml.load(dpath)
        else:
            newtoml=j.data.serializer.toml.loads(persontoml)

        #fix older toml files
        for item in ["companies"]:
            if item not in newtoml.keys():
                newtoml[item]=[]

        def addToToml(newtoml,key,val,overwrite=False):
            print ("process toml:%s:%s"%(key,val))
            if j.data.types.list.check(newtoml[key]):
                if j.data.types.list.check(val):
                    for val0 in val:
                        if val0 not in newtoml[key]:
                            newtoml[key].append(val0)
                else:
                    val=str(val).replace("'","")
                    if val not in newtoml[key]:
                        newtoml[key].append(val)
            elif j.data.types.bool.check(newtoml[key]):
                if str(val).lower() in ['true',"1","y","yes"]:
                    val=True
                else:
                    val=False
                newtoml[key]=val
            elif j.data.types.int.check(newtoml[key]):
                newtoml[key]=int(val)
            elif j.data.types.float.check(newtoml[key]):
                newtoml[key]=int(val)
            else:
                newtoml[key]=str(val)

            return newtoml

        # tomlfiles=j.sal.fs.listFilesInDir(personPath,filter="*.toml")
        # tomlfiles = [item for item in tomlfiles if not j.sal.fs.getBaseName(item) == "person.toml"]
        # tomlfiles = [item for item in tomlfiles if not j.sal.fs.getBaseName(item) == "profile.toml"]
        # if len(tomlfiles)>0:
        #     teamObj.addTodo(personPath,"found unrecognized toml files (non person or profile)")

        def process(newtoml,name):
            tpath="%s/%s.toml"%(personPath,name)

            error=False
            if j.sal.fs.exists(tpath):

                try:
                    persontoml=j.data.serializer.toml.load(tpath)
                except Exception as e:
                    teamObj.addTodo(personPath,"toml file is corrupt:%s"%tpath)
                    return newtoml

                for key,val in persontoml.items():
                    if key not in newtoml.keys():
                        if key=="experience":
                            try:
                                newtoml=addToToml(newtoml,"description_public_formal",val)
                            except Exception as e:
                                teamObj.addTodo(personPath,"type error:%s %s (%s)"%(tpath,key,e))
                        elif key=="description":
                            try:
                                newtoml=addToToml(newtoml,"description_public_formal",val)
                            except Exception as e:
                                teamObj.addTodo(personPath,"type error:%s %s (%s)"%(tpath,key,e))
                        elif key in ["escalation","action"]:
                            pass
                        else:
                            error=True
                            teamObj.addTodo(personPath,"found unrecognized key:%s in tomlfile:%s"%(key,tpath))
                    else:
                        try:
                            newtoml=addToToml(newtoml,key,val)
                        except Exception as e:
                            teamObj.addTodo(personPath,"type error:%s %s (%s)"%(tpath,key,e))

            # if error==False:
            #     j.sal.fs.remove(tpath)

            return newtoml

        newtoml=process(newtoml,"profile")
        newtoml=process(newtoml,"person")

        departm="%s:%s"%(teamObj.company,teamObj.name)
        if not departm in newtoml["departments"]:
            newtoml["departments"].append(departm)

        if not teamObj.company in newtoml["companies"]:
            newtoml["companies"].append(teamObj.company)

        for item in ["login","first_name","last_name","description_public_formal","description_public_friendly","pub_ssh_key","telegram","reports_into"]:
            if newtoml[item]=="":
                teamObj.addTodo(personPath,"empty value for:%s"%(item))
        for item in ["locations","departments","title","mobile","email"]:
            if newtoml[item]==[]:
                teamObj.addTodo(personPath,"empty value for:%s"%(item))

        def processStrList(newtoml,key):
            out=[]
            for item in newtoml[key]:
                item=item.lower().strip()
                out.append(item)
            newtoml[key]=out
            return newtoml
        
        for item in ["locations","departments","companies","departments"]:
            newtoml=processStrList(newtoml,item)

        def processStr(newtoml,key):
            val=newtoml[key]
            val=val.lower().strip()
            newtoml[key]=val
            return newtoml

        for item in ["login","first_name","last_name","telegram","skype"]:
            newtoml=processStr(newtoml,item)


        j.data.serializer.toml.dump(dpath,newtoml)

