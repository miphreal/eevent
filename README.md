# Intro

[eevent](https://github.com/miphreal/eevent/tree/master/eevent) allows to organize events hierarchically and provides a simple interface to fire custom events synchronously.

*like*
```
#!python
>>> e = Events()
>>> e.on('r:a:aa', lambda: 'aa')
>>> e.on('r:b:bb', lambda: 'bb')
>>> e.on('r:a', lambda: 'a')
>>> e.on('r:b', lambda: 'b')
>>> e.on('r', lambda: 'r')
>>> e.trigger('r:a:aa')
['r', 'a', 'aa']
>>> e.trigger('r')
['r']
>>> e.off('r:a')
>>> e.trigger('r:a:aa')
['r', 'aa']
>>> e.trigger('r:*', **e.options(propagate=e.ES_PROPAGATE_CURRENT))
['r:a', 'r:a:aa', 'r:b', 'r:b:bb']
```

More samples you can find in the [tests](https://github.com/miphreal/eevent/tree/master/tests).

Another place to find out more is [here](https://readthedocs.org/docs/eevent/en/latest/).
