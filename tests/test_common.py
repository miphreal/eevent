import unittest
from eevent import events


ARGS = (123, 'abc',)
KWARGS = {'arg': 'test'}


def func_factory(some_text):
    def func(*args, **kwargs):
        print(some_text, args, kwargs)
        return some_text
    return func


class BasicTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()
        self.e.on('my_event_name', func_factory('My Event Name'))
        self.e.on('A', func_factory('A'))
        self.e.on('B', func_factory('B'))
        self.e.on('C', func_factory('C'))
        self.e.on('A', func_factory('A+'))
        self.e.on('B', func_factory('B+'))
        self.e.on('C', func_factory('C+'))

        self.func_1 = func_factory('F1')
        self.func_2 = func_factory('F2')
        self.func_3 = func_factory('F3')
        self.e.on('F', [self.func_1, self.func_2, self.func_3])

        self.func_X = func_factory('X')
        self.e.on(['D', 'E'], [self.func_X, func_factory('X+')])

    def test_register(self):
        # registered events: my_event_name A B C D E F
        self.assertEqual(len(self.e), 7, "Seems, some events weren't registered")

    def test_trigger(self):
        results = self.e.trigger('my_event_name', *ARGS, **KWARGS)
        self.assertListEqual(results, ['My Event Name'], 'No events were fired')

        results = self.e.trigger('A', *ARGS, **KWARGS)
        self.assertListEqual(results, ['A', 'A+'], 'No events were fired')

        results = self.e.trigger('A B C'.split(), *ARGS, **KWARGS)
        self.assertListEqual(results, ['A', 'A+', 'B', 'B+', 'C', 'C+'], 'No events were fired')

        results = self.e.trigger('F', *ARGS, **KWARGS)
        self.assertListEqual(results, ['F1', 'F2', 'F3'], 'No events were fired')

        results = self.e.trigger('D', *ARGS, **KWARGS)
        self.assertListEqual(results, ['X', 'X+'], 'No events were fired')

    def test_unbind_events(self):
        self.e.off('my_event_name')
        self.assertFalse('my_event_name' in self.e, 'The event is still registered')
        results = self.e.trigger('my_event_name', *ARGS, **KWARGS)
        self.assertFalse(results, 'The event is still registered')

        self.e.off(['A', 'B', 'C'])
        results = self.e.trigger(['A', 'B', 'C'], *ARGS, **KWARGS)
        self.assertFalse(results, 'The events are still registered')

        self.e.off('F', self.func_2)
        self.assertTrue('F' in self.e, 'The F event must be registered, because it still has F1 and F3 handlers')
        results = self.e.trigger('F', *ARGS, **KWARGS)
        self.assertFalse('F2' in results, 'The func_2 is still registered')

        self.e.off(['D', 'F'], [self.func_1, self.func_X])
        self.assertTrue('D' in self.e, 'The D event must be registered, because it still has X+ handler')
        self.assertTrue('F' in self.e, 'The F event must be registered, because it still has F3 handler')
        results = self.e.trigger(['D', 'F'], *ARGS, **KWARGS)
        self.assertFalse('F1' in results or 'X' in results, 'The func_1 or func_X handlers are still registered')

        self.e.off('F', self.func_3)
        self.assertFalse('F' in self.e, "The F event is still registered "
                                        "(must be deleted, because it doesn't have any handlers")
        results = self.e.trigger('F', *ARGS, **KWARGS)
        self.assertFalse('F3' in results, 'The func_3 is still registered')

        self.e.off()
        self.assertFalse(self.e, 'Some events are still registered. All events must be cleared.')


class HierarchyTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()


class WildCardTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()


class PropagationTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()


class InvokeHandlersTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()


class OptionsTest(unittest.TestCase):

    def setUp(self):
        self.e = events.Events()
