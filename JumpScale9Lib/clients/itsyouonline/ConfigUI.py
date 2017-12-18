
from js9 import j
import npyscreen
import curses

# TO TEST IN DOCKER
# ZSSH "js9 'j.tools.develop.config()'"


class ConfigUI(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN",    MainForm)

    def change_form(self, name):
        self.switchForm(name)
        self.resetHistory()

    def exit_application(self):
        pass


class MyMenu():
    def addMenu(self):
        self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
        self.m1.addItem(text='Main', onSelect=self.go2form,
                        shortcut=None, arguments=["MAIN"], keywords=None)

    def go2form(self, name):
        self.parentApp.change_form(name)

    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")

    def whenDisplayText(self, argument):
        npyscreen.notify_confirm(argument)

    def whenJustBeep(self):
        curses.beep()

    def exit_application(self):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()
        self.parentApp.exit_application()


class MainForm(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()
        self.main()

    def main(self):
        # from IPython import embed;embed(colors='Linux')
        self.loginname = self.add_widget(
            npyscreen.TitleText, name="Your login name:")
        self.email = self.add_widget(npyscreen.TitleText, name="Your email:")
        self.fullname = self.add_widget(npyscreen.TitleText, name="Full name:")

        self.loginname.value = j.core.state.configMe["me"].get("loginname", "")
        self.email.value = j.core.state.configMe["me"].get("email", "")
        self.fullname.value = j.core.state.configMe["me"].get("fullname", "")

        # keyname = j.core.state.configMe["ssh"].get("sshkeyname", "")

        # keypath = "%s/.ssh/%s" % (j.dirs.HOMEDIR, keyname)
        # if not j.sal.fs.exists(keypath):

        sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
        keynames = [j.sal.fs.getBaseName(
            item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
        self.sshkeyname = self.add_widget(
            npyscreen.TitleSelectOne, name="YOUR SSH KEY:", values=keynames)

        sshkeyname = j.core.state.configMe["ssh"]["sshkeyname"]

        if keynames.count(sshkeyname) > 0:
            pos = keynames.index(sshkeyname)
            self.sshkeyname.set_value(pos)

        self.keynames = keynames

        # from IPython import embed
        # embed(colors='Linux')
        # else:
        #     self.sshkeyname = self.add_widget(
        #         npyscreen.TitleText, name="YOUR SSH KEY:", value=keyname)

        # from IPython import embed;embed(colors='Linux')

        # self.sshkeypath = self.add_widget(npyscreen.TitleFilenameCombo, name="Your SSH Key Path:",must_exist=True)
        # keyname=j.core.state.configGetFromDict("ssh","sshkeyname","")
        # if keyname.strip()=="":
        #     keypath="%s/.ssh/??????"%j.dirs.HOMEDIR
        # else:
        #     keypath="%s/.ssh/%s"%(j.dirs.HOMEDIR,keyname)
        # self.sshkeypath.value=keypath

    def afterEditing(self):
        j.core.state.configMe["me"]["loginname"] = self.loginname.value
        j.core.state.configMe["me"]["email"] = self.email.value
        j.core.state.configMe["me"]["fullname"] = self.fullname.value
        if len(self.sshkeyname.value) == 1:
            j.core.state.configMe["ssh"]["sshkeyname"] = self.keynames[self.sshkeyname.value[0]]
        j.core.state.configSave()

        self.exit_application()