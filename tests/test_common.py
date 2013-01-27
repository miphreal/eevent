import unittest
from eevent import events


class BasicTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()

    def test_register(self):
        self.e

