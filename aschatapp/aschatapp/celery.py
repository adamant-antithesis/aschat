from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aschatapp.settings')

app = Celery('aschatapp')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(['chats'])


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


logger = logging.getLogger(__name__)
logger.info('Celery app configured')
