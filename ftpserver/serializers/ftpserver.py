from rest_framework import serializers

from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from ftpserver.models.ftpserver import FtpServerModel


class FtpServerModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = FtpServerModel
        fields = "__all__"


class EmptySerializer(ICBaseSerializer):
    pass


class FtpServerPongSerializer(ICBaseSerializer):
    installed = serializers.BooleanField(default=False, required=False)
    run_status = serializers.BooleanField(default=False, required=False)

    def create(self, validated_data):
        return validated_data

    @staticmethod
    def get_data():
        from ftpserver.utils import ftpserver

        installed, status = ftpserver.ping()
        serializer = FtpServerPongSerializer(
            data={
                "installed": installed,
                "run_status": status,
            }
        )
        serializer.is_valid()
        return serializer.data
