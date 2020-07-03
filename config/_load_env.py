import os


class LoadEnv:
    """Load the environment variables and
    configure them into the object `InitConfig`."""

    def __init__(self, config, *envs):
        self.config = config

        for name in envs:
            if name in os.environ:
                try:
                    getattr(self, f'config_{name.lower()}')(
                        os.environ[name])
                except KeyError:
                    pass

    def config_influxdb(self, name: str):
        host, port = name.split(':')
        self.config.tools.influx.mon.host = host
        self.config.tools.influx.mon.port = int(port)

    def config_mongodb(self, name: str):
        host, port = name.split(':')
        self.config.tools.mongo.mon.host = host
        self.config.tools.mongo.mon.port = int(port)

    def config_mysql(self, name: str):
        host, port = name.split(':')
        self.config.tools.mysql.mon.host = host
        self.config.tools.mysql.mon.port = port

    def config_kafka(self, name: str):
        self.config.tools.kafka.metrics.hosts = os.environ[name]
