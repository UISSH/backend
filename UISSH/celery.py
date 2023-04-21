from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UISSH.settings")

app = Celery("UISSH")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.update(
    CELERYBEAT_SCHEDULE={
        # 'delete_ofm_cron': {
        #     'task': 'file.tasks.delete_ofm_cron',
        #     'schedule': timedelta(days=1)
        # }
    }
)
