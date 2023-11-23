from confluent_kafka import Producer, Consumer
from kafka_consumer import KafkaConsumer
from kafka_producer import KafkaProducer


class KafkaClient:
    def __init__(self):
        self.producer = KafkaProducer.create_producer()
        self.consumer = KafkaConsumer.create_consumer()

    def consume_from_topic(self, topic):
        return self.consumer.consume_from_topic(topic=topic)

    def publish_to_topic(self, topic):
        return self.producer.publish_to_topic(topic=topic)
