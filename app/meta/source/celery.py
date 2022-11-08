import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'source.settings')

app = Celery('source')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    # PROD:
    'check-deposit-every-day': {
        'task': 'deposit.check',
        'schedule': crontab(hour=0, minute=0),
    },
    'pay-deposit-every-week': {
        'task': 'deposit.pay',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),
    },

    # TEST:
    # 'check-deposit-every-day': {
    #     'task': 'deposit.check',
    #     'schedule': crontab(minute='*/1'),
    # },
    # 'pay-deposit-every-week': {
    #     'task': 'deposit.pay',
    #     'schedule': crontab(minute='*/1'),
    # },
}
app.conf.timezone = 'UTC'