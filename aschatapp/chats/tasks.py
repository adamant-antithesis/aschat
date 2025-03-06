from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import Message, Chat
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


@shared_task
def save_message(chat_id, user_id, content, timestamp):
    try:
        chat = Chat.objects.get(id=chat_id)
        message = Message.objects.create(
            chat=chat,
            user_id=user_id,
            content=content,
            created_at=datetime.fromisoformat(timestamp)
        )
        logger.info(f"Message {message.id} saved successfully")
        return f"Message {message.id} saved"
    except ObjectDoesNotExist:
        logger.error(f"Chat with ID {chat_id} not found")
        return f"Chat with ID {chat_id} not found"
