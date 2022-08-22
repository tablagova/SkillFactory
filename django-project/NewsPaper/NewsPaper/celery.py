import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'weekly_review': {
        'task': 'news.tasks.weekly_mail',
        'schedule': crontab(hour=11, minute=00, day_of_week='monday'),
    },
}
