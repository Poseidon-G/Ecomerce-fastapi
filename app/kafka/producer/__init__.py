from aiokafka import AIOKafkaProducer
import json
from app.core.config import settings

class KafkaProducer:
    def __init__(self):
        self.producer = None
    
    async def get_producer(self):
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
        return self.producer
    
    async def produce_message(self, topic: str, value: dict):
        producer = await self.get_producer()
        await producer.send_and_wait(topic, value)
    
    async def close(self):
        if self.producer:
            await self.producer.stop()

kafka_producer = KafkaProducer()