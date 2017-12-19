from js9 import j

fixed_toml = """
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


class Todo:
    def __init__(self, department, path, todo):
        path = path.replace("//", "/")
        self.department = department
        self.path = path
        self.todo = todo

    @property
    def person(self):
        return j.sal.fs.getBaseName(self.path)

    def __repr__(self):
        return "Todo %s:%s:%s:%s   " % (self.department.company, self.department.name, self.path, self.todo)

    __str__ = __repr__

class Person:
    def __init__(self, department, name, path):
        self.department = department
        self.path = path
        self.name = name
        self.todo = []

    def load(self):
        self.images_fix()
        self.toml_fix()
        self.save()

    def images_fix(self):
        #make sure we have an unprocessed.jpg
        images = j.sal.fs.listFilesInDir(person_path, filter="*.jpg")
        unprocessed_images = [item for item in images if j.sal.fs.getBaseName(item) == "unprocessed.jpg"]
        if images and not unprocessed_images:
            # did not have an unprocessed one need to copy to unprocessed name
            image = images[0]
            j.sal.fs.renameFile(image, "%s/unprocessed.jpg" % (j.sal.fs.getDirName(image)))
        elif not unprocessed_images:
            self.add_to_do(person_path, "did not find unprocessed picture, please add")        
        

    def save(self):
        pass


    @staticmethod
    def toml_fix(department_obj, person_path):

        def process(newtoml, name):
            toml_path = "%s/%s.toml" % (person_path, name)
            if j.sal.fs.exists(toml_path):
                try:
                    personal_toml = j.data.serializer.toml.load(toml_path)
                except Exception:
                    department_obj.add_to_do(person_path, "toml file is corrupt:%s" % toml_path)
                    return newtoml

                for key, val in personal_toml.items():
                    if key not in newtoml:
                        if key == "experience":
                            try:
                                newtoml = add_to_toml(newtoml, "description_public_formal", val)
                            except Exception as e:
                                department_obj.add_to_do(person_path, "type error:%s %s (%s)" % (toml_path, key, e))
                        elif key not in ["escalation", "action"]:
                            department_obj.add_to_do(person_path,
                                               "found unrecognized key:%s in toml file:%s" % (key, toml_path))
                    else:
                        try:
                            newtoml = add_to_toml(newtoml, key, val)
                        except Exception as e:
                            department_obj.add_to_do(person_path, "type error:%s %s (%s)" % (toml_path, key, e))
            return newtoml

        #just remove old stuff
        j.sal.fs.remove("%s/fixed.yaml" % person_path)
        j.sal.fs.remove("%s/fixed.toml" % person_path)

        final_toml_path = "%s/fixed_donotchange.toml" % person_path
        if j.sal.fs.exists(final_toml_path):
            new_toml = j.data.serializer.toml.load(final_toml_path)
        else:
            new_toml = j.data.serializer.toml.loads(fixed_toml) #load the template

        # fix older toml files
        new_toml.setdefault("companies", [])

        new_toml = process(new_toml, "profile")
        new_toml = process(new_toml, "person")

        department = "%s:%s" % (department_obj.company, department_obj.name)
        if department not in new_toml["departments"]:
            new_toml["departments"].append(department)

        if department_obj.company not in new_toml["companies"]:
            new_toml["companies"].append(department_obj.company)

        for item in ["login", "first_name", "last_name", "description_public_formal", "description_public_friendly",
                     "pub_ssh_key", "telegram", "reports_into", "locations", "departments", "title", "mobile", "email"]:
            if not new_toml[item]:
                department_obj.add_to_do(person_path, "empty value for:%s" % item)

        for key in ["locations", "companies", "departments"]:
            new_toml[key] = [toml_item.lower().strip() for toml_item in new_toml[key]]

        for key in ["login", "first_name", "last_name", "telegram", "skype"]:
            new_toml[key] = new_toml[key].lower().strip()

        j.data.serializer.toml.dump(final_toml_path, new_toml)

    def __repr__(self):
        return "Person %s:%s:%s" % (self.department.name, self.name, self.path)

    __str__ = __repr__
class Department:
    def __init__(self, name, path):
        self.path = path
        self.name = name
        self.todo = []
        self.persons = []

    def load(self)
        for person_path in j.sal.fs.listDirsInDir(self.path, recursive=False):
            person_name = j.sal.fs.getBaseName(person_path)
            self.persons.append(Person(self,person_name,person_path))

    def add_to_do(self, path, todo):
        todo = todo.replace("_", "-")
        td = Todo(self, path, todo)
        self.todo.append(td)

    @property
    def todo_per_person(self):
        todo2 = {}
        for todo in self.todo:
            if todo.person not in todo2:
                todo2[todo.person] = []
            todo2[todo.person].append(todo)
        return todo2

    @property
    def todo_md(self):
        if len(self.todo_per_person.items())==0:
            return ""
        md = "# Todo for department : %s\n\n" % (self.name)
        for person, todos in self.todo_per_person.items():
            md += "## %s\n\n" % person
            for todo in todos:
                md += "- %s\n" % todo.todo
            md += "\n"

        return md

    def __repr__(self):
        return "Department %s:%s" % (s self.name, self.path)

    __str__ = __repr__


class TeamManager:
    def __init__(self):
        self.__jslocation__ = "j.tools.team_manager"
        self.departments = {}

    def _add_department(self, path, name):
        if name not in self.departments:
            self.departments[name] = Department(name, path)
        return self.departments[name]

    def process(self, path=""):
        """
        if path=='' then use current dir 
        """
        
        path=j.sal.fs.getcwd()
        
        path0=path
        found=""
        #look up to find the right dir
        while path0!="":
            if j.sal.fs.exists("%s/.department"%path0):
                found=path0
                break
            path0=j.sal.fs.getParent(path0).rstrip().rstrip("/").rstrip()
        if found =="":
            raise RuntimeError("could not find .department in one of the parent dir's (or this dir):'%s'"%path)

        path=path0

        for department_path in j.sal.fs.listDirsInDir(department_path, recursive=False):
            department_name = j.sal.fs.getBaseName(department_path)
            department_obj = self._add_department(catPath, department_name, cat)

        #write all the todo's
        j.sal.fs.createDir("%s/todo" % path)
        for key, department in self.departments.items():
            path1 = "%s/todo/%s.md" % (path, department.name)
            if department.todo_md!="":
                j.sal.fs.writeFile(path1, department.todo_md)

