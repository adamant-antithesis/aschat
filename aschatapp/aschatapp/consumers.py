import aio_pika
import json
import asyncio
import logging
from .celery import app
from pathlib import Path
import os
import environ


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

CELERY_USERNAME = env("CELERY_USERNAME")
CELERY_PASSWORD = env("CELERY_PASSWORD")


async def callback(message: aio_pika.IncomingMessage):
    try:
        message_data = json.loads(message.body)
        chat_id = message_data['chat_id']
        user_id = message_data['user_id']
        content = message_data['content']
        timestamp = message_data['timestamp']
        image_data = message_data.get('image_data')
        audio_data = message_data.get('audio_data')

        result = app.send_task(
            "chats.tasks.save_message",
            args=[chat_id, user_id, content, timestamp, image_data, audio_data]
        )

        logger.info(f"Message saving result: {result.result}")

        await message.ack()
        logger.info(f"Message with chat_id {chat_id} successfully acknowledged.")

    except Exception as e:
        logger.error(f"Error processing message: {e}")


async def start_rabbitmq_consumer():
    try:
        logger.info(f"Connecting to RabbitMQ at amqp://{CELERY_USERNAME}:****@rabbitmq/")
        connection = await aio_pika.connect_robust(f"amqp://{CELERY_USERNAME}:{CELERY_PASSWORD}@rabbitmq/")
        async with connection:
            channel = await connection.channel()

            queue = await channel.declare_queue("messages_queue", durable=True)
            logger.info("Queue 'messages_queue' declared.")

            await queue.consume(callback, no_ack=False)
            logger.info("Waiting for messages. To exit press CTRL+C")

            await asyncio.Future()

    except Exception as e:
        logger.error(f"Error connecting to RabbitMQ or starting consumer: {e}")
        raise


if __name__ == '__main__':
    logger.info("Starting RabbitMQ consumer...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_rabbitmq_consumer())
