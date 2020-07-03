"""Secondary encapsulation of `logging`"""
import os
import sys
import logging

from .dadclass import Dict
from .time_process import stamp2str

self = sys.modules[__name__]

__default__: logging.getLogger


def __init__(config: Dict):
    init: Dict = config.log.pop('init', {})
    log_dir: str = init.pop('log_dir')

    for name, conf in config.log.items():

        for item in init.items():
            conf.setdefault(*item)

        # Confirm log file path.
        if not os.path.isabs(conf.handler):
            conf.handler = os.path.join(log_dir, conf.handler)

        file_handler = logging.FileHandler(conf.handler, encoding='UTF-8')
        file_handler.setFormatter(logging.Formatter(conf.logfmt, conf.datefmt))

        log = logging.getLogger(name)
        log.addHandler(file_handler)
        log.setLevel(conf.level)

        # Create pointer in self module.
        setattr(self, name, log)

        # Set the default logger handler.
        if not hasattr(self, '__default__'):
            setattr(self, '__default__', log)


def __exec__(msg, method: str, logger: logging.getLogger = None):
    # Do something.
    # current_time: str = stamp2str(format='[%d/%b/%y:%H:%M:%S %z]', local=True)
    if hasattr(self, '__default__'):
        getattr(logger or __default__, method)(msg)
    else:
        print(f'[{stamp2str(local=True)}] {method}: {msg}')
    # Do something too.


# 10
def debug(msg, logger: logging.getLogger = None):
    __exec__(msg, 'debug', logger)


# 20
def info(msg, logger: logging.getLogger = None):
    __exec__(msg, 'info', logger)


# 30
def warning(msg, logger: logging.getLogger = None):
    __exec__(msg, 'warning', logger)


# 40
def error(msg, logger: logging.getLogger = None):
    __exec__(msg, 'error', logger)


# 50
def critical(msg, logger: logging.getLogger = None):
    __exec__(msg, 'critical', logger)


fatal = critical
warn = warning

logger: logging.getLogger
