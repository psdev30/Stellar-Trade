#!/usr/bin/env python

from configparser import ConfigParser
from confluent_kafka import Consumer
from logger_setup import logger


class KafkaConsumer:
    def __init__(self, topic):
        self.logger = logger.get_logger()
        self.topic = topic
        self.consumer = None

    def create_consumer(self):
        config_parser = ConfigParser()
        config_parser.read_file('config.ini')
        config = dict(config_parser['default'])
        config.update(config_parser['consumer'])

        # Create Consumer instance
        self.consumer = Consumer(config)

        # Subscribe to topic
        topic = self.topic
        self.consumer.subscribe([topic])

    def consume_from_topic(self):
        # Poll for new messages from Kafka and print them.
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    # Initial message consumption may take up to
                    # `session.timeout.ms` for the consumer group to rebalance and start consuming
                    print("Waiting...")
                elif msg.error():
                    print("ERROR: %s".format(msg.error()))
                else:
                    # Extract the (optional) key and value, and print
                    print(
                        f"Consumed event from topic {msg.topic}: key = {msg.key().decode('utf-8')} value = {msg.value().decode('utf-8')}")
        except KeyboardInterrupt:
            pass
        finally:
            # Leave group and commit final offsets
            self.consumer.close()
