import paramiko
from django.core.files import File
from paramiko.sftp_client import SFTPClient
from rest_framework import serializers

from base.serializer import ICBaseSerializer, ICBaseModelSerializer
from terminal.models import SFTPUploadModel
from websocket.utils import format_ssh_auth_data


class SFTPUploadSerializer(ICBaseModelSerializer):
    class Meta:
        model = SFTPUploadModel
        fields = '__all__'


class SSHAuthorization(ICBaseSerializer):
    hostname = serializers.CharField(min_length=3, max_length=128)
    port = serializers.IntegerField(min_value=0, max_value=65536)
    username = serializers.CharField(min_length=1)
    password = serializers.CharField(required=False, allow_blank=True)
    private_key = serializers.CharField(required=False, allow_blank=True)
    private_key_password = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


def get_sftp(_format) -> SFTPClient:
    print({'_format': _format})
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    auth_info = format_ssh_auth_data(_format)
    try:
        client.connect(timeout=5, **auth_info)
    except paramiko.ssh_exception.BadAuthenticationType as e:
        msg = f"connection failed: {e}"
        raise serializers.ValidationError(msg)
    except Exception as e:
        raise serializers.ValidationError(f'{e}')

    return client.open_sftp()


class UploadFileSerializer(ICBaseSerializer):
    auth = SSHAuthorization()
    file = serializers.FileField()
    target_path = serializers.CharField(max_length=768)

    def create(self, validated_data):
        file: File = validated_data.get('file')
        target_path = validated_data.get('target_path')
        auth = validated_data.get('auth')
        obj = SFTPUploadModel()
        obj.target_path = target_path
        obj.username = auth.get("username")
        obj.hostname = auth.get("hostname")
        obj.save()

        print(dict(auth))
        auth = format_ssh_auth_data(dict(auth))
        sftp = get_sftp(dict(auth))

        with sftp.file(target_path, "w") as f:
            for chunk in file.chunks():
                f.write(chunk)

        obj.status = obj.StatusType.SUCCESSFUL
        obj.save()

        return SFTPUploadSerializer(obj).data

    def update(self, instance, validated_data):
        pass
