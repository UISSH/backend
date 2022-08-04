import os

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from base.utils.logger import plog
from website.applications.app_factory import AppFactory
from website.applications.core.dataclass import NewWebSiteConfig, WebServerTypeEnum
from website.models import Website
from website.models.utils import update_nginx_server_name, insert_section
from website.models.website import website_pre_save

"""
from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from  website.signals import website
"""


@receiver(pre_save, sender=Website)
def listener_pre_save(sender, instance: Website, **kwargs):
    # 保存之前修改相应的配置
    plog.debug("signal Website 'pre_save'")
    if not instance.id:
        plog.debug(f'create::{instance.name} {instance.domain}')

        if instance.index_root == "/var/www/html":
            plog.info(f"mkdir -p  /var/www/{instance.domain}")
            plog.info(f"chown www-data.www-data -R {instance.index_root}")
            instance.index_root = f"/var/www/{instance.domain}"

        else:
            plog.info(f"mkdir -p  {instance.index_root}")
            plog.info(f"chown www-data.www-data -R {instance.index_root}")

        try:
            os.system(f"mkdir -p  {instance.index_root}")
            os.system(f"chown www-data.www-data -R {instance.index_root}")
        except Exception as e:
            instance.save()
            plog.exception(f"create and chmod {instance.index_root} failed!")

        nginx_config_path = f'/etc/nginx/sites-available/{instance.domain}.conf'
        enable_nginx_config_path = f'/etc/nginx/sites-enabled/{instance.domain}.conf'
        os.system(f'touch {nginx_config_path}')

        plog.debug(instance.ssl_config)
        if instance.ssl_config['certbot']["provider"] is None:
            instance.ssl_config = {
                "certbot": {
                    "email": instance.user.email,
                    "provider": "default",
                },
                "path": {
                    "certificate": f"/etc/letsencrypt/live/{instance.domain}/fullchain.pem",
                    "key": f"/etc/letsencrypt/live/{instance.domain}/privkey.pem"
                },
                "method": "http-01"
            }
        plog.debug(instance.ssl_config)
        app_factory = AppFactory
        app_factory.load()
        config = instance.get_website_config()

        if instance.application is None:
            text = '与君初相识，犹如故人归。嗨，别来无恙！ <br> Hello World！'
            app = app_factory.get_application_module('NginxApplication', config,
                                                     {'name': 'New website',
                                                      "text": text})
            instance.application = 'NginxApplication'
        else:
            app = app_factory.get_application_module(instance.application, config, instance.application_config)

        res = app.create()
        if res.is_success():
            data = instance.get_nginx_config()
            insert_section(data, app.read(), 'app')
            with open(nginx_config_path, 'w') as f:
                f.write(data)
            os.system(f'ln -s {nginx_config_path} {enable_nginx_config_path}')
            res = os.system('nginx -t')
            if res != 0:
                os.system(f'rm {enable_nginx_config_path}')
            else:
                os.system('systemctl reload nginx')
                instance.valid_web_server_config = data
                instance.status = instance.StatusType.VALID
                instance.status_info = 'ok'
        else:
            raise RuntimeError(res.__str__())
    else:
        plog.debug(f'update::{instance.name} {instance.domain}')

    instance.ssl_config['path'] = {
        "certificate": f"/etc/letsencrypt/live/{instance.domain}/fullchain.pem",
        "key": f"/etc/letsencrypt/live/{instance.domain}/privkey.pem"
    }

    if instance.valid_web_server_config:
        # 更新 valid_web_server_config 中的 server_name 字段
        if instance.extra_domain is None:
            extra_domain = None
        else:
            extra_domain = instance.extra_domain.replace(",", " ").replace("\n", " ")
            print(extra_domain)
        instance.valid_web_server_config = update_nginx_server_name(instance.valid_web_server_config,
                                                                    instance.domain,
                                                                    extra_domain)
    website_pre_save(instance)


@receiver(pre_delete, sender=Website)
def listener_pre_delete(sender, instance: Website, **kwargs):
    plog.info(f"clear up {instance.domain} related resources.")

    def os_system_info(cmd):
        plog.info(cmd)
        os.system(cmd)

    # todo backup all data on before delete.
    if instance.application:
        app = instance.get_application_module(instance.get_website_config())
        app.stop()
        app.disable()
        app.delete()

    if instance.index_root.startswith('/var/www/'):
        os_system_info(f'rm -rf {instance.index_root}')

    # clean nginx config

    os_system_info(f'rm /etc/nginx/sites-available/{instance.domain}.conf')
    os_system_info(f'rm /etc/nginx/sites-available/{instance.domain}.conf')

    # reload nginx config
    os_system_info('systemctl reload nginx')
