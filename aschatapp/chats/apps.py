from django.apps import AppConfig
import os


class ChatsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chats"

    def ready(self):
        media_root = os.environ.get('MEDIA_ROOT', '/app/media')
        chat_images_dir = os.path.join(media_root, 'chat_images')
        
        os.makedirs(chat_images_dir, exist_ok=True)
        
        try:
            os.chmod(media_root, 0o777)
            os.chmod(chat_images_dir, 0o777)
        except Exception as e:
            print(f"Warning: Could not set permissions for media directories: {e}")
