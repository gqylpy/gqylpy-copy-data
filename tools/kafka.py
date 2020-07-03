import sys
import json
import copy

from pykafka import KafkaClient
from pykafka.topic import Topic
from pykafka.producer import Producer

from . import log
from . import over_func
from .dadclass import Dict
from .time_process import local_stamp

self = sys.modules[__name__]

__default__: KafkaClient


def __init__(config: Dict):
    init: Dict = config.kafka.pop('init', {})

    for name, conf in config.kafka.items():
        data_template: Dict = conf.pop('data_template', None)
        default_topic: str = conf.pop('default_topic', None)

        for item in init.items():
            conf.setdefault(*item)

        client = KafkaClient(**conf)
        client.data_template = data_template
        client.default_topic = client.topics[default_topic]
        client.default_producer = client.default_topic.get_producer()  # delivery_reports=True
        client.default_sync_producer = client.default_topic.get_sync_producer()

        # over_func.add(client.default_producer.stop)
        # over_func.add(client.default_sync_producer.stop)

        setattr(self, name, client)

        if not hasattr(self, '__default__'):
            setattr(self, '__default__', client)


def __get_producer__(client: KafkaClient, topic: str, sync: bool) -> Producer:
    topic: Topic = client.topics.get(topic)

    if topic and topic is not client.default_topic:
        # Get a new producer.
        if sync:
            producer: Producer = topic.get_sync_producer()
        else:
            producer: Producer = topic.get_producer()
        # over_func.add(producer.stop)
    else:
        # Get the default producer.
        if sync:
            producer: Producer = client.default_sync_producer
        else:
            producer: Producer = client.default_producer

    return producer


def pro(msg: dict, client: KafkaClient = None, topic: str = None, sync: bool = False):
    # Filtered the error, too often and non code errors.
    if msg['event_type'] == 'InfluxDBServerError':
        return

    client = client or __default__
    producer: Producer = __get_producer__(client, topic, sync)

    # Encapsulate data.
    data: Dict = copy.deepcopy(client.data_template)
    data.creation_time = local_stamp()
    data.metric.timestamp = data.creation_time * 1000
    data.metric.name = msg.pop('name', 'Unknown')
    data.metric.dimensions.update(msg)

    # Send data.
    producer.produce(json.dumps(data).encode())

    log.info(f'Producer: {dict(name=data.metric.name, **msg)}')
