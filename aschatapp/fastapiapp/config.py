import environ
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

CELERY_USERNAME = env.str("CELERY_USERNAME", default="guest")
CELERY_PASSWORD = env.str("CELERY_PASSWORD", default="guest")

SECRET_KEY = env.str("SECRET_KEY", default="change")

# External service URLs
DJANGO_API_URL = env.str("DJANGO_API_URL", default="http://django:8000/api/")
RABBITMQ_URL = env.str(
    "RABBITMQ_URL",
    default=f"amqp://{CELERY_USERNAME}:{CELERY_PASSWORD}@rabbitmq/",
)
