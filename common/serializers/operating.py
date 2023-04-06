import subprocess
from rest_framework import serializers
from base.dataclass import BaseOperatingRes
from base.dataclass import BaseOperatingResEnum


class EmptySerializer(serializers.Serializer):
    pass


class QueryOperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)


class OperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)
    result = serializers.ChoiceField(
        choices=[(tag.name, tag.value) for tag in BaseOperatingResEnum], help_text="int")
    msg = serializers.CharField(max_length=256)
    result_text = serializers.CharField(max_length=72)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ExecuteCommandSyncSerializer(serializers.Serializer):

    cwd = serializers.CharField(max_length=255)
    command = serializers.CharField(max_length=1024)

    def create(self, validated_data):
        operator_res = BaseOperatingRes()
        cwd = validated_data.get('cwd')
        command = validated_data.get(
            'command').replace("  ", " ").replace("  ", " ")

        ret = subprocess.Popen(command, shell=True, cwd=cwd,
                               stdout=subprocess.PIPE)

        if ret.stdout:
            msg = ret.stdout.read().decode('utf-8').strip()
            operator_res.set_success()

        elif ret.stderr:
            msg = ret.stderr.read().decode('utf-8').strip()
            operator_res.set_failure()
        else:
            msg = ""

        operator_res.msg = msg

        return operator_res.json()


class ExecuteCommandAsyncSerializer(serializers.Serializer):
    """ 异步执行命令，返回event_id，通过event_id查询执行结果
    第一版方案: 使用多线程，通过event_id查询执行结果            
    """

    cwd = serializers.CharField(max_length=255)
    command = serializers.CharField(max_length=1024)

    def create(self, validated_data):
        operator_res = BaseOperatingRes()
        cwd = validated_data.get('cwd')
        command = validated_data.get('command').replace(
            "  ", " ").replace("  ", " ")
        ret = subprocess.Popen(command, shell=True, cwd=cwd,
                               stdout=subprocess.PIPE)

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
