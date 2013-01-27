import unittest
from eevent import events


ARGS = (123, 'abc',)
KWARGS = {'arg': 'test'}


def func_factory(some_text):
    def func(*args, **kwargs):
        print(some_text, args, kwargs)
        return some_text
    return func


class BaseTestCase(unittest.TestCase):
    def __getattr__(self, item):
        new_name = item[0] + item.title().replace('_', '')[1:]
        if hasattr(self, new_name):
            return getattr(self, new_name)
        raise AttributeError

    def assert_list_set_equal(self, val1, val2, msg=None):
        self.assertSetEqual(set(val1), set(val2), msg)


class BasicTest(BaseTestCase):
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
        self.assert_equal(len(self.e), 7, "Seems, some events weren't registered")

    def test_trigger(self):
        results = self.e.trigger('my_event_name', *ARGS, **KWARGS)
        self.assert_list_set_equal(results, ['My Event Name'], 'No events were fired')

        results = self.e.trigger('A', *ARGS, **KWARGS)
        self.assert_list_set_equal(results, ['A', 'A+'], 'No events were fired')

        results = self.e.trigger('A B C'.split(), *ARGS, **KWARGS)
        self.assert_list_set_equal(results, ['A', 'A+', 'B', 'B+', 'C', 'C+'], 'No events were fired')

        results = self.e.trigger('F', *ARGS, **KWARGS)
        self.assert_list_set_equal(results, ['F1', 'F2', 'F3'], 'No events were fired')

        results = self.e.trigger('D', *ARGS, **KWARGS)
        self.assert_list_set_equal(results, ['X', 'X+'], 'No events were fired')

    def test_unbind_events(self):
        self.e.off('my_event_name')
        self.assert_false('my_event_name' in self.e, 'The event is still registered')
        results = self.e.trigger('my_event_name', *ARGS, **KWARGS)
        self.assert_false(results, 'The event is still registered')

        self.e.off(['A', 'B', 'C'])
        results = self.e.trigger(['A', 'B', 'C'], *ARGS, **KWARGS)
        self.assert_false(results, 'The events are still registered')

        self.e.off('F', self.func_2)
        self.assertTrue('F' in self.e, 'The F event must be registered, because it still has F1 and F3 handlers')
        results = self.e.trigger('F', *ARGS, **KWARGS)
        self.assert_false('F2' in results, 'The func_2 is still registered')

        self.e.off(['D', 'F'], [self.func_1, self.func_X])
        self.assertTrue('D' in self.e, 'The D event must be registered, because it still has X+ handler')
        self.assertTrue('F' in self.e, 'The F event must be registered, because it still has F3 handler')
        results = self.e.trigger(['D', 'F'], *ARGS, **KWARGS)
        self.assert_false('F1' in results or 'X' in results, 'The func_1 or func_X handlers are still registered')

        self.e.off('F', self.func_3)
        self.assert_false('F' in self.e, "The F event is still registered "
                                        "(must be deleted, because it doesn't have any handlers")
        results = self.e.trigger('F', *ARGS, **KWARGS)
        self.assert_false('F3' in results, 'The func_3 is still registered')

        self.e.off()
        self.assert_false(self.e, 'Some events are still registered. All events must be cleared.')


class HierarchyTest(BaseTestCase):
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
        self.assert_true('R' in results and 'R:A' in results and 'R:A:1' in results, 'Not all handlers were fired')

        results = self.e.trigger('Root:A', *ARGS, **KWARGS)
        self.assert_true('R' in results and 'R:A' in results, 'Not all handlers were fired')

        results = self.e.trigger('Root', *ARGS, **KWARGS)
        self.assert_true('R' in results, "Root handler wasn't fired")

        results = self.e.trigger(['Root:A:1', 'Root:A', 'Root:A:2'], *ARGS, **KWARGS)
        self.assert_equal(len(results), 4, 'Not all handlers were fired')

        results = self.e.trigger('A:a:1:II', *ARGS, **KWARGS)
        self.assert_list_set_equal(results, ['A:a:1:II', 'A:a'], 'Not all handlers were fired')


class WildCardTest(BaseTestCase):
    def setUp(self):
        self.e = events.Events()
        self.e.on('app:log', func_factory('app:log'))
        self.e.on('app:log:debug', func_factory('app:log:debug'))
        self.e.on('app:log:error', func_factory('app:log:error'))
        self.e.on('app:log:info', func_factory('app:log:info'))
        self.e.on('app:log:~', func_factory('app:log:~'))
        self.e.on('app:ui:content', func_factory('app:ui:content'))
        self.e.on('app:ui:*', func_factory('app:ui:*'))
        self.e.on('app:ui:footer:counter', func_factory('app:ui:footer:counter'))
        self.e.on('app:ui:header:counter', func_factory('app:ui:header:counter'))
        self.e.on('app:ui:~:counter', func_factory('app:ui:~:counter'))
        self.e.on('app:*', func_factory('app:*'))

    def test_trigger(self):
        results = self.e.trigger('app:log:info', 'fire log info')
        self.assert_list_set_equal(results, ['app:log:info', 'app:log', 'app:*', 'app:log:~'])

        results = self.e.trigger('app:log*', 'fire all log handlers')
        self.assert_equal(len(results), 6)

        results = self.e.trigger('app:~', 'fire all second level handlers')
        self.assert_list_set_equal(results, ['app:*', 'app:log'])

        results = self.e.trigger('*', 'fire all handlers')
        self.assert_equal(len(results), 11)

        results = self.e.trigger('*:counter', 'fire events with postfix ":counter"')
        self.assert_list_set_equal(results, ['app:*', 'app:ui:~:counter',
                                             'app:ui:footer:counter',
                                             'app:ui:header:counter'])


class PropagationTest(BaseTestCase):
    def setUp(self):
        self.e = events.Events()


class CallOrderTest(BaseTestCase):
    def setUp(self):
        self.e = events.Events()


class InvokeHandlersTest(BaseTestCase):
    def setUp(self):
        self.e = events.Events()


class OptionsTest(BaseTestCase):
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
