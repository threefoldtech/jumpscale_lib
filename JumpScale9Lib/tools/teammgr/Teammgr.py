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


class TODO:
    def __init__(self, team, path, todo):
        path = path.replace("//", "/")
        self.team = team
        self.path = path
        self.todo = todo

    @property
    def person(self):
        return j.sal.fs.getBaseName(self.path)

    def __repr__(self):
        return "Todo %s:%s:%s:%s   " % (self.team.company, self.team.name, self.path, self.todo)

    __str__ = __repr__


class Team:
    def __init__(self, company, name, path):
        self.company = company
        self.path = path
        self.name = name
        self.todo = []

    def add_to_do(self, path, todo):
        todo = todo.replace("_", "-")
        td = TODO(self, path, todo)
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
        md = "# TODO FOR : %s %s\n\n" % (self.company, self.name)
        for person, todos in self.todo_per_person.items():
            md += "## %s\n\n" % person
            for todo in todos:
                md += "- %s\n" % todo.todo
            md += "\n"

        return md

    def __repr__(self):
        return "Team %s:%s:%s" % (self.company, self.name, self.path)

    __str__ = __repr__


class Teammgr:
    def __init__(self):
        self.__jslocation__ = "j.tools.team_manager"
        self.teams = {}

    def _add_team(self, path, company, name):
        key = "%s_%s" % (company, name)
        if key not in self.teams:
            self.teams[key] = Team(company, name, path)
        return self.teams[key]

    def process(self, path):
        team_path = path + "/team"
        if not j.sal.fs.exists(team_path):
            raise RuntimeError("Cannot find team path:%s" % team_path)

        for team_name_path in j.sal.fs.listDirsInDir(team_path, recursive=False):
            team_name = j.sal.fs.getBaseName(team_name_path)
            for catPath in j.sal.fs.listDirsInDir(team_name_path, recursive=False):
                cat = j.sal.fs.getBaseName(catPath)
                team_obj = self._add_team(catPath, team_name, cat)
                for personPath in j.sal.fs.listDirsInDir(catPath, recursive=False):
                    images = j.sal.fs.listFilesInDir(personPath, filter="*.jpg")
                    unprocessed_images = [item for item in images if j.sal.fs.getBaseName(item) == "unprocessed.jpg"]
                    if images and not unprocessed_images:
                        # did not have an unprocessed one need to copy to unprocessed name
                        image = images[0]
                        j.sal.fs.renameFile(image, "%s/unprocessed.jpg" % (j.sal.fs.getDirName(image)))
                    elif not unprocessed_images:
                        team_obj.add_to_do(personPath, "did not find unprocessed picture, please add")

                    self.fix_toml(team_obj, personPath)

        j.sal.fs.createDir("%s/todo" % path)
        for key, team in self.teams.items():
            path1 = "%s/todo/%s_%s.md" % (path, team.company, team.name)
            j.sal.fs.writeFile(path1, team.todo_md)

    @staticmethod
    def fix_toml(team_obj, person_path):

        def add_to_toml(newtoml, key, val):
            if j.data.types.list.check(newtoml[key]):
                if j.data.types.list.check(val):
                    for val0 in val:
                        val = str(val).lower().strip()
                        if val0 not in newtoml[key]:
                            newtoml[key].append(val0)
                else:
                    val = str(val).replace("'", "")
                    if val not in newtoml[key]:
                        newtoml[key].append(val)
            elif j.data.types.bool.check(newtoml[key]):
                if str(val).lower() in ['true', "1", "y", "yes"]:
                    val = True
                else:
                    val = False
                newtoml[key] = val
            elif j.data.types.int.check(newtoml[key]):
                newtoml[key] = int(val)
            elif j.data.types.float.check(newtoml[key]):
                newtoml[key] = int(val)
            else:
                newtoml[key] = str(val)

            return newtoml

        def process(newtoml, name):
            toml_path = "%s/%s.toml" % (person_path, name)
            if j.sal.fs.exists(toml_path):
                try:
                    personal_toml = j.data.serializer.toml.load(toml_path)
                except Exception:
                    team_obj.add_to_do(person_path, "toml file is corrupt:%s" % toml_path)
                    return newtoml

                for key, val in personal_toml.items():
                    if key not in newtoml:
                        if key == "experience":
                            try:
                                newtoml = add_to_toml(newtoml, "description_public_formal", val)
                            except Exception as e:
                                team_obj.add_to_do(person_path, "type error:%s %s (%s)" % (toml_path, key, e))
                        elif key not in ["escalation", "action"]:
                            team_obj.add_to_do(person_path,
                                               "found unrecognized key:%s in toml file:%s" % (key, toml_path))
                    else:
                        try:
                            newtoml = add_to_toml(newtoml, key, val)
                        except Exception as e:
                            team_obj.add_to_do(person_path, "type error:%s %s (%s)" % (toml_path, key, e))
            return newtoml

        j.sal.fs.remove("%s/fixed.yaml" % person_path)
        j.sal.fs.remove("%s/fixed.toml" % person_path)

        final_toml_path = "%s/fixed_donotchange.toml" % person_path
        if j.sal.fs.exists(final_toml_path):
            new_toml = j.data.serializer.toml.load(final_toml_path)
        else:
            new_toml = j.data.serializer.toml.loads(fixed_toml)

        # fix older toml files
        new_toml.setdefault("companies", [])

        new_toml = process(new_toml, "profile")
        new_toml = process(new_toml, "person")

        department = "%s:%s" % (team_obj.company, team_obj.name)
        if department not in new_toml["departments"]:
            new_toml["departments"].append(department)

        if team_obj.company not in new_toml["companies"]:
            new_toml["companies"].append(team_obj.company)

        for item in ["login", "first_name", "last_name", "description_public_formal", "description_public_friendly",
                     "pub_ssh_key", "telegram", "reports_into", "locations", "departments", "title", "mobile", "email"]:
            if not new_toml[item]:
                team_obj.add_to_do(person_path, "empty value for:%s" % item)

        for key in ["locations", "companies", "departments"]:
            new_toml[key] = [toml_item.lower().strip() for toml_item in new_toml[key]]

        for key in ["login", "first_name", "last_name", "telegram", "skype"]:
            new_toml[key] = new_toml[key].lower().strip()

        j.data.serializer.toml.dump(final_toml_path, new_toml)
