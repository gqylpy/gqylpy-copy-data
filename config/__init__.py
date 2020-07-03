import sys

from ._load_env import LoadEnv
from ._init_config import InitConfig

from tools import log
from tools import Dict
from tools import abspath
from tools import save_pid
from tools import over_func
from tools import __init__ as init_tools

cnf: Dict
base: Dict
path: Dict
core: Dict
tools: Dict

cnf = InitConfig(module=__name__)
init_tools(tools)

if abspath(sys.argv[0]) == cnf.path['go.py']:
    save_pid(abspath(cnf.path.log, cnf.base.get('pidfile', 'pid')))
    over_func.add(log.logger.info, 'over')
    log.logger.info('start')
