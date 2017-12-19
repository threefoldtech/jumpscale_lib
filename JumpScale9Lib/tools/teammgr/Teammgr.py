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


class Person:
    def __init__(self, team, name, path):
        self.team = team
        self.path = path
        self.name = name
        self.todo = []
        self.path_toml = "%s/profile.toml"%(self.path)
        
        
    def infotosort_add(self,path):
        """
        to be sorted later, and to make sure we don't loose the data
        """
        dpath="%s/tosort/"%(self.path)
        j.sal.fs.createDir(dpath)
        dest="%s/%s"% (dpath,j.sal.fs.getBaseName(path))
        j.sal.fs.move(path,dest)

    def info_add(self,path):
        """
        read info try to get useful pieces out of it and add to profile
        """
        

    def fix(self):
        """
        walk over data of person and fix
        """
        if j.sal.fs.exists(self.path_toml):

            if j.sal.fs.exists(toml_path):
                try:
                    personal_toml = j.data.serializer.toml.load(toml_path)
                except Exception:
                    team_obj.todo_add(self.path, "toml file is corrupt:%s" % toml_path)
                    return newtoml

                for key, val in personal_toml.items():
                    if key not in newtoml:
                        if key == "experience":
                            try:
                                newtoml = j.data.serializer.toml.set_value(fixed_toml, "description_public_formal", val)
                            except Exception as e:
                                team_obj.todo_add(self.path, "type error:%s %s (%s)" % (toml_path, key, e))
                        elif key not in ["escalation", "action"]:
                            team_obj.todo_add(self.path,
                                               "found unrecognized key:%s in toml file:%s" % (key, toml_path))
                    else:
                        try:
                            newtoml = j.data.serializer.toml.set_value(fixed_toml, key, val)
                        except Exception as e:
                            team_obj.todo_add(self.path, "type error:%s %s (%s)" % (toml_path, key, e))
            return newtoml

        j.sal.fs.remove("%s/fixed.yaml" % self.path)
        j.sal.fs.remove("%s/fixed.toml" % self.path)

        final_toml_path = "%s/fixed_donotchange.toml" % self.path
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
                team_obj.todo_add(self.path, "empty value for:%s" % item)

        for key in ["locations", "companies", "departments"]:
            new_toml[key] = [toml_item.lower().strip() for toml_item in new_toml[key]]

        for key in ["login", "first_name", "last_name", "telegram", "skype"]:
            new_toml[key] = new_toml[key].lower().strip()

        j.data.serializer.toml.dump(final_toml_path, new_toml)


class Team:
    def __init__(self, company, name, path):
        self.company = company
        self.path = path
        self.name = name
        self.todo = []
        self.persons = []

    def todo_add(self, path, todo):
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
                        team_obj.todo_add(personPath, "did not find unprocessed picture, please add")

                    self.fix_toml(team_obj, personPath)

        j.sal.fs.createDir("%s/todo" % path)
        for key, team in self.teams.items():
            path1 = "%s/todo/%s_%s.md" % (path, team.company, team.name)
            j.sal.fs.writeFile(path1, team.todo_md)





from js9 import j
import os
from PIL import Image

source = j.sal.fs.getParent(j.sal.fs.getParent(os.path.abspath(__file__)))
j.tools.team_manager.process(source)
# TODO Change target with js9 repos config
target = j.sal.fs.getParent(source) + "/www_threefold2.0/www.threefoldtoken.com/themes/landing/static"
js_target = '{}/js/data.js'.format(target)
avatars_target = '{}/avatars'.format(target)
# Teams to exclude
excluded_teams = {
    "gig": ["external"]
}

# teams to be filtered based on company_id field
filtered_teams = {
    "gig": ["varia", "sales_marketing", "operations", "engineering"]
}

# Company id to check for filtered team {1: gig, 2: threefold}
company_id = 2


def process_image(img_path, parent_path):
    img = Image.open(img_path)
    if img.height != img.width:
        side = min((img.width, img.height))
        img = img.crop((0, 0, side, side))

    side = 252
    if img.height != side:
        img = img.resize((side, side))
    new_processed_image = "{}/processed.jpg".format(parent_path)
    img.save(new_processed_image)
    return new_processed_image


all_files = {}
for team_name_path in j.sal.fs.listDirsInDir(source+"/team", recursive=False):
    team_name = j.sal.fs.getBaseName(team_name_path)
    for department_path in j.sal.fs.listDirsInDir(team_name_path, recursive=False):
        department = j.sal.fs.getBaseName(department_path)
        if team_name in excluded_teams and department in excluded_teams[team_name]:
            continue
        team_obj = j.tools.team_manager._add_team(department_path, team_name, department)
        for person_path in j.sal.fs.listDirsInDir(department_path, recursive=False):
            # Get toml file
            j.tools.team_manager.fix_toml(team_obj, person_path)
            toml_file = "{}/fixed_donotchange.toml".format(person_path)
            if not j.sal.fs.exists(toml_file):
                continue
            all_files[person_path] = {
                'team': team_name,
                'department': department,
                'toml': toml_file,
            }

            # Get processed image
            unprocessed_image = "{}/unprocessed.jpg".format(person_path)
            processed_image = "{}/processed.jpg".format(person_path)
            if j.sal.fs.exists(processed_image):
                all_files[person_path]['image'] = processed_image
            elif j.sal.fs.exists(unprocessed_image):
                all_files[person_path]['image'] = process_image(unprocessed_image, person_path)

sections = []
for person_path, files in all_files.items():
    # skip all soft links that their links are already exists
    if j.sal.fs.isLink(person_path) and j.sal.fs.readLink(person_path) in all_files:
        continue
    print("Processing: %s" % person_path)

    person = j.data.serializer.toml.load(files['toml'])

    # exclude team members of filtered teams from different company_id
    if files["team"] in filtered_teams \
            and files["department"] in filtered_teams[files['team']] \
            and company_id not in person.get("company_id"):
        continue

    first_name = person.get('first_name', '')
    last_name = person.get('last_name', '')
    name = "{} {}".format(first_name, last_name)
    login = person.get('login')
    description = person.get('description_public_friendly') or \
                  person.get("description_public_formal") or \
                  person.get("description_internal")
    linked_in = person.get('linkedin')
    telegram = person.get('telegram')
    emails = person.get('email')
    hobbies = person.get('hobbies')
    skype = person.get('skype')
    links = person.get('links')
    github = person.get('github')
    avatar_name = ""
    if files.get('image'):
        avatar_name = "{}_{}".format(j.sal.fs.getBaseName(person_path), j.sal.fs.getBaseName(files['image']))
        j.sal.fs.copyFile(files['image'], "{}/{}".format(avatars_target, avatar_name))
    sections.append({
        "name": name,
        "login": login,
        "description": description,
        "linked_in": linked_in,
        "skype": skype,
        "github": github,
        "avatar": avatar_name,
        "telegram": telegram,
        "emails": emails,
        "hobbies": hobbies,
        "links": links
    })

# write dict to the javascript file
data = j.data.serializer.json.dumps(sections)
j.sal.fs.writeFile(js_target, "var team = {};".format(data))