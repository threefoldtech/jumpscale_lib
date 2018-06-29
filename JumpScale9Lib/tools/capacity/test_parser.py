from js9 import j
from unittest import TestCase
import os


class TestParser(TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.data1 = j.sal.fs.fileGetContents(os.path.join(dirname, 'dmidecode1.txt'))
        self.data2 = j.sal.fs.fileGetContents(os.path.join(dirname, 'dmidecode2.txt'))
        self.memory = 1024 ** 3

    def test_has_keys(self):
        hwdata = j.tools.capacity.parser.hw_info_from_dmi(self.data1)
        self.assertIn('0x0000', hwdata)
        self.assertIn('0x0001', hwdata)

    def get_report(self, data):
        hwdata = j.tools.capacity.parser.hw_info_from_dmi(data)
        return j.tools.capacity.parser.get_report(self.memory, hwdata, {})

    def test_report_data1(self):
        report = self.get_report(self.data1)
        self.assertEqual(report.CRU, 8, "Something wrong when parsing CPU data")
        self.assertEqual(report.MRU, 1, "Something wrong when parsing Memory data")


    def test_report_data2(self):
        report = self.get_report(self.data2)
        self.assertEqual(report.CRU, 4, "Something wrong when parsing CPU data")
        self.assertEqual(report.MRU, 1, "Something wrong when parsing Memory data")

    def test_report_motherboard(self):
        report = self.get_report(self.data1)
        self.assertEqual(report.motherboard[0]['serial'], 'W1KS42E13PU', 'Failed to parse serial')
