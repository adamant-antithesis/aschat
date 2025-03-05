import environ
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

CELERY_USERNAME = env.str("CELERY_USERNAME")
CELERY_PASSWORD = env.str("CELERY_PASSWORD")
