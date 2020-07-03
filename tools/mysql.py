"""Ues pymysql, One library corresponds to one connection."""
import sys
import time
import pymysql
import threading

from pymysql import cursors
from pymysql.connections import Connection

from . import logger
from .dadclass import Dict

self = sys.modules[__name__]

__lock__ = threading.Lock()

__default__: Connection


def __init__(config: Dict):
    mysql: Dict = config.tools.mysql
    init: Dict = mysql.pop('init', {})
    conn_check_cycle: int = init.pop('connect_check_cycle', None)

    for name, conf in mysql.items():

        for item in init.items():
            conf.setdefault(*item)

        conn = Connection(**conf)

        setattr(self, name, conn)

        if not hasattr(self, '__default__'):
            setattr(self, '__default__', conn)

    if mysql:
        __health_examination__(conn_check_cycle)


def sql(sql: str, one: bool = False, datastyle=dict, conn: Connection = None):
    conn = conn or __default__
    cur = conn.cursor(Transaction._datastyle[datastyle])

    with __lock__:
        result: int = cur.execute(sql)
        conn.commit()

    # for action in ['INSERT', 'UPDATE', 'DELETE']:
    #     if sql[:6].upper().startswith(action):
    #         return result

    if not sql.lstrip()[:6].upper().startswith('SELECT'):
        return result

    queryset = cur.fetchall()

    if datastyle is dict:
        queryset = Transaction.__upgrade_datastyle__(None, queryset)

    cur.close()

    return queryset[0] if one else queryset


class Transaction:
    _datastyle = {
        tuple: cursors.Cursor,
        dict: cursors.DictCursor}

    def __init__(self, datastyle=dict, conn: Connection = None):
        self.conn = conn or __default__
        self.cur = self.conn.cursor(self._datastyle[datastyle])
        self.datastyle = datastyle

    def __call__(self, sql: str) -> int:
        return self.cur.execute(sql)

    def __enter__(self):
        self.__lock__.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            self.conn.rollback()
        self.conn.commit()
        self.__lock__.release()
        self.cur.close()

    def __getattribute__(self, name):
        try:
            result = super().__getattribute__(name)
        except AttributeError:
            result = getattr(self.cur, name)

        return result

    def __invert__(self):
        return self.fetchone

    def __upgrade_datastyle__(self, data: list = None) -> list:
        """dict -> Dict"""
        return list(map(lambda x: Dict(**x), data))

    @property
    def fetchone(self):
        queryset = self.cur.fetchone()

        if self.datastyle is tuple:
            return queryset

        return Dict(**queryset)

    @property
    def fetchall(self):
        queryset = self.cur.fetchall()

        if self.datastyle is tuple:
            return queryset

        return self.__upgrade_datastyle__(queryset)

    @property
    def last_insert_id(self) -> int:
        """
        Returns the id of the data
        that was last inserted by `self.conn`
        """
        self('SELECT LAST_INSERT_ID()')

        if self.datastyle is tuple:
            return self.fetchone[0]

        return self.fetchone['LAST_INSERT_ID()']


def __health_examination__(cycle: int = 60 * 10):
    """
    Open a thread, Periodically check the database link status,
    and if it is disconnected, it will restart the connection.
    """

    def __(conns: 'Not param' = []):
        # Fetch all connection.
        for name in sys.modules[__name__].__dir__():
            value = getattr(sys.modules[__name__], name)
            if name != 'default' and isinstance(value, Connection):
                conns.append(value)

        while True:
            time.sleep(cycle)
            for conn in conns:
                try:
                    conn.ping(reconnect=True)
                except pymysql.Error:
                    logger.warning('Ping MySQL error once.')

    threading.Thread(target=__, name='PingMySQL', daemon=True).start()
