import unittest
from eevent import events


ARGS = (123, 'abc',)
KWARGS = {'arg': 'test'}


def func_factory(some_text):
    def func(*args, **kwargs):
        print(some_text, args, kwargs)
        return some_text
    return func


class UseCasesTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()


class CustomBehaviorTest(unittest.TestCase):

    def setUp(self):

        class CustomEvents(events.Events):
            pass

        self.e = CustomEvents()