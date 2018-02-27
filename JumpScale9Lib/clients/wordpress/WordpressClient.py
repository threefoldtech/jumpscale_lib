from js9 import j
JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
path = "/opt/var/data/www"
url = "localhost:8090"
title = ""
admin_user = ""
admin_password_ = ""
admin_email = ""
db_name = 'wordpress'
db_user = 'wordpress'
db_password_ = ""
port = 8090
"""
class WordpressClient(JSConfigBase):
    def __init__(self, instance, data={}, parent=None):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE)
        c = self.config.data
        self.path = c['path']
        self.url = c['url']
        self.title = c['title']
        self.admin_user = c['admin_user']
        self.admin_password = c['admin_password_']
        self.admin_email = c['admin_email']
        self.db_name = c['db_name']
        self.db_user = c['db_user']
        self.db_password = c['db_password_']
        self.port = c['port']

    def install(self, theme=None, plugins=None, reset='false'):
        """install wordpress with data given in the template
        
        Keyword Arguments:
            theme {string} -- local path, or direct download link for a theme to install (default: {None})
            plugins {[string]} -- list of plugin slugs, urls or local paths to install (default: {None})
            reset {boolean} -- if true installation will start all over again even if it was already installed (default: {False})
        """
        
        p = j.tools.prefab.local
        p.apps.wordpress.install(self.path, self.url, self.title, self.admin_user, self.admin_password, self.admin_email, 
                self.db_name, self.db_user, self.db_password, self.port, plugins, theme, reset)

    def install_plugins(self, plugins):
        """install list of plugins
        
        Arguments:
            plugins {[string]} -- list of plugin slugs, urls or local paths to install
        """

        if not plugins:
            return
        
        for plugin in plugins:
            plugins_command = """
            sudo -u wordpress -i -- wp --path={} plugin install {}
            """.format(self.path, plugin)
            self.prefab.core.run(plugins_command, die=False)
                
    def install_theme(self, theme, activate=False):
        """install a theme
        
        Arguments:
            theme {string} -- local path, or direct download link for a theme to install
        
        Keyword Arguments:
            activate {boolean} -- if True the theme will be activated after install (default: {False})
        """
        if not theme:
            return

        activate_cmd = "--activate" if activate else ""
        themes_command = """
        sudo -u wordpress -i -- wp --path={} theme install {} {}
        """.format(self.path, theme, activate_cmd)
        self.prefab.core.run(themes_command, die=False)
