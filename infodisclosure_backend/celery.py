# infodisclosure_backend/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'infodisclosure_backend.settings')

app = Celery('infodisclosure_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['public_watchers' , 'private_watchers'])

