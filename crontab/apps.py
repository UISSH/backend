import logging
import sys
from django.apps import AppConfig


class CrontabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "crontab"

    def ready(self) -> None:
        from .models import CrontabModel

        if "manage.py" in sys.argv and "runserver" not in sys.argv:
            return

        try:
            logging.debug("sync crontab job from system to database")
            CrontabModel.sync()
        except Exception as e:
            logging.error(e)
        return super().ready()
