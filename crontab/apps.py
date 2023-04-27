import logging
from django.apps import AppConfig


class CrontabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "crontab"

    def ready(self) -> None:
        from .models import CrontabModel

        try:
            logging.debug("sync crontab job from system to database")
            CrontabModel.sync()
        except Exception as e:
            logging.error(e)
        return super().ready()
