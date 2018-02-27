from js9 import j

from .WordpressClient import WordpressClient

JSConfigBase = j.tools.configmanager.base_class_configs


class WordpressFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.wordpress"
        JSConfigBase.__init__(self, WordpressClient)

    def test(self):
        """
        js9 'j.clients.wordpress.test()'
        """
        # data = {
        #     "admin_email": "test@test.com",
        #     "admin_password_": "test",
        #     "admin_user" : "test",
        #     "db_password_" : "test",
        #     "title": "test"
        # }
        
        #MAKE SURE THERE IS TEST CONNECTION CREATED
        
        wp_cl = j.clients.wordpress.get('test')
        from IPython import embed
        embed(colors='Linux')

        #TODO: do tests, like uploading pages, listing pages, adding users, ...