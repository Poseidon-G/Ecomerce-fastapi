import asyncio
from typing import Union, Optional
from aiokafka import AIOKafkaProducer
from app.core.config import settings
import json

class KafkaProducer:
    def __init__(self, compression_type: str = 'gzip'):
        self.producer = None
        self.compression_type = compression_type
    
    async def get_producer(self):
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                compression_type=self.compression_type,
                # Batch settings
                batch_size=16384,  # 16KB batches
                linger_ms=100,     # Wait up to 100ms for batching
                # Buffer settings
                buffer_memory=33554432,  # 32MB buffer
                max_request_size=1048576 # 1MB max request
            )
            await self.producer.start()
        return self.producer
    
    async def produce_message(
        self, 
        topic: str, 
        value: Union[bytes, dict],
        key: Optional[bytes] = None
    ):
        producer = await self.get_producer()
        
        # Convert dict to binary if needed
        if isinstance(value, dict):
            value = json.dumps(value).encode('utf-8')
        
        # Send with batching enabled
        await producer.send_and_wait(
            topic=topic,
            value=value,
            key=key
        )
    
    async def produce_batch(
        self,
        topic: str,
        messages: list[Union[bytes, dict]]
    ):
        """Batch send multiple messages"""
        producer = await self.get_producer()
        
        # Convert messages to binary if needed
        binary_messages = [
            json.dumps(msg).encode('utf-8') if isinstance(msg, dict) else msg
            for msg in messages
        ]
        
        # Send all messages in batch
        await asyncio.gather(*[
            producer.send_and_wait(topic, msg)
            for msg in binary_messages
        ])
    
    async def close(self):
        if self.producer:
            await self.producer.stop()

# Global instance with gzip compression
kafka_producer = KafkaProducer(compression_type='gzip')