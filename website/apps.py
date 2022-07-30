import traceback

from django.apps import AppConfig
from loguru import logger


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        try:
            from website.signals import website
        except:
            logger.log("ERROR", traceback.format_exc())
