import pathlib
import shlex
import subprocess

from rest_framework import serializers

from base.dataclass import BaseOperatingRes
from base.serializer import ICBaseSerializer
from base.utils.logger import plog
from base.utils.os_query import os_query_json


class FileSerializer(ICBaseSerializer):
    path = serializers.CharField(
        max_length=1024, help_text='Absolute file path')
    directory = serializers.CharField(
        max_length=1024, help_text='Directory of file(s)')
    filename = serializers.CharField(
        max_length=1024, help_text='Name portion of file path')
    inode = serializers.IntegerField(help_text='Filesystem inode number')
    uid = serializers.IntegerField(help_text='Owning user ID')
    gid = serializers.IntegerField(help_text='Owning group ID')
    mode = serializers.CharField(max_length=32, help_text='Permission bits')
    device = serializers.IntegerField(help_text='Device ID (optional)')
    size = serializers.IntegerField(help_text='Size of file in bytes')
    block_size = serializers.IntegerField(help_text='block_size')
    atime = serializers.IntegerField(help_text='Last access time')
    mtime = serializers.IntegerField(help_text='Last modification time')
    ctime = serializers.IntegerField(help_text='Last status change time')
    btime = serializers.IntegerField(help_text='(B)irth or (cr)eate time')
    symlink = serializers.IntegerField(
        help_text='1 if the path is a symlink, otherwise 0')
    type = serializers.CharField(max_length=16, help_text='File status')


class UserSerializer(serializers.Serializer):
    uid = serializers.IntegerField()
    username = serializers.CharField(max_length=3)

    @staticmethod
    def get_users():
        data = os_query_json(f'SELECT uid,username from  users;')
        serializer = UserSerializer(data.out, many=True)
        return serializer


class UploadFileSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    file = serializers.FileField()


class TextOperatingSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=255)
    text = serializers.CharField(max_length=10 * 1024 * 1024)

    def create(self, validated_data):
        path = validated_data.get('path')
        text = validated_data.get('text')
        with open(path, 'w') as f:
            f.write(text)
        return validated_data

    def validate(self, attrs):
        path = attrs.get('path')
        if pathlib.Path(path).exists():
            return attrs
        raise serializers.ValidationError({'path': f"{path} does not exist."})


class ActionFileSerializer(serializers.Serializer):
    current_directory = serializers.CharField(max_length=255)
    operation_command = serializers.CharField(max_length=1024)

    def create(self, validated_data):
        operator_res = BaseOperatingRes()

        current_directory = validated_data.get('current_directory')
        operation_command = validated_data.get(
            'operation_command').replace("  ", " ").replace("  ", " ")
        ret = subprocess.Popen(operation_command, shell=True, cwd=current_directory,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if ret.stdout:
            msg = ret.stdout.read().decode('utf-8')
            operator_res.set_success()

        elif ret.stderr:
            msg = ret.stderr.read().decode('utf-8')
            operator_res.set_failure()
        else:
            msg = ""

        operator_res.msg = msg

        return operator_res.json()
