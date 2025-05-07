from celery import shared_task
from .models import ProgramWatcher
from django.utils.timezone import now



@shared_task
def say_hello():
    print('hello')
