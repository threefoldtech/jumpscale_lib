from termcolor import colored
import unittest
from jumpscale import j
import uuid
import time
import logging

import random


class Utils(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        self._testID = self._testMethodName
        self._startTime = time.time()

        self._logger = logging.LoggerAdapter(logging.getLogger('SAL testcases'),
                                             {'testid': self.shortDescription() or self._testID})

    @staticmethod
    def random_string():
        return str(uuid.uuid4())[0:8]

    def log(self, msg):
        self._logger.info(msg)
