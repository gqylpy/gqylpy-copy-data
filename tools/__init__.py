import os
import sys
import hashlib
import subprocess
import collections

from . import log
from . import mongo
from . import kafka
from . import over_func

from .filetor import filetor
from .crypto import encrypt, decrypt
from .secure_shell import SecureShell
from .dadclass import Dict, SingletonMode
from .decorator import try_except, while_true
from .time_process import \
    gmt_stamp, local_stamp, \
    time2second, second2time, \
    stamp2struct, str2stamp, stamp2str


def __init__(config: Dict):
    for name in config:
        if name in globals() and hasattr(globals()[name], '__init__'):
            globals()[name].__init__(config)


def __init2__(basedir: str = None, script: bool = False, config: dict = None):
    """
    if script:
        You are running the script and can import configuration from `config`.
    else:
        This is a project package created using `yongkang`.
    """
    if not basedir and script:
        basedir = dirname(__file__)

    modules: dict = globals()
    cnf.path = Dict(root=basedir)

    for name in os.listdir(basedir):
        if not name.startswith('.'):
            cnf.path[name] = abspath(basedir, name)

    if script:
        cnf.update(Dict(config))
        if not cnf.path.__contains__('db'):
            cnf.path.db = cnf.path.root
        if not cnf.path.__contains__('log'):
            cnf.path.log = cnf.path.root
    else:
        for name in os.listdir(cnf.path.conf):
            if name not in ['__init__.py', '__pycache__']:
                cnf.update(Dict(filetor(
                    abspath(cnf.path.conf, name), type='yaml')))

    if abspath(sys.argv[0]) == cnf.path['go.py'] or script:
        pid_file = cnf.get('pidfile', 'pid')

        if not os.path.isabs(pid_file):
            pid_file: str = abspath(cnf.path.log, pid_file)

        save_pid(pid_file)

    for name in cnf:
        if modules.__contains__(name) and \
                hasattr(modules[name], '__init__'):
            modules[name].__init__(cnf)

    if cnf.__contains__('killed_alert'):
        over_func.add(
            func=aliyun.send_mail, sync=True,
            Subject="I'm terminated", TextBody=...)


def abspath(*a) -> str:
    """Return an absolute path"""
    return os.path.abspath(os.path.join(*a))


def dirname(path: str, level: int = 1) -> str:
    """Culling directories from the
    end according to `level`, usually
    used to get the project root path.
    """
    for n in range(level):
        path = os.path.dirname(os.path.abspath(path))
    return abspath(path)


def genpath(*a) -> str:
    """Generate path
    Generates a directory based on the passed in value,
    creates it if it does not exist, and returns it.
    """
    dir: str = abspath(*a)
    os.path.exists(dir) or os.makedirs(dir)
    return dir


def cmd(cmd: str) -> str:
    """
    if exec the cmd success:
        return result
    else:
        throw exception
    """
    status, output = subprocess.getstatusoutput(cmd)
    assert status == 0, f'{cmd}: {output}'
    return output


def save_pid(file: str):
    """Save the program id to file"""
    filetor(file, os.getpid())


def prt(*args, color: int = 31, font: int = 0,
        end: str = '\n', sep: str = ' ', file: open = None):
    """
    Custom Print Font and Color.

    Color:
        31-red 32-green 34-blue 37-Gray 38-black
    Font:
        0-normal 1-bold
    sep:
        string inserted between values, default a space.
    """
    print(
        f'\033[{font};{color};0m{sep.join(str(i) for i in args)}\033[0m',
        end=end, file=file)


class md5:
    def __new__(cls, data: str = None, *a, **kw):
        """Returns the encrypted string directly"""
        if data is None:
            return object.__new__(cls)

        m5 = cls(*a, **kw)
        m5.update(data)
        return m5.hexdigest

    def __init__(self, *a, **kw):
        self.m5 = hashlib.md5(*a, **kw)

    def update(self, data):
        if isinstance(data, str):
            data = data.encode('UTF-8')

        if not isinstance(data, (str, bytes)):
            data = str(data).encode('UTF-8')

        self.m5.update(data)

    def update_str(self, data: str):
        self.m5.update(data.encode('UTF-8'))

    @property
    def hexdigest(self) -> str:
        return self.m5.hexdigest()


class Response(Dict):
    """API Response"""

    def __init__(
            self, code: int = 200,
            data: dict = None,
            msg: str = 'ok'):
        self.code = code
        self.data = data or {}
        self.msg = msg


def dict_inter_process(data: dict, func=None) -> dict:
    """Dictionary internal processing
    Used to batch process values inside a dictionary.
    :param data: A dict.
    :param func: Your handler functions, ps:
        def func(name, value):
            if name == 'some value':
                return process(value)
    """
    def one(data: dict):
        for name, value in data.items():
            data[name] = two(name, value)

        return data

    def two(name=None, value={}):
        if isinstance(value, dict):
            return one(value)

        if isinstance(value, collections.Iterable) \
                and not isinstance(value, str):
            return [two(value=v) for v in value]

        value = func(name, value) or value

        return value

    return one(data)