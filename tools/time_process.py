import re
import time


def gmt_stamp(multiply_by: int = 1) -> int:
    return int(time.mktime(time.gmtime())) * multiply_by


def local_stamp(multiply_by: int = 1) -> int:
    return int(time.time()) * multiply_by


def stamp2str(
        stamp: int or float = None,
        format: str = '%F %T',
        local: bool = False
) -> str:
    """timestamp to str time"""
    return time.strftime(format, stamp2struct(stamp, local))


def stamp2struct(
        stamp: int or float = None,
        local: bool = False
) -> time.struct_time:
    """timestamp to struct time"""
    if local:
        return time.localtime(stamp)

    return time.gmtime(stamp)


def str2stamp(
        string: str,
        format: str = '%Y-%m-%d %H:%M:%S'
) -> float:
    """str time to timestamp"""
    return time.mktime(time.strptime(string, format))


def time2second(unit_time: str, result: 'Not param' = 0) -> int:
    """Pass in a unit of time,
    which will return the time in seconds."""
    for val in re.findall(r'\d+[dhms]', unit_time.lower()):
        if val[-1] == 'd':
            result += 60 * 60 * 24 * int(val[:-1])
        if val[-1] == 'h':
            result += 60 * 60 * int(val[:-1])
        if val[-1] == 'm':
            result += 60 * int(val[:-1])
        if val[-1] == 's':
            result += int(val[:-1])

    return result


def second2time(sec: int or float, result: 'Not param' = '') -> str:
    """Pass in a time in seconds,
    and it will be converted to unit time."""
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d:
        result += f'{d}d'
    if h:
        result += f'{h}h'
    if m:
        result += f'{m}m'
    if s:
        result += f'{s}s'

    return result
