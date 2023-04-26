import traceback
import logging
from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "website"

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        try:
            from website.signals import website
        except:
            logging.error(traceback.format_exc())
