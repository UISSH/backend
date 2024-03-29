from rest_framework import serializers

from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from webdav.models.webdav import WebDAVModel


class WebDAVModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = WebDAVModel
        fields = "__all__"


class EmptySerializer(ICBaseSerializer):
    pass


class WebDAVPongSerializer(ICBaseSerializer):
    installed = serializers.BooleanField(default=False, required=False)
    run_status = serializers.BooleanField(default=False, required=False)

    def create(self, validated_data):
        return validated_data

    @staticmethod
    def get_data():
        from webdav.utils import webdav

        installed, status = webdav.ping()
        serializer = WebDAVPongSerializer(
            data={
                "installed": installed,
                "run_status": status,
            }
        )
        serializer.is_valid()
        return serializer.data
