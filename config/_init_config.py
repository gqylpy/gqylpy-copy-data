import os
import re
import sys

from tools import Dict
from tools import dirname
from tools import filetor
from tools import abspath
from tools import time2second
from tools import dict_inter_process


class InitConfig(Dict):

    path: Dict
    base: Dict
    core: Dict
    tools: Dict

    base_cnf = {
        'coding': 'UTF-8',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }

    def __init__(self, module: 'A module' = None):
        self.path = Dict(root=dirname(__file__, level=2))

        self.fetch_all_abspath()

        self.load_config()

        self.tools.log.init.log_dir = self.path.log

        # Base config.
        self.base = Dict()
        self.base.update(self.base_cnf)
        self.base.title = os.path.basename(self.path.root)

        # Change unit time to second.
        dict_inter_process(self, lambda k, v: re.findall(
            r'^\d+[dhms]$', str(v)) and time2second(v))

        if module:
            for name, value in self.items():
                setattr(sys.modules[module], name, value)

    def __new__(cls, *a, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        return cls._instance

    def fetch_all_abspath(self):
        """Fetch all absolute paths under project root."""
        for name in os.listdir(self.path.root):
            if not name.startswith('.'):
                self.path[name] = abspath(self.path.root, name)

    def load_config(self):
        for name in os.listdir(self.path.config):
            if name.endswith('.yml') or name.endswith('.yaml'):
                config = Dict(filetor(abspath(self.path.config, name))) or Dict()
                config.path = self.path
                self[name.split('.')[0]] = config
