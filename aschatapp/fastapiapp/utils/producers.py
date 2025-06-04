import aio_pika
import json
from datetime import datetime

from ..config import RABBITMQ_URL
from .logging_config import get_logger

logger = get_logger(__name__)

_connection = None
_channel = None
_queue = None


async def _get_channel():
    """Get or create a RabbitMQ channel and queue."""
    global _connection, _channel, _queue
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(RABBITMQ_URL)
        _channel = await _connection.channel()
        _queue = await _channel.declare_queue("messages_queue", durable=True)
    return _channel, _queue


async def send_message_to_rabbitmq(
    chat_id: str,
    user_id: int,
    content: str,
    image_data: str | None = None,
    audio_data: str | None = None,
):
    """Publish a message to RabbitMQ using a persistent connection."""

    channel, queue = await _get_channel()

    message_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "image_data": image_data,
        "audio_data": audio_data,
    }

    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(message_data).encode()),
        routing_key=queue.name,
    )
    logger.info(f"Message sent to RabbitMQ: {message_data}")
