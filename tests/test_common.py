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
        self.e.on('Root', func_factory('R'))

        self.e.on('Root:A', func_factory('R:A'))
        self.e.on('Root:A:1', func_factory('R:A:1'))
        self.e.on('Root:A:2', func_factory('R:A:2'))

        self.e.on('Root:B:a', func_factory('R:B:a'))
        self.e.on('Root:B:b', func_factory('R:B:b'))
        self.e.on('Root:B:c', func_factory('R:B:c'))
        self.e.on('Root:B', func_factory('R:B'))

        self.e.on('A:a:1:I', func_factory('A:a:1:I'))
        self.e.on('A:a:1:II', func_factory('A:a:1:II'))
        self.e.on('A:a', func_factory('A:a'))

    def test_root_hook(self):
        results = self.e.trigger('Root:A:1', *ARGS, **KWARGS)
        self.assertTrue('R' in results and 'R:A' in results and 'R:A:1' in results, 'Not all handlers were fired')

        results = self.e.trigger('Root:A', *ARGS, **KWARGS)
        self.assertTrue('R' in results and 'R:A' in results, 'Not all handlers were fired')

        results = self.e.trigger('Root', *ARGS, **KWARGS)
        self.assertTrue('R' in results, "Root handler wasn't fired")

        results = self.e.trigger(['Root:A:1', 'Root:A', 'Root:A:2'], *ARGS, **KWARGS)
        self.assertEqual(len(results), 4, 'Not all handlers were fired')

        results = self.e.trigger('A:a:1:II', *ARGS, **KWARGS)
        self.assertListEqual(results, ['A:a:1:II', 'A:a'], 'Not all handlers were fired')


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






#
#
#
#        e.on('r:a:aa', lambda: 'r:a:aa')
#        e.on('r:b:bb', lambda: 'r:b:bb')
#        e.on('r:b', lambda: 'r:b')
#        e.on('r:a', lambda: 'r:a')
#        e.on('r', lambda: 'r')
#        e.on(['1:2:3:4:5', '~:~:3'], [lambda: 'x', lambda: 'y'])
#
#        print "e.trigger('r:a:aa')", e.trigger('r:a:aa')
#        print "e.trigger('r')", e.trigger('r')
#        print "e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'))
#        print "once: e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'), **e.options(unique_call=Events.TB_CALL_ONCE))
#        print "once, reversed: e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'),
#            **e.options(unique_call=Events.TB_CALL_ONCE, call_order=Events.CO_FROM_THE_END))
#        print "every, reversed: e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'),
#            **e.options(unique_call=Events.TB_CALL_EVERY, call_order=Events.CO_FROM_THE_END))
#        print "reversed: e.trigger('r:a:aa')", e.trigger('r:a:aa', **e.options(call_order=Events.CO_FROM_THE_END))
#
#        print 'r:*', e.trigger('r:*', **e.options(propagate=Events.ES_PROPAGATE_CURRENT))
#        print 'r:~', e.trigger('r:~')
#        print '*:b', e.trigger('*:b')
#        print '~:b', e.trigger('~:b')
#        print '~:a:~', e.trigger('~:a:~')
#
#        return e
