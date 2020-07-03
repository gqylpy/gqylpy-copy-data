import time
import functools

from . import kafka
from . import log


def try_except(except_type: type = Exception):
    """Generic for handling function exceptions"""
    def timer(fn):
        @functools.wraps(fn)
        def inner(*a, **kw):
            try:
                return fn(*a, **kw)
            except except_type as e:
                try:
                    log.error(f'{fn.__name__}.{type(e).__name__}: {e}')
                except Exception as e:
                    log.error(f'Handling exception error: {type(e).__name__}: {e}')

        return inner

    return timer


def while_true(cond=True, cycle: int = 0, before: bool = False):
    """
    The decorated function will loop forever.
    :param cond: Cyclic condition.
    :param cycle: Cycle interval.
    :param before: The interval is in front or behind.
    :return:
    """
    def timer(fn):
        @functools.wraps(fn)
        def inner(*a, **kw):
            while cond:
                before and time.sleep(cycle)
                ret = fn(*a, **kw)
                if ret == 'break':
                    break
                if ret == 'continue':
                    continue
                before or time.sleep(cycle)

        return inner

    return timer
