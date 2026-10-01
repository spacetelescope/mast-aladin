"""
The `throttle` module makes use of the example snippets from the ipywidgets docs [1]_.

References
----------
.. [1] https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#throttling
"""

import asyncio
from time import time
from functools import wraps

__all__ = ['throttle']


class Timer:
    """
    Asynchronous timer to keep track of the time between successive
    calls to the same function, used in ``throttle``
    (`Source
    <https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#throttling>`_).
    """
    def __init__(self, timeout, callback):
        """
        Parameters
        ----------
        timeout : float
            Timeout duration [seconds].
        callback : function
            Callback to execute after ``timeout``.
        """
        self._timeout = timeout
        self._callback = callback

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._callback()

    def start(self):
        self._task = asyncio.ensure_future(self._job())

    def cancel(self):
        self._task.cancel()


def throttle(wait):
    """
    Decorator that prevents a function from being called
    more than once every wait period
    (`Source
    <https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#throttling>`_).

    Parameters
    ----------
    wait : float
        Repeated updates to the decorated function will be called at most
        once per ``wait`` seconds.
    """
    def decorator(fn):
        time_of_last_call = 0
        scheduled, timer = False, None
        new_args, new_kwargs = None, None

        @wraps(fn)
        def throttled(self, *args, **kwargs):
            nonlocal new_args, new_kwargs, time_of_last_call, scheduled, timer  # noqa: F824

            def call_it():
                nonlocal new_args, new_kwargs, time_of_last_call, scheduled, timer  # noqa: F824
                time_of_last_call = time()
                result = fn(self, *new_args, **new_kwargs)
                scheduled = False
                return result

            time_since_last_call = time() - time_of_last_call
            new_args, new_kwargs = args, kwargs
            if not scheduled:
                scheduled = True
                new_wait = max(0, wait - time_since_last_call)
                timer = Timer(new_wait, call_it)
                timer.start()
        return throttled
    return decorator
