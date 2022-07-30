from rest_framework import serializers

from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from website.models import Website


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


class WebsiteModelSerializer(ICBaseModelSerializer):
    ssl_config = SSLConfigSerializer(required=False)
    # ssl_config = serializers.SerializerMethodField('_ssl_config')
    database_id = serializers.SerializerMethodField()
    database_name = serializers.SerializerMethodField()
    web_server_type_text = serializers.SerializerMethodField('_web_server_type_text')

    class Meta:
        model = Website
        fields = '__all__'

    def _ssl_config(self, obj: Website) -> SSLConfigSerializer:
        return SSLConfigSerializer(obj.ssl_config)

    def get_database_id(self, obj: Website):

        if hasattr(obj, "database"):
            return obj.database.id

    def _web_server_type_text(self, obj: Website):
        return obj.get_web_server_type_display()

    def get_database_name(self, obj: Website):

        if hasattr(obj, "database"):
            return obj.database.name

    def validate(self, data):

        return data
