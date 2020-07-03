import sys

from influxdb import InfluxDBClient

from . import dadclass
from . import over_func
from .dadclass import Dict

self = sys.modules[__name__]

__default__: InfluxDBClient


def __init__(config: Dict):
    influx: Dict = config.tools.influx
    init: Dict = influx.pop('init', {})

    for name, conf in influx.items():

        for item in init.items():
            conf.setdefault(*item)

        client = InfluxDBClient(**conf)

        over_func.add(client.close)

        setattr(self, name, client)

        if not hasattr(self, '__default__'):
            setattr(self, '__default__', client)


def query(
        sql: str,
        one: bool = False,
        epoch: str = None,
        datastyle: 'enum(dict, list)' = dict,
        client: InfluxDBClient = None,
        *a, **kw) -> list or dict:
    """
    Encapsulate the 'InfluxDBClient.query' method.

    Help:
        Turn off the highlighting of the PyCharm SQL
        statement: `File -> Editor -> Inspections -> SQL`

    :param one: Returns a piece of data.
    :param epoch: The time format.
    :param datastyle: The data type returned, dict or str
    :param client: Specified database, the default is `__default__`.
    """
    queryset = (client or __default__).query(sql, epoch=epoch, *a, **kw)

    if not queryset:
        return Dict() if datastyle is dict and one else []

    if datastyle is dict:
        data = []
        for value in queryset.raw['series'][0]['values']:
            one_data = dadclass.Dict()
            for i in range(len(value)):
                one_data[queryset.raw['series'][0]['columns'][i]] = value[i]
            data.append(one_data)
    else:
        data = queryset.raw['series'][0]['values']

    return data[0] if one else data


def write_points(data: list, client: InfluxDBClient = None, *a, **kw):
    """Encapsulate the 'InfluxDBClient.write_points' method"""
    return (client or __default__).write_points(data, *a, **kw)
