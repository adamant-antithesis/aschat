from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import Message, Chat
from datetime import datetime
import logging
import base64
from django.core.files.base import ContentFile


logger = logging.getLogger(__name__)


@shared_task
def save_message(chat_id, user_id, content, timestamp, image_data=None):
    try:
        chat = Chat.objects.get(id=chat_id)
        message = Message(
            chat=chat,
            user_id=user_id,
            content=content,
            created_at=datetime.fromisoformat(timestamp)
        )
        
        if image_data:
            logger.info(f"Processing image data for message in chat {chat_id}")
            try:

                if not image_data.startswith('data:image'):
                    logger.error("Invalid image data format")
                    return "Invalid image data format"

                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                
                if ext.lower() not in ['jpeg', 'jpg', 'png', 'gif']:
                    logger.error(f"Unsupported image format: {ext}")
                    return f"Unsupported image format: {ext}"

                filename = f'message_image_{chat_id}_{user_id}_{timestamp}.{ext}'
                
                image_file = ContentFile(base64.b64decode(imgstr), name=filename)
                message.image = image_file
                logger.info(f"Image will be saved as: {filename}")

            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return f"Error processing image: {str(e)}"

        message.save()
        logger.info(f"Message {message.id} saved successfully")
        
        response = {
            "message_id": message.id,
            "image_url": message.image.url if message.image else None
        }
        logger.info(f"Message response: {response}")
        return response
        
    except ObjectDoesNotExist:
        logger.error(f"Chat with ID {chat_id} not found")
        return f"Chat with ID {chat_id} not found"
    except Exception as e:
        logger.error(f"Unexpected error saving message: {str(e)}")
        return f"Error saving message: {str(e)}"
