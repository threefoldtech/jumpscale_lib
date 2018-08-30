from testconfig import config
from termcolor import colored
import unittest
import uuid, time
import subprocess
from jumpscale import j


NODE_CLIENT = 'local'

class BaseTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        BaseTest.node_sal = j.clients.zos.get(NODE_CLIENT, data={'host': config['main']['nodeip']})

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.node_sal = BaseTest.node_sal

    def tearDown(self):
        pass
