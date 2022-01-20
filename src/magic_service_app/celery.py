import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magic_service_app.settings')

app = Celery('magic_service_app')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
