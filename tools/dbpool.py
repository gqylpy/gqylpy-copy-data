"""Database Connection Pool
Secondary encapsulation of `DBUtils`.

:param: creator
    使用连接数据库的膜拜

:param: mincached
    初始化时，连接池中至少创建的空闲的连接，0表示不创建

:param: maxcached
    连接池中最多闲置的连接，0和None表示不限制

:param: maxshared
    连接池中最多共享的连接数量，0和None表示全部共享（这个参数不管指定多少，最后都会是0）
    因为pymysql和MySQLdb等模块的threadsafety都为1，
    所以值无论设置为多少，_maxshared永远为0，所以永远是所有连接都共享

:param: maxconnections
    连接池允许的最大连接数，0和None表示不限制连接数

:param: blocking
    连接池中如果没有可用连接后，是否阻塞等待，True:等待 False:不等待，直接报错

:param: maxusage
    一个连接最多可被使用的次数，None表示无限制

:param: setsession
    开始会话前执行的命令列表，如: ['set datastyle to ...', 'set time zone ...']

:param: ping
    Ping MySQL服务端，检查服务是否可用
    0: 从来没有  1: 从池中提取时（默认） 2: 创建游标时  4: 执行查询时  7: 总是

:param: *args **kwargs
    数据库膜拜参数

关于数据库连接池大小的疑问:

公理：你需要一个小的连接池，和一个充满了等待连接的线程队列。

如果你有10000个并发用户，设置一个10000的连接池基本等于失了智。1000仍然很恐怖。即是100也太多了。
你需要一个10来个连接的小连接池，然后让剩下的业务线程都在队列里等待。

连接池中的连接数量应该等于你的数据库能够有效同时进行的查询任务数（通常不会高于2*CPU核心数）。

我们经常见到一些小规模的web应用，应付着大约十来个的并发用户，
却使用着一个100连接数的连接池。这会对你的数据库造成极其不必要的负担。
"""
import sys

from DBUtils.PooledDB import PooledDB

from .dadclass import Dict
from .mysql import Transaction

self = sys.modules[__name__]

__default__: PooledDB


def __init__(config: Dict):
    dbpool: Dict = config.tools.dbpool
    init: Dict = dbpool.pop('init', {})

    for name, conf in dbpool.items():
        conf.creator = sys.modules[conf.creator]

        for item in init.items():
            conf.setdefault(*item)

        pool = PooledDB(**conf)

        setattr(self, name, pool)

        if not hasattr(self, '__default__'):
            setattr(self, '__default__', pool)


class mysql(Transaction):

    def __new__(
            cls, sql: str = None, one: bool = False,
            datastyle=dict, pool: PooledDB = None):
        """Is execute sql"""
        if sql is None or isinstance(sql, PooledDB):
            return object.__new__(cls)

        pool = pool or __default__

        conn = pool.connection()
        cur = conn.cursor(cls._datastyle[datastyle])

        result: int = cur.execute(sql)

        conn.commit()
        # You should execute the `conn.commit()`,
        # even if the SQL is `select ...`,
        # otherwise this connection will not be able to
        # query the data written by other connections.

        if not sql.lstrip()[:6].upper().startswith('SELECT'):
            return result

        queryset = cur.fetchall()

        if datastyle is dict:
            queryset = cls.__upgrade_datastyle__(cls, queryset)

        cur.close()

        conn.close()
        # This is not to close the connection, but to
        # return the connection to the connection pool.

        return queryset[0] if one else queryset

    def __init__(
            self, sql=None,
            one: bool = False,
            datastyle=dict,
            pool: PooledDB = None):
        pool = sql or pool or __default__

        self.conn = pool.connection()
        self.cur = self.conn.cursor(self._datastyle[datastyle])
        self.datastyle = datastyle

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            self.conn.rollback()
        self.conn.commit()
        self.cur.close()
        self.conn.close()
