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

        results = self.e.trigger(['A', 'B', 'C'], *ARGS, **KWARGS)
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
        """
        r .- a - aa - aaa
          |   `- ab - aaa
          `- b - bb - bbb
        """
        self.e = events.Events()
        self.e.on('r:a:aa:aaa', func_factory('r:a:aa:aaa'))
        self.e.on('r:a:ab:aaa', func_factory('r:a:ab:aaa'))
        self.e.on('r:b:bb:bbb', func_factory('r:b:bb:bbb'))
        self.e.on('r:a:aa', func_factory('r:a:aa'))
        self.e.on('r:a', func_factory('r:a'))
        self.e.on('r:b', func_factory('r:b'))
        self.e.on('r', func_factory('r'))

        T = self.e.ES_PROPAGATE_TO_TOP
        C = self.e.ES_PROPAGATE_CURRENT
        D = self.e.ES_PROPAGATE_TO_DEEP
        self.opt_c = self.e.options(propagate=C)
        self.opt_t = self.e.options(propagate=T)
        self.opt_d = self.e.options(propagate=D)
        self.opt_ct = self.e.options(propagate=C | T)
        self.opt_cd = self.e.options(propagate=C | D)
        self.opt_td = self.e.options(propagate=T | D)
        self.opt_tcd = self.e.options(propagate=T | C | D)

    def test_default_current_top_propagation(self):
        results = self.e.trigger('r:a:aa', **self.opt_ct)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa'])

        results = self.e.trigger('r:a:aa:aaa', **self.opt_ct)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa', 'r:a:aa:aaa'])

        results = self.e.trigger('r:a', **self.opt_ct)
        self.assert_list_set_equal(results, ['r', 'r:a'])

        results = self.e.trigger('r', **self.opt_ct)
        self.assert_list_set_equal(results, ['r'])

    def test_current_deep_propagation(self):
        results = self.e.trigger('r:a:aa', **self.opt_cd)
        self.assert_list_set_equal(results, ['r:a:aa', 'r:a:aa:aaa'])

        results = self.e.trigger('r:a:aa:aaa', **self.opt_cd)
        self.assert_list_set_equal(results, ['r:a:aa:aaa'])

        results = self.e.trigger('r:a', **self.opt_cd)
        self.assert_list_set_equal(results, ['r:a', 'r:a:aa',
                                             'r:a:aa:aaa', 'r:a:ab:aaa'])

        results = self.e.trigger('r', **self.opt_cd)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:b', 'r:a:aa',
                                             'r:a:aa:aaa', 'r:a:ab:aaa',
                                             'r:b:bb:bbb'])

    def test_top_deep_propagation(self):
        results = self.e.trigger('r:a:aa', **self.opt_td)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa:aaa'])

        results = self.e.trigger('r:a:aa:aaa', **self.opt_td)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa'])

        results = self.e.trigger('r:a', **self.opt_td)
        self.assert_list_set_equal(results, ['r', 'r:a:aa',
                                             'r:a:aa:aaa', 'r:a:ab:aaa'])

        results = self.e.trigger('r', **self.opt_td)
        self.assert_list_set_equal(results, ['r:a', 'r:b', 'r:a:aa',
                                             'r:a:aa:aaa', 'r:a:ab:aaa',
                                             'r:b:bb:bbb'])

    def test_anyway_propagation(self):
        results = self.e.trigger('r:a:aa', **self.opt_tcd)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa', 'r:a:aa:aaa'])

        results = self.e.trigger('r:a:aa:aaa', **self.opt_tcd)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa', 'r:a:aa:aaa'])

        results = self.e.trigger('r:a', **self.opt_tcd)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa',
                                             'r:a:aa:aaa', 'r:a:ab:aaa'])

        results = self.e.trigger('r', **self.opt_tcd)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:b', 'r:a:aa',
                                             'r:a:aa:aaa', 'r:a:ab:aaa',
                                             'r:b:bb:bbb'])

    def test_current_propagation(self):
        results = self.e.trigger('r:a:aa', **self.opt_c)
        self.assert_equal(len(results), 1)

        results = self.e.trigger('r:a:ab:aaa', **self.opt_c)
        self.assert_equal(len(results), 1)

        results = self.e.trigger('r:b', **self.opt_c)
        self.assert_equal(len(results), 1)

        results = self.e.trigger('r:b:bb:bbb', **self.opt_c)
        self.assert_equal(len(results), 1)

        results = self.e.trigger('r', **self.opt_c)
        self.assert_equal(len(results), 1)

    def test_top_propagation(self):
        results = self.e.trigger('r:a:aa', **self.opt_t)
        self.assert_list_set_equal(results, ['r', 'r:a'])

        results = self.e.trigger('r:a:aa:aaa', **self.opt_t)
        self.assert_list_set_equal(results, ['r', 'r:a', 'r:a:aa'])

        results = self.e.trigger('r:b', **self.opt_t)
        self.assert_list_set_equal(results, ['r'])

        results = self.e.trigger('r:b:bb:bbb', **self.opt_t)
        self.assert_list_set_equal(results, ['r', 'r:b'])

        results = self.e.trigger('r', **self.opt_t)
        self.assert_list_set_equal(results, [])

    def test_deep_propagation(self):
        results = self.e.trigger('r:a:aa', **self.opt_d)
        self.assert_list_set_equal(results, ['r:a:aa:aaa'])

        results = self.e.trigger('r:a:aa:aaa', **self.opt_d)
        self.assert_list_set_equal(results, [])

        results = self.e.trigger('r:b', **self.opt_d)
        self.assert_list_set_equal(results, ['r:b:bb:bbb'])

        results = self.e.trigger('r', **self.opt_d)
        self.assert_list_set_equal(results, ['r:a', 'r:b', 'r:a:aa', 'r:a:aa:aaa', 'r:a:ab:aaa', 'r:b:bb:bbb'])


class CallOrderTest(BaseTestCase):
    def setUp(self):
        self.e = events.Events()


class InvokeHandlersTest(BaseTestCase):
    def setUp(self):
        self.e = events.Events()
        self.func = func_factory('shared func')
        self.e.on('A', self.func)
        self.e.on('B', self.func)
        self.e.on('C', self.func)
        self.e.on('D', self.func)

        self.e.on('r:a:aa', func_factory('r:a:aa'))
        self.e.on('r:b:bb', func_factory('r:b:bb'))
        self.e.on('r', func_factory('r'))

    def test_fire_once(self):
        results = self.e.trigger(
            ['A', 'B', 'C', 'D'],
            **self.e.options(unique_call=events.Events.TB_CALL_ONCE))
        self.assert_equals(len(results), 1)

    def test_fire_every(self):
        results = self.e.trigger(
            ['A', 'B', 'C', 'D'],
            **self.e.options(unique_call=events.Events.TB_CALL_EVERY))
        self.assert_equals(len(results), 4)

    def test_hierarchical_fire_once(self):
        results = self.e.trigger(
            ['r:a:aa', 'r:b:bb'],
            **self.e.options(unique_call=events.Events.TB_CALL_ONCE))
        self.assert_equals(results.count('r'), 1)

    def test_hierarchical_fire_every(self):
        results = self.e.trigger(
            ['r:a:aa', 'r:b:bb'],
            **self.e.options(unique_call=events.Events.TB_CALL_EVERY))
        self.assert_equals(results.count('r'), 2)


class OptionsTest(BaseTestCase):
    def setUp(self):
        self.e = events.Events()
