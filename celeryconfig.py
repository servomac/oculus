from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'memory': {
        'task': 'tasks.poll',
        'schedule': crontab(minute='*/1'),
        'args': ('mem',),
    },
    'cpu': {
        'task': 'tasks.poll',
        'schedule': crontab(minute='*/1'),
        'args': ('cpu',),
    },
    'network': {
        'task': 'tasks.poll',
        'schedule': crontab(minute='*/1'),
        'args': ('net',),
    },
}

# Change this to your settings
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
