import aio_pika
import json
import logging
from datetime import datetime
from ..config import CELERY_PASSWORD, CELERY_USERNAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_message_to_rabbitmq(chat_id: str, user_id: int, content: str, image_data: str = None, audio_data: str = None):

    connection = await aio_pika.connect_robust(f"amqp://{CELERY_USERNAME}:{CELERY_PASSWORD}@rabbitmq/")
    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue('messages_queue', durable=True)

        message_data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "image_data": image_data,
            "audio_data": audio_data
        }

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message_data).encode()),
            routing_key=queue.name
        )
        logger.info(f"Message sent to RabbitMQ: {message_data}")
