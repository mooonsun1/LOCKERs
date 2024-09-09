# Lockers/config/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django settings 모듈을 환경 변수로 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lockers.settings')

app = Celery('Lockers')

# Celery 설정을 Django 설정에서 가져옴
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django app에서 Celery task를 자동으로 검색하도록 설정
app.autodiscover_tasks()
