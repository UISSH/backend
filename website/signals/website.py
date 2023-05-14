import logging
import os
import time

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from website.models import WebsiteModel

"""
from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from  website.signals import website
"""


@receiver(pre_delete, sender=WebsiteModel)
def listener_pre_delete(sender, instance: WebsiteModel, **kwargs):
    logging.info(f"clear up {instance.domain} related resources.")

    def os_system_info(cmd):
        logging.info(cmd)
        os.system(cmd)

    # TODO backup all data on before delete.
    if instance.application:
        app = instance.get_application_module(instance.get_app_website_config())
        app.stop()
        app.delete()

    if instance.index_root.startswith("/var/www/"):
        os.system(
            f"mv {instance.index_root} /tmp/{instance.index_root}{time.time()}.deleted"
        )

    # clean nginx config

    os_system_info(f"rm /etc/nginx/sites-available/{instance.domain}.conf")
    os_system_info(f"rm /etc/nginx/sites-enabled/{instance.domain}.conf")

    # reload nginx config
    os_system_info("systemctl reload nginx")
