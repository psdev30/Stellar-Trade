#!/usr/bin/env python

from configparser import ConfigParser
from confluent_kafka import Producer
from resources.logger_setup import logger


class KafkaProducer():
    def __init__(self, topic):
        self.topic = topic
        self.logger = logger.get_logger()
        self.producer = None

    def create_producer(self):
        # Parse the configuration.
        config_parser = ConfigParser()
        config_parser.read_file('config.ini')
        config = dict(config_parser['default'])

        # Create Producer instance
        self.producer = Producer(config)

        # Optional per-message delivery callback (triggered by poll() or flush())
        # when a message has been successfully delivered or permanently
        # failed delivery (after retries).

    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

    def publish_to_topic(self, ticker, data):
        self.producer.produce(self.topic, key=ticker, value=data, callback=self.delivery_callback)
        # Block until the messages are sent.
        self.producer.poll(10000)
        self.producer.flush()
