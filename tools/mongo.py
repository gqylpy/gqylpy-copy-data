import sys

from pymongo import MongoClient
from pymongo.database import Database

from . import over_func
from .dadclass import Dict


def __init__(config: Dict):
    init: Dict = config.mongo.pop('init', {})

    for name, conf in config.mongo.items():

        for item in init.items():
            conf.setdefault(item)

        client = MongoClient(**conf)

        over_func.add(client.close)

        setattr(sys.modules[__name__], name, client[name])


mon: Database
