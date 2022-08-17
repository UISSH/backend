import os
import pathlib

from rest_framework import serializers

from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from base.utils.format import format_completed_process
from base.utils.logger import plog
from website.applications.app_factory import AppFactory
from website.models import Website
from website.models.utils import insert_section, get_section, update_nginx_server_name


class SSLConfigSerializer(ICBaseSerializer):
    class CertbotSerializer(ICBaseSerializer):
        email = serializers.EmailField(required=False, allow_null=True, help_text='defaults to current user.')
        provider = serializers.CharField(default='letsencrypt', allow_null=True)

    class PathSerializer(ICBaseSerializer):
        certificate = serializers.CharField(required=False, allow_null=True,
                                            help_text='specify the path to save the certificate.')
        key = serializers.CharField(required=False, allow_null=True, help_text='specify the path to save the key.')

    certbot = CertbotSerializer(required=False, allow_null=True, )
    path = PathSerializer(required=False, allow_null=True, )
    method = serializers.CharField(default='http-01')


class WebsiteDomainConfigSerializer(ICBaseSerializer):
    domain = serializers.CharField(max_length=512)
    extra_domain = serializers.CharField(max_length=10240, allow_null=True)

    def update(self, instance: Website, validated_data):
        domain = validated_data.get('domain')
        extra_domain = validated_data.get('extra_domain')


        if domain and domain != instance.domain:
            os.system(f"rm -rf  /etc/nginx/sites-enabled/{instance.domain}.conf")
            os.system(f"rm -rf  /etc/nginx/sites-available/{instance.domain}.conf")
            instance.ssl_enable = False
            instance.domain = domain

        if extra_domain and extra_domain != instance.extra_domain:
            instance.ssl_enable = False
            instance.extra_domain = extra_domain
            extra_domain = instance.extra_domain.replace(",", " ").replace("\n", " ")

            instance.valid_web_server_config = update_nginx_server_name(instance.valid_web_server_config,
                                                                        instance.domain,
                                                                        extra_domain)

        available_nginx_config = f"/etc/nginx/sites-available/{instance.domain}.conf"
        enabled_nginx_config = f"/etc/nginx/sites-enabled/{instance.domain}.conf"

        with open(available_nginx_config, "w") as f:
            f.write(instance.valid_web_server_config)

        if not pathlib.Path(enabled_nginx_config).exists():
            os.system(f'ln -s {available_nginx_config} {enabled_nginx_config}')

        os.system('systemctl reload nginx')

        instance.save()
        return validated_data

    def validate_extra_domain(self, val: str):
        if val:
            val = val.replace("\n", " ").replace("\t", " ")
            val = val.replace("  ", " ").replace("  ", " ").replace(" ", ",")
        return val


class WebsiteConfigSerializer(ICBaseSerializer):
    web_server_config = serializers.CharField(max_length=204800)

    def update(self, instance: Website, validated_data):
        web_server_config = validated_data.get("web_server_config")
        app = instance.get_application_module(instance.get_app_new_website_config())

        data = instance.get_nginx_config()
        user_config = get_section(web_server_config, 'user')
        data = insert_section(data, user_config, 'user')
        data = insert_section(data, app.read(), 'app')

        instance.valid_web_server_config = data
        r = instance.is_valid_configuration_001()
        if r.returncode != 0:
            raise serializers.ValidationError(
                {'web_server_config': 'Invalid configuration 001:' + format_completed_process(r)})
        else:
            if instance.is_valid_configuration_002(instance.valid_web_server_config):
                instance.save()
            else:
                raise serializers.ValidationError(
                    {'web_server_config': 'Invalid configuration 002:' + format_completed_process(r)})
            return instance.valid_web_server_config


class WebsiteModelSerializer(ICBaseModelSerializer):
    ssl_config = SSLConfigSerializer(required=False)
    # ssl_config = serializers.SerializerMethodField('_ssl_config')
    database_id = serializers.SerializerMethodField()
    database_name = serializers.SerializerMethodField()
    web_server_type_text = serializers.SerializerMethodField('_web_server_type_text')
    status_text = serializers.SerializerMethodField('_status_text')

    class Meta:
        model = Website
        fields = '__all__'

    def create(self, validated_data):
        instance: Website = super(WebsiteModelSerializer, self).create(validated_data)

        # 1.Create folder and file
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
            plog.exception(f"create and chmod {instance.index_root} failed!")
        nginx_config_path = f'/etc/nginx/sites-available/{instance.domain}.conf'
        os.system(f'touch {nginx_config_path}')

        # 2.Init SSL config
        instance.or_create_ssl_config()

        # 3.Reset created instance 'ssl_enable',
        # enable website ssl: post website/{instance_pk}/enable_ssl/
        # disable website ssl: post website/{instance_pk}/disable_ssl/
        instance.ssl_enable = False

        # 4.Write web server config

        app_factory = AppFactory
        app_factory.load()

        if instance.application is None:
            text = '与君初相识，犹如故人归。嗨，别来无恙！ <br> Hello World！'
            app = app_factory.get_application_module('NginxApplication',
                                                     instance.get_app_new_website_config(),
                                                     {'name': 'New website', "text": text})
            instance.application = 'NginxApplication'
        else:
            app = app_factory.get_application_module(instance.application,
                                                     instance.get_app_new_website_config(),
                                                     instance.application_config)

        web_server_config = instance.get_nginx_config()
        web_server_config = insert_section(web_server_config, app.read(), 'app')
        old_config = instance.valid_web_server_config
        instance.valid_web_server_config = web_server_config

        if instance.is_valid_configuration_001().returncode == 0:

            if instance.is_valid_configuration_002(web_server_config):
                os.system('systemctl reload nginx')
                instance.status = instance.StatusType.VALID
                instance.status_info = 'ok'
            else:
                instance.status = instance.StatusType.ERROR
                instance.status_info = '002:nginx configuration error.r'

        else:
            instance.valid_web_server_config = old_config
            instance.status = instance.StatusType.ERROR
            instance.status_info = '001:nginx configuration error.'

        if instance.extra_domain is None:
            extra_domain = None
        else:
            extra_domain = instance.extra_domain.replace(",", " ").replace("\n", " ")

        instance.valid_web_server_config = update_nginx_server_name(instance.valid_web_server_config,
                                                                    instance.domain,
                                                                    extra_domain)

        # 5.Create application instance
        # post application/{instance_pk}/app_create/

        instance.save()
        return instance

    def update(self, instance, validated_data):

        return super(WebsiteModelSerializer, self).update(instance, validated_data)

    def _ssl_config(self, obj: Website) -> SSLConfigSerializer:
        return SSLConfigSerializer(obj.ssl_config)

    def get_database_id(self, obj: Website):

        if hasattr(obj, "database"):
            return obj.database.id

    def _web_server_type_text(self, obj: Website):
        return obj.get_web_server_type_display()

    def _status_text(self, obj: Website):
        return obj.get_status_display()

    def get_database_name(self, obj: Website):

        if hasattr(obj, "database"):
            return obj.database.name

    def validate(self, data):

        return data
