import signal
import atexit

from . import log

# The functions in this list will be
# executed at the end of the program.
__over_func__ = []


def add(func, *a, **kw):
    """Add a function that will execute
    after the main program is finished"""
    __over_func__.append((func, a, kw))


@atexit.register
def __exec__():
    """I will execute when the program exits normally (ps: exit(1))"""
    for func, a, kw in __over_func__:
        try:
            func(*a, **kw)
        except Exception as e:
            log.error(f'{func} error: {e}')


# Trigger '__exec__' function after being killed.
signal.signal(signal.SIGTERM, lambda signum, stack_frame: exit(1))
