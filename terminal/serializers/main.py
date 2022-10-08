import os
import time

import paramiko
from django.core.files import File
from paramiko.sftp_client import SFTPClient
from rest_framework import serializers

from base.serializer import ICBaseSerializer, ICBaseModelSerializer
from base.utils.logger import plog
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
        file_obj: File = validated_data.get('file')
        target_path = validated_data.get('target_path')
        auth = validated_data.get('auth')
        obj = SFTPUploadModel()
        obj.target_path = target_path
        obj.username = auth.get("username")
        obj.hostname = auth.get("hostname")
        obj.save()

        auth = format_ssh_auth_data(dict(auth))
        tmp_file = f"/tmp/{time.time()}"
        plog.debug("write file to local.")
        with open(tmp_file, "wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        plog.debug("put file to remote.")
        sftp = get_sftp(auth)
        sftp.put(tmp_file, target_path)

        obj.status = obj.StatusType.SUCCESSFUL
        obj.save()
        os.system(f'rm -rf {tmp_file}')
        return SFTPUploadSerializer(obj).data

    def update(self, instance, validated_data):
        pass
