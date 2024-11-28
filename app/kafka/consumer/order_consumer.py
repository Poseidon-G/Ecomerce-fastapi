from aiokafka import AIOKafkaConsumer
import json
import asyncio
from app.core.config import settings
from app.services.order.order_service import process_order

class KafkaConsumer:
    def __init__(self):
        self.consumer = None
    
    async def get_consumer(self, topic: str, group_id: str):
        self.consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        await self.consumer.start()
        return self.consumer
    
    async def consume_orders(self):
        consumer = await self.get_consumer(
            settings.KAFKA_ORDER_TOPIC, 
            settings.KAFKA_GROUP_ID
        )
        
        try:
            async for message in consumer:
                order_data = message.value
                await process_order(order_data)
        finally:
            await consumer.stop()

kafka_consumer = KafkaConsumer()